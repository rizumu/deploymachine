from kokki import Package, File, Execute, Template


Package("unattended-upgrades")

Execute("update-package-index", command="apt-get -qq update", action="nothing")

File("/etc/apt/apt.conf",
     owner = "root",
     group = "root",
     mode = 0644,
     content = Template("apt/apt.conf.j2"))

File("/etc/apt/sources.list",
     owner="root",
     group="root",
     mode=0644,
     content="%s\n" % "\n".join(env.config.apt.sources),
     notifies=[("run", env.resources["Execute"]["update-package-index"])])
