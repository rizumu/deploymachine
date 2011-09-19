
__description__ = "Configures the Advanced Packaging Tool for Debian systems"
__config__ = {
    "apt.sources": dict(
        display_name = "Default sources",
        description = "As found in /usr/share/apt/examples/sources.list",
        default = [
            "deb http://http.us.debian.org/debian stable main contrib non-free",
            "deb http://security.debian.org stable/updates main contrib non-free",
        ],
    ),
    "apt.configs": dict(
        display_name = "Apt configuration variables",
        description = "man apt.conf",
        default = [],
    ),
}
