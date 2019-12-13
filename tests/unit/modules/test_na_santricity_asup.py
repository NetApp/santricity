# (c) 2018, NetApp Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open

from ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_asup import NetAppESeriesAsup
from units.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class AsupTest(ModuleTestCase):
    REQUIRED_PARAMS = {
        'api_username': 'rw',
        'api_password': 'password',
        'api_url': 'http://localhost',
        'ssid': '1',
    }

    REQ_FUNC = "ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_asup.NetAppESeriesAsup.request"
    TIME_FUNC = "ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_asup.time.time"

    def _set_args(self, args=None):
        module_args = self.REQUIRED_PARAMS.copy()
        if args is not None:
            module_args.update(args)
        set_module_args(module_args)


    #
    # def test_get_config_asup_capable_false(self):
    #     """Ensure we fail correctly if ASUP is not available on this platform"""
    #     self._set_args()
    #
    #     expected = dict(asupCapable=False, onDemandCapable=True)
    #     asup = NetAppESeriesAsup()
    #     # Expecting an update
    #     with self.assertRaisesRegexp(AnsibleFailJson, r"not supported"):
    #         with patch(self.REQ_FUNC, return_value=(200, expected)):
    #             asup.get_configuration()
    #
    # def test_get_config_on_demand_capable_false(self):
    #     """Ensure we fail correctly if ASUP is not available on this platform"""
    #     self._set_args()
    #
    #     expected = dict(asupCapable=True, onDemandCapable=False)
    #     asup = NetAppESeriesAsup()
    #     # Expecting an update
    #     with self.assertRaisesRegexp(AnsibleFailJson, r"not supported"):
    #         with patch(self.REQ_FUNC, return_value=(200, expected)):
    #             asup.get_configuration()
    #
    # def test_get_config(self):
    #     """Validate retrieving the ASUP configuration"""
    #     self._set_args()
    #
    #     expected = dict(asupCapable=True, onDemandCapable=True)
    #     asup = NetAppESeriesAsup()
    #
    #     with patch(self.REQ_FUNC, return_value=(200, expected)):
    #         config = asup.get_configuration()
    #         self.assertEquals(config, expected)
    #
    # def test_update_configuration(self):
    #     """Validate retrieving the ASUP configuration"""
    #     self._set_args(dict(asup='enabled'))
    #
    #     expected = dict()
    #     initial = dict(asupCapable=True,
    #                    asupEnabled=True,
    #                    onDemandEnabled=False,
    #                    remoteDiagsEnabled=False,
    #                    schedule=dict(daysOfWeek=[], dailyMinTime=0, weeklyMinTime=0, dailyMaxTime=24, weeklyMaxTime=24))
    #     asup = NetAppESeriesAsup()
    #
    #     with patch(self.REQ_FUNC, return_value=(200, expected)) as req:
    #         with patch.object(asup, 'get_configuration', return_value=initial):
    #             updated = asup.update_configuration()
    #             self.assertTrue(req.called)
    #             self.assertTrue(updated)
    #
    # def test_update_configuration_asup_disable(self):
    #     """Validate retrieving the ASUP configuration"""
    #     self._set_args(dict(asup='disabled'))
    #
    #     expected = dict()
    #     initial = dict(asupCapable=True,
    #                    asupEnabled=True,
    #                    onDemandEnabled=False,
    #                    remoteDiagsEnabled=False,
    #                    schedule=dict(daysOfWeek=[], dailyMinTime=0, weeklyMinTime=0, dailyMaxTime=24, weeklyMaxTime=24))
    #     asup = NetAppESeriesAsup()
    #
    #     with patch(self.REQ_FUNC, return_value=(200, expected)) as req:
    #         with patch.object(asup, 'get_configuration', return_value=initial):
    #             updated = asup.update_configuration()
    #             self.assertTrue(updated)
    #
    #             self.assertTrue(req.called)
    #
    #             # Ensure it was called with the right arguments
    #             called_with = req.call_args
    #             body = json.loads(called_with[1]['data'])
    #             self.assertFalse(body['asupEnabled'])
    #
    # def test_update_configuration_enable(self):
    #     """Validate retrieving the ASUP configuration"""
    #     self._set_args(dict(asup='enabled'))
    #
    #     expected = dict()
    #     initial = dict(asupCapable=False,
    #                    asupEnabled=False,
    #                    onDemandEnabled=False,
    #                    remoteDiagsEnabled=False,
    #                    schedule=dict(daysOfWeek=[], dailyMinTime=0, weeklyMinTime=0, dailyMaxTime=24, weeklyMaxTime=24))
    #     asup = NetAppESeriesAsup()
    #
    #     with patch(self.REQ_FUNC, return_value=(200, expected)) as req:
    #         with patch.object(asup, 'get_configuration', return_value=initial):
    #             updated = asup.update_configuration()
    #             self.assertTrue(updated)
    #
    #             self.assertTrue(req.called)
    #
    #             # Ensure it was called with the right arguments
    #             called_with = req.call_args
    #             body = json.loads(called_with[1]['data'])
    #             self.assertTrue(body['asupEnabled'])
    #             self.assertTrue(body['onDemandEnabled'])
    #             self.assertTrue(body['remoteDiagsEnabled'])
    #
    # def test_update_configuration_request_exception(self):
    #     """Validate exception handling when request throws an exception."""
    #     config_response = dict(asupEnabled=True,
    #                            onDemandEnabled=True,
    #                            remoteDiagsEnabled=True,
    #                            schedule=dict(daysOfWeek=[],
    #                                          dailyMinTime=0,
    #                                          weeklyMinTime=0,
    #                                          dailyMaxTime=24,
    #                                          weeklyMaxTime=24))
    #
    #     self._set_args(dict(state="enabled"))
    #     asup = NetAppESeriesAsup()
    #     with self.assertRaises(Exception):
    #         with patch.object(asup, 'get_configuration', return_value=config_response):
    #             with patch(self.REQ_FUNC, side_effect=Exception):
    #                 asup.update_configuration()
    #
    # def test_init_schedule(self):
    #     """Validate schedule correct schedule initialization"""
    #     self._set_args(dict(state="enabled", active=True, days=["sunday", "monday", "tuesday"], start=20, end=24))
    #     asup = NetAppESeriesAsup()
    #
    #     self.assertTrue(asup.asup)
    #     self.assertEquals(asup.days, ["sunday", "monday", "tuesday"]),
    #     self.assertEquals(asup.start, 1200)
    #     self.assertEquals(asup.end, 1439)
    #
    # def test_init_schedule_invalid(self):
    #     """Validate updating ASUP with invalid schedule fails test."""
    #     self._set_args(dict(state="enabled", active=True, start=22, end=20))
    #     with self.assertRaisesRegexp(AnsibleFailJson, r"start time is invalid"):
    #         NetAppESeriesAsup()
    #
    # def test_init_schedule_days_invalid(self):
    #     """Validate updating ASUP with invalid schedule fails test."""
    #     self._set_args(dict(state="enabled", active=True, days=["someday", "thataday", "nonday"]))
    #     with self.assertRaises(AnsibleFailJson):
    #         NetAppESeriesAsup()
    #
    # def test_update(self):
    #     """Validate updating ASUP with valid schedule passes"""
    #     initial = dict(asupCapable=True,
    #                    onDemandCapable=True,
    #                    asupEnabled=True,
    #                    onDemandEnabled=False,
    #                    remoteDiagsEnabled=False,
    #                    schedule=dict(daysOfWeek=[], dailyMinTime=0, weeklyMinTime=0, dailyMaxTime=24, weeklyMaxTime=24))
    #     self._set_args(dict(state="enabled", active=True, days=["sunday", "monday", "tuesday"], start=10, end=20))
    #     asup = NetAppESeriesAsup()
    #     with self.assertRaisesRegexp(AnsibleExitJson, r"ASUP settings have been updated"):
    #         with patch(self.REQ_FUNC, return_value=(200, dict(asupCapable=True))):
    #             with patch.object(asup, "get_configuration", return_value=initial):
    #                 asup.update()
    #
    # def test_get_configuration_asup_not_available_fail(self):
    #     """Validate exception is thrown when ASUP is not available."""
    #     self._set_args(dict(state="enabled", active=True, days=["sunday", "monday", "tuesday"], start=20, end=24))
    #     asup = NetAppESeriesAsup()
    #
    #     with self.assertRaisesRegexp(AnsibleFailJson, r"ASUP is not supported on this device."):
    #         with patch(self.REQ_FUNC, return_value=(200, {"asupCapable": False, "onDemandCapable": False})):
    #             asup.get_configuration()
    #
    #     with self.assertRaisesRegexp(AnsibleFailJson, r"ASUP is not supported on this device."):
    #         with patch(self.REQ_FUNC, return_value=(200, {"asupCapable": True, "onDemandCapable": False})):
    #             asup.get_configuration()
    #
    #     with self.assertRaisesRegexp(AnsibleFailJson, r"ASUP is not supported on this device."):
    #         with patch(self.REQ_FUNC, return_value=(200, {"asupCapable": False, "onDemandCapable": True})):
    #             asup.get_configuration()
    #
    # def test_in_maintenance_mode_pass(self):
    #     """Verify in_maintenance_mode method performs successful."""
    #     self._set_args(dict(state="enabled", active=True, days=["sunday", "monday", "tuesday"], start=20, end=24))
    #     asup = NetAppESeriesAsup()
    #
    #     with patch(self.TIME_FUNC, return_value=0.0):
    #         with patch(self.REQ_FUNC, return_value=(200, [{"key": "ansible_asup_maintenance_email_list", "value": ["a@xyz.com", "b@xyz.com"]},
    #                                                       {"key": "ansible_asup_maintenance_stop_time", "value": "1573753309.260346"}])):
    #             asup.get_configuration()
    #
    #
    # def test_in_maintenance_mode_fail(self):
    #     """Verify in_maintenance_mode method throws expected exceptions."""
