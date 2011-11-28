import openstack.compute

from fabric.api import run

from deploymachine.conf import settings


def bootstrap_puppet():
    raise(NotImplementedError)
    run("apt-get install -y ruby-dev rubygems rdoc")
    if is_puppetmaster(public_ip=env.host):
        run("apt-get install -y puppetmaster")
    run("gem install puppet")


def is_puppetmaster(public_ip=None, server_name=None):
    """
    Returns ``True`` if the requested machine is the puppetmaster.
    Usage:
        fab is_puppetmaster(server_name)
    """
    compute = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                        apikey=settings.OPENSTACK_APIKEY)
    for server in compute.servers.list():
        if (server.name == settings.PUPPETMASTER and
            (public_ip == server.public_ip or server_name == server.name)):
            return True
        elif public_ip == server.public_ip or server_name == server.name:
            return False
    return False
