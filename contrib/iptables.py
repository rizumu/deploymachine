from fabric.api import env, sudo
from fabric.contrib.files import upload_template

from deploymachine.conf import settings


def iptables():
    """
    Cook the ip tables for the given role.
    Usage:
        fab appnode iptables
    """
    upload_template("templates/iptables.up.rules-{0}.j2".format("_".join(env.server_types)),
                    "/etc/iptables.up.rules", use_sudo=True, use_jinja=True,
                    context={"SSH_PORT": settings.SSH_PORT})
    sudo("iptables --flush")
    sudo("/sbin/iptables-restore < /etc/iptables.up.rules && \
          rm -rf /root/.ssh/ && reload ssh")
