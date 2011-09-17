
__description__ = "PostgreSQL backup via rackspace cloudfiles"
__config__ = {
    "cloudfiles.openstack_username": dict(
        description = "Your rackspace username",
    ),
    "cloudfiles.openstack_api_key": dict(
        description = "Your rackspace api key",
    ),
    "cloudfiles.openstack_dbdumps_container": dict(
        description = "The container where your database backups are saved",
    ),
    "cloudfiles.openstack_datacentre": dict(
        description = "The datacentre can be either `us` or `uk`",
        default = "us",
    ),
}
