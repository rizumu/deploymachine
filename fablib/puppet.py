import cloudservers

from deploymachine.conf import settings


def is_puppetmaster(public_ip=None, server_name=None):
    """
    Returns ``True`` if the requested machine is the puppetmaster.
    Usage:
        fab is_puppetmaster(server_name)
    """
    cs = cloudservers.CloudServers(settings.CUMULUS_USERNAME,
                                   settings.CUMULUS_API_KEY)
    for server in cs.servers.list():
        if (server.name == settings.PUPPETMASTER and
            (public_ip == server.public_ip or server_name == server.name)):
            return True
        elif public_ip == server.public_ip or server_name == server.name:
            return False
    print("Server not found!") #@@@ Raise an error instead?
    return False
