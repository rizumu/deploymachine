from kokki import Package, File, Template, Directory, Service


Package("monit")


Service("monit",
    supports_status=False,
    supports_restart=True,
    action="nothing")


File("%s/monitrc" % env.config.monit.config_path,
    owner="root",
    group="root",
    mode=0700,
    content=Template("monit/monitrc.j2"),
    notifies=[("restart", env.resources["Service"]["monit"])])


if env.system.platform == "ubuntu":
    File("/etc/default/monit",
        content=Template("monit/default.j2"),
        notifies=[("restart", env.resources["Service"]["monit"])])


Directory("%s/monit.d" % env.config.monit.config_path,
    owner="root",
    group="root",
    mode=0700)


Directory("/var/monit",
    owner="root",
    group="root",
    mode=0700)
