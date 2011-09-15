
import os
from kokki import Directory, Package, File, Template, Service

env.include_recipe("postgresql9")

Service("postgresql",
    supports_restart = True,
    supports_reload = True,
    supports_status = True,
    action = "nothing")

Package("postgresql-9.1",
    notifies = [("stop", env.resources["Service"]["postgresql"], True)])
Package("postgresql-server-dev-9.1")
Package("postgresql-contrib-9.1")
Package("postgis")
Package("gdal-bin")
Package("binutils")
Package("libgeos-3.2.2")
Package("libgeos-c1")
Package("libgeos-dev")
Package("libgdal1-1.8.0")
Package("libgdal1-dev")
Package("libxml2")
Package("libxml2-dev")
Package("checkinstall")
Package("proj")

File("pg_hba.conf",
    owner = "postgres",
    group = "postgres",
    mode = 0600,
    path = os.path.join(env.config.postgresql9.config_dir, "pg_hba.conf"),
    content = Template("postgresql9/pg_hba.conf.j2"),
    notifies = [("reload", env.resources["Service"]["postgresql"])])

File("postgresql.conf",
    owner = "postgres",
    group = "postgres",
    mode = 0600,
    path = os.path.join(env.config.postgresql9.config_dir, "postgresql.conf"),
    content = Template("postgresql9/postgresql.conf.j2"),
    notifies = [("restart", env.resources["Service"]["postgresql"])])

File("30-postgresql-shm.conf",
    owner = "root",
    group = "root",
    mode = 0644,
    path = "/etc/sysctl.d/30-postgresql-shm.conf",
    content = Template("postgresql9/30-postgresql-shm.conf.j2"),
    notifies = [("restart", env.resources["Service"]["postgresql"])])
    # BUG requries reboot

Directory("/usr/share/postgresql/9.1/contrib/",
    owner = "root",
    group = "root",
    mode = 0655)

Directory("{0}db_backups/".format(env.config.deploy_home),
    owner = "postgres",
    group = "deploy",
    mode = 0750)

File("/etc/cron.d/pgdumpall",
    owner = "postgres",
    group = "postgres",
    mode = 0644,
    content = Template("postgresql9/cronfile.j2"),
)

File("{0}backup2cloudfiles.sh".format(env.config.deploy_home),
    owner = "postgres",
    group = "postgres",
    mode = 0740,
    content = Template("postgresql9/backup2cloudfiles.j2"),
)
