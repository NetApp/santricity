#!/usr/bin/python

# (c) 2018, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

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
    dhcp_enable:
        description:
            - Enables a simple dhcp server to response to new E-Series storage systems.
            - This option is for static environments that do not have a DHCP server on the network. DO NOT ENABLE WHEN DHCP IS ALREADY AVAILABLE.
            - M(na_santricity_discover) must be running when turning on storage systems for the first time. This way when the system comes online it will first
              request an IP address from a local DHCP server and the module will respond with an address from the I(usable_ip_addresses) list.
        type: bool
        default: false
        required: false
    dhcp_subnet_mask:
        description:
            - IPv4 gateway address.
            - Required when I(dhcp_enable == true)
        type: str
        required: false
    dhcp_gateway:
        description:
            - IPv4 gateway address.
            - Required when I(dhcp_enable == true)
        type: str
        required: false
    usable_ip_addresses_pool:
        description:
            - List of available IP addresses (If a specific static IP address will be assigned to these systems then choose address that will not be used).
            - Addresses must be included in the I(subnet_mask) IP address range.
            - Required when I(dhcp_enable == true)
            - Addresses that are pingable will be ignored.
        type: list
        required: false
    expected_serial_numbers:
        description:
            - This option will force the discovery process to wait for all provided serial numbers.
            - List of expected serial numbers.
            - Required when I(dhcp_enable == true)
        type: list
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
import socket
import threading

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import request


class NetAppESeriesDiscover:
    """Discover E-Series storage systems."""
    SEARCH_STEP = 64  # This will be the maximum number of threads.
    SEARCH_TIMEOUT = 1

    def __init__(self):
        ansible_options = dict(subnet_mask=dict(type="str", required=True),
                               ports=dict(type="list", required=False, default=[8080, 8443, 443]),
                               dhcp_enable=dict(type="bool", required=False, default=False),
                               dhcp_subnet_mask=dict(type="str", required=False),
                               dhcp_gateway=dict(type="str", required=False),
                               usable_ip_addresses=dict(type="list", required=False),
                               expected_serial_numbers=dict(type="list", required=False))

        required_if = [["dhcp_enable", True, ["usable_ip_addresses", "expected_serial_numbers"]]]
        self.module = AnsibleModule(argument_spec=ansible_options, required_if=required_if)
        args = self.module.params

        self.subnet_mask = args["subnet_mask"]
        self.ports = []
        self.dhcp_enable = args["dhcp_enable"]
        self.dhcp_subnet_mask = args["dhcp_subnet_mask"]
        self.dhcp_gateway = args["dhcp_gateway"]
        self.usable_ip_address = args["usable_ip_addresses"]
        self.expected_serial_numbers = args["expected_serial_numbers"]

        for port in args["ports"]:
            if str(port).isdigit():
                self.ports.append(str(port))
            else:
                self.module.fail_json(msg="Invalid port! Ports must be numbers.")

        self.systems_found = {}
        self.server_ip_address = "127.0.0.1"

    def check_ip_address(self, systems_found, address):
        """Determine where an E-Series storage system is available at a specific ip address."""
        serial = None
        rest_urls = ["https://%s:%s/devmgr/utils/about" % (address, port) for port in self.ports]

        for url in rest_urls:
            try:
                rc, response = request(url, force_basic_auth=False, validate_certs=False, timeout=self.SEARCH_TIMEOUT)
                serial = response["systemId"]   # TODO: Change to saData.chassisSerialNumber which is being added to utils/about in Starlifter.2 (11.62)
            except Exception as error:
                # self.module.log("%s: %s" % (address, error))
                pass

        if serial:
            if serial in self.systems_found.keys():
                self.systems_found[serial].append(address)
            else:
                self.systems_found.update({serial: [address]})

    def discover(self):
        """Discover E-Series storage systems."""
        subnet = list(ipaddress.ip_network(u"%s" % self.subnet_mask))

        thread_pool = []
        search_count = len(subnet)
        for start in range(0, search_count, self.SEARCH_STEP):
            end = search_count if (search_count - start) < self.SEARCH_STEP else start + self.SEARCH_STEP

            for address in subnet[start:end]:
                thread = threading.Thread(target=self.check_ip_address, args=(self.systems_found, str(address)))
                thread_pool.append(thread)
                thread.start()
            for thread in thread_pool:
                thread.join()
        self.module.exit_json(msg="Discover process complete.", systems_found=self.systems_found, changed=False)


if __name__ == "__main__":
    discover = NetAppESeriesDiscover()
    discover.discover()
