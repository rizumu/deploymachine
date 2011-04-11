import os
import sys

from fabric.api import cd, env, local, sudo, put

from deploymachine.conf import settings
# Importing so commands are available to Fabric in the shell.
# @@@ make more generic, this is ugly
from deploymachine.fablib.fab import (venv, venv_local, root, appbalancer, appnode,
    dbserver, loadbalancer)
from deploymachine.fablib.bootstrap.rackspace import (cloudservers_list, cloudservers_boot,
    cloudservers_bootem, cloudservers_kill, cloudservers_sudokillem)
from deploymachine.fablib.credentials import ssh, gitconfig
from deploymachine.fablib.django import collectstatic, settings_local, syncdb, test
from deploymachine.fablib.dvcs.git import git_pull, git_pull_deploymachine
from deploymachine.fablib.iptables import iptables
from deploymachine.fablib.logs import site_logs
from deploymachine.fablib.pip import pip_install, pip_requirements, pip_uninstall
from deploymachine.fablib.provision import provisionem, provision
from deploymachine.fablib.scm.kokki import kokki
from deploymachine.fablib.scm.puppet import is_puppetmaster
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.users import useradd
from deploymachine.fablib.webservers.nginx import ensite, dissite, reload_nginx, reload_nginx
from deploymachine.fablib.webservers.maintenance_mode import splash_on, splash_off

"""
To view info on existing machines:
    cloudservers list
http://github.com/jacobian/python-cloudservers for cloudservers api.

To launch system:
    fab cloudservers-bootem
    fab root provisionem
    fab dbserver launch:dbserver
    fab appbalancer launch:appbalancer
"""

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


def launch(role):
    """
    Launches all nodes for the given role.
    Usage:
        fab loadbalancer launch:loadbalancer
    """
    if role in ("cachenode"):
        raise NotImplementedError()
    iptables()
    kokki(role)
    if role in ("appbalancer", "loadbalancer"):
        dissite(name="default")
        for site in settings.SITES:
            ensite(name=site)
    if role in ("appbalancer", "appnode"):
        sudo("aptitude build-dep -y python-psycopg2")
        sudo("groupadd --force webmaster")
        useradd(env.user, env.password)
        sudo("mkdir --parents /var/log/gunicorn/ /var/log/supervisor/ && chown -R deploy:www-data /var/log/gunicorn/")
        sudo("mkdir --parents {0} && chown -R deploy:webmaster {1} {2}".format(settings.LIB_ROOT, settings.SITES_ROOT, user=env.user))
        with cd(settings.LIB_ROOT):
            sudo("git clone git@github.com:{0}/deploy-machine.git && git checkout master".format(env.github_username), user=env.user)
        # http://www.saltycrane.com/blog/2009/07/using-psycopg2-virtualenv-ubuntu-jaunty/
        with cd(settings.LIB_ROOT):
            sudo("git clone git@github.com:{0}/scene-machine.git django-scene-machine && git checkout master".format(env.github_username), user=env.user)
            sudo("git clone git://github.com/pinax/pinax.git && git checkout {0}".format(settings.PINAX_VERSION), user=env.user)
        for site in settings.SITES:
            launch_app(site)
            syncdb(site)
        supervisor()
    if role == "dbserver":
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
    sudo("userdel --remove deploy && rm -Rf /var/www/")


def launch_app(site):
    """
    Launches a new django app by checking it out from github and building the
    virtualenv. Additionally the configuration management will need to be run
    to configure the webserver.
    """
    sudo("mkdir --parents /var/www/{0}/".format(site), user=env.user)
    with cd("/var/www/{0}/".format(site)):
        sudo("git clone git@github.com:{0}/{1}.git &&\
              git checkout master".format(env.github_username, site), user=env.user)
    settings_local("prod", site)
    generate_virtualenv(site)


def generate_virtualenv(site):
    """
    Creates or rebuilds a site's virtualenv.
    @@@ Todo, allow for muliple envs for one project. A la predictable rollbacks.
    """
    if "/home/{0}/.virtualenvs/{1}/".format(env.user, site):
        sudo("rm -rf /home/{0}/.virtualenvs/{1}/".format(env.user, site))
    with cd("/home/{0}/.virtualenvs/".format(env.user)):
        sudo("virtualenv --no-site-packages --distribute {0}".format(site, env.user), user=env.user)
    with cd("/var/www/{0}/".format(site)):
        sudo("ln -s /home/deploy/.virtualenvs/{0}/lib/python{1}/site-packages".format(site, env.python_version), user=env.user)
    venv("curl --remote-name http://python-distribute.org/distribute_setup.py &&\
          python distribute_setup.py && rm distribute*".format(site), site)
    # i forget exactly why we need to additionally install egenix-mx-base here
    # probably a psycopg2 dependency (see http://goo.gl/nEG8n)
    venv("easy_install -i http://downloads.egenix.com/python/index/ucs4/ egenix-mx-base".format(site), site)
    venv("easy_install pip && pip install virtualenv PyYaml".format(site), site)
    venv("ln -s ../settings_local.py", site)
    pip_requirements("prod", site)
    symlinks(site)
    collectstatic(site)


def launch_db(name, password):
    """
    Launches a new database. Typically used when launching a new site.
    @@@ template_postgis as a setting?
    """
    sudo("createuser --no-superuser --no-createdb --no-createrole {0}".format(name), user="postgres")
    sudo("psql --command \"ALTER USER {0} WITH PASSWORD '{1}';\"".format(name, password), user="postgres")
    sudo("createdb --template template_postgis --owner {0} {0}".format(name), user="postgres")


# define domain specific fabric methods in fabfile_local.py, not tracked by git.
try:
    from fabfile_local import *
except ImportError:
    pass
