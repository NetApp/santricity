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
module: nac_santricity_global
short_description: NetApp E-Series manage global settings configuration
description:
    - Allow the user to configure several of the global settings associated with an E-Series storage-system
version_added: '2.7'
author:
    - Michael Price (@lmprice)
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity
options:
    name:
        description:
            - Set the name of the E-Series storage-system
            - This label/name doesn't have to be unique.
            - May be up to 30 characters in length.
        aliases:
            - label
    cache_block_size:
        description:
            - Size of the cache's block size.
            - All volumes on the storage system share the same cache space; therefore, the volumes can have only one cache block size.
            - See M(nac_santricity_facts) for available sizes.
        type: int
        required: False
    cache_flush_threshold:
        description:
            - This is the percentage threshold of the amount of unwritten data that is allowed to remain on the storage array's cache before flushing.
        type: int
        required: False
    default_host_type:
        description:
            - Default host type for the storage system.
            - Either one of the following names can be specified, Linux DM-MP, VMWare, Windows, Windows Clustered, or a
              host type index which can be found in M(nac_santricity_facts)
        type: str
        required: False
    automatic_load_balancing:
        description:
            - Enables automatic load balancing.
        choices:
            - enabled
            - disabled
        required: False
notes:
    - Check mode is supported.
    - This module requires Web Services API v1.3 or newer.
"""

EXAMPLES = """
    - name: Set the storage-system name
      nac_santricity_global:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: myArrayName
        cache_block_size: 32768
        cache_flush_threshold: 80
        automatic_load_balancing: enabled
        default_host_type: Linux DM-MP
    - name: Set the storage-system name
      nac_santricity_global:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        name: myOtherArrayName
        cache_block_size: 8192
        cache_flush_threshold: 60
        automatic_load_balancing: disabled
        default_host_type: 28
"""

RETURN = """
changed:
    description: Whether global settings were changed
    returned: on success
    type: bool
    sample: true
array_name:
    description: Current storage array's name
    returned: on success
    type: str
    sample: arrayName
automatic_load_balancing:
    description: Whether automatic load balancing feature has been enabled
    returned: on success
    type: str
    sample: enabled
cache_settings:
    description: Current cache block size and flushing threshold values
    returned: on success
    type: dict
    sample: {"cache_block_size": 32768, "cache_flush_threshold": 80}
default_host_type_index:
    description: Current default host type index
    returned: on success
    type: int
    sample: 28
