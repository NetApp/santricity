# (c) 2020, NetApp, Inc
# BSD-3 Clause (see COPYING or https://opensource.org/licenses/BSD-3-Clause)
from ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_auth import NetAppESeriesAuth
from units.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

__metaclass__ = type
from units.compat import mock


class AuthTest(ModuleTestCase):
    REQUIRED_PARAMS = {'api_username': 'admin', 'api_password': 'password', 'api_url': 'http://localhost', 'ssid': '1'}
    REQ_FUNC = 'ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_auth.NetAppESeriesAuth.request'
    SLEEP_FUNC = 'ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_auth.sleep'

    def _set_args(self, **kwargs):
        module_args = self.REQUIRED_PARAMS.copy()
        if kwargs is not None:
            module_args.update(kwargs)
        set_module_args(module_args)

    def test_update_password_length_requirement_pass(self):
        """Verify update_password_length_requirement method completes as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        with mock.patch(self.REQ_FUNC, return_value=(200, {"minimumPasswordLength": 0})):
            auth.ssid = "0"
            auth.is_proxy = lambda: True
            auth.update_password_length_requirement()

            auth.ssid = "1"
            auth.user = "admin"
            auth.is_embedded_available = lambda: True
            auth.update_password_length_requirement()

        with mock.patch(self.REQ_FUNC, return_value=(200, {"minimumPasswordLength": 100})):
            auth.ssid = "0"
            auth.is_proxy = lambda: True
            auth.update_password_length_requirement()

            auth.ssid = "1"
            auth.user = "admin"
            auth.is_embedded_available = lambda: True
            auth.update_password_length_requirement()

        auth.user = "monitor"
        auth.update_password_length_requirement()

        auth.is_proxy = lambda: False

    def test_update_password_length_requirement_fail(self):
        """Verify update_password_length_requirement method fails as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        auth.ssid = "0"
        auth.is_proxy = lambda: True
        with mock.patch(self.REQ_FUNC, return_value=Exception()):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to retrieve information about storage system"):
                auth.update_password_length_requirement()

        with mock.patch(self.REQ_FUNC, side_effect=[(200, {"minimumPasswordLength": 100}), Exception()]):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed change password length requirement."):
                auth.update_password_length_requirement()

        auth.ssid = "1"
        auth.user = "admin"
        auth.is_embedded_available = lambda: True
        with self.assertRaisesRegexp(AnsibleFailJson, "Failed to retrieve information about storage system"):
            with mock.patch(self.REQ_FUNC, return_value=Exception()):
                auth.update_password_length_requirement()

        with self.assertRaisesRegexp(AnsibleFailJson, "Failed change password length requirement."):
            with mock.patch(self.REQ_FUNC, side_effect=[(200, {"minimumPasswordLength": 100}), Exception()]):
                auth.update_password_length_requirement()

        auth.user = "admin"
        auth.is_proxy = lambda: False
        with self.assertRaisesRegexp(AnsibleFailJson, "Failed to retrieve information about storage system"):
            with mock.patch(self.REQ_FUNC, return_value=Exception()):
                auth.update_password_length_requirement()

        with self.assertRaisesRegexp(AnsibleFailJson, "Failed change password length requirement."):
            with mock.patch(self.REQ_FUNC, side_effect=[(200, {"minimumPasswordLength": 100}), Exception()]):
                auth.update_password_length_requirement()

    def test_restore_password_length_requirement_pass(self):
        """Verify restore_password_length_requirement method completes as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        auth.current_password_length_requirement = None
        auth.restore_password_length_requirement()

        auth.current_password_length_requirement = 10
        with mock.patch(self.SLEEP_FUNC, return_value=None):
            with mock.patch(self.REQ_FUNC, side_effect=[(422, None), (422, None), (204, None)]):
                auth.ssid = "0"
                auth.is_proxy = lambda: True
                auth.restore_password_length_requirement()

            with mock.patch(self.REQ_FUNC, side_effect=[(204, None)]):
                auth.ssid = "1"
                auth.is_embedded_available = lambda: True
                auth.restore_password_length_requirement()

            with mock.patch(self.REQ_FUNC, side_effect=[(422, None), (422, None), (422, None), (422, None), (204, None)]):
                auth.is_embedded = lambda: True
                auth.restore_password_length_requirement()

    def test_restore_password_length_requirement_fail(self):
        """Verify restore_password_length_requirement method fails as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()
        auth.current_password_length_requirement = 10

        with mock.patch(self.SLEEP_FUNC, return_value=None):
            with mock.patch(self.REQ_FUNC, return_value=(422, None)):
                auth.ssid = "0"
                auth.is_proxy = lambda: True
                with self.assertRaisesRegexp(AnsibleFailJson, "Failed change password length requirement."):
                    auth.restore_password_length_requirement()

                auth.ssid = "1"
                auth.is_embedded_available = lambda: True
                with self.assertRaisesRegexp(AnsibleFailJson, "Failed change password length requirement."):
                    auth.restore_password_length_requirement()

                auth.is_embedded = lambda: True
                with self.assertRaisesRegexp(AnsibleFailJson, "Failed change password length requirement."):
                    auth.restore_password_length_requirement()

    def test_password_change_required_pass(self):
        """Verify password_change_required method completes as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        auth.ssid = "0"
        auth.is_proxy = lambda: True
        auth.update_password_length_requirement = lambda: None
        with mock.patch(self.REQ_FUNC, side_effect=[(200, None), (401, None)]):
            self.assertFalse(auth.password_change_required())
            self.assertTrue(auth.password_change_required())

        auth.ssid = "1"
        auth.user = "ARRAY_RO"
        with mock.patch(self.REQ_FUNC, side_effect=[(200, None)]):
            self.assertTrue(auth.password_change_required())

        auth.user = "admin"
        with mock.patch(self.REQ_FUNC, side_effect=[(204, None), (422, None)]):
            self.assertFalse(auth.password_change_required())
            self.assertTrue(auth.password_change_required())

        auth.user = "monitor"
        auth.is_embedded_available = lambda: True
        with mock.patch(self.REQ_FUNC, side_effect=[(200, None), (401, None)]):
            self.assertFalse(auth.password_change_required())
            self.assertTrue(auth.password_change_required())

        auth.is_proxy = lambda: False
        auth.user = "ARRAY_RO"
        with mock.patch(self.REQ_FUNC, side_effect=[(200, None)]):
            self.assertTrue(auth.password_change_required())

        auth.user = "ARRAY_RW"
        with mock.patch(self.REQ_FUNC, side_effect=[(204, None), (422, None)]):
            self.assertFalse(auth.password_change_required())
            self.assertTrue(auth.password_change_required())

        auth.user = "admin"
        with mock.patch(self.REQ_FUNC, side_effect=[(200, None), (401, None)]):
            self.assertFalse(auth.password_change_required())
            self.assertTrue(auth.password_change_required())

    def test_password_change_required_fail(self):
        """Verify password_change_required method fails as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        auth.ssid = "0"
        auth.user = "ARRAY_RW"
        auth.is_proxy = lambda: True
        auth.update_password_length_requirement = lambda: None
        with self.assertRaisesRegexp(AnsibleFailJson, "ARRAY_RW, ARRAY_RO are not valid users for SANtricity Web Services Proxy."):
            auth.password_change_required()

        auth.user = "admin"
        with mock.patch(self.REQ_FUNC, return_value=(422, None)):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to validate password status."):
                auth.password_change_required()

        auth.ssid = "1"
        with mock.patch(self.REQ_FUNC, return_value=(404, None)):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to validate password status."):
                auth.password_change_required()

        auth.user = "monitor"
        auth.is_embedded_available = lambda: True
        with mock.patch(self.REQ_FUNC, return_value=(422, None)):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to validate password status."):
                auth.password_change_required()

        auth.is_embedded_available = lambda: False
        with mock.patch(self.REQ_FUNC, return_value=(422, None)):
            with self.assertRaisesRegexp(AnsibleFailJson, "Storage array without SANtricity Web Services must choose 'ARRAY_RW' or 'ARRAY_RO'."):
                auth.password_change_required()

        auth.user = "ARRAY_RW"
        auth.is_proxy = lambda: False
        with mock.patch(self.REQ_FUNC, return_value=(404, None)):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to validate password status."):
                auth.password_change_required()

        auth.user = "admin"
        auth.is_proxy = lambda: False
        with mock.patch(self.REQ_FUNC, return_value=(422, None)):
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to validate password status."):
                auth.password_change_required()

    def test_set_array_password_pass(self):
        """Verify set_array_password method completes as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        auth.is_proxy = lambda: True
        with mock.patch(self.REQ_FUNC, return_value=(200, None)):
            auth.ssid = "0"
            auth.set_array_password()

            auth.ssid = "1"
            auth.set_array_password()

            auth.user = "monitor"
            auth.is_embedded_available = lambda: True
            auth.set_array_password()

        auth.is_proxy = lambda: False
        with mock.patch(self.REQ_FUNC, return_value=(200, None)):
            auth.user = "ARRAY_RW"
            auth.set_array_password()

            auth.user = "monitor"
            auth.set_array_password()

    def test_set_array_password_fail(self):
        """Verify set_array_password method fails as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()

        auth.is_proxy = lambda: True
        with mock.patch(self.REQ_FUNC, return_value=Exception()):
            auth.ssid = "0"
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to set proxy password."):
                auth.set_array_password()

            auth.ssid = "1"
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to set storage system password."):
                auth.set_array_password()

            auth.user = "monitor"
            auth.is_embedded_available = lambda: True
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to set embedded user password."):
                auth.set_array_password()

        auth.is_proxy = lambda: False
        with mock.patch(self.REQ_FUNC, return_value=Exception()):
            auth.user = "ARRAY_RW"
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to set storage system password."):
                auth.set_array_password()

            auth.user = "monitor"
            with self.assertRaisesRegexp(AnsibleFailJson, "Failed to set embedded user password."):
                auth.set_array_password()

    def test_apply_pass(self):
        """Verify apply method completes as expected."""
        self._set_args(current_admin_password="adminpass", password="password", user="admin")
        auth = NetAppESeriesAuth()
        auth.restore_password_length_requirement = lambda: None

        with self.assertRaisesRegexp(AnsibleExitJson, "Password has not been changed."):
            auth.password_change_required = lambda: False
            auth.module.check_mode = True
            auth.apply()

            auth.password_change_required = lambda: True
            auth.module.check_mode = True
            auth.apply()

        with self.assertRaisesRegexp(AnsibleExitJson, "Password has been changed."):
            auth.password_change_required = lambda: True
            auth.set_array_password = lambda: None
            auth.module.check_mode = False
            auth.apply()
