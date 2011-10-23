import os
import openstack.compute

from deploymachine.conf import settings


def is_puppetmaster(public_ip=None, server_name=None):
    """
    Returns ``True`` if the requested machine is the puppetmaster.
    Usage:
        fab is_puppetmaster(server_name)
    """
    compute = openstack.compute.Compute(username=settings.OPEN_STACK_USERNAME,
                                        apikey=settings.OPEN_STACK_API_KEY)
    for server in compute.servers.list():
        if (server.name == settings.PUPPETMASTER and
            (public_ip == server.public_ip or server_name == server.name)):
            return True
        elif public_ip == server.public_ip or server_name == server.name:
            return False
    return False
