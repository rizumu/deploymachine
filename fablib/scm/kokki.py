from os.path import join

from fabric.api import cd, env, local, sudo, put
from fabric.contrib.files import upload_template

from deploymachine.conf import settings
from deploymachine.fablib.dvcs.git import git_pull_deploymachine
from deploymachine.fablib.providers.rackspace import cloudservers_get_ips
from deploymachine.fablib.supervisor import supervisor
from deploymachine.fablib.webservers.nginx import reload_nginx


def kokki(roles, restart=False, new_style=False):
    """
    Cook all nodes for the given role.
    Usage:
        fab appnode kokki:appnode.dbserver.loadbalancer,restart=False,new_style=False
    """
    if type(roles) == str:
        roles = " ".join(roles.split('.'))
    elif type(roles) == list:
        roles = " ".join(roles)
    public_ip_addresses = cloudservers_get_ips([role for role in settings.CLOUD_SERVERS],
                                               append_port=False)
    upload_template("kokki-config.j2", "/home/deploy/kokki-config.py",
                     context={"deploymachine_settings": settings}, use_jinja=True)
    for public_ip in public_ip_addresses:
        # put the local cookbooks on the server
        local("rsync -e 'ssh -p {0}' -avzp \
               {1}kokki-cookbooks/ deploy@{2}:/home/deploy/kokki-cookbooks/".format(
               settings.SSH_PORT, settings.DEPLOYMACHINE_LOCAL_ROOT, public_ip))
    # run kokki and restart the apps
    with cd(settings.DEPLOY_HOME):
        sudo("kokki -f kokki-config.py {0}".format(roles))
    if restart and role == "appnode":
        reload_nginx()
        supervisor()
