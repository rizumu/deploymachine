from fabric.api import env, sudo
from fabric.contrib.files import upload_template

from deploymachine.conf import settings
from deploymachine.contrib.kokki import kokki
from deploymachine.contrib.openstack_api import openstack_get_ips


def iptables():
    """
    Change the ip tables for the given role.
    Usage:
        fab appnode iptables
    """
    sudo("rm /etc/iptables.up.rules")
    for role in env.server_types:
        kokki(role)
