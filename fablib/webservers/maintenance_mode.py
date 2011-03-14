from fabric.api import env, sudo

from deploymachine.conf import settings


def splash_on(site):
    "Put the 'maintenance' page up."
    sudo("cp {0}/maintenance.html /var/www/{1}/maintenance.html".format(
             settings.DEPLOY_MACHINE_ROOT, site), user=env.deploy_username)


def splash_off(site):
    "Take the 'maintenance' page down."
    sudo("rm /var/www/{0}/maintenance.html".format(site), user=env.deploy_username)
