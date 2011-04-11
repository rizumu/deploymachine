from os.path import join

from fabric.api import cd, env, local, sudo, put

from deploymachine.conf import settings
from deploymachine.fablib.dvcs.git import git_pull_deploymachine
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.webservers.nginx import reload_nginx


def kokki(role, restart=False, new_style=False):
    """
    Cook all nodes for the given role.
    Usage:
        fab appnode kokki:appnode,restart=False,new_style=False
    """
    raise NotImplementedError() # needs testing
    # @@@ temp hack while upgrading kokki versions in progress
    if new_style:
        cookbook_list = ["kcb-modified", "kcb-new", "kcb-unmodified"]
    else:
        cookbook_list = ["kokki-cookbooks"]
    # put the local cookbooks on the server
    with cd(settings.DEPLOYMACHINE_HOME):
        local("git push")
    git_pull_deploymachine()
    # run kokki and restart the apps
    with cd(settings.DEPLOY_HOME):
        sudo("kokki kokki-config.yaml {0}".format(role))
    if restart and role in ("appnode", "appbalancer"):
        reload_nginx()
        supervisor()
