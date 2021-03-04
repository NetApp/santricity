#!/usr/bin/python

# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: na_santricity_snapshot
short_description: NetApp E-Series storage system's snapshots.
description: Manage NetApp E-Series manage the storage system's snapshots.
author: Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity_doc
options:
  state:
    description:
      - When I(state==absent) ensures the I(type) has been removed.
      - When I(state==present) ensures the I(type) is available.
      - When I(state==rollback) the consistency group will be rolled back to the point-in-time snapshot images selected by I(pit_name or pit_timestamp).
      - I(state==rollback) will always return changed since it is not possible to evaluate the current state of the base volume in relation to a snapshot image. 
    type: str
    choices:
      - absent
      - present
      - rollback
    default: present
    required: false
  type:
    description:
      - Type of snapshot object to effect.
      - Group indicates a snapshot consistency group; consistency groups may have one or more base volume members which are defined in I(volumes).
      - Pit indicates a snapshot consistency group point-in-time image(s); a snapshot image will be taken of each base volume when I(state==present).
      - When I(state==absent and type==image), I(image_name) or I(image_timestamp) must be defined and all point-in-time images created prior to the selection
        will also be deleted.
      - View indicates a consistency group snapshot volume of particular point-in-time image(s); snapshot volumes will be created for each base volume member.
      - Views are created from images from a single point-in-time so once created they cannot be modified.
    type: str
    choices:
      - group
      - pit
      - view
    required: false
  group_name:
    description:
      - Name of the snapshot consistency group or snapshot volume.
      - Be sure to use different names for snapshot consistency groups and snapshot volumes to avoid name conflicts.
    type: str
    required: true
  volumes:
    description:
      - Details for each consistency group base volume for defining reserve capacity, preferred reserve capacity storage pool, and snapshot volume options.
      - When I(state==present and type==group) the volume entries will be used to add or remove base volume from a snapshot consistency group.
      - When I(state==present and type==view) the volume entries will be used to select images from a point-in-time for their respective snapshot volumes.
      - If I(state==present and type==view) and I(volume) is not specified then all volumes will be selected with the defaults.
      - Views are created from images from a single point-in-time so once created they cannot be modified.
      - When I(state==rollback) then I(volumes) can be used to specify which base volumes to rollback; otherwise all consistency group volumes will rollback.
    type: list
    required: false
    suboptions:
      volume:
        description:
          - Base volume for consistency group.
        type: str
        required: true
      reserve_capacity_pct:
        description:
          - Percentage of base volume capacity to reserve for snapshot copy-on-writes (COW).
          - Used to define reserve capacity for both snapshot consistency group volume members and snapshot volumes.
        type: int
        default: 40
        required: false
      preferred_reserve_storage_pool:
        description:
          - Preferred storage pool or volume group for the reserve capacity volume.
          - The base volume's storage pool or volume group will be selected by default if not defined.
          - Used to specify storage pool or volume group for both snapshot consistency group volume members and snapshot volumes
        default: None
        type: str
        required: false
      snapshot_volume_writable:
        description:
          - Whether snapshot volume of base volume images should be writable.
        type: bool
        default: true
        required: false
      snapshot_volume_validate:
        description:
          - Whether snapshot volume should be validated which includes both a media scan and parity validation.
        type: bool
        default: false
        required: false
  maximum_snapshots:
    description:
      - Total number of snapshot images to maintain.
    default: 32
    required: false
  alert_threshold_pct:
    description:
      - Percent of filled reserve capacity to issue alert.
    type: int
    default: 75
    required: false
  reserve_capacity_full_policy:
    description:
      - Policy for full reserve capacity.
      - Purge deletes the oldest snapshot image for the base volume in the consistency group.
      - Reject writes to base volume (keep snapshot images valid).
    choices:
      - purge
      - reject
    type: str
    default: purge
    required: false
  rollback_priority:
    description:
      - Storage system priority given to restoring snapshot point in time.
    type: str
    choices:
      - highest
      - high
      - medium
      - low
      - lowest
    default: medium
    required: false
  rollback_backup:
    description:
      - Whether a point-in-time snapshot should be taken prior to performing a rollback.
    type: bool
    default: true
    required: false
  pit_name:
    description:
      - Name of a consistency group's snapshot images.
    type: str
    required: false
  pit_description:
    description:
      - Arbitrary description for a consistency group's snapshot images
    type: str
    required: false
  pit_timestamp:
    description:
      - Snapshot image timestamp in the YYYY-MM-DD HH:MM:SS (AM|PM) (hours, minutes, seconds, and day-period are optional)
      - Define only as much time as necessary to distinguish the desired snapshot image from the others.
      - 24 hour time will be assumed if day-period indicator (AM, PM) is not specified.
      - The terms latest and oldest may be used to select newest and oldest consistency group images.
      - Mutually exclusive with I(pit_name or pit_description) 
    type: str
    required: false
    examples:
      - 2019-05-18 15:17:08
      - newest
      - oldest
  view_name:
    description:
      - Consistency group snapshot volume group.
      - Required when I(state==volume) or when ensuring the views absence when I(state==absent).
    type: "str"
    required: false
"""
EXAMPLES = """
- name: Ensure snapshot consistency group exists.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: present
    type: group
    group_name: snapshot_group1
    volumes:
      - volume: vol1
        reserve_capacity_pct: 20
        preferred_reserve_storage_pool: vg1
      - volume: vol2
        reserve_capacity_pct: 30
      - volume: vol3
    alert_threshold_pct: 80
    maximum_snapshots: 30
- name: Take the current consistency group's base volumes point-in-time snapshot images.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: present
    type: pit
    group_name: snapshot_group1
    pit_name: pit1
    pit_description: Initial consistency group's point-in-time snapshot images.
- name: Ensure snapshot consistency group view exists.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: present
    type: view
    group_name: snapshot_group1
    pit_name: pit1
    view_name: view1
    volumes:
      - volume: vol1
        reserve_capacity_pct: 20
        preferred_reserve_storage_pool: vg4
        snapshot_volume_writable: false
        snapshot_volume_validate: true
      - volume: vol2
        reserve_capacity_pct: 20
        preferred_reserve_storage_pool: vg4
        snapshot_volume_writable: true
        snapshot_volume_validate: true
      - volume: vol3
        reserve_capacity_pct: 20
        preferred_reserve_storage_pool: vg4
        snapshot_volume_writable: false
        snapshot_volume_validate: true
    alert_threshold_pct: 80
    maximum_snapshots: 30
