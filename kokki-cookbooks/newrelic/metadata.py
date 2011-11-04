
__description__ = "New Relic settings"
__config__ = {
    "newrelic.version": dict(
        description="Version of newrelic agent to install from pypi",
        default="0.5.58.122",
    ),
    "newrelic.license_key": dict(
        description="License key for newrelic agent",
        default=None,
    ),
    "newrelic.ini_file": dict(
        description="Location for the newrelic ini file",
        default="/etc/newrelic.ini",
    ),
    "newrelic.log_file": dict(
        description="Location for newrelic agent log file",
        default="/var/log/newrelic-python-agent.log",
    ),
    "newrelic.application_name": dict(
        description="Name of application as shown in the New Relic UI.",
        default="Python Application",
    ),
}
