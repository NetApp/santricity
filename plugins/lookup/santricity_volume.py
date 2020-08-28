# (c) 2020, NetApp, Inc
# BSD-3 Clause (see COPYING or https://opensource.org/licenses/BSD-3-Clause)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError
from itertools import product


class LookupModule(LookupBase):

    def run(self, inventory, **kwargs):
        if isinstance(inventory, list):
            inventory = inventory[0]

        if ("eseries_storage_pool_configuration" not in inventory.keys() or not isinstance(inventory["eseries_storage_pool_configuration"], list) or
                len(inventory["eseries_storage_pool_configuration"]) == 0):
            return list()

        vol_list = list()
        for sp_info in inventory["eseries_storage_pool_configuration"]:

            if "name" not in sp_info.keys() or "volumes" not in sp_info.keys():
                continue

            if not isinstance(sp_info["volumes"], list):
                raise AnsibleError("Volumes must be a list")

            for sp in patternize(sp_info["name"], inventory):
                for vol_info in sp_info["volumes"]:

                    if not isinstance(vol_info, dict):
                        raise AnsibleError("Volume in the storage pool, %s, must be a dictionary." % sp_info["name"])

                    for vol in patternize(vol_info["name"], inventory, storage_pool=sp):
                        vol_options = dict()

                        # Add common_volume_configuration information
                        combined_volume_metadata = {}
                        if "common_volume_configuration" in sp_info:
                            for option, value in sp_info["common_volume_configuration"].items():
                                vol_options.update({option: value})
                            if "volume_metadata" in sp_info["common_volume_configuration"].keys():
                                combined_volume_metadata.update(sp_info["common_volume_configuration"]["volume_metadata"])

                        # Add/update volume specific information
                        for option, value in vol_info.items():
                            vol_options.update({option: value})
                        if "volume_metadata" in vol_info.keys():
                            combined_volume_metadata.update(vol_info["volume_metadata"])
                            vol_options.update({"volume_metadata": combined_volume_metadata})


                        if "state" in sp_info and sp_info["state"] == "absent":
                            vol_options.update({"state": "absent"})

                        vol_options.update({"name": vol, "storage_pool_name": sp})
                        vol_list.append(vol_options)
        return vol_list


def patternize(pattern, inventory, storage_pool=None):
    """Generate list of strings determined by a pattern"""
    if storage_pool:
        pattern = pattern.replace("[pool]", storage_pool)

    if inventory:
        inventory_tokens = re.findall(r"\[[a-zA-Z0-9_]*\]", pattern)
        for token in inventory_tokens:
            pattern = pattern.replace(token, str(inventory[token[1:-1]]))

    tokens = re.findall(r"\[[0-9]-[0-9]\]|\[[a-z]-[a-z]\]|\[[A-Z]-[A-Z]\]", pattern)
    segments = "%s".join(re.split(r"\[[0-9]-[0-9]\]|\[[a-z]-[a-z]\]|\[[A-Z]-[A-Z]\]", pattern))

    if len(tokens) == 0:
        return [pattern]

    combinations = []
    for token in tokens:
        start, stop = token[1:-1].split("-")

        try:
            start = int(start)
            stop = int(stop)
            combinations.append([str(number) for number in range(start, stop + 1)])
        except ValueError:
            combinations.append([chr(number) for number in range(ord(start), ord(stop) + 1)])

    return [segments % subset for subset in list(product(*combinations))]
