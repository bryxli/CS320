import re
import netaddr
import pandas as pd
from bisect import bisect

ips = pd.read_csv("ip2location.csv")

def lookup_region(ip_address):
    ip_address = re.sub(r"[a-zA-Z]", "0", ip_address)
    idx = bisect(ips["low"], int(netaddr.IPAddress(ip_address)))
    if idx >= len(ips):
        location = "-"
    else:
        location = ips.iloc[idx - 1]["region"]
    return location

class Filing:
    def __init__(self, html):
        self.dates = re.findall(r"19\d{2}\-\d{2}\-\d{2}|20\d{2}\-\d{2}\-\d{2}", html)
        sic = re.findall(r"SIC=[^0-9]*(\d+)", html)
        if len(sic) == 0:
            self.sic = None
        else:
            self.sic = int(sic[0])
        self.addresses = []
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                lines.append(line.strip())
            self.addresses.append("\n".join(lines))
            if self.addresses[-1] == "":
                self.addresses.pop()

    def state(self):
        for address in self.addresses:
            code = re.findall(r"([A-Z]{2})\s\d{5}", address)
            if len(code) > 0:
                return code[0]
        return None