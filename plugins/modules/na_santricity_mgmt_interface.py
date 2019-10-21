#!/usr/bin/python

# (c) 2018, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'certified'}

DOCUMENTATION = """
---
module: na_santricity_mgmt_interface
short_description: NetApp E-Series manage management interface configuration
description:
    - Configure the E-Series management interfaces
author:
    - Michael Price (@lmprice)
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity_doc
options:
    state:
        description:
            - Enable or disable IPv4 network interface configuration.
            - Either IPv4 or IPv6 must be enabled otherwise error will occur.
            - Only required when enabling or disabling IPv4 network interface
        choices:
            - enable
            - disable
        required: no
        aliases:
            - enable_interface
    controller:
        description:
            - The controller that owns the port you want to configure.
            - Controller names are represented alphabetically, with the first controller as A,
             the second as B, and so on.
            - Current hardware models have either 1 or 2 available controllers, but that is not a guaranteed hard
             limitation and could change in the future.
        required: yes
        choices:
            - A
            - B
    name:
        description:
            - The port to modify the configuration for.
            - The list of choices is not necessarily comprehensive. It depends on the number of ports
              that are present in the system.
            - The name represents the port number (typically from left to right on the controller),
              beginning with a value of 1.
            - Mutually exclusive with I(channel).
        aliases:
            - port
            - iface
    channel:
        description:
            - The port to modify the configuration for.
            - The channel represents the port number (typically from left to right on the controller),
              beginning with a value of 1.
            - Mutually exclusive with I(name).
    address:
        description:
            - The IPv4 address to assign to the interface.
            - Should be specified in xx.xx.xx.xx form.
            - Mutually exclusive with I(config_method=dhcp)
        required: no
    subnet_mask:
        description:
            - The subnet mask to utilize for the interface.
            - Should be specified in xx.xx.xx.xx form.
            - Mutually exclusive with I(config_method=dhcp)
        required: no
    gateway:
        description:
            - The IPv4 gateway address to utilize for the interface.
            - Should be specified in xx.xx.xx.xx form.
            - Mutually exclusive with I(config_method=dhcp)
        required: no
    config_method:
        description:
            - The configuration method type to use for network interface ports.
            - dhcp is mutually exclusive with I(address), I(subnet_mask), and I(gateway).
        choices:
            - dhcp
            - static
        required: no
    dns_config_method:
        description:
            - The configuration method type to use for DNS services.
            - dhcp is mutually exclusive with I(dns_address), and I(dns_address_backup).
        choices:
            - dhcp
            - static
        required: no
    dns_address:
        description:
            - Primary IPv4 DNS server address
        required: no
    dns_address_backup:
        description:
            - Backup IPv4 DNS server address
            - Queried when primary DNS server fails
        required: no
    ntp_config_method:
        description:
            - The configuration method type to use for NTP services.
            - disable is mutually exclusive with I(ntp_address) and I(ntp_address_backup).
            - dhcp is mutually exclusive with I(ntp_address) and I(ntp_address_backup).
        choices:
            - disable
            - dhcp
            - static
        required: no
    ntp_address:
        description:
            - Primary IPv4 NTP server address
        required: no
    ntp_address_backup:
        description:
            - Backup IPv4 NTP server address
            - Queried when primary NTP server fails
        required: no
    ssh:
        type: bool
        description:
            - Enable ssh access to the controller for debug purposes.
            - This is a controller-level setting.
            - rlogin/telnet will be enabled for ancient equipment where ssh is not available.
        required: no
notes:
    - Check mode is supported.
    - When using SANtricity Web Services Proxy, use M(na_santricity_storage_system) to update management paths. This is required because of a known issue
      and will be addressed in the proxy version 4.1. After the resolution the management ports should automatically be updated.
    - The interface settings are applied synchronously, but changes to the interface itself (receiving a new IP address
      via dhcp, etc), can take seconds or minutes longer to take effect.
"""

