import errno
import os
import paramiko

from fabric.api import cd, env, local, run
from fabric.colors import green, red, yellow
from fabric.contrib.files import upload_template, sed, uncomment
from fabric.network import connect
from fabric.utils import abort

from deploymachine.conf import settings
from deploymachine.contrib.openstack_api import openstack_get_ips
from deploymachine.contrib.archlinux import bootstrap_archlinux
from deploymachine.contrib.ubuntu import bootstrap_ubuntu
from deploymachine.contrib.puppet import is_puppetmaster
from deploymachine.contrib.salt import is_saltmaster, bootstrap_salt
from deploymachine.contrib.users import useradd


def provision():
    """
    Provisions all unprovisioned servers.
    Usage:
        fab root provision

    .. warning::
        If you get the following error, kill the machine and try again:
        ``Server key was changed recently, or possible man-in-the-middle attack.``
        @@@ Figure out why this occasionaly happens and prevent it.

    .. note::
        For a new datacenter, use rankmirrors to generate a ``templates/mirrorlist``::
            $ cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
            $ sed '/^#\S/ s|#||' -i /etc/pacman.d/mirrorlist.backup
            $ rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist
    """
    # @@@ Consider checking if the server is still in the BUILD stage
    # preliminary testing to determine if machine can and should be provisioned
    if env.user != "root":
        abort("Must provision as root: ``fab root provision``")
    if settings.SSH_PORT == "22":
        abort("Security Error: change ``settings.SSH_PORT`` to something other than ``22``")
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=env.host, username=env.user)
        client.close()
    except EnvironmentError as exc:
        client.close()
        if exc.errno == errno.ECONNREFUSED:
            print(green("``{0}`` has already been provisioned, skipping".format(env.host)))
            return
        raise

    # permanently add server to the list of known hosts
    local("ssh {0}@{1} -o StrictHostKeyChecking=no &".format(env.user, env.host))

    # upgrade system and install base packages
    if settings.OPENSTACK_IMAGE == 55:
        bootstrap_archlinux()

    if settings.OPENSTACK_IMAGE == 115:
        bootstrap_ubuntu()

    # @@@ salt should setup the firewall!
    upload_template("templates/iptables.up.rules-provision.j2", "/etc/iptables.up.rules",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    sed("/etc/rc.conf", "syslog-ng network", "syslog-ng iptables network")

    bootstrap_salt()
