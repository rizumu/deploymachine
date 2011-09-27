
import os
import openstack.compute

from kokki import Execute, Package, Directory, File, Template, Service


apt_list_path = "/etc/apt/sources.list.d/nginx-stable-natty.list"

Execute("apt-update-nginx", command="apt-get update", action="nothing")

apt = None
if env.system.platform == "ubuntu":
    Package("python-software-properties")
    Execute("add-apt-repository ppa:nginx/stable",
        not_if = lambda:os.path.exists(apt_list_path),
        notifies = [("run", env.resources["Execute"]["apt-update-nginx"], True)])


def get_internal_appnode_ips():
    appnode_list = []
    compute = openstack.compute.Compute(username=env.config.openstack_compute.username,
                                        apikey=env.config.openstack_compute.api_key)
    for server in compute.servers.list():
        if "app" in server.name:  # matches appnode, appbalancer, dbappbalancer
            appnode_list.append(server.addresses["private"][0])
    return appnode_list


Package("nginx")

Directory(env.config.nginx.log_dir,
    mode=0755,
    owner=env.config.nginx.user,
    action="create")

for nxscript in ("nxensite", "nxdissite"):
    File("/usr/sbin/%s" % nxscript,
        content=Template("nginx/%s.j2" % nxscript),
        mode=0755,
        owner="root",
        group="root")

File("nginx.conf",
    path="%s/nginx.conf" % env.config.nginx.dir,
    content=Template("nginx/nginx.conf.j2"),
    owner="root",
    group="root",
    mode=0644)

File("htpasswd",
    path="%s/htpasswd" % env.config.nginx.dir,
    content="admin:{0}\n".format(env.config.nginx.munin_password_encrypted),
    owner="root",
    group="root",
    mode=0644)

Service("nginx",
    supports_status=True,
    supports_restart=True,
    supports_reload=True,
    action="start",
    subscribes=[("reload", env.resources["File"]["nginx.conf"])])

if "librato.silverline" in env.included_recipes:
    File("/etc/default/nginx",
        owner="root",
        group="root",
        mode=0644,
        content=(
            "export SL_NAME=nginx\n"
        ),
        notifies=[("restart", env.resources["Service"]["nginx"])])

for site in env.config.nginx.sites:
    File("%s/sites-available/%s" % (env.config.nginx.dir, site["name"]),
        content=Template(
            "nginx/site-gunicorn.j2",
            variables={
                "site": site,
                "appnode_internal_ip_list": get_internal_appnode_ips(),
            }
        ),
        owner="root",
        group="root",
        mode=0644,
        notifies=[("reload", env.resources["Service"]["nginx"])])
