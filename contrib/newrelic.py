from fabric.api import local
from deploymachine.conf import settings


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
        key=settings.NEWRELIC_API_KEY)
    local("curl {url}{action} -X POST -H 'X-Api-Key: {key}'".format(**fmt_dict))

