from os.path import join

from fabric.api import cd, env, run, lcd, local

import deploymachine_settings as settings


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
    "Load balancer."
    env_base(["loadbalancer"])
    env.node_type = ["loadbalancer"]


def appnode():
    "Appplication node."
    env_base(["appnode"])
    env.node_type = ["appnode"]


def cachenode():
    "Redis cachenode and/or messagequeue."
    env_base(["cachenode"])
    env.node_type = ["cachenode"]


def broker():
    "Message queue broker. Use if RabbitMQ is desired over redis."
    env_base(["broker"])
    env.node_type = ["broker"]


def dbserver():
    "Database server."
    env_base(["dbserver"])
    env.node_type = ["dbserver"]


def appbalancer():
    "All-in-one, except the database, a combined ``loadbalancer``, ``appnode``, ``cachenode``"
    env_base(["loadbalancer", "appnode", "cachenode"])
    env.node_type = ["appbalancer"]


def allinone():
    "A true all-in-one, a combined ``loadbalancer``, ``appnode``, ``cachenode``, ``dbserver``."
    env_base(["loadbalancer", "appnode", "cachenode", "dbserver"])
    env.node_type = "allinone"


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
