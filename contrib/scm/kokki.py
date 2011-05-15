from os.path import join

from fabric.api import cd, env, local, sudo, put
from fabric.contrib.files import upload_template

from deploymachine.conf import settings
from deploymachine.contrib.dvcs.git import git_pull_deploymachine
from deploymachine.contrib.providers.openstack_api import openstack_get_ips
from deploymachine.contrib.supervisor import supervisor
from deploymachine.contrib.webservers.nginx import reload_nginx


def kokki(role, restart=False):
    """
    Cook all nodes for the given role.
    Usage:
        fab appnode kokki:appnode.dbserver.loadbalancer,restart=False
    """
    nodes = []
    for node in settings.OPENSTACK_SERVERS:
        if role in node["roles"]:
            nodes.append(node)
    if nodes == []: return
    public_ip_addresses = openstack_get_ips(env.server_types, port=settings.SSH_PORT, append_port=False)
    upload_template("kokki-config.j2", "/home/deploy/kokki-config.py",
                     context={"deploymachine_settings": settings}, use_jinja=True)
    for public_ip in public_ip_addresses:
        # put the local cookbooks on the server
        local("rsync -e 'ssh -p {0}' -avzp \
               {1}kokki-cookbooks/ deploy@{2}:/home/deploy/kokki-cookbooks/".format(
               settings.SSH_PORT, settings.DEPLOYMACHINE_LOCAL_ROOT, public_ip))
    # run kokki and restart the apps
    with cd(settings.DEPLOY_HOME):
        sudo("kokki -f kokki-config.py {0}".format(role))
    if restart and role == "appnode":
        reload_nginx()
        supervisor()
