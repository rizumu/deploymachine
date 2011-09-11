import base64
import json

from fabric.api import local

from BaseHTTPServer import BaseHTTPRequestHandler
from urllib2 import Request, URLError, urlopen

from deploymachine.conf import settings

# sudo gem install --remote dnsimple-ruby

# Update Pythons list of error codes with some that are missing
newhttpcodes = {
    422:("Unprocessable Entity", "HTTP_UNPROCESSABLE_ENTITY"),
    423:("Locked", "HTTP_LOCKED"),
    424:("Failed Dependency", "HTTP_FAILED_DEPENDENCY"),
    425:("No code", "HTTP_NO_CODE"),
    426:("Upgrade Required", "HTTP_UPGRADE_REQUIRED"),
}


for code in newhttpcodes:
    BaseHTTPRequestHandler.responses[code] = newhttpcodes[code]


def change_loadbalancer_ip(old_ip, new_ip):
    dns = DNSimple()
    for domain in dns.get_domains():
        domain_id = domain["domain"]["id"]
        domain_name = domain["domain"]["name"]
        if not domain_name in settings.ACTIVE_DOMAIN_LIST:
            continue
        site_records = dns.rest_helper("/domains/{0}/records.json".format(domain_id))
        for arecord in [r for r in site_records if r["record"]["content"] == old_ip]:
            local("dnsimple record:update {0} {1} name:{2} content:{3} ttl:{4} prio:{5}".format(
                domain_name,
                arecord["record"]["id"],
                arecord["record"]["name"],
                new_ip,
                arecord["record"]["ttl"],
                arecord["record"]["prio"],
            ))
            # arecord_id = arecord["record"]["id"]
            # updated_arecord = [{
            #     "record": {
            #         "name": arecord["record"]["name"],
            #         "content": (new_ip),
            #         "ttl": arecord["record"]["ttl"],
            #         "prio": arecord["record"]["prio"],
            #     }
            # }]
            #dns.rest_helper("/domains/{0}/records/{1}.json".format(domain_name, arecord_id), json.dumps(updated_arecord))


class DNSimple(object):
    def __init__(self):
        self.useragent = "Deploymachine Python API"
        self.endpoint = "https://dnsimple.com"
        self.authstring = self.get_authstring(self.endpoint,
                                              settings.DNSIMPLE_USERNAME,
                                              settings.DNSIMPLE_PASSWORD)

    def get_authstring(self, endpoint, username, password):
        encodedstring = base64.encodestring("{0}:{1}".format(username, password)).strip()
        return "Basic {0}".format(encodedstring)

    def rest_helper(self, url, postdata=None):
        """Does GET requests and (if postdata specified) POST requests.
        For POSTs we do NOT encode our data, as DNSimple's REST API expects square brackets
        which are normally encoded according to RFC 1738. urllib.urlencode encodes square brackets
        which the API does not like.
        """
        url = self.endpoint + url
        headers = {"Authorization": self.authstring,
                   "User-Agent": self.useragent}
        result = self.request_helper(Request(url, postdata, headers))
        if result:
            return json.loads(result)
        else:
            return None

    def request_helper(self, request):
        """Does requests and maps HTTP responses into delicious Python juice"""
        try:
            handle = urlopen(request)
        except URLError, e:
            # Check returned URLError for issues and report "em
            if hasattr(e, "reason"):
                print "We failed to reach a server."
                print "Reason: ", e.reason
                return
            elif hasattr(e, "code"):
                print "Error code: ", e.code
                print "\n".join(BaseHTTPRequestHandler.responses[e.code])
                return
        else:
            return handle.read()

    def get_domains(self):
        """Get a list of all domains in your account."""
        return self.rest_helper("/domains.json")

