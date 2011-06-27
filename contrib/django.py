import deploymachine
import os
import sys

from fabric.api import local, put, sudo
from fabric.contrib.files import upload_template
from jinja2 import Environment, PackageLoader

from deploymachine.conf import settings
from deploymachine.contrib.fab import venv, venv_local


def collectstatic(site=None):
    """
    Build the static media files.
    Usage:
        fab collectstatic:sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        venv("python manage.py collectstatic --noinput", site)


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
                "db_password": settings.DATABASES[database],
                "openstack_username": settings.OPENSTACK_USERNAME,
                "openstack_api_key": settings.OPENSTACK_API_KEY,
            }
            upload_template(filename, destination, context=context, use_jinja=True)
        else:
            print("Invalid connection type. Use ``dev`` or ``prod``.")


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


def syncdb(site):
    "Call syncdb for the given site."
    venv("python manage.py syncdb --noinput".format(site), site)


def test():
    "Run tests."
    local("python manage.py test")


# TODO: migrations stuff
