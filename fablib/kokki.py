from fabric.api import cd, env, local, sudo, put

from deploymachine.conf import settings
from deploymachine.fablib.dvcs.git import git_pull_deploy_machine
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.webservers.nginx import reload_nginx


def kokki(role, restart=False, new_style=False):
    """
    Cook all nodes for the given role.
    Usage:
        fab appnode kokki:appnode,restart=False,new_style=False
    """
    raise NotImplementedError() #needs upgrading
    git_pull_deploy_machine()
    put("{0}/kokki-config.yaml".format(settings.DEPLOY_MACHINE_ROOT),
        "/home/kokki/kokki-config.yaml".format(env.user), mode=0644)
    if new_style:
        cookbook_list = ["kcb-modified", "kcb-new", "kcb-unmodified"]
    else:
        cookbook_list = ["kokki-cookbooks"]
    for cookbook_dir in cookbook_list:
        local("rsync -avzp --rsh='ssh -p{0}' --delete {1}/{2}/ {3}:/home/{4}/{2}/".format(
               env.port, settings.DEPLOY_MACHINE_ROOT, cookbook_dir, env.host, env.user))
        with cd("/home/{0}/".format(env.user)):
            sudo("rm -rf {0}{1} && mv {1} {0}{1}".format(env.kokki_dir, cookbook_dir))
            sudo("chown -R {0}:{0} {1}{2}".format(
                  settings.KOKKI_USERNAME, env.kokki_dir, cookbook_dir))
    with cd(env.kokki_dir):
        sudo("kokki kokki-config.yaml {0}".format(role))
    if restart and role in ("appnode", "appbalancer"):
        reload_nginx()
        supervisor()
