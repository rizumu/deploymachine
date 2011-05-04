from os.path import join

from fabric.api import cd, run
from fabric.contrib.files import append

from fablib.credentials import ssh, gitconfig

from deploymachine.conf import settings


def useradd(username):
    """
    Adds the ``deploy`` user to the nodes.

    ...note At one time DeployMachine handled creation of multiple user
    accounts, but now it only creates a single deploy user. Adding
    addtitional users is best taken care of in a kokki cookbook.
    """
    if settings.DOTFILE_REPOSITORY:
        run("useradd --password {0} --groups wheel,sshers deploy".format(settings.DEPLOY_PASSWORD_ENCRYPTED))
        run("git clone {0} {1}".format(settings.DOTFILE_REPOSITORY, settings.DEPLOY_HOME))
        append(join(settings.DEPLOY_HOME, ".git/info/exclude"), "\*") # exclude everything from git
    with cd(settings.DEPLOY_HOME):
        run("mkdir .virtualenvs")
        run("mkdir --mode 700 .ssh/")
    run("chsh --shell /bin/bash deploy")
    ssh()
    gitconfig()
