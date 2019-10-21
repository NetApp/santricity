#!/usr/bin/python

# (c) 2016, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {"metadata_version": "1.1",
                    "status": ["preview"],
                    "supported_by": "community"}


DOCUMENTATION = """
module: na_santricity_storage_system
version_added: "2.2"
short_description: NetApp E-Series manage SANtricity web services proxy storage arrays
description:
    - Manage the arrays accessible via a NetApp Web Services Proxy for NetApp E-series storage arrays.
author:
    - Kevin Hulquest (@hulquest)
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity_doc
options:
    state:
        description:
            - Whether the specified array should be configured on the Web Services Proxy or not.
        required: true
        choices: ["present", "absent"]
    controller_addresses:
        description:
            - The list addresses for the out-of-band management adapter or the agent host.
            - Mutually exclusive with I(array_wwn).
        type: str
        required: false
    array_subnet_mask:
        description:
            - IPv4 subnet mask specified in CIDR form. Example 192.168.1.1/24
            - This is used to discover E-Series storage arrays.
    array_serial:
        description:
            - This is the enclosure's serial number
            - Enclosure serial number is printed on a silver label affixed to the top of the system enclosure
            - Mutually exclusive with I(controller_addresses) and I(array_wwn).
        type: str
        required: False
    array_wwn:
        description:
            - The WWN of the array to manage.
            - Only necessary if in-band managing multiple arrays on the same agent host.
            - Mutually exclusive with I(controller_addresses)
        type: str
        required: false
    array_password:
        description:
            - The management password of the array to manage.
        type: str
        required: true
    meta_tags:
        description:
            - Optional meta tags to associate to this storage system
        type: dict
        required: false
    accept_array_certificate:
        description:
            - Accept the storage array's certificate even when it is self-signed.
            - Older systems that only support SYMbol should not use this option.
        required: false
        default: true
    set_array_password:
        description:
            - Set the password of the storage array to I(array_password) when the password has not been set.
note:
    - When changing the controller IP addresses the web services proxy needs to be removed and added due to a known issue in the proxy before version 4.1.
      This will result in a lost of historic information! Use M(na_santricity_storage_system) to update the proxy's IP addresses.
"""

EXAMPLES = """
---
    - name: Ensure presence of storage system
      na_santricity_storage_system:
        ssid: "1"
        api_url: https://192.168.1.100:8443/devmgr/v2
        api_username: admin
        api_password: adminpass
        validate_certs: true
        state: present
        array_password: arraypass
        clear_array_password: true
        controller_addresses:
          - 192.168.1.100
          - 192.168.1.102
    - name: Ensure presence of storage system
      na_santricity_storage_system:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        state: present
        array_serial: 012345678901
        array_subnet_mask: 192.168.1.0/27
        meta_tags:
            use: corporate
            location: sunnyvale
"""

RETURN = """
msg:
    description: State of request
    type: str
    returned: always
    sample: "Storage system removed."
"""
import ipaddress

from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule
from ansible.module_utils._text import to_native
from pprint import pformat
from time import sleep
from random import random


