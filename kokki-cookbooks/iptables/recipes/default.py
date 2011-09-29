import openstack.compute

from kokki import Execute, File, Template, Service


def get_openstack_ips():
    compute = openstack.compute.Compute(username=env.config.openstack_compute.username,
                                        apikey=env.config.openstack_compute.api_key)
    ip_addresses = dict(APPNODE_INTERNAL_IPS=[])
    for server in compute.servers.list():
        if "balancer" in server.name:  # matches loadbalancer, appbalancer, dbappbalancer
            ip_addresses["loadbalancer_internal_ip"] = server.addresses["private"][0]
        if "app" in server.name:  # matches appnode, appbalancer, dbappbalancer
            ip_addresses["appnode_internal_ips"] = server.addresses["private"][0]
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
    content=Template("supervisor/iptables.j2")
)
