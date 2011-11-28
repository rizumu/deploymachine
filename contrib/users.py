from crypt import crypt
from os.path import join

from fabric.api import cd, run
from fabric.contrib.files import append

from deploymachine.contrib.credentials import put_sshkeys, put_gitconfig

from deploymachine.conf import settings


def useradd(username):
    """
    Adds the ``deploy`` user to the nodes.

    ...note::
    At one time DeployMachine handled creation of multiple user
    accounts, but now, for simplicity, it only creates a single deploy user.
    Adding addtitional users, if desired, is best done via a confirguration
    management tool.
    """
    if settings.DOTFILE_REPOSITORY:
        run("useradd --password {0} --groups wheel,sshers deploy".format(settings.DEPLOY_PASSWORD_ENCRYPTED))
        run("git clone {0} {1}".format(settings.DOTFILE_REPOSITORY, settings.DEPLOY_HOME))
        append(join(settings.DEPLOY_HOME, ".git/info/exclude"), "\*")  # exclude everything from git
    else:
        run("mkdir {0}".format(settings.DEPLOY_HOME))
    with cd(settings.DEPLOY_HOME):
        run("mkdir .virtualenvs")
        run("mkdir --mode 700 .ssh/")
    run("chsh --shell /bin/bash deploy")
    put_sshkeys()
    put_gitconfig()
    run("chown -R {0}:{0} /home/{0}/".format(settings.DEPLOY_USERNAME))


def change_password(user):
    password = prompt("Enter a new password for user %s:" % user)
    crypted_password = crypt(password, "salt")
    sudo("usermod --password %s %s" % (crypted_password, user), pty=False)
