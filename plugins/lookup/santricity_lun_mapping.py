from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError


class LookupModule(LookupBase):

    def run(self, inventory, volumes, **kwargs):
        if isinstance(inventory, list):
            inventory = inventory[0]

        if isinstance(volumes, dict):   # This means that there is only one volume and volumes was stripped of its list
            volumes = [volumes]

        if "storage_array_facts" not in inventory.keys():
            raise AnsibleError("Storage array information not available. Collect facts using na_santricity_facts module.")

        luns_by_target = inventory["storage_array_facts"]["storage_array_facts"]["netapp_luns_by_target"]
        mapping_info = list()
        for volume in volumes:

            # Check whether storage pool has specified a target host
            if "host" in volume:

                # Existing lun mappings
                if volume["host"] in luns_by_target:
                    for mapped_volume_name, mapped_lun in luns_by_target[volume["host"]]:
                        if mapped_volume_name == volume["name"]:
                            mapping_info.append({"volume": volume["name"], "target": volume["host"], "lun": mapped_lun})
                            break
                    else:
                        used_list = [lun for vol, lun in luns_by_target[volume["host"]]]
                        next_lun = 1
                        while next_lun in used_list:
                            next_lun += 1

                        luns_by_target[volume["host"]].append(('_', next_lun))
                        mapping_info.append({"volume": volume["name"], "target": volume["host"], "lun": next_lun})

                # Map volume to host groups
                elif volume["host"] in inventory["groups"]:
                    mapped_luns = []
                    for host in inventory["groups"][volume["host"]]:
                        if host in luns_by_target:
                            mapped_luns.extend(luns_by_target[host])
                    luns_by_target.update({volume["host"]: mapped_luns})

                    used_list = [lun for vol, lun in luns_by_target[volume["host"]]]
                    next_lun = 1
                    while next_lun in used_list:
                        next_lun += 1
                    mapping_info.append({"volume": volume["name"], "target": volume["host"], "lun": next_lun})

                # Map volume to host
                else:
                    luns_by_target.update({volume["host"]: luns_by_target["default_hostgroup"]})

                    used_list = [lun for vol, lun in luns_by_target[volume["host"]]]
                    next_lun = 1
                    while next_lun in used_list:
                        next_lun += 1

                    mapping_info.append({"volume": volume["name"], "target": volume["host"], "lun": next_lun})

        # Add an manually created hosts
        return mapping_info
