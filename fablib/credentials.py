import os

from fabric.api import put
from fabric.contrib.files import append, exists

from deploymachine.conf import settings


def ssh():
    """
    Add or modify all of the machines SSH keys.

    For more info, see the installation documentation regarding SSH.
    """
    put("{0}/ssh/rackspacecloud_rsa".format(settings.DEPLOY_MACHINE_ROOT),
        "/home/deploy/.ssh/rackspacecloud_rsa", mode=0600)
    put("{0}/ssh/rackspacecloud_rsa.pub".format(settings.DEPLOY_MACHINE_ROOT),
        "/home/deploy/.ssh/rackspacecloud_rsa.pub", mode=0644)
    put("{0}/ssh/config".format(settings.DEPLOY_MACHINE_ROOT),
        "/home/deploy/.ssh/config", mode=0600)
    put("{0}/ssh/authorized_keys".format(settings.DEPLOY_MACHINE_ROOT),
        "/home/deploy/.ssh/authorized_keys", mode=0600)
    open("/tmp/authorized_keys", "w")
    for admin in settings.ADMIN_SSH_KEYS:
        append("/home/deploy/.ssh/authorized_keys", "# {0}".format(admin))
        append("{0}/ssh/authorized_keys".format(settings.DEPLOY_MACHINE_ROOT),
               open("{0}/ssh/{1}".format(settings.DEPLOY_MACHINE_ROOT, admin), "rb").read())


def gitconfig():
    """
    Add or modify all of the machines github config.
    """
    github_config = "\
    [github]\
        user = {0}\
        token = {1}\
    ".format(settings.GITHUB_USERNAME, settings.GITHUB_TOKEN)
    if exists("/home/deploy/.gitconfig"):
        os.remove("/home/deploy/.gitconfig")
    open("/home/deploy/.gitconfig", "w").close() 
    append("/home/deploy/.gitconfig", github_config)