EXAMPLES = """
    - name: Configure the first port on the A controller with a static IPv4 address
      na_santricity_mgmt_interface:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: "1"
        controller: "A"
        config_method: static
        address: "192.168.1.100"
        subnet_mask: "255.255.255.0"
        gateway: "192.168.1.1"

    - name: Disable ipv4 connectivity for the second port on the B controller
      na_santricity_mgmt_interface:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: "2"
        controller: "B"
        enable_interface: no

    - name: Enable ssh access for ports one and two on controller A
      na_santricity_mgmt_interface:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: "{{ item }}"
        controller: "A"
        ssh: yes
      loop:
        - 1
        - 2

    - name: Configure static DNS settings for the first port on controller A
      na_santricity_mgmt_interface:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: "1"
        controller: "A"
        dns_config_method: static
        dns_address: "192.168.1.100"
        dns_address_backup: "192.168.1.1"

    - name: Configure static NTP settings for ports one and two on controller B
      na_santricity_mgmt_interface:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: "{{ item }}"
        controller: "B"
        ntp_config_method: static
        ntp_address: "129.100.1.100"
        ntp_address_backup: "127.100.1.1"
      loop:
        - 1
        - 2
"""

RETURN = """
msg:
    description: Success message
    returned: on success
    type: str
    sample: The interface settings have been updated.
enabled:
    description:
        - Indicates whether IPv4 connectivity has been enabled or disabled.
        - This does not necessarily indicate connectivity. If dhcp was enabled absent a dhcp server, for instance,
          it is unlikely that the configuration will actually be valid.
    returned: on success
    sample: True
    type: bool
"""
import time

