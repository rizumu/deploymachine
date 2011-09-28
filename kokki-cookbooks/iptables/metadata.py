
__description__ = "sendmail - an electronic mail transport agent"
__config__ = {
    "iptables.public_ports": dict(
        description="Allow all HTTP and HTTPS to individual application ports.",
    ),
    "iptables.public_port_ranges": dict(
        description="Allow all HTTP and HTTPS connections to application port ranges.",
        default=["8000:8001"]
    ),
    "iptables.munin_node_port": dict(
        description="Munin node port.",
        default="4949",
    ),
    "iptables.psql_port": dict(
        description="Postgresql port.",
        default="5432",
    ),
    "iptables.redis_port": dict(
        description="redis port.",
        default="6379",
    ),
    "iptables.rabbitmq_port": dict(
        description="Rabbitmq port.",
        default="5672",
    ),
    "iptables.monit_port": dict(
        description="Monit port.",
        default="2812",
    ),
    "iptables.ssh_port": dict(
        description="SSH port.",
        default="22",
    ),
}
