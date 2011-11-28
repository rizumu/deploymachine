import openstack.compute

from fabric.api import run

from deploymachine.conf import settings


def bootstrap_chef():
    raise(NotImplementedError)
    run("apt-get install -y ruby-dev rubygems rdoc")
    run("gem install chef")


def is_chefserver(public_ip=None, server_name=None):
    """
    Returns ``True`` if the requested machine is the chefserver.
    Usage:
        fab is_chefserver(server_name)
    """
    compute = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                        apikey=settings.OPENSTACK_APIKEY)
    for server in compute.servers.list():
        if (server.name == settings.CHEFSERVER and
            (public_ip == server.public_ip or server_name == server.name)):
            return True
        elif public_ip == server.public_ip or server_name == server.name:
            return False
    return False
