from fabric.api import local

from deploymachine.conf import settings
from deploymachine.fablib.fab import venv, venv_local


def pip_requirements(connection, site=None):
    """
    Run the pip requirements file for a project.
    Usage:
        fab appnode pip_requirements:prod,sitename
    """
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        if connection == "dev":
            venv_local("yes w | pip install -r requirements", site)
        elif connection == "prod":
            venv("yes w | pip install -r requirements.txt", site)
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")


def pip_install(connection, repo, package, path=None, version=None, site=None):
    """
    Run the pip requirements file for a project.
    Usage:
        fab pip_install:dev,git,django-oauth-access,git://github.com/eldarion,site=rizumu
        fab appnode pip_install:prod,pypi,Django,version=1.2.3,site=rizumu
    """
    if repo in ["git", "hg"]:
        fmt_egg = "{0}+{1}/{2}".format(repo, path, package)
        if version:
            fmt_egg += "@{0}".format(version)
        fmt_egg += "#egg={0}".format(package)
    elif repo == "pypi":
        fmt_egg = package
        if version:
            fmt_egg += "=={0}".format(version)
    else:
        print("Repo type does not exist, use git, hg, or pypi")
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        if connection == "dev":
            venv_local("pip install --ignore-installed {0}".format(fmt_egg), site)
        elif connection == "prod":
            venv("pip install --ignore-installed {0}".format(fmt_egg), site)
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")

def pip_uninstall(connection, package, site=None):
    """
    Run the pip requirements file for a project.
    Usage:
        fab pip_uninstall:dev,PIL,rizumu
        fab appnode pip_uninstall:prod,PIL,rizumu
    """
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        try:
            if connection == "dev":
                venv_local("pip uninstall --yes {0}".format(package), site)
            elif connection == "prod":
                venv("pip uninstall --yes {0}".format(package), site)
            else:
                print("Bad connection type. Use ``dev`` or ``prod``.")
        except:
            print('Cannot uninstall requirement {0} on site {1}, not installed'.format(package, site))
