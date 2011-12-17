from fabric.api import local
from fabric.colors import red, yellow, green
from fabric.decorators import task

import deploymachine_settings as settings
from deploymachine.contrib.fab import venv, venv_local


@task
def pip_requirements(connection, site=None):
    """
    Run the pip requirements file for a project, or all projects.
    Usage:
        fab appnode pip_requirements:prod,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        print(green("started pip install for {0}".format(site)))
        if connection == "dev":
            venv_local("pip install --upgrade pip", site)
            venv_local("pip install --quiet --requirement=requirements.txt", site)
        elif connection == "prod":
            venv("pip install --upgrade pip", site)
            venv("pip install --quiet --requirement=requirements.txt", site)
        else:
            print(red("Bad connection type. Use ``dev`` or ``prod``."))
        print(green("finished pip install for {0}".format(site)))


@task
def pip_install(connection, repo, package, path=None, version=None, site=None, nodeps=False):
    """
    Install one package for a project, or all projects.
    Usage:
        fab pip_install:dev,git,django-oauth-access,git://github.com/eldarion,site=rizumu
        fab appnode pip_install:prod,pypi,Django,version=1.2.3,site=rizumu
    """
    if repo in ["git", "hg", "github"]:
        if repo == "github":
            path = "git://github.com/{0}".format(path)
            repo = "git"
        fmt_egg = "{0}+{1}/{2}".format(repo, path, package)
        if version:
            fmt_egg += "@{0}".format(version)
        fmt_egg += "#egg={0}".format(package)
    elif repo == "pypi":
        fmt_egg = package
        if version:
            fmt_egg += "=={0}".format(version)
    else:
        print(red("Repo type does not exist, use git, hg, or pypi"))
        raise(NotImplementedError)
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        args = ""
        if nodeps:
            args += "--no-dependencies"
        if connection == "dev":
            venv_local("pip install --ignore-installed {0} {1}".format(args, fmt_egg), site)
        elif connection == "prod":
            venv("pip install --ignore-installed {0} {1}".format(args, fmt_egg), site)
        else:
            print(red("Bad connection type. Use ``dev`` or ``prod``."))


@task
def pip_uninstall(connection, package, site=None):
    """
    Uninstall one package for a project, or all projects.
    Usage:
        fab pip_uninstall:dev,PIL,rizumu
        fab appnode pip_uninstall:prod,PIL,rizumu
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        try:
            if connection == "dev":
                venv_local("pip uninstall --yes {0}".format(package), site)
            elif connection == "prod":
                venv("pip uninstall --yes {0}".format(package), site)
            else:
                print(red("Bad connection type. Use ``dev`` or ``prod``."))
        except:
            print(red('Cannot uninstall requirement {0} on site {1}, not installed'.format(package, site)))