"""
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule
from ansible.module_utils._text import to_native


class NetAppESeriesGlobalSettings(NetAppESeriesModule):
    HOST_TYPE_INDEXES = {"linux dm-mp": 28, "vmware": 10, "windows": 1, "windows clustered": 8}

    def __init__(self):
        version = "02.00.0000.0000"
        ansible_options = dict(cache_block_size=dict(type="int", require=False),
                               cache_flush_threshold=dict(type="int", required=False),
                               default_host_type=dict(type="str", require=False),
                               automatic_load_balancing=dict(type="str", choices=["enabled", "disabled"], required=False),
                               name=dict(type='str', required=False, aliases=['label']))

        super(NetAppESeriesGlobalSettings, self).__init__(ansible_options=ansible_options,
                                                          web_services_version=version,
                                                          supports_check_mode=True)
        args = self.module.params
        self.cache_block_size = args["cache_block_size"]
        self.cache_flush_threshold = args["cache_flush_threshold"]
        self.host_type_index = args["default_host_type"]
        self.autoload_enabled = args["automatic_load_balancing"] == "enabled"
        self.name = args["name"]

        if not self.url.endswith('/'):
            self.url += '/'

        self.current_configuration_cache = None

    def get_current_configuration(self, update=False):
        """Retrieve the current storage array's global configuration."""
        if self.current_configuration_cache is None or update:
            self.current_configuration_cache = dict()

            # Get the storage array's capabilities and available options
            try:
                rc, capabilities = self.request("storage-systems/%s/capabilities" % self.ssid)
                self.current_configuration_cache["autoload_capable"] = "capabilityAutoLoadBalancing" in capabilities["productCapabilities"]
                self.current_configuration_cache["cache_block_size_options"] = capabilities["featureParameters"]["cacheBlockSizes"]
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve storage array capabilities. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            try:
                rc, host_types = self.request("storage-systems/%s/host-types" % self.ssid)
                self.current_configuration_cache["host_type_options"] = dict()
                for host_type in host_types:
                    self.current_configuration_cache["host_type_options"].update({host_type["code"].lower(): host_type["index"]})
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve storage array host options. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            # Get the current cache settings
            try:
                rc, settings = self.request("storage-systems/%s/graph/xpath-filter?query=/sa" % self.ssid)
                self.current_configuration_cache["cache_settings"] = {"cache_block_size": settings[0]["cache"]["cacheBlkSize"],
                                                                      "cache_flush_threshold": settings[0]["cache"]["demandFlushThreshold"]}
                self.current_configuration_cache["default_host_type_index"] = settings[0]["defaultHostTypeIndex"]
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve cache settings. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            try:
                rc, array_info = self.request("storage-systems/%s" % self.ssid)
                self.current_configuration_cache["autoload_enabled"] = array_info["autoLoadBalancingEnabled"]
                self.current_configuration_cache["host_connectivity_reporting_enabled"] = array_info["hostConnectivityReportingEnabled"]
                self.current_configuration_cache["name"] = array_info['name']
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve *. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return self.current_configuration_cache

    def change_cache_block_size_required(self):
        """Determine whether cache block size change is required."""
        if self.cache_block_size is None:
            return False

        current_available_block_sizes = self.get_current_configuration()["cache_block_size_options"]
        if self.cache_block_size not in current_available_block_sizes:
            self.module.fail_json(msg="Invalid cache block size. Array [%s]. Available cache block sizes [%s]." % (self.ssid, current_available_block_sizes))

        return self.cache_block_size != self.get_current_configuration()["cache_settings"]["cache_block_size"]

    def change_cache_flush_threshold_required(self):
        """Determine whether cache flush percentage change is required."""
        if self.cache_flush_threshold is None:
            return False

        if self.cache_flush_threshold < 0 or self.cache_flush_threshold > 100:
            self.module.fail_json(msg="Invalid cache flushing threshold, it must be equal to or between 0 and 100. Array [%s]" % self.ssid)

        return self.cache_flush_threshold != self.get_current_configuration()["cache_settings"]["cache_flush_threshold"]

    def change_host_type_required(self):
        """Determine whether default host type change is required."""
        if self.host_type_index is None:
            return False

        current_available_host_types = self.get_current_configuration()["host_type_options"]
        if isinstance(self.host_type_index, str):
            self.host_type_index = self.host_type_index.lower()

        if self.host_type_index in self.HOST_TYPE_INDEXES.keys():
            self.host_type_index = self.HOST_TYPE_INDEXES[self.host_type_index]
        elif self.host_type_index in current_available_host_types.keys():
            self.host_type_index = current_available_host_types[self.host_type_index]

        if self.host_type_index not in current_available_host_types.values():
            self.module.fail_json(msg="Invalid host type index! Array [%s]. Available host options [%s]." % (self.ssid, current_available_host_types))

        return int(self.host_type_index) != self.get_current_configuration()["default_host_type_index"]

    def change_autoload_enabled_required(self):
        """Determine whether automatic load balancing state change is required."""
        if self.autoload_enabled is None:
            return False

        change_required = False
        if self.autoload_enabled and not self.get_current_configuration()["autoload_capable"]:
            self.module.fail_json(msg="Automatic load balancing is not available. Array [%s]." % self.ssid)

        if self.autoload_enabled:
            if not self.get_current_configuration()["autoload_enabled"] or not self.get_current_configuration()["host_connectivity_reporting_enabled"]:
                change_required = True
        elif self.get_current_configuration()["autoload_enabled"]:
            change_required = True

        return change_required

    def change_name_required(self):
        """Determine whether storage array name change is required."""
        if self.name is None:
            return False

        if self.name and len(self.name) > 30:
            self.module.fail_json(msg="The provided name is invalid, it must be < 30 characters in length. Array [%s]" % self.ssid)

        return self.name != self.get_current_configuration()["name"]

    def update_cache_settings(self):
        """Update cache block size and/or flushing threshold."""
        block_size = self.cache_block_size if self.cache_block_size else self.get_current_configuration()["cache_settings"]["cache_block_size"]
        threshold = self.cache_flush_threshold if self.cache_flush_threshold else self.get_current_configuration()["cache_settings"]["cache_flush_threshold"]
        try:
            rc, cache_settings = self.request("storage-systems/%s/symbol/setSACacheParams?verboseErrorResponse=true" % self.ssid, method="POST",
                                              data={"cacheBlkSize": block_size, "demandFlushAmount": threshold, "demandFlushThreshold": threshold})
        except Exception as error:
            self.module.fail_json(msg="Failed to set cache settings. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def update_host_type(self):
        """Update default host type."""
        try:
            rc, default_host_type = self.request("storage-systems/%s/symbol/setStorageArrayProperties?verboseErrorResponse=true" % self.ssid, method="POST",
                                                 data={"settings": {"defaultHostTypeIndex": self.host_type_index}})
        except Exception as error:
            self.module.fail_json(msg="Failed to set default host type. Array [%s]. Error [%s]" % (self.ssid, to_native(error)))

    def update_autoload_enabled(self):
        """Update automatic load balancing state."""
        if self.autoload_enabled and not self.get_current_configuration()["host_connectivity_reporting_enabled"]:
            try:
                rc, host_connectivity_reporting = self.request("storage-systems/%s/symbol/setHostConnectivityReporting?verboseErrorResponse=true" % self.ssid,
                                                               method="POST", data={"enableHostConnectivityReporting": self.autoload_enabled})
            except Exception as error:
                self.module.fail_json(msg="Failed to enable host connectivity reporting which is needed for automatic load balancing state."
                                          " Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        try:
            rc, autoload = self.request("storage-systems/%s/symbol/setAutoLoadBalancing?verboseErrorResponse=true" % self.ssid,
                                        method="POST", data={"enableAutoLoadBalancing": self.autoload_enabled})
        except Exception as error:
            self.module.fail_json(msg="Failed to set automatic load balancing state. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def update_name(self):
        """Update storage array's name."""
        try:
            rc, result = self.request("storage-systems/%s/configuration" % self.ssid, method="POST", data={"name": self.name})
        except Exception as err:
            self.module.fail_json(msg="We failed to set the storage array name! Array Id [%s]. Error [%s]." % (self.ssid, to_native(err)))

    def update(self):
        """Ensure the storage array's global setting are correctly set."""
        change_required = False
        self.get_current_configuration()

        if (self.change_autoload_enabled_required() or self.change_cache_block_size_required() or self.change_cache_flush_threshold_required() or
                self.change_host_type_required() or self.change_name_required()):
            change_required = True

        if change_required and not self.module.check_mode:
            if self.change_autoload_enabled_required():
                self.update_autoload_enabled()
            if self.change_cache_block_size_required() or self.change_cache_flush_threshold_required():
                self.update_cache_settings()
            if self.change_host_type_required():
                self.update_host_type()
            if self.change_name_required():
                self.update_name()
            # self.module.fail_json(msg=change_required)

        self.get_current_configuration(update=True)
        self.module.exit_json(changed=change_required,
                              cache_settings=self.get_current_configuration()["cache_settings"],
                              default_host_type_index=self.get_current_configuration()["default_host_type_index"],
                              automatic_load_balancing="enabled" if self.get_current_configuration()["autoload_enabled"] else "disabled",
                              array_name=self.get_current_configuration()["name"])


if __name__ == '__main__':
    global_settings = NetAppESeriesGlobalSettings()
    global_settings.update()
