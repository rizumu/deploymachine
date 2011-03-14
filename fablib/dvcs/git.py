from fabric.api import env, cd, sudo

from deploymachine.conf import settings
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.fab import venv


def git_pull(site=None):
    """
    Update site(s) repository.
        fab appnode git-pull:sitename
    """
    if site is None:
        site_list = settings.SITES
    else:
        site_list = [site]
    for site in site_list:
        venv("git pull", site)
        supervisor("gunicorn-{0}".format(site))


def git_pull_deploy_machine():
    with cd(settings.DEPLOY_MACHINE_ROOT):
        sudo("git pull", user=env.deploy_username)


def git_log(site=None):
    "show last 3 commits"
    venv("git log -3", "rizumu")
    with cd(settings.SCENE_MACHINE_ROOT):
        sudo("git log -3", user=env.user)
    with cd(settings.PINAX_ROOT):
        sudo("git log -3", user=env.user)
