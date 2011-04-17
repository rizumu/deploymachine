from fabric.api import local, put, sudo
from jinja2 import Environment, PackageLoader

from deploymachine.conf import settings
from deploymachine.fablib.fab import venv, venv_local


def collectstatic(site=None):
    """
    Build the static media files.
    Usage:
        fab collectstatic:sitename
    """
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        venv("python manage.py collectstatic --noinput", site)

def generate_settings_main(connection, site=None):
    """
    Generate the site(s) main ``settings.py`` file.
    Usage:
        fab generate_settings_main:dev,sitename
    """
    project_module = getattr(settings, 'PROJECT_MODULE', "deploymachine")
    env = Environment(loader=PackageLoader("{0}".format(project_module),
                                           "templates_deploymachine"))
    template = env.get_template("scenemachine_settings_main.j2")
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        result = template.render(settings.SETTINGS_CUSTOM[site])
        if connection == "dev":
            r_file = open("{0}{1}/{1}/settings.py".format(
                settings.SITES_LOCAL_ROOT, site), "w")
            r_file.write(result)
            r_file.close()
        elif connection == "prod":
            print("not implemented yet")
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")


def generate_settings_local(connection, database, site=None):
    """
    Generate the site(s) settings_local files.
    Usage:
        fab generate_settings_local:dev,dbname,sitename
    """
    project_module = getattr(settings, 'PROJECT_MODULE', "deploymachine")
    env = Environment(loader=PackageLoader("{0}".format(project_module),
                                           "templates_deploymachine"))
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        if connection == "dev":
            template = env.get_template("scenemachine_settings_dev.j2")
            result = template.render(site=site)
            r_file = open("{0}{1}/{1}/settings_local.py".format(
                settings.SITES_LOCAL_ROOT, site), "w")
            r_file.write(result)
            r_file.close()
        elif connection == "prod":
            template = env.get_template("scenemachine_settings_prod.j2")
            result = template.render(site=site,
                                     psql_port=settings.PSQL_PORT,
                                     db_password=settings.DATABASES[database])
            print("not implemented yet")
            # use fabric to put template
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")


def generate_urls_main(connection, site=None):
    """
    Generate the site(s) main ``urls.py`` file.
    Usage:
        fab generate_urls_main:dev,sitename
    """
    project_module = getattr(settings, 'PROJECT_MODULE', "deploymachine")
    env = Environment(loader=PackageLoader("{0}".format(project_module),
                                           "templates_deploymachine"))
    template = env.get_template("scenemachine_urls_main.j2")
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        result = template.render(settings.SETTINGS_CUSTOM[site])
        if connection == "dev":
            r_file = open("{0}{1}/{1}/urls.py".format(
                settings.SITES_LOCAL_ROOT, site), "w")
            r_file.write(result)
            r_file.close()
        elif connection == "prod":
            print("not implemented yet")
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")


def syncdb(site):
    "Call syncdb for the given site."
    venv("python manage.py syncdb --noinput".format(site), site)


def test():
    "Run tests."
    local("python manage.py test")


#@@ migrations stuff
