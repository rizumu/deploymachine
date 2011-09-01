import errno
import paramiko

from fabric.api import cd, env, local, run, put
from fabric.contrib.files import append, upload_template
from fabric.network import connect
from fabric.utils import abort

from deploymachine.conf import settings
from deploymachine.contrib.providers.openstack_api import openstack_get_ips
from deploymachine.contrib.scm.puppet import is_puppetmaster
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
    # preliminary testing to determine if machine can and should be provisioned
    if env.user != "root":
        abort("Must provision as root: ``fab root provision``")
    if settings.SSH_PORT == "22":
        abort("Must change ``settings.SSH_PORT`` to something other than ``22``")
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=env.host, username=env.user)
        client.close()
    except EnvironmentError as exc:
        client.close()
        if exc.errno == errno.ECONNREFUSED:
            print("{0} is already provisioned".format(env.host))
            return
        else:
            raise
    # system setup
    local("ssh {0}@{1} -o StrictHostKeyChecking=no &".format(env.user, env.host))
    run("sed -i 's/universe/universe multiverse/g' /etc/apt/sources.list")
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("aptitude update && aptitude -y safe-upgrade")
    run("aptitude install -y {0}".format(" ".join(settings.BASE_PACKAGES)))
    # deploy user setup
    run("groupadd wheel && groupadd sshers")
    run("cp /etc/sudoers /etc/sudoers.bak")
    append("/etc/sudoers", "%wheel  ALL=(ALL) ALL")
    useradd("deploy")
    upload_template("templates/sshd_config.j2", "/etc/ssh/sshd_config",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    # pip/virtualenv for system python
    with cd("/tmp/"):
        run("curl --remote-name http://python-distribute.org/distribute_setup.py")
        run("python distribute_setup.py && rm distribute*")
        run("git clone git://github.com/xvzf/vcprompt.git")
    with cd("/tmp/vcprompt/"):
        run("python setup.py install && rm -rf /tmp/vcprompt/")
    run("easy_install pip && pip install virtualenv")
    # software configuration management
    if "kokki" in settings.CONFIGURATORS:
        run("aptitude install -y python-jinja2")
        run("pip install git+git://github.com/samuel/kokki#egg=kokki \
                         git+git://github.com/jacobian/openstack.compute#egg=openstack_compute")
    if "chef" or "puppet" in settings.CONFIGURATORS:
        run("aptitude install -y ruby-dev rubygems rdoc")
        if "chef" in settings.CONFIGURATORS:
            run("gem install chef")
        if "puppet" in settings.CONFIGURATORS:
            if is_puppetmaster(public_ip=env.host):
                run("aptitude install -y puppetmaster")
            run("gem install puppet")
    run("chown -R {0}:{0} /home/{0}/".format("deploy"))
    # firewall + prevent root login
    upload_template("templates/iptables.up.rules-provision.j2", "/etc/iptables.up.rules",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    put("{0}templates/iptables".format(settings.DEPLOYMACHINE_LOCAL_ROOT),
        "/etc/network/if-pre-up.d/iptables", mode=0755)
    run("/sbin/iptables-restore < /etc/iptables.up.rules && reload ssh")
