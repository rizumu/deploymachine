import os

from fabric.api import cd, env, sudo, run, put
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import reboot

import deploymachine_settings as settings

# Importing everything so commands are available to Fabric in the shell.
from deploymachine.contrib import (django, dnsimple, fab, git, kokki, logs, nginx,
    maintenance_mode, newrelic, pip, postgresql, redis, salt, supervisor, virtualenv)
# define domain specific fabric methods in fabfile_local.py, not tracked by git.
try:
    import fabfile_local as local
except ImportError:
    pass


@task
def launch(dbtemplate="template_postgis"):
    """
    Launches all nodes in the given env: ./contrib/fab.py

    Usage:
        fab loadbalancer launch
        fab dbserver launch:template_postgis
        fab appnode launch
        fab cachenode launch
        fab appbalancer launch
    """
    raise NotImplementedError()
    if exists("{0}.launched".format(settings.DEPLOY_HOME)):
        print(green("``{0}`` has already been launched, skipping".format(env.host)))
        return

    # These Python packages are essential for bootstrapping.
    BASE_PYTHON_PACKAGES = [
        "Mercurial==2.0",
        "virtualenv==1.6.4",
        "Jinja2==2.6",
    ]
    if hasattr(settings, "EXTRA_BASE_PYTHON_PACKAGES"):
        BASE_PYTHON_PACKAGES.append(settings.EXTRA_BASE_PYTHON_PACKAGES)

    # python/pip setup
    # run("wget http://python-distribute.org/distribute_setup.py && python distribute_setup.py")
    # run("easy_install pip")
    # run("pip install {0}".format(" ".join(BASE_PYTHON_PACKAGES)))
    # run("pip install meld3==0.6.7")  # https://bugs.launchpad.net/ubuntu/+source/supervisor/+bug/777862

    # server type specifics
    if "broker" or "cachenode" in env.server_types:
        pass

    if "loadbalancer" in env.server_types:
        sudo("ls -hal")
        nginx.dissite(site="default")
        for site in settings.SITES:
            nginx.ensite(site=site["name"])

    if "dbserver" in env.server_types:
        reboot(10)  # Kokki changed the `shhmax` kernel settings, reboot required.
        if dbtemplate == "template_postgis":
            # http://proft.me/2011/08/31/ustanovka-geodjango-postgresql-9-postgis-pod-ubunt/
            with cd("/tmp/"):
                run("wget http://postgis.refractions.net/download/postgis-1.5.3.tar.gz")
                run("tar zxvf postgis-1.5.3.tar.gz")
            with cd("/tmp/postgis-1.5.3/"):
                sudo("./configure && make && checkinstall --pkgname postgis-1.5.3 --pkgversion 1.5.3-src --default")
            run("wget http://docs.djangoproject.com/en/dev/_downloads/create_template_postgis-1.5.sh -O /tmp/create_template_postgis-1.5.sh")
            run("chmod 777 /tmp/create_template_postgis-1.5.sh")
            sudo("/tmp/create_template_postgis-1.5.sh", user="postgres")
            sudo("rm -rf /tmp/*postgis*")
        else:
            raise NotImplementedError()

        for dbname, password in settings.DATABASES.iteritems():
            postgresql.pg_dblaunch(dbname, password, dbtemplate)

    if "appnode" in env.server_types:
        sudo("mkdir --parents /var/log/gunicorn/ /var/log/supervisor/ && chown -R deploy:www-data /var/log/gunicorn/")  # move to recipies
        sudo("ln -sf /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/")
        sudo("ln -sf /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/")
        sudo("ln -sf /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/")
        if not exists(settings.LIB_ROOT):
            run("mkdir --parents {0}".format(settings.LIB_ROOT))
            with cd(settings.LIB_ROOT):
                run("git clone git@github.com:{0}/deploymachine.git && git checkout master".format(settings.GITHUB_USERNAME))
            with cd(settings.LIB_ROOT):
                # TODO move these into a contrib_local list or call an extra checkouts signal?
                run("git clone git@github.com:{0}/scenemachine.git scenemachine && git checkout master".format(settings.GITHUB_USERNAME))
                run("git submodule init && git submodule update")
                run("git clone git://github.com/pinax/pinax.git")
            with cd(settings.PINAX_ROOT):
                run("git checkout {0}".format(settings.PINAX_VERSION))
        launch_apps()

    print(green("sucessfully launched!"))
    run("touch {0}.launched".format(settings.DEPLOY_HOME))


@task
def unlaunch_apps():
    """
    Undo the launch step for an app, useful for debugging without reprovisioning.
    """
    for site in settings.SITES:
        unlaunch_app(site["name"])


@task
def unlaunch_app(site):
    """
    Undo the launch step for an app, useful for debugging without reprovisioning.
    """
    run("rm -Rf {0}{1}/".format(settings.SITES_ROOT, site))


@task
def launch_apps():
    "Launch all apps defined in ``settings_deploymachine.py``."
    for site in settings.SITES:
        launch_app(site["name"])
    supervisor.restart()


@task
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
    virtualenv.generate_virtualenv("prod", site)
    django.generate_settings_local("prod", "scenemachine", site)  # TODO: remove hardcoded database name.
    django.generate_settings_main("prod", site)
    django.staticfiles(site)
    django.syncdb(site)
