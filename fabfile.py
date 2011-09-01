import os

from fabric.api import cd, env, local, sudo, put, run
from fabric.contrib.files import exists

from deploymachine.conf import settings
# Importing everything so commands are available to Fabric in the shell.
from deploymachine.contrib.fab import (venv, venv_local, root, appbalancer, appnode,
    dbserver, dbappbalancer, loadbalancer)
from deploymachine.contrib.providers.openstack_api import (openstack_list, openstack_boot,
    openstack_bootem, openstack_kill, openstack_sudokillem)
from deploymachine.contrib.credentials import ssh, gitconfig
from deploymachine.contrib.django import (collectstatic, generate_settings_local,
    generate_settings_main, generate_urls_main, syncdb, test)
from deploymachine.contrib.dvcs.git import git_pull, git_pull_deploymachine
from deploymachine.contrib.iptables import iptables
from deploymachine.contrib.logs import site_logs
from deploymachine.contrib.pip import pip_install, pip_requirements, pip_uninstall
from deploymachine.contrib.provision import provision
from deploymachine.contrib.scm.kokki import kokki
from deploymachine.contrib.scm.puppet import is_puppetmaster
from deploymachine.contrib.supervisor import supervisor
from deploymachine.contrib.users import useradd
from deploymachine.contrib.webservers.nginx import ensite, dissite, reload_nginx, reload_nginx
from deploymachine.contrib.webservers.maintenance_mode import splash_on, splash_off

# define domain specific fabric methods in fabfile_local.py, not tracked by git.
try:
    from fabfile_local import *
except ImportError:
    pass

"""
To view info on existing machines:
    openstack-compute list (or) fab openstack list
http://github.com/jacobian/openstack.compute for more info on the OpenStack API.

Aside from prelimiary customizations and ongoing maintenance...

    From start to finish:
        fab openstack_bootem
        fab root provision
        fab loadbalancer launch
        fab dbserver launch
        fab appbalancer launch
"""


def launch(template="template1"):
    """
    Launches all nodes in the given env: ./contrib/fab.py

    Usage:
        fab loadbalancer launch
        fab dbserver launch:template_postgis
        fab appnode launch
        fab appbalancer launch
    """
    if ("cachenode" or "brokernode") in env.server_types:
        raise NotImplementedError()

    iptables()

    for role in env.server_types:
        kokki(role)

    if "loadbalancer" in env.server_types:
        dissite(site="default")
        for site in settings.SITES:
            ensite(site=site["name"])

    if "dbserver" in env.server_types:
        if db_template == "template_postgis":
            sudo("createdb -E UTF8 template_postgis -T template0", user="postgres")  # Create the template spatial database.
            sudo("createlang -d template_postgis plpgsql", user="postgres")  # Adding PLPGSQL language support.
            sudo("psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\"", user="postgres")
            sudo("psql -d template_postgis -f $(pg_config --sharedir)/contrib/postgis.sql", user="postgres")  # Loading the PostGIS SQL routines
            sudo("psql -d template_postgis -f $(pg_config --sharedir)/contrib/spatial_ref_sys.sql", user="postgres")
            sudo("psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\"", user="postgres")  # Enabling users to alter spatial tables.
            sudo("psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\"", user="postgres")
        else:
            raise NotImplementedError

        for name, password in settings.DATABASES.iteritems():
            launch_db(name, password, db_template)

    if "appnode" in env.server_types:
        sudo("mkdir --parents /var/log/gunicorn/ /var/log/supervisor/ && chown -R deploy:www-data /var/log/gunicorn/")  # move to recipies
        if not exists(settings.LIB_ROOT):
            run("mkdir --parents {0}".format(settings.LIB_ROOT))
            with cd(settings.LIB_ROOT):
                run("git clone git@github.com:{0}/deploymachine.git && git checkout master".format(settings.GITHUB_USERNAME))
            with cd(settings.LIB_ROOT):
                # TODO move these into contrib_local
                run("git clone git@github.com:{0}/scenemachine.git scenemachine && git checkout master".format(settings.GITHUB_USERNAME))
                run("git clone git://github.com/pinax/pinax.git")
            with cd(settings.PINAX_ROOT):
                run("git checkout {0}".format(settings.PINAX_VERSION))
        # call an extra checkouts signal?
        launch_apps()


def unlaunch():
    """
    Undo the launch step, useful for debugging without reprovisioning.
    """
    sudo("rm -Rf {0}".format(settings.SITES_ROOT))


def launch_apps():
    "Launch all apps defined in ``settings_deploymachine.py``."
    for site in settings.SITES:
        launch_app(site["name"])
    supervisor()


def launch_app(site):
    """
    Launches a new django app by checking it out from github and building the
    virtualenv. Additionally the configuration management will need to be run
    to configure the webserver.
    """
    run("mkdir --parents {0}{1}/".format(settings.SITES_ROOT, site))
    if not exists("{0}{1}/{1}/".format(settings.SITES_ROOT, site)):
        with cd("{0}{1}/".format(settings.SITES_ROOT, site)):
            run("git clone --branch master git@github.com:{0}/{1}.git".format(settings.GITHUB_USERNAME, site))
    generate_virtualenv(site)
    generate_settings_local("prod", "scenemachine", site)  # TODO: remove hardcoded database name.
    generate_settings_main("prod", site)
    collectstatic(site)
    syncdb(site)


def generate_virtualenv(site):
    """
    Creates or rebuilds a site's virtualenv.
    TODO muliple envs for one site, aka predictable rollbacks.
    """
    run("rm -rf {0}{1}/".format(settings.VIRTUALENVS_ROOT, site))
    with cd(settings.VIRTUALENVS_ROOT):
        run("virtualenv --no-site-packages --distribute {0}".format(site, settings.DEPLOY_USERNAME))
    if not exists("{0}{1}/site-packages".format(settings.SITES_ROOT, site)):
        with cd("{0}{1}".format(settings.SITES_ROOT, site)):
            run("ln -s {0}{1}/lib/python{2}/site-packages".format(settings.VIRTUALENVS_ROOT, site, settings.PYTHON_VERSION))
    pip_requirements("prod", site)
    try:
        # Hack to add sylinks for personal libraries which aren't on pypi and therefore not in requirements.
        symlinks("prod", site)
    except ImportError:
        pass


def launch_db(name, password, db_template="template1"):
    """
    Launches a new database. Typically used when launching a new site.
    An alternative database template is ``template_postgis`` for GeoDjango.
    """
    sudo("createuser --no-superuser --no-createdb --no-createrole {0}".format(name), user="postgres")
    sudo("psql --command \"ALTER USER {0} WITH PASSWORD '{1}';\"".format(name, password), user="postgres")
    sudo("createdb --template {0} --owner {1} {1}".format(db_template, name), user="postgres")
