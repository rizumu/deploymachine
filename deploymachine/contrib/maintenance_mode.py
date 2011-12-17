import os

from fabric.api import env, sudo
from fabric.decorators import task

import deploymachine_settings as settings


@task
def splash_on(site):
    "Put the 'maintenance' page up."
    sudo("cp {0} {1}".format(
          os.path.join(settings.DEPLOYMACHINE_ROOT, "maintenance.html"),
          os.path.join(settings.SITES_ROOT, site, "maintenance.html")),
          user=env.deploy_username)


@task
def splash_off(site):
    "Take the 'maintenance' page down."
    sudo("rm {0}".format(join(settings.SITES_ROOT, site, "maintenance.html")),
          user=env.deploy_username)
