from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: santricity_hosts
    author: Nathan Swartz
    short_description: 
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

        if "storage_array_facts" not in inventory.keys():
            raise AnsibleError("Storage array information not available. Collect facts using na_santricity_facts module.")

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
                                        info["expected_hosts"].update({expected_host: {"state": "present",
                                                                                       "host_type": volume["host_type"] if "host_type" in volume else "0",
                                                                                       "group": volume["host"]}})

                                    # Determine if group exists on the storage array and any hosts associated
                                    group_current_hosts = []
                                    for group in inventory["storage_array_facts"]["storage_array_facts"]["netapp_host_groups"]:
                                        if volume["host"] == group["id"] or volume["host"] == group["name"]:
                                            for current_host in inventory["storage_array_facts"]["storage_array_facts"]["netapp_hosts"]:
                                                if group["id"] == current_host["group_id"]:
                                                    group_current_hosts.append(current_host["name"])
                                                    info["current_hosts"].update({current_host["name"]: {"group": volume["host"], "ports": current_host["ports"]}})

                                    info["host_groups"].update({volume["host"]: group_current_hosts})

                            elif volume["host"] in hosts:
                                info["expected_hosts"].update({volume["host"]: {"state": "present",
                                                                                "host_type": volume["host_type"] if "host_type" in volume else "0",
                                                                                "group": None}})

                            elif volume["host"] not in non_inventory_hosts and volume["host"] not in non_inventory_groups:
                                raise AnsibleError("Expected host or host group does not exist in your Ansible inventory and is not specified in"
                                                   " eseries_host_object variable!")
        return [info]
