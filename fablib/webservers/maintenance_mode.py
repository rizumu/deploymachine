from fabric.api import env, sudo

from deploymachine.conf import settings


def splash_on(site):
    "Put the 'maintenance' page up."
    sudo("cp {0} {1}".format(
             join(settings.DEPLOYMACHINE_ROOT, "/maintenance.html")
             join(settings.SITES_ROOT, site, "/maintenance.html"), 
             user=env.deploy_username)


def splash_off(site):
    "Take the 'maintenance' page down."
    sudo("rm {0}".format(
             join(settings.SITES_ROOT, site, "maintenance.html"),
             user=env.deploy_username)
