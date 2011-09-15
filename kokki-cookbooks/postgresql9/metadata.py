
__description__ = "PostgreSQL database 9.1"
__config__ = {
    "postgresql9.data_dir": dict(
        description = "Location of the PostgreSQL databases",
        default = "/var/lib/postgresql/9.1/main",
    ),
    "postgresql9.config_dir": dict(
        description = "Location of the PostgreSQL configuration files",
        default = "/etc/postgresql/9.1/main",
    ),
    "postgresql9.pidfile": dict(
        description = "Path to the PostgreSQL pid file",
        default = "/var/run/postgresql/9.1-main.pid",
    ),
    "postgresql9.unix_socket_directory": dict(
        default = None,
    ),
    "postgresql9.listen_addresses": dict(
        description = "IP addresses PostgreSQL should listen on (* for all interfaces)",
        default = ["localhost"],
    ),
    "postgresql9.port": dict(
        description = "Port PostgreSQL should bind to",
        default = 5432,
    ),
    "postgresql9.max_connections": dict(
        description = "Maximum numbers of connections",
        default = 100,
    ),
    "postgresql9.auth": dict(
        description = "List of auth configs",
        default = [
            dict(
                type = "local",
                database = "all",
                user = "all",
                method = "ident",
            ),
            dict(
                type = "host",
                database = "all",
                user = "all",
                cidr = "127.0.0.1/32",
                method = "md5",
            ),
            dict(
                type = "host",
                database = "all",
                user = "all",
                cidr = "::1/128",
                method = "md5",
            ),
        ],
    ),
    "postgresql9.ssl": dict(
        default = False,
    ),
    # tip: Set to 25% available RAM and move up/down 5% to find sweet spot
    "postgresql9.shared_buffers": dict(
        default = "64MB",
    ),
    # tip: Planning hint that tells PG how much RAM it can expect for OS disk cache.
    # Set to 50-75% of available RAM.
    "postgresql9.effective_cache_size": dict(
        default = "128MB",
    ),
    # tip: Per process amount of ORDER BY space. 5MBs is a good starting point.
    "postgresql9.work_mem": dict(
        default = "5MB",
    ),
    # tip: Set to 16MB and forget it.
    "postgresql9.wal_buffers": dict(
        default = "16MB",
    ),
    # tip: Increase to at least 10.
    "postgresql9.checkpoint_segments": dict(
        default = "10",
    ),
    # tip: 50MB for every GB of RAM.
    "postgresql9.maintenance_work_mem": dict(
        default = "16MB",
    ),
    # tip: turn off with data loss risks
    "postgresql9.synchronous_commit": dict(
        default = "off",
    ),
    # tip: Set to 1000 to detect slow queries.
    "postgresql9.log_min_duration_statement": dict(
        description = "-1 is disabled, 0 logs all statements and their durations, > 0 logs only statements running at least this number of milliseconds",
        default = -1,
    ),
    "postgresql9.locale": dict(
        default = "en_US.UTF-8",
    ),
    # Streaming replication
    "postgresql9.max_wal_senders": dict(
        description = "Maximum number of WAL sender processes",
        default = 0,
    ),
    "postgresql9.wal_sender_delay": dict(
        description = "walsender cycle time, 1-10000 milliseconds",
        default = "200ms",
    ),
    # Standby Servers
    "postgresql9.hot_standby": dict(
        description = "Allow queries during discovery",
        default = False,
    ),
}

for k, v in __config__.iteritems():
    if isinstance(v['default'], basestring):
        v["default"] = v["default"].format(config=__config__)
