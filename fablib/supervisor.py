from fabric.api import sudo

from deploymachine.conf import settings


def supervisor(process=None):
    """
    Kills all supervisor managed processes, or an individual one by name.
    Usage:
        fab appbalancer supervisor:gunicorn-snowprayers
    """
    if process is None:
        process_list = ["gunicorn-{0}".format(site) for site in settings.SITES]
    else:
        process_list = [process]
    for process in process_list:
        sudo("supervisorctl restart {0}".format(process))
