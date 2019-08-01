#!/usr/bin/python

# (c) 2016, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: nac_santricity_feature_pack
version_added: "2.9"
short_description: NetApp E-Series manages feature packs
description:
    - Ensure specific firmware versions are activated on E-Series storage system.
author:
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity
options:
    feature_key:
        description:
            - Path to the feature pack key file.
        required: true
    wait_for_reboot:
        description:
            - Wait for feature pack to be enabled before completing.
        type: bool
        default: false
"""
EXAMPLES = """
- name: Enable feature pack
  nac_santricity_feature_pack:
    ssid: "{{ eseries_ssid }}"
    api_url: "{{ eseries_api_url }}"
    api_username: "{{ eseries_api_username }}"
    api_password: "{{ eseries_api_password }}"
    validate_certs: "{{ eseries_validate_certs }}"
    feature_key: "path/to/feature-pack.key"
    wait_for_reboot: True
"""
RETURN = """changed=self.is_change_required, expected_submodel_id=self.expected_submodel_id, current_submodel_id=self.current_submodel_id
msg:
    description: Status and version of firmware and NVSRAM. 
    type: str
    returned: always
    sample: 
      - {"changed": false, "current_submodel_id": 321, "expected_submodel_id": 321}

"""
import re

from time import sleep
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule, create_multipart_formdata, request
from ansible.module_utils._text import to_native


class NetAppESeriesFeaturePack(NetAppESeriesModule):
    REBOOT_TIMEOUT_SEC = 15*60

    def __init__(self):
        ansible_options = dict(feature_key=dict(type="str", required=True),
                               wait_for_reboot=dict(type="bool", default=False))

        super(NetAppESeriesFeaturePack, self).__init__(ansible_options=ansible_options,
                                                       web_services_version="02.00.0000.0000",
                                                       supports_check_mode=False)

        args = self.module.params
        self.feature_key = args["feature_key"]
        self.wait_for_reboot = args["wait_for_reboot"]
        self.expected_submodel_id_cache = None
        self.current_submodel_id_cache = None

    @property
    def expected_submodel_id(self):
        """Determine and return the expected submodel id."""
        if self.expected_submodel_id_cache is None:
            with open(self.feature_key, "rb") as fh:
                transition_phrase = re.search(b"BUNDLE_KEY_[0-9]{3}_[0-9]{3}", fh.read())
                if not transition_phrase:
                    self.module.fail_json(msg="Invalid feature key. Array [%s]." % self.ssid)

                self.expected_submodel_id_cache = int(transition_phrase[0].decode("utf-8").split("_")[-1])

        return self.expected_submodel_id_cache

    @property
    def current_submodel_id(self):
        """Determine and return the current submodel id."""
        if self.current_submodel_id_cache is None:
            try:
                rc, response = self.request("storage-systems/%s/capabilities" % self.ssid)
                self.current_submodel_id_cache = int(response["featureBundle"]["bundleSubmodelId"])
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve system capabilities. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return self.current_submodel_id_cache

    @property
    def is_change_required(self):
        """Determine whether feature pack should be enabled."""
        return self.current_submodel_id != self.expected_submodel_id

    def enable_feature_pack(self):
        """Enable the feature pack key."""
        filename = re.split(r"/", self.feature_key)[-1]
        files = [("keyFile", filename, self.feature_key)]
        headers, data = create_multipart_formdata(files)
        try:
            self.request("storage-systems/%s/feature-pack" % self.ssid, method="POST", headers=headers, data=data)
        except Exception as error:
            self.module.fail_json(msg="No changes made. Array [%s]. Error [%s].\nheaders [%s]\ndata [%s] [%s] [%s]"
                                      % (self.ssid, to_native(error), headers, data, self.expected_submodel_id, self.current_submodel_id))

    def wait_for_controller_reboot(self):
        """Wait for SANtricity Web Services Embedded to be available after reboot."""
        sleep(60)  # wait for controller to reboot
        about_url = self.url + self.DEFAULT_REST_API_ABOUT_PATH
        for count in range(0, int((self.REBOOT_TIMEOUT_SEC - 60) / 5)):
            sleep(5)
            try:
                rc, data = request(about_url, timeout=self.DEFAULT_TIMEOUT, headers=self.DEFAULT_HEADERS, ignore_errors=True, **self.creds)
                if rc == 200:
                    break
            except Exception as error:
                pass
        else:
            self.module.fail_json(msg="Timeout waiting for Santricity Web Services Embedded. Array [%s]" % self.ssid)

    def apply(self):
        """Apply firmware policy has been enforced on E-Series storage system."""

        if self.is_change_required and not self.module.check_mode:
            self.enable_feature_pack()
            if self.wait_for_reboot:
                self.wait_for_controller_reboot()

        self.module.exit_json(changed=self.is_change_required, expected_submodel_id=self.expected_submodel_id, current_submodel_id=self.current_submodel_id)


def main():
    feature = NetAppESeriesFeaturePack()
    feature.apply()


if __name__ == '__main__':
    main()
