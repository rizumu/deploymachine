
import os
from kokki import Execute, Package


apt_list_path_pg = "/etc/apt/sources.list.d/pitti-postgresql-natty.list"
apt_list_path_gis = "/etc/apt/sources.list.d/ubuntugis-ubuntugis-unstable-natty.list"

Execute("apt-update-postgresql9", command="apt-get update", action="nothing")

apt = None
if env.system.platform == "ubuntu":
    Package("python-software-properties")
    Execute("add-apt-repository ppa:pitti/postgresql",
        not_if = lambda:os.path.exists(apt_list_path_pg),
        notifies = [("run", env.resources["Execute"]["apt-update-postgresql9"], True)])
    Execute("add-apt-repository ppa:ubuntugis/ubuntugis-unstable",
        not_if = lambda:os.path.exists(apt_list_path_gis),
        notifies = [("run", env.resources["Execute"]["apt-update-postgresql9"], True)])
