import os
from kokki import Execute, File, Package, Service, Template

env.include_recipe("sendmail")

Service("sendmail",
    supports_restart = True,
    supports_reload = True,
    supports_status = True,
    action = "nothing")

Package("sasl2-bin")
Package("sendmail")

Execute("sendmailconfig", command="sendmailconfig", action="nothing")
Execute("newaliases", command="newaliases", action="nothing")

File("/etc/mail/sendmail.mc",
    owner = "root",
    group = "smmsp",
    mode = 0644,
    content = Template("sendmail/sendmail.mc.j2"),
    notifies = [("restart", env.resources["Service"]["sendmail"]),
                ("run", env.resources["Execute"]["sendmailconfig"], True)],
)

File("/etc/mail/submit.mc",
    owner = "root",
    group = "smmsp",
    mode = 0644,
    content = Template("sendmail/submit.mc.j2"),
    notifies = [("restart", env.resources["Service"]["sendmail"]),
                ("run", env.resources["Execute"]["sendmailconfig"], True)],
)

File("/etc/aliases",
    owner = "root",
    group = "root",
    mode = 0644,
    content = Template("sendmail/aliases.j2"),
    notifies = [("run", env.resources["Execute"]["newaliases"], True)],
)

# Unfortunately, there is no automagic way to migrate to /etc/sasldb2 :(
# You'll want to make sure /etc/default/saslauthd is setup to start,
# and has at least MECHANISMS="pam" !


#❄  sudo newaliases
#WARNING: local host name (dbserver) is not qualified; see cf/README: WHO AM I?
#/etc/mail/aliases: line 23: abuse... Warning: duplicate alias name abuse
#/etc/mail/aliases: line 27: root:           ... missing value for alias
#/etc/mail/aliases: 15 aliases, longest 10 bytes, 175 bytes total
