import json
import openstack.compute

from kokki import Execute, File, Template, Service


def get_openstack_ips():
    fabric_env = json.loads(env.config.fabric_env)
    compute = openstack.compute.Compute(username=env.config.openstack_compute.username,
                                        apikey=env.config.openstack_compute.api_key)
    ip_addresses = dict(APPNODE_INTERNAL_IPS=[])
    if fabric_env["node_type"] == "allinone":
        ip_addresses["loadbalancer_internal_ip"] = "127.0.0.1"
        ip_addresses["appnode_internal_ips"] = ["127.0.0.1"]
    elif fabric_env["node_type"] == "appbalancer":
        raise(NotImplementedError)
    else:
        for server in compute.servers.list():
            if "loadbalancer" in server.name:
                ip_addresses["loadbalancer_internal_ip"] = server.addresses["private"][0]
            if "appnode" in server.name:
                ip_addresses["appnode_internal_ips"] = server.addresses["private"]
    return ip_addresses


Execute("iptables-restore",
    action="nothing",
    command=("iptables --flush && /sbin/iptables-restore < /etc/iptables.up.rules"),
)

File("/etc/iptables.up.rules",
    owner="root",
    group="root",
    mode=0644,
    notifies=[("run", env.resources["Execute"]["iptables-restore"], True)],
    content=Template(
        "iptables/iptables.up.rules.j2",
        variables=get_openstack_ips()
    ))

File("/etc/network/if-pre-up.d/iptables",
    owner="root",
    group="root",
    mode=0644,
    content=Template("iptables/iptables.j2")
)
