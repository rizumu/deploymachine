from fabric.api import cd, env, local, run, put
from fabric.contrib.files import append, upload_template

from deploymachine.conf import settings
from deploymachine.fablib.providers.rackspace import cloudservers_get_ips
from deploymachine.fablib.scm.puppet import is_puppetmaster
from deploymachine.fablib.users import useradd


def provisionem():
    """
    Provisions all nodes.
    Usage:
        fab root provisionem
    """
    public_ip_addresses = cloudservers_get_ips([role for role in settings.CLOUDSERVERS],
                                               append_port=False)
    for public_ip in public_ip_addresses:
        if is_puppetmaster(public_ip=public_ip):
            provision(public_ip, puppetmaster=True)
        else:
            provision(public_ip)


def provision(public_ip, puppetmaster=False):
    """
    Provisions a node.
    Usage:
        fab root provision:ip=127.0.0.1

    .. warning::
        If you get the following error, kill the machine and try again:
        ``Server key was changed recently, or possible man-in-the-middle attack.``
        @@@ Figure out why this occasionaly happens and prevent it.

    """
    if env.user != 'root':
        raise NotImplementedError()
    # system
    local("ssh {0}@{1} -o StrictHostKeyChecking=no &".format("root", public_ip))
    run("sed -i 's/universe/universe multiverse/g' /etc/apt/sources.list")
    run("/usr/sbin/locale-gen en_US.UTF-8 && /usr/sbin/update-locale LANG=en_US.UTF-8")
    run("aptitude update && aptitude -y safe-upgrade")
    run("aptitude install -y {0}".format(" ".join(settings.BASE_PACKAGES)))
    # users
    run("groupadd wheel && groupadd sshers")
    run("cp /etc/sudoers /etc/sudoers.bak")
    append("/etc/sudoers", "%wheel  ALL=(ALL) ALL")
    useradd("deploy")
    upload_template("templates/sshd_config.j2", "/etc/ssh/sshd_config",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    # pip/virtualenv on system python
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
        put("{0}kokki-config.py".format(settings.DEPLOYMACHINE_LOCAL_ROOT),
            "/home/deploy/kokki-config.py", mode=0644)
        local("rsync -avzp {0}kokki-cookbooks {1}@{2}:/home/deploy/kokki-cookbooks".format(
               settings.DEPLOYMACHINE_LOCAL_ROOT, "root", public_ip))
        run("chown -R {0}:{0} /home/{0}/".format("deploy"))
        run("pip install git+git://github.com/samuel/kokki#egg=kokki python-cloudservers=={0}".format(
             settings.PYTHON_CLOUDSERVERS_VERSION))
    if "chef" or "puppet" in settings.CONFIGURATORS:
        run("aptitude install -y ruby-dev rubygems rdoc")
        if "chef" in settings.CONFIGURATORS:
            run("gem install chef")
        if "puppet" in settings.CONFIGURATORS:
            if puppetmaster == True:
                run("aptitude install -y puppetmaster")
            run("gem install puppet")
            # https://github.com/uggedal/ddw-puppet # puppet example
    # firewall + prevent root login
    upload_template("templates/iptables.up.rules-provision.j2", "/etc/iptables.up.rules",
                    context={"SSH_PORT": settings.SSH_PORT}, use_jinja=True)
    put("{0}templates/iptables".format(settings.DEPLOYMACHINE_LOCAL_ROOT),
        "/etc/network/if-pre-up.d/iptables", mode=0755)
    run("/sbin/iptables-restore < /etc/iptables.up.rules && /etc/init.d/ssh reload")
