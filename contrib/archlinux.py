import os

from fabric.api import run
from fabric.contrib.files import append, put, uncomment

from deploymachine.conf import settings


def bootstrap_archlinux(action="install"):
    # The following core packages are essential for bootstrapping.
    BASE_PACKAGES = [
        "base-devel",
        "curl",
        "git",
        "yaourt",
    ]
    if hasattr(settings, "EXTRA_BASE_ARCHLINUX_PACKAGES"):
        BASE_PACKAGES.append(settings.EXTRA_BASE_ARCHLINUX_PACKAGES)

    uncomment("/etc/pacman.d/mirrorlist", "Server")
    run("pacman -Syu --noconfirm")
    run("pacman-db-upgrade")
    put(os.path.join(settings.DEPLOYMACHINE_LOCAL_ROOT, "templates/mirrorlist"), "/etc/pacman.d/mirrorlist")
    run("rm /etc/profile.d/locale.sh")
    append("/etc/pacman.conf", "\n[archlinuxfr]\nServer = http://repo.archlinux.fr/$arch", use_sudo=True)
    run("pacman -Syu --noconfirm")
    run("pacman -S --noconfirm {0}".format(" ".join(BASE_PACKAGES)))
