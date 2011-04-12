from os.path import join

from fabric.api import cd, env, sudo, local

from providers.rackspace import cloudservers_get_ips
from deploymachine.conf import settings


def root():
    env.hosts = cloudservers_get_ips([role for role in settings.CLOUDSERVERS])
    env.user = "root"
    env.github_username = settings.GITHUB_USERNAME


def env_base(server_types):
    "This is the base from which all server types inherit from."
    env.user = settings.DEPLOY_USERNAME
    env.password = settings.DEPLOY_PASSWORD_RAW
    env.github_username = settings.GITHUB_USERNAME
    env.hosts = cloudservers_get_ips(server_types, settings.SSH_PORT)
    env.internal = cloudservers_get_ips(server_types, settings.SSH_PORT, "private")
    env.python_version = settings.PYTHON_VERSION
    env.server_types = server_types


def loadbalancer():
    "Load balancer server type. Server specific settings here."
    env_base(["loadbalancer"])


def appnode():
    "Appplication node server type. Server specific settings here."
    env_base(["appnode"])


def dbserver():
    "Database environment server type. Server specific settings here."
    env_base(["dbserver"])


def appbalancer():
    "Combined ``loadbalancer`` and ``appnode`` environment specific settings."
    env_base(["appbalancer"])


def dbappbalancer():
    "Combined ``loadbalancer``, ``appnode``, ``dbserver`` environment specific settings."
    env_base(["dbappbalancer"])


def venv(command, site):
    "The Python virtual environment used on the servers."
    with cd("/var/www/{0}/{0}".format(site)):
        sudo("source {0} && {1}".format(
             join(settings.VIRTUALENVS_DIR, site, "/bin/activate"), command), user=env.user)


def venv_local(command, site):
    "The Python virtual environment used on the local machine."
    with cd(join(settings.VIRTUALENVS_DIR, site)):
        local("source {0} && {1}".format(
              join(settings.VIRTUALENVS_DIR, site, "/bin/activate"), command))
