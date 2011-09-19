from kokki import Package, File, Execute, Template

Package("unattended-upgrades")

Execute("update-package-index",
        action="nothing",
        command="DEBIAN_FRONTEND=noninteractive apt-get -qq update")

File("/etc/apt/apt.conf",
     owner = "root",
     group = "root",
     mode = 0644,
     content = Template("apt/apt.conf.j2"))

File("/etc/apt/sources.list",
     owner = "root",
     group = "root",
     mode = 0644,
     content = "%s\n" % "\n".join(env["apt"]["sources"]),
     notifies = [("run", env.resources["Execute"]["update-package-index"])])
