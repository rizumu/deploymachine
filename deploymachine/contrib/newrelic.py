from fabric.api import local
from fabric.decorators import task

import deploymachine_settings as settings


@task
def newrelic(action):
    """
    Enable or disable pinging
    Usaage:
        fab newrelic:disable
        fab newrelic:enable
    """
    fmt_dict = dict(
        action=action,
        url=settings.NEWRELIC_PING_URL,
        key=settings.NEWRELIC_APIKEY)
    local("curl {url}{action} -X POST -H 'X-Api-Key: {key}'".format(**fmt_dict))

