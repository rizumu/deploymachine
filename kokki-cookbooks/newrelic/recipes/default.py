import os

from kokki import Execute, File, Template


Execute("pip install newrelic=={0}".format(env.config.newrelic.version))

File("{0}".format(env.config.newrelic.ini_file),
     content=Template("newrelic/newrelic.ini.j2"),
     owner="deploy",
     group="root",
     mode=0644)

File("{0}".format(env.config.newrelic.log_file),
     content="",
     owner="deploy",
     group="root",
     mode=0644)
