#!/usr/bin/python

# (c) 2020, NetApp, Inc
# BSD-3 Clause (see COPYING or https://opensource.org/licenses/BSD-3-Clause)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
---
module: na_santricity_discover
short_description: NetApp E-Series discover E-Series storage systems
description: Module searches a subnet range and returns any available E-Series storage systems.
author: Nathan Swartz (@ndswartz)
options:
    subnet_mask:
        description:
            - This is the IPv4 search range for discovering E-Series storage arrays.
            - IPv4 subnet mask specified in CIDR form. Example 192.168.1.0/24 would search the range 192.168.1.0 to 192.168.1.255.
            - Be sure to include all management paths in the search range.
        type: str
        required: true
    ports:
        description:
            - This option allows a specific port to be tested.
            - The ports 8080, 8443, and 443 will always be checked. 
        type: list
        default: [8080, 8443, 443]
        required: false
    proxy_url:
        description:
            - Web Services Proxy REST API URL. example: https://192.168.1.100:8443/devmgr/v2/
            - Required for discovering systems before Web Services 4.2
        type: str
        required: false
    proxy_user:
        description:
            - Web Service Proxy user
            - Required for discovering systems before Web Services 4.2
        type: str
        required: false
    proxy_user:
        description:
            - Web Service Proxy user password
            - Required for discovering systems before Web Services 4.2
        type: str
        required: false
    proxy_validate_certs:
        description:
            - Whether to validate Web Service Proxy SSL certificate
        type: bool
        default: true
        required: false
notes:
    - Chassis serial numbers will only be available from systems running SANtricity version 11.62 or later.
    - Only E-Series storage systems utilizing SANtricity Web Services Embedded REST API will be discovered.
"""

EXAMPLES = """
- name: Discover all E-Series storage systems on the network.
  na_santricity_discover:
    subnet_mask: 192.168.1.0/24
"""

RETURN = """
msg:
    description: Success message
    returned: on success
    type: str
    sample: The discover E-Series storage systems.
