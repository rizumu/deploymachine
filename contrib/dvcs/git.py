from fabric.api import env, cd, sudo

from deploymachine.conf import settings
from deploymachine.contrib.supervisor import supervisor
from deploymachine.contrib.fab import venv


def git_pull(site=None):
    """
    Update site(s) repository.
        fab appnode git-pull:sitename
    """
    if site is None:
        sites = [site["name"] for site in settings.SITES]
    else:
        sites = [site]
    for site in sites:
        venv("git pull", site)
        supervisor("gunicorn-{0}".format(site))


def git_pull_deploymachine():
    with cd(settings.DEPLOYMACHINE_ROOT):
        sudo("git pull", user=settings.DEPLOY_USERNAME)


def git_log(site=None):
    "show last 3 commits"
    venv("git log -3", "rizumu")
