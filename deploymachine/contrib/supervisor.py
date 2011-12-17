import time
from fabric.api import sudo
from fabric.decorators import task

import deploymachine_settings as settings
from deploymachine.contrib.newrelic import newrelic


@task
def restart(process=None):
    """
    Kills all supervisor managed processes, or an individual process by name.
    Usage:
        fab appbalancer supervisor.restart:gunicorn-snowprayers
    """
    if hasattr(settings, "NEWRELIC_PING_URL"):
        newrelic("disable")
    if process is None:
        sudo("supervisorctl restart all".format(process))
    else:
        sudo("supervisorctl restart {0}".format(process))
    if hasattr(settings, "NEWRELIC_PING_URL"):
        time.sleep(10)
        newrelic("enable")
