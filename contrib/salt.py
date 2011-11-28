import os
import time
import openstack.compute

from fabric.api import env, sudo
from fabric.contrib.files import sed
from fabric.contrib.project import rsync_project

from deploymachine.conf import settings
from deploymachine.contrib.openstack_api import openstack_get_ip
from deploymachine.contrib.users import useradd


def highstate(match="'*'"):
    """
    run salt state.highstate for the given hosts
    """
    # @@@ Make smart enough so that a minion may trigger highstate on saltmaster
    if is_saltmaster(public_ip=env.host):
        sudo("salt {0} state.highstate".format(match))


def upload_saltstates():
    """
    Sync local salt-states to the saltmaster
    """
    if is_saltmaster(public_ip=env.host):
        # @@@ private (get saltstate directories from config)
        # using `rsync_project` because `upload_project` fails for an unknown reason
        rsync_project("/tmp/salt-states-rsync", settings.SALTSTATES_LOCAL_ROOT, delete=True)
        sudo("rsync --recursive --links --times --compress --update --delete \
                    /tmp/salt-states-rsync/ /srv/salt/ && chown -R root:root /srv/salt/")


def is_saltmaster(public_ip=None, server_name=None):
    """
    Returns ``True`` if the requested machine is the salt-master.
    Usage:
        fab is_saltmaster(server_name)
    """
    compute = openstack.compute.Compute(username=settings.OPENSTACK_USERNAME,
                                        apikey=settings.OPENSTACK_APIKEY)
    for server in compute.servers.list():
        if (server.name == settings.SALTMASTER and
            (public_ip == server.public_ip or server_name == server.name)):
            return True
        elif public_ip == server.public_ip or server_name == server.name:
            return False
    return False
