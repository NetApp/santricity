# (c) 2020, NetApp, Inc
# BSD-3 Clause (see COPYING or https://opensource.org/licenses/BSD-3-Clause)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: santricity_hosts
    author: Nathan Swartz
    short_description: Collects host information
    description:
        - Collects current host, expected host and host group inventory definitions.
    options:
        inventory:
            description:
                - E-Series storage array inventory, hostvars[inventory_hostname].
                - Run na_santricity_facts prior to calling
            required: True
            type: complex
"""
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, inventory, **kwargs):
        if isinstance(inventory, list):
            inventory = inventory[0]

        if ("eseries_storage_pool_configuration" not in inventory or not isinstance(inventory["eseries_storage_pool_configuration"], list) or
                len(inventory["eseries_storage_pool_configuration"]) == 0):
            return list()

        if "eseries_storage_pool_configuration" not in inventory.keys():
            raise AnsibleError("eseries_storage_pool_configuration must be defined. See nar_santricity_host role documentation.")

        info = {"current_hosts": {}, "expected_hosts": {}, "host_groups": {}}

        groups = []
        hosts = []
        non_inventory_hosts = []
        non_inventory_groups = []
        for group in inventory["groups"].keys():
            groups.append(group)
            hosts.extend(inventory["groups"][group])

        if "eseries_host_object" in inventory.keys():
            non_inventory_hosts = [host["name"] for host in inventory["eseries_host_object"]]
            non_inventory_groups = [host["group"] for host in inventory["eseries_host_object"] if "group" in host]

        # Determine expected hosts and host groups
        for storage_pool in inventory["eseries_storage_pool_configuration"]:
            if "volumes" in storage_pool:
                for volume in storage_pool["volumes"]:

                    if (("state" in volume and volume["state"] == "present") or
                            ("eseries_volume_state" in inventory and inventory["eseries_volume_state"] == "present") or
                            ("state" not in volume and "eseries_volume_state" not in inventory)):
                        if "host" in volume:
                            if volume["host"] in groups:

                                if volume["host"] not in info["host_groups"].keys():

                                    # Add all expected group hosts
                                    for expected_host in inventory["groups"][volume["host"]]:
                                        if "host_type" in volume:
                                            info["expected_hosts"].update({expected_host: {"state": "present",
                                                                                           "host_type": volume["host_type"],
                                                                                           "group": volume["host"]}})
                                        elif "common_volume_configuration" in storage_pool and "host_type" in storage_pool["common_volume_configuration"]:
                                            info["expected_hosts"].update({expected_host: {"state": "present",
                                                                                           "host_type": storage_pool["common_volume_configuration"]["host_type"],
                                                                                           "group": volume["host"]}})
                                        elif "eseries_system_default_host_type" in inventory:
                                            info["expected_hosts"].update({expected_host: {"state": "present",
                                                                                           "host_type": inventory["eseries_system_default_host_type"],
                                                                                           "group": volume["host"]}})
                                        else:
                                            info["expected_hosts"].update({expected_host: {"state": "present",
                                                                                           "group": volume["host"]}})

                                    info["host_groups"].update({volume["host"]: inventory["groups"][volume["host"]]})

                            elif volume["host"] in hosts:
                                if "host_type" in volume:
                                    info["expected_hosts"].update({volume["host"]: {"state": "present",
                                                                                    "host_type": volume["host_type"],
                                                                                    "group": None}})
                                elif "common_volume_configuration" in storage_pool and "host_type" in storage_pool["common_volume_configuration"]:
                                    info["expected_hosts"].update({volume["host"]: {"state": "present",
                                                                                    "host_type": storage_pool["common_volume_configuration"]["host_type"],
                                                                                    "group": volume["host"]}})
                                elif "eseries_system_default_host_type" in inventory:
                                    info["expected_hosts"].update({volume["host"]: {"state": "present",
                                                                                    "host_type": inventory["eseries_system_default_host_type"],
                                                                                    "group": volume["host"]}})
                                else:
                                    info["expected_hosts"].update({volume["host"]: {"state": "present",
                                                                                    "group": None}})

                            elif volume["host"] not in non_inventory_hosts and volume["host"] not in non_inventory_groups:
                                raise AnsibleError("Expected host or host group does not exist in your Ansible inventory and is not specified in"
                                                   " eseries_host_object variable!")

        return [info]
