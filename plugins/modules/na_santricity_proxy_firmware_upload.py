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
module: v
version_added: "2.9"
short_description: NetApp E-Series manage proxy firmware uploads.
description:
    - Ensure specific firmware versions are available on SANtricity Web Services Proxy.
author:
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity_proxy_doc
options:
    nvsram:
        description:
            - List of paths for the NVSRAM files.
            - All NVSRAM files that are not specified will be removed from the proxy if they exist.
        type: list
        required: false
    firmware:
        description:
            - List of paths for the firmware files.
            - All firmware files that are not specified will be removed from the proxy if they exist.
        type: list
        required: false
    remove_unlisted_files:
        description:
            - Remove all unspecified firmware or NVSRAM files
        type: bool
        required: false
        default: true
"""
EXAMPLES = """
- name: Ensure proxy has the expected firmware versions.
  na_santricity_proxy_firmware_upload:
    api_url: "https://192.168.1.100:8443/devmgr/v2"
    api_username: "admin"
    api_password: "adminpass"
    validate_certs: true
    nvsram:
      - "path/to/nvsram1"
      - "path/to/nvsram2"
    firmware:
      - "path/to/firmware1"
      - "path/to/firmware2"
"""
RETURN = """
msg:
    description: Status and version of firmware and NVSRAM.
    type: str
    returned: always
    sample:
"""
import os

from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule, create_multipart_formdata, request


class NetAppESeriesProxyFirmwareUpload(NetAppESeriesModule):
    HEALTH_CHECK_TIMEOUT_MS = 120
    COMPATIBILITY_CHECK_TIMEOUT_SEC = 60
    DEFAULT_TIMEOUT = 60 * 15       # This will override the NetAppESeriesModule request method timeout.
    REBOOT_TIMEOUT_SEC = 15 * 60

    def __init__(self):
        ansible_options = dict(
            nvsram=dict(type="list", required=False),
            firmware=dict(type="list", required=False),
            remove_unlisted_files=dict(type="bool", required=False, default=True))

        super(NetAppESeriesProxyFirmwareUpload, self).__init__(ansible_options=ansible_options,
                                                               web_services_version="02.00.0000.0000",
                                                               supports_check_mode=True)

        args = self.module.params
        self.remove_unlisted_files = args["remove_unlisted_files"]
        self.files = {}
        if args["nvsram"]:
            for nvsram in args["nvsram"]:
                path = nvsram
                name = os.path.basename(nvsram)
                if not os.path.exists(path) or os.path.isdir(path):
                    self.module.fail_json(msg="NVSRAM file does not exist! File [%s]." % path)
                self.files.update({name: path})
        if args["firmware"]:
            for firmware in args["firmware"]:
                path = firmware
                name = os.path.basename(firmware)
                if not os.path.exists(path) or os.path.isdir(path):
                    self.module.fail_json(msg="Firmware file does not exist! File [%s]." % path)
                self.files.update({name: path})

        self.add_files = []
        self.remove_files = []
        self.upload_failures = []

    def determine_changes(self):
        """Determine whether files need to be added or removed."""
        try:
            rc, results = self.request("firmware/cfw-files")
            current_files = [result["filename"] for result in results]

            # Populate remove file list
            if self.remove_unlisted_files:
                for current_file in current_files:
                    if current_file not in self.files.keys():
                        self.remove_files.append(current_file)

            # Populate add file list
            for expected_file in self.files.keys():
                if expected_file not in current_files:
                    self.add_files.append(expected_file)

        except Exception as error:
            self.module.fail_json(msg="Failed to retrieve current firmware file listing.")

    def upload_file(self, filename):
        """Upload firmware and nvsram file."""
        fields = [("validate", "true")]
        files = [("firmwareFile", filename, self.files[filename])]
        headers, data = create_multipart_formdata(files=files, fields=fields)
        try:
            rc, response = self.request("firmware/upload/", method="POST", data=data, headers=headers)
        except Exception as error:
            self.upload_failures.append(filename)
            self.module.warn(msg="Failed to upload firmware file. File [%s]" % filename)

    def remove_file(self, filename):
        """Remove firmware and nvsram file."""
        try:
            rc, response = self.request("firmware/upload/%s" % filename, method="DELETE")
        except Exception as error:
            self.upload_failures.append(filename)
            self.module.warn(msg="Failed to delete firmware file. File [%s]" % filename)

    def apply(self):
        """Upgrade controller firmware."""
        change_required = False
        if not self.is_proxy():
            self.module.fail_json(msg="Module can only be executed against SANtricity Web Services Proxy.")
        
        self.determine_changes()
        if self.add_files or self.remove_files:
            change_required = True

        if change_required and not self.module.check_mode:
            for filename in self.add_files:
                self.upload_file(filename)
            for filename in self.remove_files:
                self.remove_file(filename)

        self.module.exit_json(changed=change_required, files_added=self.add_files, files_removed=self.remove_files)


if __name__ == '__main__':
    proxy_firmware_upload = NetAppESeriesProxyFirmwareUpload()
    proxy_firmware_upload.apply()
