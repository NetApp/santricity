#!/usr/bin/python

# (c) 2020, NetApp, Inc
# BSD-3 Clause (see COPYING or https://opensource.org/licenses/BSD-3-Clause)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
---
module: na_santricity_auth
short_description: NetApp E-Series set or update the password for a storage array device or SANtricity Web Services Proxy.
description:
    - Sets or updates the password for a storage array device or SANtricity Web Services Proxy.
author:
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity_doc
options:
    current_admin_password:
        description:
            - The current admin password.
            - Only required when the password has been set.
        type: str
        required: false
    password:
        description:
            - The password you would like to set.
            - Cannot be more than 30 characters.
            - Clearing the admin password will clear the read-only password
        type: str
        required: true
    user:
        description:
            - The local user account password to update
        type: str
        choices: ["admin", "monitor", "support", "security", "storage", "ARRAY_RW", "ARRAY_RO"]
        default: "admin"
note:
    - Set I(ssid=="0") when attempting to change the password for SANtricity Web Services Proxy.
    - SANtricity Web Services Proxy storage password will be updated when changing the password on a managed storage system from the proxy; This is only true
      when the storage system has been previously contacted.  

"""

EXAMPLES = """
- name: Set the initial password
  na_santricity_auth:
    ssid: 1
    api_url: https://192.168.1.100:8443/devmgr/v2
    api_username: admin
    api_password: adminpass
    validate_certs: true
    current_admin_password: currentadminpass
    password: newpassword123
    user: admin
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
from time import sleep


