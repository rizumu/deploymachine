import os
from kokki import Directory, Package, File, Template, Service

env.include_recipe("postgresql-cloudfiles-backup")

Package("python-rackspace-cloudfiles")

Directory("{0}db_backups/".format(env.config.cloudfiles.deploy_home),
    owner = "postgres",
    group = "deploy",
    mode = 0750)

File("/etc/cron.d/pgdump",
    owner = "postgres",
    group = "postgres",
    mode = 0644,
    content = Template("postgresql-cloudfiles-backup/cronfile.j2"),
)

File("{0}cloudfiles_uploader.py".format(env.config.cloudfiles.deploy_home),
    owner = "postgres",
    group = "postgres",
    mode = 0740,
    content = Template("postgresql-cloudfiles-backup/cloudfiles_uploader.py.j2"),
)
