from os.path import join

from fabric.api import cd, env, run, lcd, local

from providers.openstack_api import openstack_get_ips
from deploymachine.conf import settings


def root():
    env.hosts = openstack_get_ips()
    env.user = "root"


def env_base(server_types):
    "This is the base from which all server types inherit from."
    env.user = settings.DEPLOY_USERNAME
    env.password = settings.DEPLOY_PASSWORD_RAW
    env.hosts = openstack_get_ips(server_types, settings.SSH_PORT)
    env.internal = openstack_get_ips(server_types, settings.SSH_PORT, "private")
    env.server_types = server_types


def loadbalancer():
    "Load balancer server type. Server specific settings here."
    env_base(["loadbalancer"])


def appnode():
    "Appplication node server type. Server specific settings here."
    env_base(["appnode"])


def broker():
    "Message queue broker server type."
    env_base(["broker"])


def dbserver():
    "Database environment server type. Server specific settings here."
    env_base(["dbserver"])


def appbalancer():
    "Combined ``loadbalancer`` and ``appnode`` environment specific settings."
    env_base(["appnode", "loadbalancer"])


def dbappbalancer():
    "Combined ``loadbalancer``, ``appnode``, ``dbserver`` environment specific settings."
    env_base(["appnode", "dbserver", "loadbalancer"])


def venv(command, site):
    "The Python virtual environment used on the servers."
    with cd("{0}{1}/{1}".format(settings.SITES_ROOT, site)):
        run("source {0} && {1}".format(
             join(settings.VIRTUALENVS_ROOT, site, "bin/activate"), command))


def venv_local(command, site):
    "The Python virtual environment used on the local machine."
    with lcd("{0}{1}/{1}/".format(settings.SITES_LOCAL_ROOT, site)):
        local("source {0} && {1}".format(
              join(settings.VIRTUALENVS_LOCAL_ROOT, site, "bin/activate"), command))