from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule
from ansible.module_utils._text import to_native
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class NetAppESeriesMgmtInterface(NetAppESeriesModule):
    MAXIMUM_VERIFICATION_TIMEOUT = 120
    def __init__(self):
        ansible_options = dict(state=dict(type="str", choices=["enable", "disable"], aliases=["enable_interface"], required=False),
                               controller=dict(type="str", required=True, choices=["A", "B"]),
                               name=dict(type="str", aliases=["port", "iface"]),
                               channel=dict(type="int"),
                               address=dict(type="str", required=False),
                               subnet_mask=dict(type="str", required=False),
                               gateway=dict(type="str", required=False),
                               config_method=dict(type="str", required=False, choices=["dhcp", "static"]),
                               dns_config_method=dict(type="str", required=False, choices=["dhcp", "static"]),
                               dns_address=dict(type="str", required=False),
                               dns_address_backup=dict(type="str", required=False),
                               ntp_config_method=dict(type="str", required=False, choices=["disable", "dhcp", "static"]),
                               ntp_address=dict(type="str", required=False),
                               ntp_address_backup=dict(type="str", required=False),
                               ssh=dict(type="bool", required=False))

        mutually_exclusive = [["name", "channel"]]
        required_if = [["state", "enable", ["config_method"]],
                       ["config_method", "static", ["address", "subnet_mask"]],
                       ["dns_config_method", "static", ["dns_address"]],
                       ["ntp_config_method", "static", ["ntp_address"]]]

        super(NetAppESeriesMgmtInterface, self).__init__(ansible_options=ansible_options,
                                                         web_services_version="02.00.0000.0000",
                                                         required_if=required_if,
                                                         mutually_exclusive=mutually_exclusive,
                                                         supports_check_mode=True)

        args = self.module.params

        self.controller = args["controller"]
        self.name = args["name"]
        self.channel = args["channel"]

        self.config_method = args["config_method"]
        self.address = args["address"]
        self.subnet_mask = args["subnet_mask"]
        self.gateway = args["gateway"]
        self.enable_interface = None if args["state"] is None else args["state"] == "enable"

        self.dns_config_method = args["dns_config_method"]
        self.dns_address = args["dns_address"]
        self.dns_address_backup = args["dns_address_backup"]

        self.ntp_config_method = args["ntp_config_method"]
        self.ntp_address = args["ntp_address"]
        self.ntp_address_backup = args["ntp_address_backup"]

        self.ssh = args["ssh"]

        self.check_mode = self.module.check_mode
        self.post_body = dict()

        self.alt_interface_addresses = []
        self.alt_url_path = None

    @property
    def controllers(self):
        """Retrieve a mapping of controller labels to their references
        {
            'A': '070000000000000000000001',
            'B': '070000000000000000000002',
        }
        :return: the controllers defined on the system
        """
        try:
            rc, controllers = self.request("storage-systems/%s/controllers" % self.ssid)
        except Exception as err:
            controllers = list()
            self.module.fail_json(msg="Failed to retrieve the controller settings. Array Id [%s]. Error [%s]." % (self.ssid, to_native(err)))

        controllers.sort(key=lambda c: c['physicalLocation']['slot'])

        controllers_dict = dict()
        i = ord('A')
        for controller in controllers:
            label = chr(i)
            settings = dict(controllerSlot=controller['physicalLocation']['slot'],
                            controllerRef=controller['controllerRef'],
                            ssh=controller['networkSettings']['remoteAccessEnabled'])
            controllers_dict[label] = settings
            i += 1

        return controllers_dict

    @property
    def interface(self):
        net_interfaces = list()
        try:
            rc, net_interfaces = self.request("storage-systems/%s/configuration/ethernet-interfaces" % self.ssid)
        except Exception as err:
            self.module.fail_json(msg="Failed to retrieve defined management interfaces. Array Id [%s]. Error [%s]." % (self.ssid, to_native(err)))

        controllers = self.controllers
        controller = controllers[self.controller]

        # Find the correct interface
        iface = None
        for net in net_interfaces:
            if net["controllerRef"] == controller["controllerRef"]:
                if self.name:
                    if net["alias"] == self.name or net["interfaceName"] == self.name:
                        iface = net
                elif self.channel:
                    if net["channel"] == self.channel:
                        iface = net
                elif net["ipv4Enabled"] and net["linkStatus"] == "up":
                    self.alt_interface_addresses.append(net["ipv4Address"])
            elif net["ipv4Enabled"] and net["linkStatus"] == "up":
                self.alt_interface_addresses.append(net["ipv4Address"])

        if iface is None:
            identifier = self.name if self.name is not None else self.channel
            self.module.fail_json(msg="We could not find an interface matching [%s] on Array=[%s]." % (identifier, self.ssid))

        return dict(alias=iface["alias"],
                    channel=iface["channel"],
                    link_status=iface["linkStatus"],
                    enabled=iface["ipv4Enabled"],
                    address=iface["ipv4Address"],
                    gateway=iface["ipv4GatewayAddress"],
                    subnet_mask=iface["ipv4SubnetMask"],
                    dns_config_method=iface["dnsProperties"]["acquisitionProperties"]["dnsAcquisitionType"],
                    dns_servers=iface["dnsProperties"]["acquisitionProperties"]["dnsServers"],
                    ntp_config_method=iface["ntpProperties"]["acquisitionProperties"]["ntpAcquisitionType"],
                    ntp_servers=iface["ntpProperties"]["acquisitionProperties"]["ntpServers"],
                    config_method=iface["ipv4AddressConfigMethod"],
                    controllerRef=iface["controllerRef"],
                    controllerSlot=iface["controllerSlot"],
                    ipv6Enabled=iface["ipv6Enabled"],
                    id=iface["interfaceRef"], )

    def get_enable_interface_settings(self, iface, expected_iface, update, body):
        """Enable or disable the IPv4 network interface."""
        if self.enable_interface:
            if not iface["enabled"]:
                update = True
            body["ipv4Enabled"] = True
        else:
            if iface["enabled"]:
                update = True
            body["ipv4Enabled"] = False

        expected_iface["enabled"] = body["ipv4Enabled"]
        return update, expected_iface, body

    def get_interface_settings(self, iface, expected_iface, update, body):
        """Update network interface settings."""

        if self.config_method == "dhcp":
            if iface["config_method"] != "configDhcp":
                update = True
            body["ipv4AddressConfigMethod"] = "configDhcp"

        else:
            if iface["config_method"] != "configStatic":
                update = True
            body["ipv4AddressConfigMethod"] = "configStatic"

            if iface["address"] != self.address:
                update = True
            body["ipv4Address"] = self.address

            if iface["subnet_mask"] != self.subnet_mask:
                update = True
            body["ipv4SubnetMask"] = self.subnet_mask

            if self.gateway and iface["gateway"] != self.gateway:
                update = True
            body["ipv4GatewayAddress"] = self.gateway

            expected_iface["address"] = body["ipv4Address"]
            expected_iface["subnet_mask"] = body["ipv4SubnetMask"]
            expected_iface["gateway"] = body["ipv4GatewayAddress"]

        expected_iface["config_method"] = body["ipv4AddressConfigMethod"]

        return update, expected_iface, body

    def get_dns_server_settings(self, iface, expected_iface, update, body):
        """Add DNS server information to the request body."""
        if self.dns_config_method == "dhcp":
            if iface["dns_config_method"] != "dhcp":
                update = True
            body["dnsAcquisitionDescriptor"] = dict(dnsAcquisitionType="dhcp")

        elif self.dns_config_method == "static":
            dns_servers = [dict(addressType="ipv4", ipv4Address=self.dns_address)]
            if self.dns_address_backup:
                dns_servers.append(dict(addressType="ipv4", ipv4Address=self.dns_address_backup))

            body["dnsAcquisitionDescriptor"] = dict(dnsAcquisitionType="stat", dnsServers=dns_servers)

            if (iface["dns_config_method"] != "stat" or
                    len(iface["dns_servers"]) != len(dns_servers) or
                    (len(iface["dns_servers"]) == 2 and
                     (iface["dns_servers"][0]["ipv4Address"] != self.dns_address or
                      iface["dns_servers"][1]["ipv4Address"] != self.dns_address_backup)) or
                    (len(iface["dns_servers"]) == 1 and
                     iface["dns_servers"][0]["ipv4Address"] != self.dns_address)):
                update = True

            expected_iface["dns_servers"] = dns_servers

        expected_iface["dns_config_method"] = body["dnsAcquisitionDescriptor"]["dnsAcquisitionType"]
        return update, expected_iface, body

    def get_ntp_server_settings(self, iface, expected_iface, update, body):
        """Add NTP server information to the request body."""
        if self.ntp_config_method == "disable":
            if iface["ntp_config_method"] != "disabled":
                update = True
            body["ntpAcquisitionDescriptor"] = dict(ntpAcquisitionType="disabled")

        elif self.ntp_config_method == "dhcp":
            if iface["ntp_config_method"] != "dhcp":
                update = True
            body["ntpAcquisitionDescriptor"] = dict(ntpAcquisitionType="dhcp")

        elif self.ntp_config_method == "static":
            ntp_servers = [dict(addrType="ipvx", ipvxAddress=dict(addressType="ipv4", ipv4Address=self.ntp_address))]
            if self.ntp_address_backup:
                ntp_servers.append(dict(addrType="ipvx",
                                        ipvxAddress=dict(addressType="ipv4", ipv4Address=self.ntp_address_backup)))

            body["ntpAcquisitionDescriptor"] = dict(ntpAcquisitionType="stat", ntpServers=ntp_servers)

            if (iface["ntp_config_method"] != "stat" or
                    len(iface["ntp_servers"]) != len(ntp_servers) or
                    ((len(iface["ntp_servers"]) == 2 and
                      (iface["ntp_servers"][0]["ipvxAddress"]["ipv4Address"] != self.ntp_address or
                      iface["ntp_servers"][1]["ipvxAddress"]["ipv4Address"] != self.ntp_address_backup)) or
                     (len(iface["ntp_servers"]) == 1 and
                      iface["ntp_servers"][0]["ipvxAddress"]["ipv4Address"] != self.ntp_address))):
                update = True

            expected_iface["ntp_servers"] = ntp_servers

        expected_iface["ntp_config_method"] = body["ntpAcquisitionDescriptor"]["ntpAcquisitionType"]
        return update, expected_iface, body

    def get_remote_ssh_settings(self, settings, update, body):
        """Configure network interface ports for remote ssh access."""
        if self.ssh != settings["ssh"]:
            update = True

        body["enableRemoteAccess"] = self.ssh
        return update, body

    def update_url(self):
        """Update eseries base class url if on is available."""
        if self.alt_interface_addresses:
            parsed_url = urlparse.urlparse(self.url)
            location = parsed_url.netloc.split(":")
            location[0] = self.alt_interface_addresses[0]
            self.url = "%s://%s/" % (parsed_url.scheme, ":".join(location))

    def update_array(self, settings, iface):
        """Update controller with new interface, dns service, ntp service and/or remote ssh access information.

        :returns: whether information passed will modify the controller's current state
        :rtype: bool
        """
        update = False
        body = dict(controllerRef=settings['controllerRef'],
                    interfaceRef=iface['id'])
        expected_iface = iface.copy()
        is_embedded = self.is_embedded()

        # Populate the body of the request and check for changes
        if self.enable_interface is not None:
            update, expected_iface, body = self.get_enable_interface_settings(iface, expected_iface, update, body)
        if self.config_method is not None:
            update, expected_iface, body = self.get_interface_settings(iface, expected_iface, update, body)
        if self.dns_config_method is not None:
            update, expected_iface, body = self.get_dns_server_settings(iface, expected_iface, update, body)
        if self.ntp_config_method is not None:
            update, expected_iface, body = self.get_ntp_server_settings(iface, expected_iface, update, body)
        if self.ssh is not None:
            update, body = self.get_remote_ssh_settings(settings, update, body)
            iface["ssh"] = self.ssh
            expected_iface["ssh"] = self.ssh
        if update and not self.check_mode:
            try:
                rc, response = self.request("storage-systems/%s/configuration/ethernet-interfaces" % self.ssid, method="POST", timeout=10, data=body)
                if rc == 200:
                    return update

            except Exception as error:
                self.module.warn("The management port change request was execute but the response was interrupted!"
                                 " This may simple be due to the channel that was effected. Verifying changes were successful...")

            # Validate all changes have been made
            if is_embedded:
                self.update_url()

            for retries in range(self.MAXIMUM_VERIFICATION_TIMEOUT):
                updated_iface = {"ssh": self.controllers[self.controller]["ssh"]}
                updated_iface.update(self.interface)
                self.module.warn(",".join(["%s: %s" % (key, updated_iface[key] == expected_iface[key]) for key in expected_iface.keys()]))
                if all([updated_iface[key] == expected_iface[key] for key in expected_iface.keys()]):
                    break
                time.sleep(1)
            else:
                self.module.fail_json(msg="Changes failed to complete! Timeout waiting for management interface to update. Array [%s]." % self.ssid)
            self.module.warn("complete")
        return update

    def check_health(self, retries=30):
        """It's possible, due to a previous operation, for the API to report a 424 (offline) status for the
         storage-system. Therefore, we run a manual check with retries to attempt to contact the system before we
         continue.
        """
        try:
            rc, data = self.request("storage-systems/%s/controllers" % self.ssid, ignore_errors=True)

            # We've probably recently changed the interface settings and it's still coming back up: retry.
            if rc == 424:
                if retries:
                    time.sleep(1)
                    self.check_health(retries - 1)
                else:
                    self.module.fail_json(msg="Failed to pull storage-system information. Array Id [%s] Message [%s]." % (self.ssid, data))
            elif rc >= 300:
                self.module.fail_json(msg="Failed to pull storage-system information. Array Id [%s] Message [%s]." % (self.ssid, data))
        # This is going to catch cases like a connection failure
        except Exception as err:
            if retries:
                time.sleep(1)
                self.check_health(retries - 1)
            else:
                self.module.fail_json(msg="Connection failure: failed to modify the network settings! Array Id [%s]. Error [%s]." % (self.ssid, to_native(err)))

    def update(self):
        """Update storage system with necessary changes."""
        # Check if the storage array can be contacted
        self.check_health()

        # make the necessary changes to the storage system
        settings = self.controllers[self.controller]
        iface = self.interface
        update = self.update_array(settings, iface)

        self.module.exit_json(msg="The interface settings have been updated.", changed=update)


if __name__ == '__main__':
    interface = NetAppESeriesMgmtInterface()
    interface.update()
