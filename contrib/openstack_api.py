import os
import openstack.compute

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


def openstack_list():
    """
    List active nodes.
    Usage:
        fab openstack list
    """
    print(local("openstack-compute list"))


def openstack_boot(nodename, flavor=1, image=69):
    """
    Boot a new node.
    Optionally takes an image name/id from which to clone from, or a flavor type.
    Usage:
        fab openstack_boot:role,nodename
    """
    compute = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                        apikey=settings.OPENSTACK_API_KEY)
    if nodename in [server.name for server in compute.servers.list()]:
        print("``{0}`` has already been booted, skipping.".format(nodename))
        return
    try:
        image_id = int(image)
    except ValueError:
        for i in openstack.servers.api.images.list():
            if i.name == image:
                image_id = i.id
                break
        else:
            abort("Image not found. Run ``openstack image-list`` to view options.")
    local("openstack-compute boot --key {0} --image={1} --flavor={2} {3}".format(
           settings.SSH_PUBLIC_KEY, image_id, flavor, nodename))


def openstack_bootem():
    """
    Boots the nodes for all roles in ``OPENSTACK``.
    Optionally takes an image name/id from which to clone from.
    Usage:
        fab openstack_bootem
    """
    for node in settings.OPENSTACK_SERVERS:
        openstack_boot(node["nodename"], node["flavor"], node["image"])


def openstack_kill(nodename):
    """
    Kills a node.
    Usage:
        fab openstack_kill:nodename
    """
    local("openstack-compute delete {0} || true".format(nodename))


def openstack_sudokillem():
    """
    Kills all nodes, database too, be careful!
    Usage:
        fab openstack_sudokillem
    """
    for node in settings.OPENSTACK_SERVERS:
        openstack_kill(node["nodename"])


def openstack_get_ips(roles=[], port="22", ip_type="public", append_port=True):
    """
    Returns an ip list (public or private) of all nodes for the given role(s) or
    all nodes if no roles were provided. Optionally disable appending of the port number.
    Usage:
        fab openstack_get_ips(["appnode"], PORT, "private")
    """
    ips = []
    compute = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                        apikey=settings.OPENSTACK_API_KEY)
    for server in compute.servers.list():
        # Verify (by name) that the live server was defined in the settings.
        try:
            node = [n for n in settings.OPENSTACK_SERVERS if n['nodename'] == server.name][0]
        except IndexError:
            continue
        # If a ``roles`` list was passed in, verify it matches the node's roles.
        if roles and sorted(roles) != sorted(node["roles"]):
            continue
        if append_port:
            ips.append(server.addresses[ip_type][0] + ":" + port)
        else:
            ips.append(server.addresses[ip_type][0])
    return ips
