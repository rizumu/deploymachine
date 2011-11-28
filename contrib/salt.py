import os
import time
import openstack.compute

from fabric.api import env, run, cd
from fabric.contrib.files import contains, sed, uncomment
from fabric.contrib.project import rsync_project

from deploymachine.contrib.openstack_api import openstack_get_ip
from deploymachine.contrib.users import useradd
from deploymachine.conf import settings


def bootstrap_salt():
    """
    Install salt from github, update the settings, and start the daemons.
    """
    # @@@ these commands are arch linux specific 'python2', 'rc.conf'
    run("pacman -S --noconfirm rsync cython cython2 python2-jinja \
                                python2-yaml python-m2crypto pycrypto zeromq")

    run("git clone git://github.com/zeromq/pyzmq.git")
    with cd("pyzmq"):
        run("python2 setup.py install --optimize=1")

    run("git clone git://github.com/saltstack/salt.git")
    with cd("salt"):
        run("python2 setup.py install --optimize=1")
        run("cp pkg/arch/salt-* /etc/rc.d/ && chmod 755 /etc/rc.d/salt*")

    if is_saltmaster(public_ip=env.host):
        rsync_project("/srv/salt", "/home/rizumu/www/lib/salt-states/", delete=True)
        sed("/etc/rc.conf", "crond sshd", "crond sshd salt-master")
        run("/etc/rc.d/salt-master start")

    # all servers are minions, including the saltmaster
    sed("/etc/rc.conf", "crond sshd", "crond sshd salt-minion")
    sed("/etc/salt/minion", "\#master\: salt", "master: {0}".format(
        openstack_get_ip(settings.SALTMASTER, ip_type="private")))
    run("/etc/rc.d/salt-minion start")

    if is_saltmaster(public_ip=env.host):
        time.sleep(5)
        run("salt-key -A")  # @@@ don't accept all!

    run("/etc/rc.d/salt-master restart")
    run("/etc/rc.d/salt-minion restart")

    run("groupadd sshers")
    useradd("deploy")  # allow login to deploy account until ssh salt state is figured out

    if is_saltmaster(public_ip=env.host):
        run("salt '*' state.highstate")


def is_saltmaster(public_ip=None, server_name=None):
    """
    Returns ``True`` if the requested machine is the salt-master.
    Usage:
        fab is_saltmaster(server_name)
    """
    compute = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                        apikey=settings.OPENSTACK_APIKEY)
    for server in compute.servers.list():
        if (server.name == settings.SALTMASTER and
            (public_ip == server.public_ip or server_name == server.name)):
            return True
        elif public_ip == server.public_ip or server_name == server.name:
            return False
    return False