"""
import ipaddress
import json
import threading
from time import sleep

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import request
from ansible.module_utils._text import to_native

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class NetAppESeriesDiscover:
    """Discover E-Series storage systems."""
    SEARCH_STEP = 128  # This will be the maximum number of threads.
    SEARCH_TIMEOUT = 1
    DEFAULT_CONNECTION_TIMEOUT_SEC = 1
    DEFAULT_GRAPH_DISCOVERY_TIMEOUT = 30
    DEFAULT_PASSWORD_STATE_TIMEOUT = 30
    DEFAULT_DISCOVERY_TIMEOUT_SEC = 300
    PROXYLESS_WEB_SERVICES_MINIMUM = "04.20.0000.0000"

    def __init__(self):
        ansible_options = dict(subnet_mask=dict(type="str", required=True),
                               ports=dict(type="list", required=False, default=[8443, 443, 8080]),
                               proxy_url=dict(type="str", required=False),
                               proxy_user=dict(type="str", required=False),
                               proxy_password=dict(type="str", required=False, no_log=True),
                               proxy_validate_certs=dict(type="bool", default=True, required=False))

        required_together = [["proxy_url", "proxy_user", "proxy_password"]]
        self.module = AnsibleModule(argument_spec=ansible_options, required_together=required_together)
        args = self.module.params

        self.subnet_mask = args["subnet_mask"]
        self.ports = []
        self.proxy_url = args["proxy_url"]
        if args["proxy_url"]:
            parsed_url = list(urlparse.urlparse(args["proxy_url"]))
            parsed_url[2] = "/devmgr/utils/about"
            self.proxy_about_url = urlparse.urlunparse(parsed_url)
            parsed_url[2] = "/devmgr/v2/"
            self.proxy_url = urlparse.urlunparse(parsed_url)
            self.proxy_user = args["proxy_user"]
            self.proxy_password = args["proxy_password"]
            self.proxy_validate_certs = args["proxy_validate_certs"]

        for port in args["ports"]:
            if str(port).isdigit():
                self.ports.append(str(port))
            else:
                self.module.fail_json(msg="Invalid port! Ports must be numbers.")

        self.systems_found = {}

    def check_ip_address(self, systems_found, address):
        """Determine where an E-Series storage system is available at a specific ip address."""
        for port in self.ports:
            if port == "8080":
                url = "http://%s:%s/devmgr/v2/" % (address, port)
            else:
                url = "https://%s:%s/devmgr/v2/" % (address, port)

            try:
                rc, graph = request(url + "storage-systems/1/graph", validate_certs=False, url_username="admin", url_password="", timeout=self.SEARCH_TIMEOUT)

                sa_data = graph["sa"]["saData"]
                if sa_data["chassisSerialNumber"] in systems_found:
                    systems_found[sa_data["chassisSerialNumber"]]["api_urls"].append(url)
                else:
                    systems_found.update({sa_data["chassisSerialNumber"]: {"api_urls": [url], "label": sa_data["storageArrayLabel"]}})
                break
            except Exception as error:
                pass

    def no_proxy_discover(self):
        """Discover E-Series storage systems using embedded web services."""
        subnet = list(ipaddress.ip_network(u"%s" % self.subnet_mask))

        thread_pool = []
        search_count = len(subnet)
        for start in range(0, search_count, self.SEARCH_STEP):
            end = search_count if (search_count - start) < self.SEARCH_STEP else start + self.SEARCH_STEP

            for address in subnet[start:end]:
                thread = threading.Thread(target=self.check_ip_address, args=(self.systems_found, address))
                thread_pool.append(thread)
                thread.start()
            for thread in thread_pool:
                thread.join()

    def verify_proxy_service(self):
        """Verify proxy url points to a web services proxy."""
        self.module.log("%s" % self.proxy_about_url)
        try:
            rc, about = request(self.proxy_about_url, validate_certs=self.proxy_validate_certs)
            if not about["runningAsProxy"]:
                self.module.fail_json(msg="Web Services is not running as a proxy!")
        except Exception as error:
            self.module.fail_json(msg="Proxy is not available! Check proxy_url.")

    def test_systems_found(self, systems_found, serial, label, addresses):
        """Verify and build api urls."""
        api_urls = []
        for address in addresses:
            for port in self.ports:
                if port == "8080":
                    url = "http://%s:%s/devmgr/" % (address, port)
                else:
                    url = "https://%s:%s/devmgr/" % (address, port)

                try:
                    rc, response = request(url + "utils/about", validate_certs=False, timeout=self.SEARCH_TIMEOUT)
                    api_urls.append(url + "v2/")
                    break
                except Exception as error:
                    pass
        systems_found.update({serial: {"api_urls": api_urls, "label": label}})

    def proxy_discover(self):
        """Search for array using it's chassis serial from web services proxy."""
        self.verify_proxy_service()
        subnet = ipaddress.ip_network(u"%s" % self.subnet_mask)

        try:
            rc, request_id = request(self.proxy_url + "discovery", method="POST", validate_certs=self.proxy_validate_certs,
                                     force_basic_auth=True, url_username=self.proxy_user, url_password=self.proxy_password,
                                     data=json.dumps({"startIP": str(subnet[0]), "endIP": str(subnet[-1]),
                                                      "connectionTimeout": self.DEFAULT_CONNECTION_TIMEOUT_SEC}))

            # Wait for discover to complete
            try:
                for iteration in range(self.DEFAULT_DISCOVERY_TIMEOUT_SEC):
                    rc, discovered_systems = request(self.proxy_url + "discovery?requestId=%s" % request_id["requestId"],
                                                     validate_certs=self.proxy_validate_certs,
                                                     force_basic_auth=True, url_username=self.proxy_user, url_password=self.proxy_password)

                    if not discovered_systems["discoverProcessRunning"]:

                        thread_pool = []
                        for system in discovered_systems["storageSystems"]:
                            if "https" in system["supportedManagementPorts"]:
                                addresses = []
                                for controller in system["controllers"]:
                                    addresses.extend(controller["ipAddresses"])

                                thread = threading.Thread(target=self.test_systems_found,
                                                          args=(self.systems_found, system["serialNumber"], system["label"], addresses))
                                thread_pool.append(thread)
                                thread.start()

                        for thread in thread_pool:
                            thread.join()
                        break
                    sleep(1)
                else:
                    self.module.fail_json(msg="Timeout waiting for array discovery process. Subnet [%s]" % self.subnet_mask)
            except Exception as error:
                self.module.fail_json(msg="Failed to get the discovery results. Error [%s]." % to_native(error))
        except Exception as error:
            self.module.fail_json(msg="Failed to initiate array discovery. Error [%s]." % to_native(error))

    def discover(self):
        """Discover E-Series storage systems."""
        if self.proxy_url:
            self.proxy_discover()
        else:
            self.no_proxy_discover()

        self.module.exit_json(msg="Discover process complete.", systems_found=self.systems_found, changed=False)


if __name__ == "__main__":
    discover = NetAppESeriesDiscover()
    discover.discover()