class NetAppESeriesStorageSystem(NetAppESeriesModule):
    DEFAULT_CONNECTION_TIMEOUT_SEC = 1
    DEFAULT_DISCOVERY_TIMEOUT_SEC = 120
    MANAGEMENT_PATH_FIX_PROXY_VERSION = "04.20.0000.0000"

    def __init__(self):
        version = "02.00.0000.0000"
        ansible_options = dict(state=dict(required=True, choices=["present", "absent"]),
                               controller_addresses=dict(type="list", required=False),
                               array_subnet_mask=dict(type="str", required=False),
                               array_serial=dict(type="str", required=False),
                               array_wwn=dict(type="str", required=False),
                               array_password=dict(type="str", required=False, no_log=True),
                               meta_tags=dict(type="dict", required=False),
                               accept_array_certificate=dict(type="bool", required=False, default=True))

        mutually_exclusive = [["controller_addresses", "array_wwn"],
                              ["controller_addresses", "array_serial"],
                              ["array_wwn", "array_serial"]]

        required_one_of = [["controller_addresses", "array_wwn", "array_serial"]]
        required_together = [["array_serial", "array_subnet_mask"],
                             ["array_subnet_mask", "array_serial"]]

        super(NetAppESeriesStorageSystem, self).__init__(ansible_options=ansible_options,
                                                         web_services_version=version,
                                                         mutually_exclusive=mutually_exclusive,
                                                         required_together=required_together,
                                                         required_one_of=required_one_of,
                                                         supports_check_mode=True)
        args = self.module.params
        self.state = args["state"]
        self.controller_addresses = args["controller_addresses"]
        self.array_wwn = args["array_wwn"]
        self.array_subnet_mask = args["array_subnet_mask"]
        self.array_serial = args["array_serial"]
        self.array_password = args["array_password"] if args["array_password"] else ""
        self.accept_array_certificate = args["accept_array_certificate"]

        self.meta_tags = dict()
        if args["meta_tags"]:
            for key in args["meta_tags"].keys():
                if not isinstance(args["meta_tags"][key], list):
                    self.meta_tags.update({key: [args["meta_tags"][key]]})

        self.DEFAULT_HEADERS.update({"x-netapp-password-validate-method": "none"})
        self.stateless_token = "".join([chr(int(random() * 95 + 32)) for i in range(32)])

        if self.array_wwn:
            self.array_wwn = self.array_wwn.upper()

        self.system_info_cache = None
        self.system_changes_cache = None
        self.get_changes_cache = None
        self.is_supplied_array_password_valid_cache = None
        self.is_current_stored_password_valid_cache = None
        self.is_system_password_set_cache = None

    def discover_array(self):
        """Search for array using the world wide identifier."""
        subnet = ipaddress.ip_network(u"%s" % self.array_subnet_mask)

        try:
            rc, request_id = self.request("discovery", method="POST", data={"startIP": str(subnet[0]), "endIP": str(subnet[-1]),
                                                                            "connectionTimeout": self.DEFAULT_CONNECTION_TIMEOUT_SEC})
            try:
                for iteration in range(self.DEFAULT_DISCOVERY_TIMEOUT_SEC):
                    rc, results = self.request("discovery?requestId=%s" % request_id["requestId"])

                    if not results["discoverProcessRunning"]:
                        for storage_system in results["storageSystems"]:
                            if storage_system["serialNumber"] == self.array_serial:
                                self.controller_addresses = storage_system["ipAddresses"]
                                break
                        break
                    sleep(1)
                else:
                    self.module.fail_json(msg="Timeout waiting for array discovery process. Array [%s]. Subnet [%s]" % (self.ssid, self.array_subnet_mask))
            except Exception as error:
                self.module.fail_json(msg="Failed to get the discovery results. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            if not self.controller_addresses:
                self.module.fail_json(msg="Failed to discover the storage array. Array [%s]. Serial [%s]" % (self.ssid, self.array_serial))

        except Exception as error:
            self.module.fail_json(msg="Failed to initiate array discovery. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def system_info(self):
        """Get current web services proxy storage systems."""
        system_info = {}
        try:
            rc, storage_systems = self.request("storage-systems")

            for storage_system in storage_systems:
                if storage_system["id"] == self.ssid:
                    system_info = storage_system
                    break

            self.module.log(pformat(self.system_info_cache))
        except Exception as error:
            self.module.fail_json(msg="Failed to retrieve storage systems. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return system_info

    def is_supplied_array_password_valid(self):
        """Whether the supplied array password matches the current device password."""
        if self.is_supplied_array_password_valid_cache is None:
            body = {"currentAdminPassword": self.array_password, "adminPassword": True, "newPassword": self.array_password}
            if self.is_embedded_available():
                rc, password_info = self.request("storage-systems/%s/forward/devmgr/v2/storage-systems/1/passwords" % self.ssid, method="POST",
                                                 ignore_errors=True, data=body)
            else:
                rc, response = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", ignore_errors=True, data=body)

            if rc == 204:
                self.is_supplied_array_password_valid_cache = True
            elif rc == 422:
                self.is_supplied_array_password_valid_cache = False
            else:
                self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

        return self.is_supplied_array_password_valid_cache

    def is_current_stored_password_valid(self):
        """Determine whether the current stored password is valid."""
        if self.is_current_stored_password_valid_cache is None:
            self.is_current_stored_password_valid_cache = False
            rc, response = self.request("storage-systems/%s/validatePassword" % self.ssid, method="POST", ignore_errors=True)

            if rc == 204:
                self.is_current_stored_password_valid_cache = True
            elif rc == 422:
                self.is_current_stored_password_valid_cache = False
            else:
                self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

        return self.is_current_stored_password_valid_cache

    def has_stored_password_changed(self):
        """Determine whether the store password has changed."""
        change_password = False
        if (self.array_password and not self.is_system_password_set()) or (not self.array_password and self.is_system_password_set()):
            change_password = True
        elif self.is_supplied_array_password_valid():
            rc, response = self.request("storage-systems/%s/stored-password/validate" % self.ssid, method="POST", ignore_errors=True,
                                        data={"password": self.array_password})
            if rc == 200:
                change_password = not response["isValidPassword"]

            # Proxy versions prior to 4.1 will not have this endpoint so use the older method of determining password changes
            elif rc == 404 and not self.is_current_stored_password_valid():
                change_password = True
        else:
            self.module.fail_json(msg="The supplied array_password is not a valid password for the storage array. Array [%s]." % self.ssid)

        return change_password

    def get_changes(self, update=False):
        """Determine whether storage system configuration changes are required """
        # Check whether the supplied password matches the stored password.
        if self.system_info() and (self.get_changes_cache is None or update):
            self.get_changes_cache = dict()

            if self.has_stored_password_changed():
                self.get_changes_cache["storedPassword"] = self.array_password

            # Check addresses or array wwn
            if self.array_wwn:
                if self.array_wwn != self.system_info()["wwn"]:
                    self.get_changes_cache["wwn"] = self.array_wwn

            elif self.controller_addresses:
                if sorted(self.controller_addresses) != sorted(self.system_info()["managementPaths"]):
                    self.get_changes_cache["controllerAddresses"] = self.controller_addresses
                elif self.system_info()["ip1"] not in self.system_info()["managementPaths"]:
                    self.get_changes_cache["controllerAddresses"] = self.controller_addresses
                elif self.system_info()["ip2"] not in self.system_info()["managementPaths"]:
                    self.get_changes_cache["controllerAddresses"] = self.controller_addresses

            else:
                self.module.fail_json(msg="Controller addresses failed to be discovered or supplied. Array [%s]." % self.ssid)

            # Check meta tags (length, keys, values)
            if len(self.meta_tags.keys()) != len(self.system_info()["metaTags"]):
                if len(self.meta_tags.keys()) == 0:
                    self.get_changes_cache["removeAllTags"] = True
                else:
                    self.get_changes_cache["metaTags"] = self.structure_meta_tags()
            else:
                current_meta_tags = dict()
                for meta_tag in self.system_info()["metaTags"]:
                    current_meta_tags.update({meta_tag["key"]: meta_tag["valueList"]})
                    if meta_tag["key"] not in self.meta_tags.keys():
                        self.get_changes_cache["metaTags"] = self.structure_meta_tags()
                        break
                else:
                    for meta_tag in current_meta_tags.keys():
                        if sorted(self.meta_tags[meta_tag]) != sorted(current_meta_tags[meta_tag]):
                            self.get_changes_cache["metaTags"] = self.structure_meta_tags()
                            break

            if self.accept_array_certificate:
                if "https" not in self.system_info()["supportedManagementPorts"]:
                    self.accept_array_certificate = False
                elif self.system_info()["certificateStatus"] != "trusted":
                    self.get_changes_cache["acceptCertificate"] = self.accept_array_certificate

        return self.get_changes_cache

    def structure_meta_tags(self):
        """Structure the meta tags for the request body."""
        structured_meta_tags = []
        if self.meta_tags:
            for key in self.meta_tags.keys():
                if isinstance(self.meta_tags[key], list):
                    structured_meta_tags.append({"key": key, "valueList": self.meta_tags[key]})
                else:
                    structured_meta_tags.append({"key": key, "valueList": [self.meta_tags[key]]})

        return structured_meta_tags

    def is_system_password_set(self, stateless=False):
        """Determine whether password has been set."""
        if self.is_system_password_set_cache is None:
            if stateless:
                try:
                    stateless_headers = self.DEFAULT_HEADERS.copy()
                    stateless_headers.update({"x-netapp.mgr-paths": ",".join(self.controller_addresses),
                                              "x-netapp-webapi-client-token": self.stateless_token})
                    rc, password_info = self.request("storage-systems/stateless/passwords", headers=stateless_headers)
                    self.is_system_password_set_cache = password_info["adminPasswordSet"]

                except Exception as error:
                    self.module.fail_json(msg="Failed to retrieve array password state. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))
            else:
                try:
                    rc, password_info = self.request("storage-systems/%s/passwords" % self.ssid)
                    self.is_system_password_set_cache = password_info["adminPasswordSet"]
                except Exception as error:
                    self.module.fail_json(msg="Failed to retrieve array password state. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return self.is_system_password_set_cache

    def set_system_password(self):
        """Set the array password with it has not been set."""
        try:
            rc, storage_system = self.request("storage-systems/%s/passwords" % self.ssid, method="POST",
                                              data={"currentAdminPassword": "", "adminPassword": True, "newPassword": self.array_password})
        except Exception as error:
            self.module.fail_json(msg="Failed to set storage system password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def add_system(self):
        """Add basic storage system definition to the web services proxy."""
        set_password = False
        body = {"id": self.ssid, "acceptCertificate": self.accept_array_certificate, "password": self.array_password}
        if not self.is_system_password_set(stateless=True) and self.array_password:
            set_password = True
            body.update({"password": ""})
        if self.controller_addresses:
            body.update({"controllerAddresses": self.controller_addresses})
        if self.array_wwn:
            body.update({"wwn": self.array_wwn})
        if self.meta_tags:
            body.update({"metaTags": self.structure_meta_tags()})

        try:
            rc, storage_system = self.request("storage-systems", method="POST", data=body)
        except Exception as error:
            self.module.fail_json(msg="Failed to add storage system. Array [%s]. Error [%s]" % (self.ssid, to_native(error)))

        if set_password:
            self.set_system_password()

    def update_system(self):
        """Update storage system configuration."""
        if not self.is_system_password_set() and self.array_password:
            self.set_system_password()

        if self.get_changes(update=True):
            if not self.is_web_services_version_met(self.MANAGEMENT_PATH_FIX_PROXY_VERSION) and "controllerAddresses" in self.get_changes():
                self.module.warn("The storage system will be removed and then re-added due to known issue in your Web Services Proxy version."
                                 " See note in documentation.")
                self.remove_system()
                self.add_system()
            else:
                try:
                    rc, storage_system = self.request("storage-systems/%s" % self.ssid, method="POST", data=self.get_changes())
                except Exception as error:
                    self.module.fail_json(msg="Failed to update storage system. Array [%s]. Error [%s]" % (self.ssid, to_native(error)))

    def remove_system(self):
        """Remove storage system."""
        try:
            rc, storage_system = self.request("storage-systems/%s" % self.ssid, method="DELETE")
        except Exception as error:
            self.module.fail_json(msg="Failed to remove storage system. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def apply(self):
        """Determine whether changes are required and, if necessary, apply them."""
        if self.is_embedded():
            self.module.fail_json(msg="Cannot add storage systems to SANtricity Web Services Embedded instance. Array [%s]." % self.ssid)

        changes_required = None
        if self.state == "present":

            if self.array_serial:
                self.discover_array()

            if self.system_info():
                self.is_system_password_set()
                if self.get_changes():
                    changes_required = True
            else:
                changes_required = True
        elif self.system_info():
            changes_required = True

        if changes_required and not self.module.check_mode:
            if self.state == "present":
                if self.system_info():
                    self.update_system()
                    self.module.exit_json(msg="Storage system [%s] was updated." % self.ssid, changed=changes_required)
                else:
                    self.add_system()
                    self.module.exit_json(msg="Storage system [%s] was added." % self.ssid, changed=changes_required)

            elif self.system_info():
                self.remove_system()
                self.module.exit_json(msg="Storage system [%s] was removed." % self.ssid, changed=changes_required)

        self.module.exit_json(msg="No changes were required for storage system [%s]." % self.ssid, changed=changes_required)


if __name__ == '__main__':
    systems = NetAppESeriesStorageSystem()
    systems.apply()
