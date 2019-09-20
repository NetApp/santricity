#!/usr/bin/python

# (c) 2016, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {"metadata_version": "1.1",
                    "status": ["preview"],
                    "supported_by": "community"}


DOCUMENTATION = """
module: nac_santricity_storage_system
version_added: "2.2"
short_description: NetApp E-Series manage SANtricity web services proxy storage arrays
description:
    - Manage the arrays accessible via a NetApp Web Services Proxy for NetApp E-series storage arrays.
author:
    - Kevin Hulquest (@hulquest)
    - Nathan  Swartz (@ndswartz)
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
        required: false
        default: false
    force_password_update:
        description:
            - Force password change regardless of whether it can be validated
            - This option will disregard all password checks when I(force_password_update==True).
        type: bool
        required: false
        default: false
"""

EXAMPLES = """
---
    - name: Ensure presence of storage system
      nac_santricity_storage_system:
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
      nac_santricity_storage_system:
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
from time import sleep


class NetAppESeriesStorageSystem(NetAppESeriesModule):
    DEFAULT_CREDENTIALS = [("admin", "admin")]
    DEFAULT_CONNECTION_TIMEOUT_SEC = 10
    DEFAULT_DISCOVERY_TIMEOUT_SEC = 120

    def __init__(self):
        version = "02.00.0000.0000"
        ansible_options = dict(state=dict(required=True, choices=["present", "absent"]),
                               controller_addresses=dict(type="list", required=False),
                               array_subnet_mask=dict(type="str", required=False),
                               array_serial=dict(type="str", required=False),
                               array_wwn=dict(type="str", required=False),
                               array_password=dict(type="str", required=False, no_log=True),
                               meta_tags=dict(type="dict", required=False),
                               accept_array_certificate=dict(type="bool", required=False, default=False),
                               force_password_update=dict(type="bool", required=False, default=False))

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
        self.array_password = args["array_password"]
        self.accept_array_certificate = args["accept_array_certificate"]
        self.force_password_update = args["force_password_update"]

        self.meta_tags = dict()
        if args["meta_tags"]:
            for key in args["meta_tags"].keys():
                if not isinstance(args["meta_tags"][key], list):
                    self.meta_tags.update({key: [args["meta_tags"][key]]})

        if self.array_wwn:
            self.array_wwn = self.array_wwn.upper()

        self.system_info_cache = None
        self.system_changes_cache = None
        self.are_changes_required_cache = None
        self.is_supplied_array_password_valid_cache = None
        self.is_current_stored_password_valid_cache = None

    def get_discovered_array_address_list(self, addresses):
        """Temporarily add array to retrieve complete address."""
        system_exists = False
        system_id = ""
        system_addresses = None
        try:
            rc, storage_system = self.request("storage-systems", method="POST", data={"controllerAddresses": addresses, "password": self.array_password})
            system_exists = storage_system["alreadyExists"]
            system_id = storage_system["id"]

            for attempt in range(self.DEFAULT_DISCOVERY_TIMEOUT_SEC):
                try:
                    rc, resp = self.request("storage-systems/%s/graph/xpath-filter?query=//controller/netInterfaces/ethernet/ipv4Address" % system_id)
                    system_addresses = [address for address in resp if address != "0.0.0.0"]
                    break
                except Exception as error:
                    sleep(1)
                    pass
            else:
                self.module.fail_json(msg="Discovery failed to retrieve array list. Array [%s]." % self.ssid)

        except Exception as error:
            self.module.fail_json(msg="Discovery failed to temporarily add storage system. Array [%s]. Error [%s]" % (self.ssid, to_native(error)))
        finally:
            # Ensure that temporarily added system is removed if created
            if not system_exists:
                try:
                    rc, storage_system = self.request("storage-systems/%s" % system_id, method="DELETE")
                except Exception as error:
                    self.module.fail_json(msg="Discovery failed to remove temporary storage system, [%s]. Array [%s]. Error [%s]."
                                              % (system_id, self.ssid, to_native(error)))

        return system_addresses

    def discover_array(self):
        """Search for array using the world wide identifier."""
        subnet = ipaddress.ip_network(u"%s" % self.array_subnet_mask)

        try:
            rc, request_id = self.request("discovery", method="POST", data={"startIP": str(subnet[0]), "endIP": str(subnet[-1]),
                                                                            "connectionTimeout": self.DEFAULT_CONNECTION_TIMEOUT_SEC})
            search_complete = False

            try:
                while not search_complete:
                    rc, results = self.request("discovery?requestId=%s" % request_id["requestId"])

                    # Search current findings
                    search_complete = not results["discoverProcessRunning"]
                    for storage_system in results["storageSystems"]:
                        if storage_system["serialNumber"] == self.array_serial:
                            # Clear discovery request so that other requests can ensue.
                            try:
                                rc, request_id = self.request("discovery", method="DELETE")
                            except Exception as error:
                                self.module.fail_json(msg="Failed to delete discovery search. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

                            search_complete = True
                            self.controller_addresses = self.get_discovered_array_address_list(storage_system["ipAddresses"])
                            self.module.log("Controller addresses: %s" % self.controller_addresses)
                            break

                    sleep(1)
            except Exception as error:
                self.module.fail_json(msg="Failed to get the discovery results. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            # Ensure system has been discovered, otherwise fail.
            if search_complete and not self.controller_addresses:
                self.module.fail_json(msg="Failed to discover the storage array. Array [%s]." % self.ssid)

        except Exception as error:
            self.module.fail_json(msg="Failed to initiate array discovery. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    @property
    def system_info(self):
        """Get current web services proxy storage systems."""
        if self.system_info_cache is None:
            try:
                rc, storage_systems = self.request("storage-systems")

                for storage_system in storage_systems:
                    if storage_system["id"] == self.ssid:
                        self.system_info_cache = storage_system
                        break
                else:
                    self.system_info_cache = {}

            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve storage systems. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return self.system_info_cache

    def is_supplied_array_password_valid(self):
        """Whether the supplied array password matches the current device password."""
        if self.is_supplied_array_password_valid_cache is None:
            self.is_supplied_array_password_valid_cache = False
            rc, response = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", ignore_errors=True,
                                        data={"currentAdminPassword": self.array_password, "adminPassword": True, "newPassword": self.array_password})

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

    def are_changes_required(self, update=False):
        """Determine whether storage system configuration changes are required """
        if self.system_info and (self.are_changes_required_cache is None or update):
            self.are_changes_required_cache = False

            # Check addresses or array wwn
            if self.array_wwn:
                if self.array_wwn != self.system_info["wwn"]:
                    self.are_changes_required_cache = True
            elif self.controller_addresses:
                if sorted(self.controller_addresses) != sorted(self.system_info["managementPaths"]):
                    self.are_changes_required_cache = True
            else:
                self.module.fail_json(msg="Controller addresses failed to be discovered or supplied. Array [%s]." % self.ssid)

            # Check meta tags (length, keys, values)
            if len(self.meta_tags.keys()) != len(self.system_info["metaTags"]):
                self.are_changes_required_cache = True
            else:
                current_meta_tags = dict()
                for meta_tag in self.system_info["metaTags"]:
                    current_meta_tags.update({meta_tag["key"]: meta_tag["valueList"]})
                    if meta_tag["key"] not in self.meta_tags.keys():
                        self.are_changes_required_cache = True
                        break
                else:
                    for meta_tag in current_meta_tags.keys():
                        if sorted(self.meta_tags[meta_tag]) != sorted(current_meta_tags[meta_tag]):
                            self.are_changes_required_cache = True
                            break

            if self.accept_array_certificate and self.system_info["certificateStatus"] != "trusted":
                self.are_changes_required_cache = True

            # Check whether the supplied password matches the stored password.
            if self.force_password_update:
                self.are_changes_required_cache = True
            # elif self.is_supplied_array_password_valid():     # TODO: ??? PROXY does not seem to be accepting the current admin password of the storage array.
            #     if not self.is_current_stored_password_valid():
            #         self.are_changes_required_cache = True
            # else:
            #     self.module.fail_json(msg="The supplied array_password is not a valid password for the storage array. Array [%s]." % self.ssid)

        return self.are_changes_required_cache

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

    def set_initial_system_password(self):
        """Set the array password with it has not been set."""

        if self.array_password and self.set_initial_array_password:
            try:
                rc, password_info = self.request("storage-systems/%s/passwords" % self.ssid)

                # Set storage system's admin password
                if not password_info["adminPasswordSet"]:

                    # Ensure that proxy password is not set
                    try:
                        rc, storage_system = self.request("storage-systems/%s" % self.ssid, method="POST", data={"storedPassword": ""})
                    except Exception as error:
                        self.module.fail_json(msg="Failed to clear storage system's password. Array [%s]. Error [%s]" % (self.ssid, to_native(error)))

                    try:
                        headers = self.DEFAULT_HEADERS.update({"x-netapp-password-validate-method": "none"})
                        rc, storage_system = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", headers=headers,
                                                          data={"currentAdminPassword": "", "adminPassword": True, "newPassword": self.array_password})
                    except Exception as error:
                        self.module.fail_json(msg="Failed to set storage system password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            except Exception as error:
                self.module.fail_json(msg="Failed to validate storage system password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def add_system(self):
        """Add basic storage system definition to the web services proxy."""
        data = {"id": self.ssid,
                "acceptCertificate": self.accept_array_certificate,
                "metaTags": self.structure_meta_tags()}

        if self.controller_addresses:
            data.update({"controllerAddresses": self.controller_addresses})
        if self.array_wwn:
            data.update({"wwn": self.array_wwn})
        if self.array_password:
            data.update({"password": self.array_password})
        if self.structure_meta_tags():
            data.update({"metaTags": self.structure_meta_tags()})
        else:
            data.update({"removeAllTags": True})

        try:
            rc, storage_system = self.request("storage-systems", method="POST", data=data)

            # Check if system already exists
            if rc == 200:
                self.module.fail_json(msg="System already exists. Array [%s]." % self.ssid)
        except Exception as error:
            self.module.fail_json(msg="Failed to add storage system. Array [%s]. Error [%s]" % (self.ssid, to_native(error)))

    def update_system(self):
        """Update storage system configuration."""
        data = {"acceptCertificate": self.accept_array_certificate, "metaTags": self.structure_meta_tags()}

        if self.controller_addresses:
            data.update({"controllerAddresses": self.controller_addresses})
        if self.array_password:
            data.update({"storedPassword": self.array_password})
        if self.structure_meta_tags():
            data.update({"metaTags": self.structure_meta_tags()})
        else:
            data.update({"removeAllTags": True})

        try:
            rc, storage_system = self.request("storage-systems/%s" % self.ssid, method="POST", data=data)
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

        changes_required = False
        if self.state == "present":
            if self.array_serial:
                self.discover_array()

            if self.system_info:
                if self.are_changes_required():
                    changes_required = True
            else:
                changes_required = True
        elif self.system_info:
            changes_required = True

        if changes_required and not self.module.check_mode:
            if self.state == "present":
                if self.system_info:
                    self.update_system()
                    self.module.exit_json(msg="Storage system [%s] was updated." % self.ssid, changed=changes_required)
                else:
                    self.add_system()
                    self.module.exit_json(msg="Storage system [%s] was added." % self.ssid, changed=changes_required)

            elif self.system_info:
                self.remove_system()
                self.module.exit_json(msg="Storage system [%s] was removed." % self.ssid, changed=changes_required)

        self.module.exit_json(msg="No changes were required for storage system [%s]." % self.ssid, changed=changes_required)


if __name__ == '__main__':
    systems = NetAppESeriesStorageSystem()
    systems.apply()
