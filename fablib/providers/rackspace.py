import os

import cloudservers
from fabric.api import local

from deploymachine.conf import settings


"""
Flavors:
    +----+---------------+-------+------+
    | ID |      Name     |  RAM  | Disk |
    +----+---------------+-------+------+
    | 1  | 256 server    | 256   | 10   |
    | 2  | 512 server    | 512   | 20   |
    | 3  | 1GB server    | 1024  | 40   |
    | 4  | 2GB server    | 2048  | 80   |
    | 5  | 4GB server    | 4096  | 160  |
    | 6  | 8GB server    | 8192  | 320  |
    | 7  | 15.5GB server | 15872 | 620  |
    +----+---------------+-------+------+
"""


def cloudservers_list():
    """
    List active nodes.
    Usage:
        fab boot:role,nodename
    """
    print(local("cloudservers list"))


def cloudservers_boot(role, nodename, flavor=1, image=settings.CLOUD_SERVERS_DEFAULT_IMAGE_ID):
    """
    Boot a new node.
    Optionally takes an image name/id from which to clone from, or a flavor type.
    Usage:
        fab boot:role,nodename
    """
    cs = cloudservers.CloudServers(os.environ.get("CLOUD_SERVERS_USERNAME"),
                                   os.environ.get("CLOUD_SERVERS_API_KEY"))
    if nodename in [i.name for i in cs.servers.list()]:
        print("``{0}`` has already been booted, skipping.".format(nodename))
        return
    try:
        image_id = int(image)
    except ValueError:
        for i in cs.servers.api.images.list():
            if i.name == image:
                image_id = i.id
                break
        else:
            abort("Image not found. Run ``cloudservers image-list`` to view options.")
    local("cloudservers boot --key {0} --image={1} --flavor={2} --meta role={3} {4}".format(
           settings.SSH_PUBLIC_KEY, image_id, flavor, role, nodename))


def cloudservers_bootem(image=settings.CLOUD_SERVERS_DEFAULT_IMAGE_ID):
    """
    Boots the nodes for all roles in ``CLOUDSERVERS``.
    Optionally takes an image name/id from which to clone from.
    Usage:
        fab bootem
    """
    for role, nodes in settings.CLOUDSERVERS.iteritems():
        for node in nodes:
            cloudservers_boot(role, node[0], node[1], image)


def cloudservers_kill(nodename):
    """
    Kills a node.
    Usage:
        fab cloudservers_kill:nodename
    """
    local("cloudservers delete {0} || true".format(nodename))


def cloudservers_sudokillem():
    """
    Kills all nodes, database too, be careful!
    Usage:
        fab killem
    """
    for role, nodes in settings.CLOUDSERVERS.iteritems():
        for node in nodes:
            cloudservers_kill(node[0])


def cloudservers_get_ips(roles, port="22", ip_type="public", append_port=True):
    """
    Returns an ip list (public or private) of all nodes for the given role(s).
    Usage:
        fab cloudservers_get_ips("appnode", PORT, "private")
    """
    ips = []
    cs = cloudservers.CloudServers(os.environ.get("CLOUD_SERVERS_USERNAME"),
                                   os.environ.get("CLOUD_SERVERS_API_KEY"))
    for server in cs.servers.list():
        for role in roles:
            if role == server.metadata["role"] and append_port:
                ips.append(server.addresses[ip_type][0] + ":" + port)
            if role == server.metadata["role"] and not append_port:
                ips.append(server.addresses[ip_type][0])
    return ips
