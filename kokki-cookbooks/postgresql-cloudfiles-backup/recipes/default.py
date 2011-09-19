import os
from kokki import Directory, Package, File, Template, Service


Package("python-rackspace-cloudfiles")
Package("duplicity")

Directory("{0}/dbdumps/".format(env.config.cloudfiles.deploy_home),
    owner = "postgres",
    group = "deploy",
    mode = 0750)

File("/etc/cron.d/dbdumps",
    owner = "postgres",
    group = "postgres",
    mode = 0644,
    content = Template("postgresql-cloudfiles-backup/cronfile.j2"),
)

File("{0}/duplicity_uploader.sh".format(env.config.cloudfiles.deploy_home),
    owner = "postgres",
    group = "postgres",
    mode = 0740,
    content = Template("postgresql-cloudfiles-backup/duplicity_uploader.sh.j2"),
)

File("{0}/duplicity_downloader.sh".format(env.config.cloudfiles.deploy_home),
    owner = "postgres",
    group = "postgres",
    mode = 0740,
    content = Template("postgresql-cloudfiles-backup/duplicity_downloader.sh.j2"),
)
