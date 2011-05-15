
import cloudservers

from kokki import Package, Directory, File, Template, Service


def get_internal_appnode_ips():
    appnode_list = []
    cs = cloudservers.CloudServers(env.config.cloud_servers.username,
                                   env.config.cloud_servers.api_key)
    for server in cs.servers.list():
        if server.metadata["role"] == "appnode":
            appnode_list.append(server.addresses["private"][0])
    return appnode_list


Package("nginx")

Directory(env.config.nginx.log_dir,
    mode = 0755,
    owner = env.config.nginx.user,
    action = "create")

for nxscript in ("nxensite", "nxdissite"):
    File("/usr/sbin/%s" % nxscript,
        content = Template("nginx/%s.j2" % nxscript),
        mode = 0755,
        owner = "root",
        group = "root")

File("nginx.conf",
    path = "%s/nginx.conf" % env.config.nginx.dir,
    content = Template("nginx/nginx.conf.j2"),
    owner = "root",
    group = "root",
    mode = 0644)

Service("nginx",
    supports_status = True,
    supports_restart = True,
    supports_reload = True,
    action = "start",
    subscribes = [("reload", env.resources["File"]["nginx.conf"])])

if "librato.silverline" in env.included_recipes:
    File("/etc/default/nginx",
        owner = "root",
        group = "root",
        mode = 0644,
        content = (
            "export SL_NAME=nginx\n"
        ),
        notifies = [("restart", env.resources["Service"]["nginx"])])

for site in env.config.nginx.sites:
    File("%s/sites-available/%s" % (
            env.config.nginx.dir,
            site["name"]),
            content=Template("nginx/site-gunicorn.j2",
            variables={
                "site": site,
                "appnode_internal_ip_list": get_internal_appnode_ips()
            }
        ),
        owner = "root",
        group = "root",
        mode = 0644,
        notifies =[("reload", env.resources["Service"]["nginx"])])
