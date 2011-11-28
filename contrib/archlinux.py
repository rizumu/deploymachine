import os
import time

from fabric.api import cd, env, run
from fabric.contrib.files import append, put, sed, uncomment

from deploymachine.conf import settings
from deploymachine.contrib.openstack_api import openstack_get_ip
from deploymachine.contrib.salt import is_saltmaster, upload_saltstates


def bootstrap_archlinux(action="install"):
    # The following core packages are essential for bootstrapping.
    BASE_PACKAGES = [
        "base-devel",
        "curl",
        "git",
        "yaourt",
    ]
    if hasattr(settings, "EXTRA_BASE_ARCHLINUX_PACKAGES"):
        BASE_PACKAGES.append(settings.EXTRA_BASE_ARCHLINUX_PACKAGES)

    # setup pacman/yaourt and install base packages
    uncomment("/etc/pacman.d/mirrorlist", "Server")
    run("pacman -Syu --noconfirm")
    run("pacman-db-upgrade")
    put(os.path.join(settings.DEPLOYMACHINE_LOCAL_ROOT, "templates/mirrorlist"), "/etc/pacman.d/mirrorlist")
    run("rm /etc/profile.d/locale.sh")
    append("/etc/pacman.conf", "\n[archlinuxfr]\nServer = http://repo.archlinux.fr/$arch", use_sudo=True)
    run("pacman -Syu --noconfirm")
    run("pacman -S --noconfirm {0}".format(" ".join(BASE_PACKAGES)))

    bootstrap_salt_github()


def bootstrap_salt_github():
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

    upload_saltstates()

    if is_saltmaster(public_ip=env.host):
        sed("/etc/rc.conf", "crond sshd", "crond sshd salt-master")
        run("/etc/rc.d/salt-master start")

    # setup all servers as minions, including the saltmaster
    # @@@ consider breaking out to a boot_minion method
    # @@@ make `get_ip`` provider agnostic so it can work with S3
    sed("/etc/rc.conf", "crond sshd", "crond sshd salt-minion")
    sed("/etc/salt/minion", "\#master\: salt", "master: {0}".format(
        openstack_get_ip(settings.SALTMASTER, ip_type="private")))
    run("/etc/rc.d/salt-minion start")

    if is_saltmaster(public_ip=env.host):
        time.sleep(5)
        run("salt-key -A")  # @@@ don't accept all!

    run("/etc/rc.d/salt-master restart")
    run("/etc/rc.d/salt-minion restart")