- name: Rollback base volumes to consistency group's point-in-time pit1.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: present
    type: group
    group_name: snapshot_group1
    pit_name: pit1
    rollback: true
    rollback_priority: high
- name: Ensure snapshot consistency group view no longer exists.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: absent
    type: view
    group_name: snapshot_group1
    view_name: view1
- name: Ensure that the consistency group's base volumes point-in-time snapshot images pit1 no longer exists.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: absent
    type: image
    group_name: snapshot_group1
    pit_name: pit1
- name: Ensure snapshot consistency group no longer exists.
  na_santricity_snapshot:
    ssid: "1"
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    state: absent
    type: group
    group_name: snapshot_group1
"""
RETURN = """
changed:
    description: Whether changes have been made.
    type: bool
    returned: always
    sample: true
"""
from datetime import datetime
import re

from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule


class NetAppESeriesSnapshot(NetAppESeriesModule):
    DEFAULT_RESERVE_CAPACITY_PCT = 40

    def __init__(self):
        ansible_options = dict(state=dict(type="str", default="present", choices=["absent", "present", "rollback"], required=False),
                               type=dict(type="str", default="group", choices=["group", "pit", "view"], required=False),
                               group_name=dict(type="str", required=True),
                               volumes=dict(type="list", required=False,
                                            suboptions=dict(volume=dict(type="str", required=True),
                                                            reserve_capacity_pct=dict(type="int", default=40, required=False),
                                                            preferred_reserve_storage_pool=dict(type="str", default=None, required=False),
                                                            snapshot_volume_writable=dict(type="bool", default=True, required=False),
                                                            snapshot_volume_validate=dict(type="bool", default=False, required=False))),
                               maximum_snapshots=dict(type="int", default=32, required=False),
                               alert_threshold_pct=dict(type="int", default=75, required=False),
                               reserve_capacity_full_policy=dict(type="str", default="purge", choices=["purge", "reject"], required=False),
                               rollback=dict(type="bool", default=False, required=False),
                               rollback_priority=dict(type="str", default="medium", choices=["highest", "high", "medium", "low", "lowest"], required=False),
                               rollback_backup=dict(type="bool", default=True, required=False),
                               pit_name=dict(type="str", required=False),
                               pit_description=dict(type="str", required=False),
                               pit_timestamp=dict(type="str", required=False),
                               view_name=dict(type="str", required=False))

        super(NetAppESeriesSnapshot, self).__init__(ansible_options=ansible_options,
                                                    web_services_version="05.00.0000.0000",
                                                    supports_check_mode=True)
        args = self.module.params
        self.state = args["state"]
        self.type = args["type"]
        self.group_name = args["group_name"]
        self.maximum_snapshots = args["maximum_snapshots"]
        self.alert_threshold_pct = args["alert_threshold_pct"]
        self.reserve_capacity_full_policy = "purgepit" if args["reserve_capacity_full_policy"] == "purge" else "failbasewrites"
        self.rollback_priority = args["rollback_priority"]
        self.rollback_backup = args["rollback_backup"]
        self.rollback_priority = args["rollback_priority"]
        self.pit_name = args["pit_name"]
        self.pit_description = args["pit_description"]
        self.view_name = args["view_name"]

        # Complete volume definitions.
        self.volumes = {}
        if args["volumes"]:
            for volume_info in args["volumes"]:
                reserve_capacity_pct = volume_info["reserve_capacity_pct"] if "reserve_capacity_pct" in volume_info else self.DEFAULT_RESERVE_CAPACITY_PCT
                preferred_reserve_storage_pool = volume_info["preferred_reserve_storage_pool"] if "preferred_reserve_storage_pool" in volume_info else None
                snapshot_volume_writable = volume_info["snapshot_volume_writable"] if "snapshot_volume_writable" in volume_info else True
                snapshot_volume_validate = volume_info["snapshot_volume_validate"] if "snapshot_volume_validate" in volume_info else False
                self.volumes.update({volume_info["volume"]: {"reserve_capacity_pct": reserve_capacity_pct,
                                                             "preferred_reserve_storage_pool": preferred_reserve_storage_pool,
                                                             "snapshot_volume_writable": snapshot_volume_writable,
                                                             "snapshot_volume_validate": snapshot_volume_validate}})

        # Check and convert pit_timestamp to datetime object. volume: snap-vol1
        self.pit_timestamp = None
        self.pit_timestamp_tokens = 0
        if args["pit_timestamp"]:
            if args["pit_timestamp"] in ["newest", "oldest"]:
                self.pit_timestamp = args["pit_timestamp"]
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} (AM|PM|am|pm)", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d %I:%M:%S %p")
                self.pit_timestamp_tokens = 6
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} (AM|PM|am|pm)", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d %I:%M %p")
                self.pit_timestamp_tokens = 5
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2} (AM|PM|am|pm)", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d %I %p")
                self.pit_timestamp_tokens = 4
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d %H:%M:%S")
                self.pit_timestamp_tokens = 6
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d %H:%M")
                self.pit_timestamp_tokens = 5
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d %H")
                self.pit_timestamp_tokens = 4
            elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", args["pit_timestamp"]):
                self.pit_timestamp = datetime.strptime(args["pit_timestamp"], "%Y-%m-%d")
                self.pit_timestamp_tokens = 3
            else:
                self.module.fail_json(msg="Invalid argument! pit_timestamp must be in the form YYYY-MM-DD HH:MM:SS (AM|PM) (time portion is optional)."
                                          " Array [%s]." % self.ssid)

        # Check for required arguments
        if self.state == "present":
            if self.type == "group":
                if not self.volumes:
                    self.module.fail_json(msg="Missing argument! Volumes must be defined to create a snapshot consistency group."
                                              " Group [%s]. Array [%s]" % (self.group_name, self.ssid))
            elif self.type == "pit":
                if self.pit_timestamp and self.pit_name:
                    self.module.fail_json(msg="Invalid arguments! Either define pit_name with or without pit_description or pit_timestamp."
                                              " Group [%s]. Array [%s]" % (self.group_name, self.ssid))
                if not (self.pit_name or self.pit_timestamp):
                    self.module.fail_json(msg="Missing argument! Either pit_name or pit_timestamp must be defined to create a consistency group point-in-time"
                                              " snapshot. Group [%s]. Array [%s]" % (self.group_name, self.ssid))
            elif self.type == "view":
                if not self.view_name:
                    self.module.fail_json(msg="Missing argument! view_name must be defined to create a snapshot consistency group view."
                                              " Group [%s]. Array [%s]" % (self.group_name, self.ssid))
        else:
            if self.type == "pit":
                if self.pit_name and self.pit_timestamp:
                    self.module.fail_json(msg="Invalid arguments! Either define pit_name or pit_timestamp."
                                              " Group [%s]. Array [%s]" % (self.group_name, self.ssid))
                if not (self.pit_name or self.pit_timestamp):
                    self.module.fail_json(msg="Missing argument! Either pit_name or pit_timestamp must be defined to create a consistency group point-in-time"
                                              " snapshot. Group [%s]. Array [%s]" % (self.group_name, self.ssid))
            elif self.type == "view":
                if not self.view_name:
                    self.module.fail_json(msg="Missing argument! view_name must be defined to create a snapshot consistency group view."
                                              " Group [%s]. Array [%s]" % (self.group_name, self.ssid))

        # Check whether request needs to be forwarded on to the controller web services rest api.
        self.url_path_prefix = ""
        if not self.is_embedded():
            if self.ssid == "0" or self.ssid == "proxy":
                self.module.fail_json(msg="Snapshot is not a valid operation for SANtricity Web Services Proxy! ssid cannot be '0' or 'proxy'."
                                          " Array [%s]" % self.ssid)
            self.url_path_prefix = "storage-systems/%s/forward/devmgr/v2/" % self.ssid

        self.cache = {"get_consistency_group": {},
                      "get_all_storage_pools_by_id": {},
                      "get_all_storage_pools_by_name": {},
                      "get_all_volumes_by_id": {},
                      "get_all_volumes_by_name": {},
                      "get_all_concat_volumes_by_id": {},
                      "get_pit_images_by_timestamp": {},
                      "get_pit_images_by_name": {},
                      "get_pit_images_metadata": {},
                      "get_pit_info": None,
                      "get_consistency_group_view": {},
                      "view_changes_required": []}

    def get_all_storage_pools_by_id(self):
        """Retrieve and return all storage pools/volume groups."""
        if not self.cache["get_all_storage_pools_by_id"]:
            try:
                rc, storage_pools = self.request("storage-systems/%s/storage-pools" % self.ssid)

                for storage_pool in storage_pools:
                    self.cache["get_all_storage_pools_by_id"].update({storage_pool["id"]: storage_pool})
                    self.cache["get_all_storage_pools_by_name"].update({storage_pool["name"]: storage_pool})
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve volumes! Error [%s]. Array [%s]." % (error, self.ssid))

        return self.cache["get_all_storage_pools_by_id"]

    def get_all_storage_pools_by_name(self):
        """Retrieve and return all storage pools/volume groups."""
        if not self.cache["get_all_storage_pools_by_name"]:
            self.get_all_storage_pools_by_id()

        return self.cache["get_all_storage_pools_by_name"]

    def get_all_volumes_by_id(self):
        """Retrieve and return a dictionary of all thick and thin volumes keyed by id."""
        if not self.cache["get_all_volumes_by_id"]:
            try:
                rc, thick_volumes = self.request("storage-systems/%s/volumes" % self.ssid)
                rc, thin_volumes = self.request("storage-systems/%s/thin-volumes" % self.ssid)

                for volume in thick_volumes + thin_volumes:
                    self.cache["get_all_volumes_by_id"].update({volume["id"]: volume})
                    self.cache["get_all_volumes_by_name"].update({volume["name"]: volume})
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve volumes! Error [%s]. Array [%s]." % (error, self.ssid))

        return self.cache["get_all_volumes_by_id"]

    def get_all_volumes_by_name(self):
        """Retrieve and return a dictionary of all thick and thin volumes keyed by name."""
        if not self.cache["get_all_volumes_by_name"]:
            self.get_all_volumes_by_id()

        return self.cache["get_all_volumes_by_name"]

    def get_all_concat_volumes_by_id(self):
        """Retrieve and return a dictionary of all thick and thin volumes keyed by id."""
        if not self.cache["get_all_concat_volumes_by_id"]:
            try:
                rc, concat_volumes = self.request("storage-systems/%s/repositories/concat" % self.ssid)

                for volume in concat_volumes:
                    self.cache["get_all_concat_volumes_by_id"].update({volume["id"]: volume})
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve reserve capacity volumes! Error [%s]. Array [%s]." % (error, self.ssid))

        return self.cache["get_all_concat_volumes_by_id"]

    def get_consistency_group(self):
        """Retrieve consistency groups and return information on the expected group."""
        existing_volumes = self.get_all_volumes_by_id()

        if not self.cache["get_consistency_group"]:
            try:
                rc, consistency_groups = self.request("storage-systems/%s/consistency-groups" % self.ssid)

                for consistency_group in consistency_groups:
                    if consistency_group["label"] == self.group_name:
                        rc, member_volumes = self.request("storage-systems/%s/consistency-groups/%s/member-volumes" % (self.ssid, consistency_group["id"]))

                        self.cache["get_consistency_group"].update({"consistency_group_id": consistency_group["cgRef"],
                                                                    "alert_threshold_pct": consistency_group["fullWarnThreshold"],
                                                                    "maximum_snapshots": consistency_group["autoDeleteLimit"],
                                                                    "rollback_priority": consistency_group["rollbackPriority"],
                                                                    "reserve_capacity_full_policy": consistency_group["repFullPolicy"],
                                                                    "sequence_numbers": consistency_group["uniqueSequenceNumber"],
                                                                    "base_volumes": []})

                        for member_volume in member_volumes:
                            base_volume = existing_volumes[member_volume["volumeId"]]
                            base_volume_size_b = int(base_volume["totalSizeInBytes"])
                            total_reserve_capacity_b = int(member_volume["totalRepositoryCapacity"])
                            reserve_capacity_pct = int(round(float(total_reserve_capacity_b) / float(base_volume_size_b) * 100))

                            rc, concat = self.request("storage-systems/%s/repositories/concat/%s" % (self.ssid, member_volume["repositoryVolume"]))

                            self.cache["get_consistency_group"]["base_volumes"].append({"name": base_volume["name"],
                                                                                        "id": base_volume["id"],
                                                                                        "base_volume_size_b": base_volume_size_b,
                                                                                        "total_reserve_capacity_b": total_reserve_capacity_b,
                                                                                        "reserve_capacity_pct": reserve_capacity_pct,
                                                                                        "repository_volume_info": concat})
                        break

            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve snapshot consistency groups! Error [%s]. Array [%s]." % (error, self.ssid))

        return self.cache["get_consistency_group"]

    def get_candidates(self, base_volumes):
        """Determine the base volume candidates. The information passed via base_volumes will be added to the return structure."""
        existing_storage_pools_by_id = self.get_all_storage_pools_by_id()
        existing_storage_pools_by_name = self.get_all_storage_pools_by_name()
        existing_volumes_by_name = self.get_all_volumes_by_name()

        base_volumes_info = []
        for volume_name, volume_info in base_volumes.items():
            if volume_name in existing_volumes_by_name:
                base_volume_storage_pool_id = existing_volumes_by_name[volume_name]["volumeGroupRef"]
                base_volume_storage_pool_name = existing_storage_pools_by_id[base_volume_storage_pool_id]["name"]

                preferred_reserve_storage_pool = base_volume_storage_pool_id
                if volume_info["preferred_reserve_storage_pool"]:
                    preferred_reserve_storage_pool = existing_storage_pools_by_name[volume_info["preferred_reserve_storage_pool"]]["id"]

                initial_base_volumes_info = volume_info
                initial_base_volumes_info.update({"name": volume_name,
                                                  "id": existing_volumes_by_name[volume_name]["id"],
                                                  "storage_pool_name": base_volume_storage_pool_name,
                                                  "storage_pool_id": base_volume_storage_pool_id,
                                                  "preferred_reserve_storage_pool": preferred_reserve_storage_pool,
                                                  "candidate": None})
                base_volumes_info.append(initial_base_volumes_info)
            else:
                self.module.fail_json(msg="Volume does not exist! Volume [%s]. Group [%s]. Array [%s]." % (volume_name, self.group_name, self.ssid))

        # Get the reserve capacity volume candidates.
        storage_pool_requirements = {}
        for candidate_count, base_volume_info in enumerate(base_volumes_info):
            candidate_request = {"candidateRequest": {"baseVolumeRef": base_volume_info["id"],
                                                      "percentCapacity": base_volume_info["reserve_capacity_pct"],
                                                      "concatVolumeType": "snapshot"}}

            try:
                rc, candidates = self.request("storage-systems/%s/repositories/concat/single" % self.ssid, method="POST", data=candidate_request)

                for candidate in candidates:
                    if candidate["volumeGroupId"] == base_volume_info["preferred_reserve_storage_pool"]:
                        if candidate["volumeGroupId"] not in storage_pool_requirements:
                            storage_pool_requirements.update({candidate["volumeGroupId"]: int(candidate["capacity"])})
                        else:
                            storage_pool_requirements[candidate["volumeGroupId"]] += int(candidate["capacity"])

                        candidate_name = candidate["candidate"]["newVolCandidate"]["memberVolumeLabel"]
                        candidate_number = int(re.search("[0-9]+", candidate_name)[0])
                        candidate["candidate"]["newVolCandidate"]["memberVolumeLabel"] = candidate_name.replace(str(candidate_number),
                                                                                                                str(candidate_number + candidate_count))
                        base_volume_info["candidate"] = candidate
                        break
                else:
                    self.module.fail_json(msg="Failed to retrieve capacity volume candidate in preferred storage pool or volume group!"
                                              " Volume [%s]. Group [%s]. Array [%s]." % (base_volume_info["name"], self.group_name, self.ssid))
            except Exception as error:
                self.module.fail_json(msg="Failed to get reserve capacity candidates!"
                                          " Volumes %s. Group [%s]. Array [%s]. Error [%s]" % (base_volume_info["name"], self.group_name, self.ssid, error))

        # Verify storage requirements
        insufficient_volumes = []
        for storage_pool_id, storage_pool_requirement in storage_pool_requirements.items():
            if storage_pool_requirement > int(existing_storage_pools_by_id[storage_pool_id]["freeSpace"]):
                insufficient_volumes.append(existing_storage_pools_by_id[storage_pool_id]["name"])

        if insufficient_volumes:
            self.module.fail_json(msg="Insufficient space for reserve capacity volumes!"
                                      " Volumes %s. Group [%s]. Array [%s]." % (insufficient_volumes, self.group_name, self.ssid))

        return base_volumes_info

    def get_pit_images_metadata(self):
        """Retrieve and return consistency group snapshot images' metadata keyed on timestamps."""
        if not self.cache["get_pit_images_metadata"]:
            try:
                rc, key_values = self.request(self.url_path_prefix + "key-values")

                for entry in key_values:
                    if re.search("ansible_%s_" % self.group_name, entry["key"]):
                        name = entry["key"].replace("ansible_%s_" % self.group_name, "")
                        values = entry["value"].split("|")
                        if len(values) == 3:
                            timestamp, image_id, description = values
                            self.cache["get_pit_images_metadata"].update({timestamp: {"name": name, "description": description}})

            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve consistency group snapshot images metadata!  Array [%s]. Error [%s]." % (self.ssid, error))

        return self.cache["get_pit_images_metadata"]

    def get_pit_images_by_timestamp(self):
        """Retrieve and return snapshot images."""
        if not self.cache["get_pit_images_by_timestamp"]:
            group_id = self.get_consistency_group()["consistency_group_id"]
            images_metadata = self.get_pit_images_metadata()

            try:
                rc, images = self.request("storage-systems/%s/consistency-groups/%s/snapshots" % (self.ssid, group_id))
                for image_info in images:

                    metadata = {"id": "", "name": "", "description": ""}
                    if image_info["pitTimestamp"] in images_metadata.keys():
                        metadata = images_metadata[image_info["pitTimestamp"]]

                    timestamp = datetime.fromtimestamp(int(image_info["pitTimestamp"]))
                    info = {"id": image_info["id"],
                            "name": metadata["name"],
                            "timestamp": timestamp,
                            "description": metadata["description"],
                            "sequence_number": image_info["pitSequenceNumber"],
                            "base_volume_id": image_info["baseVol"],
                            "image_info": image_info}

                    if timestamp not in self.cache["get_pit_images_by_timestamp"].keys():
                        self.cache["get_pit_images_by_timestamp"].update({timestamp: {"sequence_number": image_info["pitSequenceNumber"], "images": [info]}})
                        if metadata["name"]:
                            self.cache["get_pit_images_by_name"].update({metadata["name"]: {"sequence_number": image_info["pitSequenceNumber"],
                                                                                            "images": [info]}})
                    else:
                        self.cache["get_pit_images_by_timestamp"][timestamp]["images"].append(info)
                        if metadata["name"]:
                            self.cache["get_pit_images_by_name"][metadata["name"]]["images"].append(info)

            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve consistency group snapshot images!"
                                          " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

        return self.cache["get_pit_images_by_timestamp"]

    def get_pit_images_by_name(self):
        """Retrieve and return snapshot images."""
        if not self.cache["get_pit_images_by_name"]:
            self.get_pit_images_by_timestamp()

        return self.cache["get_pit_images_by_name"]

    def get_pit_info(self):
        """Determine consistency group's snapshot images base on provided arguments (pit_name or timestamp)."""

        def _check_timestamp(timestamp):
            """Check whether timestamp matches I(pit_timestamp)"""
            return (self.pit_timestamp.year == timestamp.year and
                    self.pit_timestamp.month == timestamp.month and
                    self.pit_timestamp.day == timestamp.day and
                    (self.pit_timestamp_tokens < 4 or self.pit_timestamp.hour == timestamp.hour) and
                    (self.pit_timestamp_tokens < 5 or self.pit_timestamp.minute == timestamp.minute) and
                    (self.pit_timestamp_tokens < 6 or self.pit_timestamp.second == timestamp.second))

        if self.cache["get_pit_info"] is None:

            if self.pit_name:
                pit_images_by_name = self.get_pit_images_by_name()
                if self.pit_name in pit_images_by_name.keys():
                    self.cache["get_pit_info"] = pit_images_by_name[self.pit_name]

                    if self.pit_timestamp:
                        for image in self.cache["get_pit_info"]["images"]:
                            if not _check_timestamp(image["timestamp"]):
                                self.module.fail_json(msg="Snapshot image does not exist that matches both name and supplied timestamp!"
                                                          " Group [%s]. Image [%s]. Array [%s]." % (self.group_name, image, self.ssid))
            elif self.pit_timestamp:
                group = self.get_consistency_group()
                pit_images_by_timestamp = self.get_pit_images_by_timestamp()
                sequence_number = None

                if self.pit_timestamp == "newest":
                    sequence_number = group["sequence_numbers"][-1]

                    for image_timestamp in pit_images_by_timestamp.keys():
                        if int(pit_images_by_timestamp[image_timestamp]["sequence_number"]) == int(sequence_number):
                            self.cache["get_pit_info"] = pit_images_by_timestamp[image_timestamp]
                            break
                elif self.pit_timestamp == "oldest":
                    sequence_number = group["sequence_numbers"][0]
                    for image_timestamp in pit_images_by_timestamp.keys():
                        if int(pit_images_by_timestamp[image_timestamp]["sequence_number"]) == int(sequence_number):
                            self.cache["get_pit_info"] = pit_images_by_timestamp[image_timestamp]
                            break
                else:
                    for image_timestamp in pit_images_by_timestamp.keys():
                        if _check_timestamp(image_timestamp):
                            if sequence_number and sequence_number != pit_images_by_timestamp[image_timestamp]["sequence_number"]:
                                self.module.fail_json(msg="Multiple snapshot images match the provided timestamp and do not have the same sequence number!"
                                                          " Group [%s]. Array [%s]." % (self.group_name, self.ssid))

                            sequence_number = pit_images_by_timestamp[image_timestamp]["sequence_number"]
                            self.cache["get_pit_info"] = pit_images_by_timestamp[image_timestamp]

        return self.cache["get_pit_info"]

    def create_changes_required(self):
        """Determine the required state changes for creating a new consistency group."""
        changes = {"create_group": {"name": self.group_name,
                                    "alert_threshold_pct": self.alert_threshold_pct,
                                    "maximum_snapshots": self.maximum_snapshots,
                                    "reserve_capacity_full_policy": self.reserve_capacity_full_policy,
                                    "rollback_priority": self.rollback_priority},
                   "add_volumes": self.get_candidates(self.volumes)}

        return changes

    def update_changes_required(self):
        """Determine the required state changes for updating an existing consistency group."""
        group = self.get_consistency_group()
        changes = {"update_group": {},
                   "add_volumes": [],
                   "remove_volumes": [],
                   "expand_reserve_capacity": [],
                   "trim_reserve_capacity": []}

        # Check if consistency group settings need to be updated.
        if group["alert_threshold_pct"] != self.alert_threshold_pct:
            changes["update_group"].update({"alert_threshold_pct": self.alert_threshold_pct})
        if group["maximum_snapshots"] != self.maximum_snapshots:
            changes["update_group"].update({"maximum_snapshots": self.maximum_snapshots})
        if group["rollback_priority"] != self.rollback_priority:
            changes["update_group"].update({"rollback_priority": self.rollback_priority})
        if group["reserve_capacity_full_policy"] != self.reserve_capacity_full_policy:
            changes["update_group"].update({"reserve_capacity_full_policy": self.reserve_capacity_full_policy})

        # Check if base volumes need to be added or removed from consistency group.
        remaining_base_volumes = {base_volumes["name"]: base_volumes for base_volumes in group["base_volumes"]}
        add_volumes = {}
        expand_volumes = {}

        for volume_name, volume_info in self.volumes.items():
            reserve_capacity_pct = volume_info["reserve_capacity_pct"]
            if volume_name in remaining_base_volumes:

                # Check if reserve capacity needs to be expanded or trimmed.
                base_volume_reserve_capacity_pct = remaining_base_volumes[volume_name]["reserve_capacity_pct"]
                if reserve_capacity_pct > base_volume_reserve_capacity_pct:

                    expand_reserve_capacity_pct = reserve_capacity_pct - base_volume_reserve_capacity_pct
                    expand_volumes.update({volume_name: {"reserve_capacity_pct": expand_reserve_capacity_pct,
                                                         "preferred_reserve_storage_pool": volume_info["preferred_reserve_storage_pool"],
                                                         "reserve_volume_id": remaining_base_volumes[volume_name]["repository_volume_info"]["id"]}})

                elif reserve_capacity_pct < base_volume_reserve_capacity_pct:
                    existing_volumes_by_id = self.get_all_volumes_by_id()
                    existing_volumes_by_name = self.get_all_volumes_by_name()
                    existing_concat_volumes_by_id = self.get_all_concat_volumes_by_id()
                    trim_pct = base_volume_reserve_capacity_pct - reserve_capacity_pct

                    # Check whether there are any snapshot images; if there are then throw an exception indicating that a trim operation
                    #   cannot be done when snapshots exist.
                    for timestamp, image in self.get_pit_images_by_timestamp():
                        if existing_volumes_by_id(image["base_volume_id"])["name"] == volume_name:
                            self.module.fail_json(msg="Reserve capacity cannot be trimmed when snapshot images exist for base volume!"
                                                      " Base volume [%s]. Group [%s]. Array [%s]." % (volume_name, self.group_name, self.ssid))

                    # Collect information about all that needs to be trimmed to meet or exceed required trim percentage.
                    concat_volume_id = remaining_base_volumes[volume_name]["repository_volume_info"]["id"]
                    concat_volume_info = existing_concat_volumes_by_id[concat_volume_id]
                    base_volume_info = existing_volumes_by_name[volume_name]
                    base_volume_size_bytes = int(base_volume_info["totalSizeInBytes"])

                    total_member_volume_size_bytes = 0
                    member_volumes_to_trim = []
                    for trim_count, member_volume_id in enumerate(reversed(concat_volume_info["memberRefs"][1:])):
                        member_volume_info = existing_volumes_by_id[member_volume_id]
                        member_volumes_to_trim.append(member_volume_info)

                        total_member_volume_size_bytes += int(member_volume_info["totalSizeInBytes"])
                        total_trimmed_size_pct = round(total_member_volume_size_bytes / base_volume_size_bytes * 100)

                        if total_trimmed_size_pct >= trim_pct:
                            changes["trim_reserve_capacity"].append({"concat_volume_id": concat_volume_id, "trim_count": trim_count + 1})

                            # Expand after trim if needed.
                            if total_trimmed_size_pct > trim_pct:
                                expand_reserve_capacity_pct = total_trimmed_size_pct - trim_pct
                                expand_volumes.update({volume_name: {"reserve_capacity_pct": expand_reserve_capacity_pct,
                                                                     "preferred_reserve_storage_pool": volume_info["preferred_reserve_storage_pool"],
                                                                     "reserve_volume_id": remaining_base_volumes[volume_name]["repository_volume_info"]["id"]}})
                            break
                    else:
                        initial_reserve_volume_info = existing_volumes_by_id[concat_volume_info["memberRefs"][0]]
                        minimum_capacity_pct = round(int(initial_reserve_volume_info["totalSizeInBytes"]) / base_volume_size_bytes * 100)
                        self.module.fail_json(msg="Cannot delete initial reserve capacity volume! Minimum reserve capacity percent [%s]."
                                                  " Base volume [%s]. Group [%s]. Array [%s]." % (minimum_capacity_pct, volume_name, self.group_name, self.ssid))

                remaining_base_volumes.pop(volume_name)
            else:
                add_volumes.update({volume_name: {"reserve_capacity_pct": reserve_capacity_pct,
                                                  "preferred_reserve_storage_pool": volume_info["preferred_reserve_storage_pool"]}})

        changes["add_volumes"] = self.get_candidates(add_volumes)
        changes["expand_reserve_capacity"] = self.get_candidates(expand_volumes)
        changes["remove_volumes"] = remaining_base_volumes

        return changes

    def get_consistency_group_view(self):
        """Determine and return consistency group view."""
        group_id = self.get_consistency_group()["consistency_group_id"]

        if not self.cache["get_consistency_group_view"]:
            try:
                rc, views = self.request("storage-systems/%s/consistency-groups/%s/views" % (self.ssid, group_id))

                # Check for existing view (collection of snapshot volumes for a consistency group) within consistency group.
                for view in views:
                    if view["name"] == self.view_name:
                        self.cache["get_consistency_group_view"] = view
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve consistency group's views!"
                                          " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

        return self.cache["get_consistency_group_view"]

    def view_changes_required(self):
        """Determine the changes required for snapshot consistency group point-in-time view."""
        # Check whether consistency group view already exists.
        if self.get_consistency_group_view():
            return {}

        changes = {}
        snapshot_images_info = self.get_pit_info()
        existing_volumes_by_id = self.get_all_volumes_by_id()
        changes.update({"name": self.view_name,
                        "pitSequenceNumber": snapshot_images_info["sequence_number"],
                        "requests": []})

        candidates = self.get_candidates(self.volumes)
        for candidate_info in candidates:
            for image in snapshot_images_info["images"]:

                if candidate_info["candidate"]["baseMappableObjectId"] == image["base_volume_id"]:
                    volume_inventory_info = self.volumes[existing_volumes_by_id[candidate_info["candidate"]["baseMappableObjectId"]]["name"]]
                    changes["requests"].append({"pitId": image["id"],
                                                "candidate": candidate_info["candidate"]["candidate"],
                                                "accessMode": "readWrite" if volume_inventory_info["snapshot_volume_writable"] else "readOnly",
                                                "scanMedia": volume_inventory_info["snapshot_volume_validate"],
                                                "validateParity": volume_inventory_info["snapshot_volume_validate"]})

        return changes

    def rollback_changes_required(self):
        """Determine the changes required for snapshot consistency group point-in-time rollback."""
        return self.get_pit_info()

    def remove_snapshot_consistency_group(self, info):
        """remove a new snapshot consistency group."""
        try:
            rc, resp = self.request("storage-systems/%s/consistency-groups/%s" % (self.ssid, info["consistency_group_id"]), method="DELETE")
        except Exception as error:
            self.module.fail_json(msg="Failed to remove snapshot consistency group! Group [%s]. Array [%s]." % (self.group_name, self.ssid))

    def create_snapshot_consistency_group(self, group_info):
        """Create a new snapshot consistency group."""
        consistency_group_request = {"name": self.group_name,
                                     "fullWarnThresholdPercent": group_info["alert_threshold_pct"],
                                     "autoDeleteThreshold": group_info["maximum_snapshots"],
                                     "repositoryFullPolicy": group_info["reserve_capacity_full_policy"],
                                     "rollbackPriority": group_info["rollback_priority"]}

        try:
            rc, group = self.request("storage-systems/%s/consistency-groups" % self.ssid, method="POST", data=consistency_group_request)
            self.cache["get_consistency_group"].update({"consistency_group_id": group["cgRef"]})
        except Exception as error:
            self.module.fail_json(msg="Failed to remove snapshot consistency group! Group [%s]. Array [%s]." % (self.group_name, self.ssid))

    def update_snapshot_consistency_group(self, group_info):
        """Create a new snapshot consistency group."""
        group_id = self.get_consistency_group()["consistency_group_id"]
        consistency_group_request = {"name": self.group_name}
        if "alert_threshold_pct" in group_info.keys():
            consistency_group_request.update({"fullWarnThresholdPercent": group_info["alert_threshold_pct"]})
        if "maximum_snapshots" in group_info.keys():
            consistency_group_request.update({"autoDeleteThreshold": group_info["maximum_snapshots"]})
        if "reserve_capacity_full_policy" in group_info.keys():
            consistency_group_request.update({"repositoryFullPolicy": group_info["reserve_capacity_full_policy"]})
        if "rollback_priority" in group_info.keys():
            consistency_group_request.update({"rollbackPriority": group_info["rollback_priority"]})

        try:
            rc, group = self.request("storage-systems/%s/consistency-groups/%s" % (self.ssid, group_id), method="POST", data=consistency_group_request)
            return group["cgRef"]
        except Exception as error:
            self.module.fail_json(msg="Failed to remove snapshot consistency group! Group [%s]. Array [%s]." % (self.group_name, self.ssid))

    def add_base_volumes(self, volume_info_list):
        """Add base volume(s) to the consistency group."""
        group_id = self.get_consistency_group()["consistency_group_id"]
        member_volume_request = {"volumeToCandidates": {}}

        for info in volume_info_list:
            member_volume_request["volumeToCandidates"].update({info["id"]: info["candidate"]["candidate"]})
        try:
            rc, resp = self.request("storage-systems/%s/consistency-groups/%s/member-volumes/batch" % (self.ssid, group_id),
                                    method="POST", data=member_volume_request)
        except Exception as error:
            self.module.fail_json(msg="Failed to add reserve capacity volume! Base volumes %s. Group [%s]. Error [%s]."
                                      " Array [%s]." % (", ".join([volume for volume in member_volume_request.keys()]), self.group_name, error, self.ssid))

    def remove_base_volumes(self, volume_info_list):
        """Add base volume(s) to the consistency group."""
        group_id = self.get_consistency_group()["consistency_group_id"]

        for name, info in volume_info_list.items():
            try:
                rc, resp = self.request("storage-systems/%s/consistency-groups/%s/member-volumes/%s" % (self.ssid, group_id, info["id"]), method="DELETE")
            except Exception as error:
                self.module.fail_json(msg="Failed to add reserve capacity volume! Base volume [%s]. Group [%s]. Error [%s]. "
                                          "Array [%s]." % (name, self.group_name, error, self.ssid))

    def expand_reserve_capacities(self, expand_reserve_volume_info_list):
        """Expand base volume(s) reserve capacity."""
        for info in expand_reserve_volume_info_list:
            expand_request = {"repositoryRef": info["reserve_volume_id"],
                              "expansionCandidate": info["candidate"]["candidate"]}
            try:
                rc, resp = self.request("/storage-systems/%s/repositories/concat/%s/expand" % (self.ssid, info["reserve_volume_id"]),
                                        method="POST", data=expand_request)
            except Exception as error:
                self.module.fail_json(msg="Failed to add reserve capacity volume! Group [%s]. Error [%s]. Array [%s]." % (self.group_name, error, self.ssid))

    def trim_reserve_capacities(self, trim_reserve_volume_info_list):
        """trim base volume(s) reserve capacity."""
        for info in trim_reserve_volume_info_list:
            trim_request = {"concatVol": info["concat_volume_id"],
                            "trimCount": info["trim_count"],
                            "retainRepositoryMembers": False}
            try:
                rc, trim = self.request("storage-systems/%s/symbol/trimConcatVolume?verboseErrorResponse=true" % self.ssid, method="POST", data=trim_request)
            except Exception as error:
                self.module.fail_json(msg="Failed to trim reserve capacity. Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

    def generate_pit_images(self):
        """Generate snapshot image(s) for the base volumes in the consistency group."""
        group_id = self.get_consistency_group()["consistency_group_id"]

        try:
            rc, images = self.request("storage-systems/%s/consistency-groups/%s/snapshots" % (self.ssid, group_id), method="POST")

            # Embedded web services should store the pit_image metadata since sending it to the proxy will be written to it instead.
            if self.pit_name:
                try:
                    rc, key_values = self.request(self.url_path_prefix + "key-values/ansible_%s_%s" % (self.group_name, self.pit_name), method="POST",
                                                  data="%s|%s|%s" % (images[0]["pitTimestamp"], self.pit_name, self.pit_description))
                except Exception as error:
                    self.module.fail_json(msg="Failed to create metadata for snapshot images!"
                                              " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))
        except Exception as error:
            self.module.fail_json(msg="Failed to create consistency group snapshot images!"
                                      " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

    def remove_pit_images(self, pit_info):
        """Remove selected snapshot point-in-time images."""
        group_id = self.get_consistency_group()["consistency_group_id"]

        pit_sequence_number = int(pit_info["sequence_number"])
        sequence_numbers = set(int(pit_image["sequence_number"]) for timestamp, pit_image in self.get_pit_images_by_timestamp().items()
                               if int(pit_image["sequence_number"]) < pit_sequence_number)
        sequence_numbers.add(pit_sequence_number)

        for sequence_number in sorted(sequence_numbers):

            try:
                rc, images = self.request("storage-systems/%s/consistency-groups/%s/snapshots/%s" % (self.ssid, group_id, sequence_number), method="DELETE")
            except Exception as error:
                self.module.fail_json(msg="Failed to create consistency group snapshot images!"
                                          " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

        # Embedded web services should store the pit_image metadata since sending it to the proxy will be written to it instead.
        if self.pit_name:
            try:
                rc, key_values = self.request(self.url_path_prefix + "key-values/ansible_%s_%s" % (self.group_name, self.pit_name), method="DELETE")
            except Exception as error:
                self.module.fail_json(msg="Failed to delete metadata for snapshot images!"
                                          " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

    def generate_view(self, snapshot_volume_request):
        """Generate a consistency group view."""
        group_id = self.get_consistency_group()["consistency_group_id"]

        try:
            rc, images = self.request("storage-systems/%s/consistency-groups/%s/views/batch" % (self.ssid, group_id),
                                      method="POST", data=snapshot_volume_request)
        except Exception as error:
            self.module.fail_json(msg="Failed to create consistency group snapshot volumes!"
                                      " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

    def remove_view(self, view_id):
        """Remove a consistency group view."""
        group_id = self.get_consistency_group()["consistency_group_id"]

        try:
            rc, images = self.request("storage-systems/%s/consistency-groups/%s/views/%s" % (self.ssid, group_id, view_id), method="DELETE")
        except Exception as error:
            self.module.fail_json(msg="Failed to create consistency group snapshot volumes!"
                                      " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

    def rollback(self, rollback_info):
        """Rollback consistency group base volumes to point-in-time snapshot images."""
        group_info = self.get_consistency_group()
        group_id = group_info["consistency_group_id"]

        if self.rollback_backup:
            self.generate_pit_images()

        # Ensure consistency group rollback priority is set correctly prior to rollback.
        if self.rollback_priority:
            try:
                rc, resp = self.request("storage-systems/%s/consistency-groups/%s" % (self.ssid, group_id), method="POST",
                                        data={"rollbackPriority": self.rollback_priority})
            except Exception as error:
                self.module.fail_json(msg="Failed to updated consistency group rollback priority!"
                                          " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

        try:
            rc, resp = self.request("storage-systems/%s/symbol/startPITRollback" % self.ssid, method="POST",
                                    data={"pitRef": [image["id"] for image in rollback_info["images"]]})
        except Exception as error:
            self.module.fail_json(msg="Failed to initiate rollback operations!" " Group [%s]. Array [%s]. Error [%s]." % (self.group_name, self.ssid, error))

    def apply(self):
        """Apply any required snapshot state changes."""

        changes_required = False
        group = self.get_consistency_group()
        group_changes = {}

        # Determine which changes are required if at all.
        if group:
            if self.state == "absent":
                if self.type == "group":
                    if self.group_name:
                        changes_required = True
                elif self.type == "pit":
                    group_changes = self.get_pit_info()
                    if group_changes:
                        changes_required = True
                elif self.type == "view":
                    group_changes = self.get_consistency_group_view()
                    if group_changes:
                        changes_required = True
            elif self.state == "present":
                if self.type == "group":
                    group_changes = self.update_changes_required()
                    if (group_changes["update_group"] or
                            group_changes["add_volumes"] or
                            group_changes["remove_volumes"] or
                            group_changes["expand_reserve_capacity"] or
                            group_changes["trim_reserve_capacity"]):
                        changes_required = True
                elif self.type == "pit":
                    changes_required = True
                elif self.type == "view":
                    if not self.volumes:
                        for volume in group["base_volumes"]:
                            self.volumes.update({volume["name"]: None})
                    group_changes = self.view_changes_required()
                    if group_changes:
                        changes_required = True
            elif self.state == "rollback":
                if not self.volumes:
                    for volume in group["base_volumes"]:
                        self.volumes.update({volume["name"]: None})
                group_changes = self.rollback_changes_required()
                if group_changes:
                    changes_required = True
        else:
            if self.state == "present":
                if self.type == "group":
                    group_changes = self.create_changes_required()
                    changes_required = True
                elif self.type == "pit":
                    self.module.fail_json("Snapshot point-in-time images cannot be taken when the snapshot consistency group does not exist!"
                                          " Group [%s]. Array [%s]." % (self.group_name, self.ssid))
                elif self.type == "view":
                    self.module.fail_json("Snapshot view cannot be created when the snapshot consistency group does not exist!"
                                          " Group [%s]. Array [%s]." % (self.group_name, self.ssid))
            elif self.type == "rollback":
                self.module.fail_json("Rollback operation is not available when the snapshot consistency group does not exist!"
                                      " Group [%s]. Array [%s]." % (self.group_name, self.ssid))

        # Apply any required changes.
        if changes_required and not self.module.check_mode:
            if group:
                if self.state == "absent":
                    if self.type == "group":
                        self.remove_snapshot_consistency_group(group)
                    elif self.type == "pit":
                        self.remove_pit_images(group_changes)
                    elif self.type == "view":
                        self.remove_view(group_changes["id"])

                elif self.state == "present":
                    if self.type == "group":
                        if group_changes["update_group"]:
                            self.update_snapshot_consistency_group(group_changes["update_group"])
                        if group_changes["add_volumes"]:
                            self.add_base_volumes(group_changes["add_volumes"])
                        if group_changes["remove_volumes"]:
                            self.remove_base_volumes(group_changes["remove_volumes"])
                        if group_changes["trim_reserve_capacity"]:
                            self.trim_reserve_capacities(group_changes["trim_reserve_capacity"])
                        if group_changes["expand_reserve_capacity"]:
                            self.expand_reserve_capacities(group_changes["expand_reserve_capacity"])
                    elif self.type == "pit":
                        self.generate_pit_images()
                    elif self.type == "view":
                        self.generate_view(group_changes)

                elif self.state == "rollback":
                    self.rollback(group_changes)

            elif self.type == "group":
                self.create_snapshot_consistency_group(group_changes["create_group"])
                self.add_base_volumes(group_changes["add_volumes"])

        self.module.exit_json(changed=changes_required, group_changes=group_changes)


def main():
    snapshot = NetAppESeriesSnapshot()
    snapshot.apply()


if __name__ == "__main__":
    main()
