from os.path import join

from fabric.api import cd, run
from fabric.contrib.files import append
from fablib.credentials import ssh, gitconfig

from deploymachine.conf import settings


def useradd(username):
    """
    Adds a ``deploy`` user to the nodes.

    At one time DeployMachine handled creation of multiple user accounts, but
    now it only creates a deploy user. Adding addtitional users is better
    off handled in a kokki cookbook.
    """
    if username == settings.DEPLOY_USERNAME:
        if settings.DOTFILE_REPOSITORY:
            run("useradd --password {0} --groups wheel,sshers deploy".format(settings.DEPLOY_PASSWORD))
            run("git clone {0} {1}".format(settings.DOTFILE_REPOSITORY, settings.DEPLOY_HOME))
            append(join(settings.DEPLOY_HOME, "/.git/info/exclude"), "\*") # exclude everything from git
        else:
            run("useradd --password {0} --create-home --groups wheel,sshers deploy".format(settings.PASSWORD))
        with cd(settings.DEPLOY_HOME):
            run("mkdir .virtualenvs")
            run("mkdir --mode 700 .ssh/")
        run("chsh --shell /bin/bash deploy")
        ssh()
        gitconfig()
    else:
        raise NotImplementedError()
