from fabric.api import env, sudo
from fabric.contrib.files import upload_template

from deploymachine.conf import settings
from providers.openstack_api import openstack_get_ips


def iptables():
    """
    Cook the ip tables for the given role.
    Usage:
        fab appnode iptables
    """
    context = {
        "SSH_PORT": settings.SSH_PORT,
        "PGSQL_PORT": settings.PGSQL_PORT,
        "RABBITMQ_PORT": settings.RABBITMQ_PORT,
        "REDIS_PORT": settings.REDIS_PORT,
        "MUNIN_PORT": settings.MUNIN_PORT,
    }
    context["APPNODE_INTERNAL_IPS"] = openstack_get_ips(
        ["appnode"], port=settings.SSH_PORT, ip_type="private", append_port=False)
    context["LOADBALANCER_INTERNAL_IP"] = openstack_get_ips(
        ["loadbalancer"], port=settings.SSH_PORT, ip_type="private", append_port=False)[0]
    upload_template("templates/iptables.up.rules-{0}.j2".format("_".join(env.server_types)),
                    "/etc/iptables.up.rules", use_sudo=True, use_jinja=True, context=context)
    sudo("iptables --flush")
    sudo("/sbin/iptables-restore < /etc/iptables.up.rules && \
          rm -rf /root/.ssh/ && reload ssh")
