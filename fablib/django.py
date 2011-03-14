from fabric.api import local, put, sudo

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


def settings_local(connection, site=None):
    """
    Copy the site(s) development local settings.
    Usage:
        fab settings:dev,sitename
    """
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        if connection == "dev":
            venv_local("cp {0}/settings_local_dev/{1}.py /var/www/{1}/settings_local.py".format(settings.DEPLOY_MACHINE_ROOT, site), site)
        elif connection == "prod":
            put("{0}/settings_local_prod/{1}.py".format(settings.DEPLOY_MACHINE_ROOT, site), "/tmp/settings_local.py", mode=0755)
            sudo("chown deploy:webmaster /tmp/settings_local.py && mv /tmp/settings_local.py /var/www/{0}/settings_local.py".format(site))
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")


def syncdb(site):
    "Call syncdb for the given site."
    venv("python manage.py syncdb --noinput".format(site), site)


def test():
    "Run tests."
    local("python manage.py test")


#@@ south stuff
