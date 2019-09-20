#!/usr/bin/python

# (c) 2016, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1",
                    "status": ["preview"],
                    "supported_by": "community"}

DOCUMENTATION = """
---
module: nac_santricity_auth
short_description: NetApp E-Series set or update the password for a storage array.
description:
    - Sets or updates the password for a storage array.
author:
    - Nathan Swartz (@ndswartz)
options:
    current_password:
        description:
            - The current admin password. Only required when the password has been set.
        type: str
        required: false
    password:
        description:
            - The password you would like to set.
            - Cannot be more than 30 characters.
        type: str
        required: true
    set_admin:
        description:
            - Whether to update the admin password.
            - If I(set_admin==False) then the read-only account is updated.
        type: bool
        default: true
        required: false
"""

EXAMPLES = """
- name: Set the initial password
  nac_santricity_auth:
    ssid: 1
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    validate_certs: true
    password: arraypass
"""

RETURN = """
msg:
    description: Success message
    returned: success
    type: str
    sample: "Password Updated Successfully"
"""
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule
from ansible.module_utils._text import to_native


class NetAppESeriesAuth(NetAppESeriesModule):
    DEFAULT_CREDENTIALS = [("admin", "admin")]
    DEFAULT_CONNECTION_TIMEOUT_SEC = 10
    DEFAULT_DISCOVERY_TIMEOUT_SEC = 30

    def __init__(self):
        version = "02.00.0000.0000"
        ansible_options = dict(current_password=dict(type="str", required=False, no_log=True),
                               password=dict(type="str", required=True, no_log=True),
                               set_admin=dict(type="bool", required=False, default=True))

        super(NetAppESeriesAuth, self).__init__(ansible_options=ansible_options, web_services_version=version, supports_check_mode=True)
        args = self.module.params
        self.current_password = args["current_password"] if args["current_password"] else ""
        self.password = args["password"]
        self.set_admin = args["set_admin"]

        self.is_password_set_cache = None

        # Check whether request needs to be forwarded on to the controller web services rest api.
        self.url_path_prefix = ""
        if not self.is_embedded() and self.ssid != 0:
            self.url_path_prefix = "storage-systems/%s/forward/devmgr/v2/" % self.ssid

    def is_password_set(self):
        """Determine whether password has been set."""
        if self.is_password_set_cache is None:
            try:
                rc, password = self.request("storage-systems/%s/passwords" % self.ssid)
                self.is_password_set_cache = password["adminPasswordSet"] if self.set_admin else password["readOnlyPasswordSet"]
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve current password status. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return self.is_password_set_cache

    def password_change_required(self):
        """Verify whether the current password is expected array password. Works only against embedded systems."""
        change_required = (self.is_password_set() and not self.password) or (not self.is_password_set() and self.password)
        if self.is_password_set() and self.password:
            rc, response = self.request(self.url_path_prefix + "storage-systems/%s/passwords" % self.ssid, method="POST", ignore_errors=True,
                                        data={"currentAdminPassword": self.password, "adminPassword": self.set_admin, "newPassword": self.password})

            if rc == 204:
                change_required = False
            elif rc == 422:
                change_required = True
            else:
                self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

        return change_required

    def set_array_password(self):
        """Set the array password."""
        try:
            headers = self.DEFAULT_HEADERS.update({"x-netapp-password-validate-method": "none"})
            rc, storage_system = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", headers=headers,
                                              data={"currentAdminPassword": self.current_password if self.is_password_set() else "",
                                                    "adminPassword": True, "newPassword": self.password})
        except Exception as error:
            self.module.fail_json(msg="Failed to set storage system password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def apply(self):
        """Apply any required changes."""
        change_required = self.password_change_required()
        if change_required and not self.module.check_mode:
            self.set_array_password()

        self.module.exit_json(msg="Password has been changed. Array [%s]." % self.ssid, changed=change_required)


if __name__ == '__main__':
    auth = NetAppESeriesAuth()
    auth.apply()
