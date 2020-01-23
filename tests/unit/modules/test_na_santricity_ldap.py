# (c) 2018, NetApp Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_ldap import NetAppESeriesLdap
from units.modules.utils import ModuleTestCase, set_module_args, AnsibleFailJson, AnsibleExitJson
from units.compat import mock


class LdapTest(ModuleTestCase):
    REQUIRED_PARAMS = {
        'api_username': 'admin',
        'api_password': 'password',
        'api_url': 'http://localhost',
        'ssid': '1',
        'state': 'absent',
    }
    REQ_FUNC = 'ansible_collections.netapp_eseries.santricity.plugins.modules.na_santricity_ldap.NetAppESeriesLdap.request'

    # def _make_ldap_instance(self):
    #     self._set_args()
    #     ldap = NetAppESeriesLdap()
    #     ldap.base_path = '/'
    #     return ldap
    #
    # def _set_args(self, **kwargs):
    #     module_args = self.REQUIRED_PARAMS.copy()
    #     module_args.update(kwargs)
    #     set_module_args(module_args)
    #
    # def test_init_defaults(self):
    #     """Validate a basic run with required arguments set."""
    #     self._set_args(state='present',
    #                    username='myBindAcct',
    #                    password='myBindPass',
    #                    server='ldap://example.com:384',
    #                    search_base='OU=Users,DC=example,DC=com',
    #                    role_mappings={'.*': ['storage.monitor']})
    #
    #     ldap = NetAppESeriesLdap()
    #
    # def test_init(self):
    #     """Validate a basic run with required arguments set."""
    #     self._set_args()
    #     ldap = NetAppESeriesLdap()
    #
    # def test_get_full_configuration(self):
    #     self._set_args()
    #
    #     resp = dict(result=None)
    #
    #     with mock.patch(self.REQ_FUNC, return_value=(200, resp)):
    #         ldap = self._make_ldap_instance()
    #         result = ldap.get_full_configuration()
    #         self.assertEqual(resp, result)
    #
    # def test_get_full_configuration_failure(self):
    #     self._set_args()
    #
    #     resp = dict(result=None)
    #     with self.assertRaises(AnsibleFailJson):
    #         with mock.patch(self.REQ_FUNC, side_effect=Exception):
    #             ldap = self._make_ldap_instance()
    #             ldap.get_full_configuration()
    #
    # def test_get_configuration(self):
    #     self._set_args()
    #
    #     resp = dict(result=None)
    #
    #     with mock.patch(self.REQ_FUNC, return_value=(200, resp)):
    #         ldap = self._make_ldap_instance()
    #         result = ldap.get_configuration('')
    #         self.assertEqual(resp, result)
    #
    #     with mock.patch(self.REQ_FUNC, return_value=(404, resp)):
    #         ldap = self._make_ldap_instance()
    #         result = ldap.get_configuration('')
    #         self.assertIsNone(result)
    #
    # def test_clear_configuration(self):
    #     self._set_args()
    #
    #     # No changes are required if the domains are empty
    #     config = dict(ldapDomains=[])
    #
    #     ldap = self._make_ldap_instance()
    #     with mock.patch.object(ldap, 'get_full_configuration', return_value=config):
    #         with mock.patch(self.REQ_FUNC, return_value=(204, None)):
    #             msg, result = ldap.clear_configuration()
    #             self.assertFalse(result)
    #
    #     config = dict(ldapDomains=['abc'])
    #
    #     # When domains exist, we need to clear
    #     ldap = self._make_ldap_instance()
    #     with mock.patch.object(ldap, 'get_full_configuration', return_value=config):
    #         with mock.patch(self.REQ_FUNC, return_value=(204, None)) as req:
    #             msg, result = ldap.clear_configuration()
    #             self.assertTrue(result)
    #             self.assertTrue(req.called)
    #
    #             # Valid check_mode makes no changes
    #             req.reset_mock()
    #             ldap.check_mode = True
    #             msg, result = ldap.clear_configuration()
    #             self.assertTrue(result)
    #             self.assertFalse(req.called)
    #
    # def test_clear_single_configuration(self):
    #     self._set_args()
    #
    #     # No changes are required if the domains are empty
    #     config = 'abc'
    #
    #     ldap = self._make_ldap_instance()
    #     with mock.patch.object(ldap, 'get_configuration', return_value=config):
    #         with mock.patch(self.REQ_FUNC, return_value=(204, None)) as req:
    #             msg, result = ldap.clear_single_configuration()
    #             self.assertTrue(result)
    #
    #             # Valid check_mode makes no changes
    #             req.reset_mock()
    #             ldap.check_mode = True
    #             msg, result = ldap.clear_single_configuration()
    #             self.assertTrue(result)
    #             self.assertFalse(req.called)
    #
    #     # When domains exist, we need to clear
    #     ldap = self._make_ldap_instance()
    #     with mock.patch.object(ldap, 'get_configuration', return_value=None):
    #         with mock.patch(self.REQ_FUNC, return_value=(204, None)) as req:
    #             msg, result = ldap.clear_single_configuration()
    #             self.assertFalse(result)
    #             self.assertFalse(req.called)
    #
    # def test_update_configuration(self):
    #     self._set_args()
    #
    #     config = dict(id='abc')
    #     body = dict(id='xyz')
    #
    #     ldap = self._make_ldap_instance()
    #     with mock.patch.object(ldap, 'make_configuration', return_value=body):
    #         with mock.patch.object(ldap, 'get_configuration', return_value=config):
    #             with mock.patch(self.REQ_FUNC, return_value=(200, None)) as req:
    #                 msg, result = ldap.update_configuration()
    #                 self.assertTrue(result)
    #
    #                 # Valid check_mode makes no changes
    #                 req.reset_mock()
    #                 ldap.check_mode = True
    #                 msg, result = ldap.update_configuration()
    #                 self.assertTrue(result)
    #                 self.assertFalse(req.called)
    #
    # def test_update(self):
    #     self._set_args()
    #
    #     ldap = self._make_ldap_instance()
    #     with self.assertRaises(AnsibleExitJson):
    #         with mock.patch.object(ldap, 'get_base_path', return_value='/'):
    #             with mock.patch.object(ldap, 'update_configuration', return_value=('', True)) as update:
    #                 ldap.ldap = True
    #                 msg, result = ldap.update()
    #                 self.assertTrue(result)
    #                 self.assertTrue(update.called)
    #
    # def test_update_disable(self):
    #     self._set_args()
    #
    #     ldap = self._make_ldap_instance()
    #     with self.assertRaises(AnsibleExitJson):
    #         with mock.patch.object(ldap, 'get_base_path', return_value='/'):
    #             with mock.patch.object(ldap, 'clear_single_configuration', return_value=('', True)) as update:
    #                 ldap.ldap = False
    #                 ldap.identifier = 'abc'
    #                 msg, result = ldap.update()
    #                 self.assertTrue(result)
    #                 self.assertTrue(update.called)
    #
    # def test_update_disable_all(self):
    #     self._set_args()
    #
    #     ldap = self._make_ldap_instance()
    #     with self.assertRaises(AnsibleExitJson):
    #         with mock.patch.object(ldap, 'get_base_path', return_value='/'):
    #             with mock.patch.object(ldap, 'clear_configuration', return_value=('', True)) as update:
    #                 ldap.ldap = False
    #                 msg, result = ldap.update()
    #                 self.assertTrue(result)
    #                 self.assertTrue(update.called)
    #
    # def test_get_configuration_failure(self):
    #     self._set_args()
    #
    #     with self.assertRaises(AnsibleFailJson):
    #         with mock.patch(self.REQ_FUNC, side_effect=Exception):
    #             ldap = self._make_ldap_instance()
    #             ldap.get_configuration('')
    #
    #     # We expect this for any code not in [200, 404]
    #     with self.assertRaises(AnsibleFailJson):
    #         with mock.patch(self.REQ_FUNC, return_value=(401, '')):
    #             ldap = self._make_ldap_instance()
    #             result = ldap.get_configuration('')
    #             self.assertIsNone(result)
    #
    # def test_make_configuration(self):
    #     """Validate the make_configuration method that translates Ansible params to the input body"""
    #     data = dict(state='present',
    #                 username='myBindAcct',
    #                 password='myBindPass',
    #                 server='ldap://example.com:384',
    #                 search_base='OU=Users,DC=example,DC=com',
    #                 role_mappings={'.*': ['storage.monitor']},
    #                 )
    #
    #     self._set_args(**data)
    #     ldap = NetAppESeriesLdap()
    #     expected = dict(id='default',
    #                     bindLookupUser=dict(user=data['username'],
    #                                         password=data['password'], ),
    #                     groupAttributes=['memberOf'],
    #                     ldapUrl=data['server'],
    #                     names=['example.com'],
    #                     searchBase=data['search_base'],
    #                     roleMapCollection=[{"groupRegex": ".*",
    #                                         "ignoreCase": True,
    #                                         "name": "storage.monitor"
    #                                         }
    #                                        ],
    #                     userAttribute='sAMAccountName'
    #                     )
    #
    #     actual = ldap.make_configuration()
    #     self.maxDiff = None
    #     self.assertEqual(expected, actual)
