from fabric.api import env, cd, lcd, local

from deploymachine.conf import settings
from deploymachine.contrib.supervisor import supervisor
from deploymachine.contrib.fab import venv, venv_local


def git_pull(connection, site=None):
    """
    Checkout the site(s) repository.
        fab git_pull:dev
        fab git_pull:dev,sitename
        fab appnode git_pull:prod
        fab appnode git_pull:prod,sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        if connection == "dev":
            venv_local("git pull", site)
        elif connection == "prod":
            venv("git pull", site)
            supervisor("gunicorn-{0}".format(site))
        else:
            print("Bad connection type. Use ``dev`` or ``prod``.")


def git_pull_deploymachine():
    """
    Checkout the local deploymachine repository.
        fab appnode git_pull_deploymachine
    """
    with lcd(settings.DEPLOYMACHINE_LOCAL_ROOT):
        local("git pull")


def git_log(site=None):
    "show last 3 commits"
    venv("git log -3", "rizumu")
