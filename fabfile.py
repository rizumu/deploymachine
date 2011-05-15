from fabric.api import cd, env, local, sudo, put, run

from deploymachine.conf import settings
# Importing everything so commands are available to Fabric in the shell.
from deploymachine.fablib.fab import (venv, venv_local, root, appbalancer, appnode,
    dbserver, loadbalancer)
from deploymachine.fablib.providers.rackspace import (cloudservers_list, cloudservers_boot,
    cloudservers_bootem, cloudservers_kill, cloudservers_sudokillem)
from deploymachine.fablib.credentials import ssh, gitconfig
from deploymachine.fablib.django import (collectstatic, generate_settings_local,
    generate_settings_main, generate_urls_main, syncdb, test)
from deploymachine.fablib.dvcs.git import git_pull, git_pull_deploymachine
from deploymachine.fablib.iptables import iptables
from deploymachine.fablib.logs import site_logs
from deploymachine.fablib.pip import pip_install, pip_requirements, pip_uninstall
from deploymachine.fablib.provision import provision
from deploymachine.fablib.scm.kokki import kokki
from deploymachine.fablib.scm.puppet import is_puppetmaster
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.users import useradd
from deploymachine.fablib.webservers.nginx import ensite, dissite, reload_nginx, reload_nginx
from deploymachine.fablib.webservers.maintenance_mode import splash_on, splash_off

# define domain specific fabric methods in fabfile_local.py, not tracked by git.
try:
    from fabfile_local import *
except ImportError:
    pass

"""
To view info on existing machines:
    cloudservers list
http://github.com/jacobian/python-cloudservers for cloudservers api.

To launch system:
    fab cloudservers-bootem
    fab root provision
    fab dbserver launch:dbserver
    fab appbalancer launch:appbalancer
"""


def launch(roles):
    """
    Launches all nodes for the given roles.
    Usage:
        fab appbalancer launch:loadbalancer.appnode
    """
    roles = roles.split(".")
    if "cachenode" in roles:
        pass # raise NotImplementedError()
    iptables()
    kokki(roles)
    if "loadbalancer" in roles:
        dissite(site="default")
        for site in settings.SITES:
            ensite(site=site)
    if "appnode" in roles:
        sudo("aptitude build-dep -y python-psycopg2")
        sudo("mkdir --parents /var/log/gunicorn/ /var/log/supervisor/ && chown -R deploy:www-data /var/log/gunicorn/")
        run("mkdir --parents {0}".format(settings.LIB_ROOT))
        with cd(settings.LIB_ROOT):
            run("git clone git@github.com:{0}/deploymachine.git && git checkout master".format(env.github_username))
        with cd(settings.LIB_ROOT):
            # TODO move these into fablib_local
            run("git clone git@github.com:{0}/scenemachine.git scenemachine && git checkout master".format(env.github_username))
            run("git clone git://github.com/pinax/pinax.git")
        with cd(settings.PINAX_ROOT):
            run("git checkout {0}".format(settings.PINAX_VERSION))
    for site in settings.SITES:
        launch_app(site)
        syncdb(site)
        supervisor()
    if "dbserver" in roles:
        sudo("createdb -E UTF8 template_postgis", user="postgres") # Create the template spatial database.
        sudo("createlang -d template_postgis plpgsql", user="postgres") # Adding PLPGSQL language support.
        sudo("psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\"", user="postgres")
        sudo("psql -d template_postgis -f $(pg_config --sharedir)/contrib/postgis.sql", user="postgres") # Loading the PostGIS SQL routines
        sudo("psql -d template_postgis -f $(pg_config --sharedir)/contrib/spatial_ref_sys.sql", user="postgres")
        sudo("psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\"", user="postgres") # Enabling users to alter spatial tables.
        sudo("psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\"", user="postgres")
        for name, password in settings.DATABASES.iteritems():
            launch_db(name, password)


def unlaunch():
    """
    Undo the launch step, useful for debugging without reprovisioning.
    """
    sudo("rm -Rf {0}".format(settings.SITES_ROOT))


def launch_app(site):
    """
    Launches a new django app by checking it out from github and building the
    virtualenv. Additionally the configuration management will need to be run
    to configure the webserver.
    """
    run("mkdir --parents {0}{1}/".format(settings.SITES_ROOT, site))
    with cd("{0}{1}/".format(settings.SITES_ROOT, site)):
        run("git clone --branch master git@github.com:{0}/{1}.git".format(settings.github_username, site))
    generate_virtualenv(site)
    generate_settings_local("prod", site)
    generate_settings_main("prod", site)
    collectstatic(site)


def generate_virtualenv(site):
    """
    Creates or rebuilds a site's virtualenv.
    TODO muliple envs for one site, aka predictable rollbacks.
    """
    run("rm -rf {0}{1}/".format(settings.VIRTUALENVS_ROOT, site))
    with cd(settings.VIRTUALENVS_ROOT):
        run("virtualenv --no-site-packages --distribute {0}".format(site, settings.DEPLOY_USERNAME))
    with cd("{0}{1}".format(settings.SITES_ROOT, site)):
        run("ln -s {0}{1}/lib/python{2}/site-packages".format(settings.VIRTUALENVS_ROOT, site, settings.python_version))
    # egenix-mx-base is a strange psycopg2 dependency (http://goo.gl/paKd5 & http://goo.gl/nEG8n)
    venv("easy_install -i http://downloads.egenix.com/python/index/ucs4/ egenix-mx-base".format(site), site)
    pip_requirements("prod", site)
    try:
        # Hack to add sylinks for personal libraries which aren't on pypi and therefore not in requirements.
        symlinks("prod", site)
    except ImportError:
        pass


def launch_db(name, password, template="template1"):
    """
    Launches a new database. Typically used when launching a new site.
    An alternative template option is ``template_postgis`` for GeoDjango.
    """
    sudo("createuser --no-superuser --no-createdb --no-createrole {0}".format(name), user="postgres")
    sudo("psql --command \"ALTER USER {0} WITH PASSWORD '{1}';\"".format(name, password), user="postgres")
    sudo("createdb --template {0} --owner {1} {1}".format(template, name), user="postgres")
