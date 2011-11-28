from os.path import join

from fabric.api import put, run
from fabric.contrib.files import append, upload_template

from deploymachine.conf import settings


def put_sshkeys():
    """
    Add initial or update the machines SSH keys.

    For more info, see the installation documentation regarding SSH.
    """
    put(join(settings.DEPLOYMACHINE_LOCAL_ROOT, "ssh/rackspacecloud_rsa"),
        join(settings.DEPLOY_HOME, ".ssh/rackspacecloud_rsa"), mode=0600)
    put(join(settings.DEPLOYMACHINE_LOCAL_ROOT, "ssh/rackspacecloud_rsa.pub"),
        join(settings.DEPLOY_HOME, ".ssh/rackspacecloud_rsa.pub"), mode=0644)
    put(join(settings.DEPLOYMACHINE_LOCAL_ROOT, "ssh/config"),
        join(settings.DEPLOY_HOME, ".ssh/config"), mode=0600)
    # HACK to put an empty authorized_keys which personal pub keys are appended to
    put(join(settings.DEPLOYMACHINE_LOCAL_ROOT, "ssh/authorized_keys"),
        join(settings.DEPLOY_HOME, ".ssh/authorized_keys"), mode=0600)
    for admin in settings.ADMIN_SSH_KEYS:
        sshkey = join(settings.DEPLOYMACHINE_LOCAL_ROOT, "ssh/", admin)
        append(join(settings.DEPLOY_HOME, ".ssh/authorized_keys"), "# {0}".format(admin))
        append(join(settings.DEPLOY_HOME, ".ssh/authorized_keys"), open(sshkey, "rb").read())


def put_gitconfig():
    """
    Add or update the machines git config with your private github settings.
    """
    upload_template("templates/gitconfig.j2", join(settings.DEPLOY_HOME, ".gitconfig"),
                    context={
                        "GITHUB_USERNAME": settings.GITHUB_USERNAME,
                        "GITHUB_TOKEN": settings.GITHUB_TOKEN,
                    }, use_jinja=True)
