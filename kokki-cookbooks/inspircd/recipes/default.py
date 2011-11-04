import os
from kokki import Fail, File, Script


def install_package(name, url, creates):
    filename = url.rsplit("/", 1)[-1]
    dirname = filename
    while dirname.rsplit(".", 1)[-1] in ("gz", "tar", "tgz", "bz2"):
        dirname = dirname.rsplit(".", 1)[0]

    fmt_dict = dict(
        name=name,
        url=url,
        dirname=dirname,
        filename=filename)

    if not dirname:
        raise Fail("Unable to figure out directory name of project for URL {url}".format(**fmt_dict))
    Script("install-{name}".format(**fmt_dict),
        not_if=lambda: os.path.exists(creates),
        cwd="/usr/local/src",
        code=(
            "wget {url}\n"
            "tar -zxvf {filename}\n"
            "cd {dirname}\n"
            "./configure && make install\n"
            "ldconfig\n").format(**fmt_dict))

install_package("inspircd",
    creates="/usr/local/sbin/inspircd",
    url="https://s3.amazonaws.com/sector5d/inspircd-2.0.5-1-x86_64.pkg.tar.xz")

# File("/etc/inspircd/inspircd.conf",
#     content=Template("inspircd/inspircd.conf.j2"),
#     owner="irc",
#     group="irc",
#     mode=0644)
