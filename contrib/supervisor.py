from fabric.api import sudo

from deploymachine.conf import settings


def supervisor(process=None):
    """
    Kills all supervisor managed processes, or an individual one by name.
    Usage:
        fab appbalancer supervisor:gunicorn-snowprayers
    """
    process_list = []
    if process is None:
        sudo("supervisorctl restart all".format(process))
    else:
        sudo("supervisorctl restart {0}".format(process))
