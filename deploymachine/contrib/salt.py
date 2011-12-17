from fabric.api import env, sudo
from fabric.contrib.project import rsync_project
from fabric.decorators import task

import deploymachine_settings as settings


@task
def highstate(match="'*'"):
    """
    run salt state.highstate for the given hosts
    """
    # @@@ Make smart enough so that a minion may trigger highstate on saltmaster
    sudo("salt {0} state.highstate".format(match))


@task
def upload_saltstates():
    """
    Sync local salt-states to the saltmaster
    """
    # @@@ private (get saltstate directories from config)
    # using `rsync_project` because `upload_project` fails for an unknown reason
    rsync_project("/tmp/salt-states-rsync", settings.SALTSTATES_LOCAL_ROOT, delete=True)
    sudo("rsync --recursive --links --times --compress --update --delete \
                /tmp/salt-states-rsync/ /srv/salt/ && chown -R root:root /srv/salt/")
