from fabric.api import sudo

from deploymachine.conf import settings
from deploymachine.contrib.newrelic import newrelic


def supervisor(process=None):
    """
    Kills all supervisor managed processes, or an individual process by name.
    Usage:
        fab appbalancer supervisor:gunicorn-snowprayers
    """
    if hasattr(settings, "NEWRELIC_PING_URL"):
        newrelic("disable")
    if process is None:
        sudo("supervisorctl restart all".format(process))
    else:
        sudo("supervisorctl restart {0}".format(process))
    if hasattr(settings, "NEWRELIC_PING_URL"):
        newrelic("enable")