class NetAppESeriesAuth(NetAppESeriesModule):
    def __init__(self):
        version = "02.00.0000.0000"
        ansible_options = dict(current_admin_password=dict(type="str", required=False, no_log=True),
                               password=dict(type="str", required=True, no_log=True),
                               user=dict(type="str", default="admin", choices=["admin", "monitor", "support", "security", "storage", "ARRAY_RW", "ARRAY_RO"]))

        super(NetAppESeriesAuth, self).__init__(ansible_options=ansible_options, web_services_version=version, supports_check_mode=True)
        args = self.module.params
        self.current_admin_password = args["current_admin_password"] if args["current_admin_password"] else ""
        self.password = args["password"] if args["password"] else ""
        self.user = args["user"]

        self.DEFAULT_HEADERS.update({"x-netapp-password-validate-method": "none"})

        self.is_password_set_cache = None
        self.is_https_available_cache = None
        self.current_password_length_requirement = None

    def update_password_length_requirement(self):
        """Adjust password length required if required."""
        # Update proxy password length requirement
        if self.is_proxy():
            if self.ssid == "0":
                try:
                    rc, system_info = self.request("local-users/info",  force_basic_auth=False)
                    self.current_password_length_requirement = system_info["minimumPasswordLength"]

                    # Reduce password length requirement
                    if self.current_password_length_requirement > len(self.password):
                        try:
                            rc, system_info = self.request("local-users/password-length", method="POST", data={"minimumPasswordLength": len(self.password)})
                        except Exception as error:
                            self.module.fail_json(msg="Failed change password length requirement. Array [%s]. Error [%s]."
                                                      % (self.ssid, to_native(error)))
                except Exception as error:
                    self.module.fail_json(msg="Failed to retrieve information about storage system [%s]. Error [%s]." % (self.ssid, to_native(error)))

            elif self.is_embedded_available() and self.user in ["admin", "ARRAY_RW"]:
                try:
                    rc, system_info = self.request("storage-systems/%s/forward/devmgr/v2/storage-systems/1/local-users/info" % self.ssid,
                                                   force_basic_auth=False)
                    self.current_password_length_requirement = system_info["minimumPasswordLength"]

                    # Reduce password length requirement
                    if self.current_password_length_requirement > len(self.password):
                        try:
                            rc, system_info = self.request("storage-systems/%s/forward/devmgr/v2/storage-systems/1/local-users/password-length" % self.ssid,
                                                           method="POST", data={"minimumPasswordLength": len(self.password)})
                        except Exception as error:
                            self.module.fail_json(msg="Failed change password length requirement. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))
                except Exception as error:
                    self.module.fail_json(msg="Failed to retrieve information about storage system [%s]. Error [%s]." % (self.ssid, to_native(error)))

        # Update storage systems with web services
        elif self.is_embedded() and self.user in ["admin", "ARRAY_RW"]:
            try:
                rc, system_info = self.request("storage-systems/%s/local-users/info" % self.ssid,  force_basic_auth=False)
                self.current_password_length_requirement = system_info["minimumPasswordLength"]

                # Reduce password length requirement
                if self.current_password_length_requirement > len(self.password):
                    try:
                        rc, system_info = self.request("storage-systems/%s/local-users/password-length" % self.ssid,
                                                       method="POST", data={"minimumPasswordLength": len(self.password)})
                    except Exception as error:
                        self.module.fail_json(msg="Failed change password length requirement. Array [%s]. Error [%s]."
                                                  % (self.ssid, to_native(error)))
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve information about storage system [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def restore_password_length_requirement(self, retries=10):
        """Restore original password length requirement."""
        if self.current_password_length_requirement is not None:
            for iteration in range(retries):
                if self.is_proxy():

                    # Restore proxy password length requirement
                    if self.ssid == "0":
                        rc, system_info = self.request("local-users/password-length", method="POST", ignore_errors=True,
                                                       data={"minimumPasswordLength": self.current_password_length_requirement})

                    # Restore storage array password length requirement
                    elif self.is_embedded_available():
                        rc, system_info = self.request("storage-systems/%s/forward/devmgr/v2/storage-systems/1/local-users/password-length" % self.ssid,
                                                       ignore_errors=True, method="POST",
                                                       data={"minimumPasswordLength": self.current_password_length_requirement})

                # Restore storage array password length requirement
                elif self.is_embedded():
                    rc, system_info = self.request("storage-systems/%s/local-users/password-length" % self.ssid, ignore_errors=True,
                                                   method="POST", data={"minimumPasswordLength": self.current_password_length_requirement})

                if rc == 204:
                    break
                sleep(0.1)
            else:
                self.module.fail_json(msg="Failed change password length requirement. Array [%s]." % self.ssid)

    def password_change_required(self):
        """Verify whether the current password is expected array password. Works only against embedded systems."""
        self.update_password_length_requirement()

        change_required = False
        if self.is_proxy():

            # Update proxy's local users
            if self.ssid == "0":
                if self.user in ["ARRAY_RW", "ARRAY_RO"]:
                    self.module.fail_json(msg="ARRAY_RW, ARRAY_RO are not valid users for SANtricity Web Services Proxy.")

                rc, response = self.request("utils/login", rest_api_path=self.DEFAULT_BASE_PATH, method="POST", ignore_errors=True, force_basic_auth=False,
                                            data={"userId": self.user, "password": self.password})
                if rc == 200:
                    change_required = False
                elif rc == 401:
                    change_required = True
                else:
                    self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

            # Currently the read-only array password is untestable
            elif self.user == "ARRAY_RO":
                change_required = True

            # Update read-write array password using the password endpoint. Placing "admin" here will cause web services to update the array password as well
            #   the stored password which is important because it prevents an invalid password state on the proxy.
            elif self.user in ["admin", "ARRAY_RW"]:
                rc, response = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", ignore_errors=True,
                                            data={"currentAdminPassword": self.password, "adminPassword": True, "newPassword": self.password})
                if rc == 204:
                    change_required = False
                elif rc == 422:
                    change_required = True
                else:
                    self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

            # Change embedded local user passwords
            elif self.is_embedded_available():
                rc, response = self.request("storage-systems/%s/forward/devmgr/utils/login" % self.ssid,
                                            force_basic_auth=False, method="POST", ignore_errors=True, data={"userId": self.user, "password": self.password})
                if rc == 200:
                    change_required = False
                elif rc == 401:
                    change_required = True
                else:
                    self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

            else:
                self.module.fail_json(msg="Storage array without SANtricity Web Services must choose 'ARRAY_RW' or 'ARRAY_RO'. Array [%s]" % self.ssid)

        # Currently the read-only array password is untestable update using the embedded password endpoint
        elif self.user == "ARRAY_RO":
            change_required = True

        # Update read-write array password using the embedded password endpoint
        elif self.user == "ARRAY_RW":
            rc, response = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", ignore_errors=True,
                                        data={"currentAdminPassword": self.password, "adminPassword": True, "newPassword": self.password})
            if rc == 204:
                change_required = False
            elif rc == 422:
                change_required = True
            else:
                self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

        # Update embedded local users
        else:
            rc, response = self.request("utils/login", rest_api_path=self.DEFAULT_BASE_PATH, method="POST", ignore_errors=True, force_basic_auth=False,
                                        data={"userId": self.user, "password": self.password})
            if rc == 200:
                change_required = False
            elif rc == 401:
                change_required = True
            else:
                self.module.fail_json(msg="Failed to validate password status. Array [%s]. Error [%s]." % (self.ssid, (rc, response)))

        return change_required

    def set_array_password(self):
        """Set the array password."""
        if self.is_proxy():

            # Update proxy's local users
            if self.ssid == "0":
                try:
                    body = {"currentAdminPassword": self.current_admin_password, "updates": {"userName": self.user, "newPassword": self.password}}
                    rc, proxy = self.request("local-users", method="POST", data=body)
                except Exception as error:
                    self.module.fail_json(msg="Failed to set proxy password. Error [%s]." % to_native(error))

                if self.user == "admin":
                    self.creds["url_password"] = self.password

            # Update password using the password endpoints
            elif self.user in ["admin", "ARRAY_RW", "ARRAY_RO"]:
                try:
                    update_admin = self.user in ["admin", "ARRAY_RW"]
                    body = {"currentAdminPassword": self.current_admin_password, "newPassword": self.password, "adminPassword": update_admin}
                    rc, storage_system = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", data=body)
                except Exception as error:
                    self.module.fail_json(msg="Failed to set storage system password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

            # Update embedded local user passwords
            elif self.is_embedded_available():
                try:
                    body = {"currentAdminPassword": self.current_admin_password, "updates": {"userName": self.user, "newPassword": self.password}}
                    rc, proxy = self.request("storage-systems/%s/forward/devmgr/v2/storage-systems/1/local-users" % self.ssid, method="POST", data=body)
                except Exception as error:
                    self.module.fail_json(msg="Failed to set embedded user password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        # Update embedded local users
        elif self.user in ["ARRAY_RW", "ARRAY_RO"]:
            try:
                update_admin = self.user == "ARRAY_RW"
                body = {"currentAdminPassword": self.current_admin_password, "newPassword": self.password, "adminPassword": update_admin}
                rc, storage_system = self.request("storage-systems/%s/passwords" % self.ssid, method="POST", data=body)

                if self.user == "ARRAY_RW":
                    self.creds["url_password"] = self.password
            except Exception as error:
                self.module.fail_json(msg="Failed to set storage system password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))
        else:
            try:
                body = {"currentAdminPassword": self.current_admin_password, "updates": {"userName": self.user, "newPassword": self.password}}
                rc, proxy = self.request("storage-systems/%s/local-users" % self.ssid, method="POST", data=body)

                if self.user == "admin":
                    self.creds["url_password"] = self.password
            except Exception as error:
                self.module.fail_json(msg="Failed to set embedded user password. Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

    def apply(self):
        """Apply any required changes."""
        try:
            change_required = self.password_change_required()

            if change_required and not self.module.check_mode:
                self.set_array_password()
                self.module.exit_json(msg="Password has been changed. Array [%s]." % self.ssid, changed=change_required)

            self.module.exit_json(msg="Password has not been changed. Array [%s]." % self.ssid, changed=change_required)
        finally:
            self.restore_password_length_requirement()


if __name__ == '__main__':
    auth = NetAppESeriesAuth()
    auth.apply()
