import deploymachine
import os
import sys
import time

from httplib import CannotSendRequest
from ssl import SSLError

from fabric.api import local, put, run, sudo
from fabric.colors import green, red, yellow
from fabric.contrib.files import append, contains, exists, upload_template
from fabric.decorators import task

from jinja2 import Environment, PackageLoader

import deploymachine_settings as settings
from deploymachine.contrib.fab import venv, venv_local


@task
def staticfiles(site=None, wipe=False):
    """
    Collect, compress, and sync the static media files to rackspace.
    Usage:
        fab staticfiles:sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]

    if wipe:
        wipe = "--wipe"

    for site in sites:
        if not contains("{0}{1}".format(settings.SITES_ROOT, "static.log"), site):
            print(yellow(time.ctime()))
            venv("python manage.py collectstatic --noinput --verbosity=0", site)
            venv("python manage.py compress --verbosity=0", site)
            local("fab cachenode redis_flushdb:0")
            try:
                venv("python manage.py syncstatic {0}".format(wipe), site)
            except (SSLError, CannotSendRequest):
                print(red("syncstatic failed 1 time for {0}".format(site)))
                sleep(30)
                try:
                    venv("python manage.py syncstatic {0}".format(wipe), site)
                except (SSLError, CannotSendRequest):
                    print(red("syncstatic failed 2 times for {0}".format(site)))
                    sleep(30)
                    venv("python manage.py syncstatic {0}".format(wipe), site)
            append("{0}{1}".format(settings.SITES_ROOT, "static.log"), site)
            print(green("sucessfully collected/compressed/synced staticfiles for {0}".format(site)))
            print(green(time.ctime()))
    run("rm {0}{1}".format(settings.SITES_ROOT, "static.log"))
    if len(sites) > 1:
        print(green("sucessfully collected/compressed/synced staticfiles for all sites!".format(site)))


@task
def generate_settings_main(connection, site=None):
    """
    Generate the site(s) main ``settings.py`` file.
    Usage:
        fab generate_settings_main:dev,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        if connection == "dev":
            env = Environment(loader=PackageLoader("deploymachine", "templates"))
            template = env.get_template("settings_main.j2")
            result = template.render(settings.SETTINGS_CUSTOM[site])
            r_file = open("{0}{1}/{1}/settings.py".format(settings.SITES_LOCAL_ROOT, site), "w")
            r_file.write(result)
            r_file.close()
        elif connection == "prod":
            filename = "templates/settings_main.j2"
            destination = "{0}{1}/{1}/settings.py".format(settings.SITES_ROOT, site)
            context = settings.SETTINGS_CUSTOM[site]
            upload_template(filename, destination, context=context, use_jinja=True)
        else:
            print("Invalid connection type. Use ``dev`` or ``prod``.")


@task
def generate_settings_local(connection, database, site=None):
    """
    Generate the site(s) settings_local files.
    Usage:
        fab generate_settings_local:dev,dbname,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        if connection == "dev":
            env = Environment(loader=PackageLoader("deploymachine", "templates"))
            template = env.get_template("settings_local_dev.j2")
            result = template.render(site=site)
            r_file = open("{0}{1}/{1}/settings_local.py".format(settings.SITES_LOCAL_ROOT, site), "w")
            r_file.write(result)
            r_file.close()
        elif connection == "prod":
            filename = "templates/settings_local_prod.j2"
            destination = "{0}{1}/{1}/settings_local.py".format(settings.SITES_ROOT, site)
            context = {
                "site": site,
                "psql_port": settings.PGSQL_PORT,
                "redis_port": settings.REDIS_PORT,
                "db_password": settings.DATABASES[database],
                "openstack_username": settings.OPENSTACK_USERNAME,
                "openstack_api_key": settings.OPENSTACK_APIKEY,
            }
            upload_template(filename, destination, context=context, use_jinja=True)
        else:
            print("Invalid connection type. Use ``dev`` or ``prod``.")


@task
def generate_urls_main(connection, site=None):
    """
    Generate the site(s) main ``urls.py`` file.
    Usage:
        fab generate_urls_main:dev,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        if connection == "dev":
            env = Environment(loader=PackageLoader("deploymachine", "templates"))
            template = env.get_template("urls_main.j2")
            result = template.render(settings.SETTINGS_CUSTOM[site])
            r_file = open("{0}{1}/{1}/urls.py".format(settings.SITES_LOCAL_ROOT, site), "w")
            r_file.write(result)
            r_file.close()
        elif connection == "prod":
            filename = "templates/urls_main.j2"
            destination = "{0}{1}/{1}/settings_local.py".format(settings.SITES_ROOT, site)
            context = {
                "site": site,
                "psql_port": settings.PGSQL_PORT,
                "db_password": settings.DATABASES[database],
            }
            upload_template(filename, destination, context=context, use_jinja=True)
        else:
            print("Invalid connection type. Use ``dev`` or ``prod``.")


@task
def syncdb(site):
    "Call syncdb for the given site."
    venv("python manage.py syncdb --noinput".format(site), site)


@task
def test():
    "Run tests."
    local("python manage.py test")


# TODO: migrations stuff
