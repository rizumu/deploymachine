import errno
import paramiko

from fabric.api import cd, env, local, run, put
from fabric.contrib.files import append, upload_template
from fabric.network import connect
from fabric.utils import abort

from deploymachine.conf import settings
from deploymachine.contrib.openstack_api import openstack_get_ips
from deploymachine.contrib.puppet import is_puppetmaster
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

    """
    # @@@ Check if the server is still in the BUILD stage
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
            print("``{0}`` has already been provisioned, skipping".format(env.host))
            return
        else:
            raise
    # system setup
    local("ssh {0}@{1} -o StrictHostKeyChecking=no &".format(env.user, env.host))
    run("sed -i 's/universe/universe multiverse/g' /etc/apt/sources.list")
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("apt-get update && apt-get -y dist-upgrade")
    run("apt-get install -y {0}".format(" ".join(settings.BASE_OS_PACKAGES)))
    # python/pip setup
    run("wget http://python-distribute.org/distribute_setup.py && python distribute_setup.py")
    run("easy_install pip")
    run("pip install {0}".format(" ".join(settings.BASE_PYTHON_PACKAGES)))
    run("pip install meld3==0.6.7")  # https://bugs.launchpad.net/ubuntu/+source/supervisor/+bug/777862
    # deploy user setup
    run("groupadd wheel && groupadd sshers")
    run("cp /etc/sudoers /etc/sudoers.bak")
    append("/etc/sudoers", "%wheel  ALL=(ALL) ALL")
    useradd("deploy")
    upload_template("templates/sshd_config.j2", "/etc/ssh/sshd_config",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    # software configuration management
    if "kokki" in settings.CONFIGURATORS:
        run("pip install git+git://github.com/samuel/kokki#egg=kokki \
                         git+git://github.com/jacobian/openstack.compute#egg=openstack_compute")
    if "chef" in settings.CONFIGURATORS:
        raise(NotImplementedError)
        run("apt-get install -y ruby-dev rubygems rdoc")
        run("gem install chef")
    if "puppet" in settings.CONFIGURATORS:
        raise(NotImplementedError)
        if is_puppetmaster(public_ip=env.host):
            run("apt-get install -y puppetmaster")
        run("gem install puppet")
    run("chown -R {0}:{0} /home/{0}/".format("deploy"))
    # firewall + prevent root login
    upload_template("templates/iptables.up.rules-provision.j2", "/etc/iptables.up.rules",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    put("{0}templates/iptables".format(settings.DEPLOYMACHINE_LOCAL_ROOT),
        "/etc/network/if-pre-up.d/iptables", mode=0755)
    run("/sbin/iptables-restore < /etc/iptables.up.rules && reload ssh")
