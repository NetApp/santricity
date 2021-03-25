#!/usr/bin/python

# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
---
module: na_santricity_backup
short_description: NetApp E-Series storage configuration backup.
description: Builds a complete Ansible inventory structure of the storage system in JSON format.
author: Nathan Swartz (@ndswartz)
extends_documentation_fragment:
  - netapp_eseries.santricity.santricity.santricity_doc
"""

EXAMPLES = """
  - name: Get current storage system inventory configuration.
    na_santricity_backup:
"""

RETURN = """
changed:
  description: Only information is being returned; no changes.
  returned: on success
  type: bool
  sample: true
configuration:
  description: Configuration details in JSON format
  returned: on success
  type: complex
  sample:
"""
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule
from ansible.module_utils._text import to_native


class NetAppESeriesBackup(NetAppESeriesModule):
    def __init__(self):
        version = "02.00.0000.0000"
        ansible_options = dict()
        super(NetAppESeriesBackup, self).__init__(ansible_options=ansible_options, web_services_version=version)

        self.graph_cache = None

    def graph(self):
        """Storage system graph."""
        if self.graph_cache is None:
            try:
                rc, self.graph_cache = self.request("storage-system/%s/graph" % self.ssid)
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve the storage system graph! Array [%s]. Error [%s]." % (self.ssid, to_native(error)))

        return self.graph_cache

    def get_global(self):
        """Get the configuration details for na_santricity_global module."""


    def get_configuration(self):
        """Determine Ansible configuration details and return structure."""
        configuration = {}

        self.module.exit_json(changes=False, configuration=configuration)


def main():
    backup = NetAppESeriesBackup()
    backup.get_configuration()


if __name__ == "__main__":
    main()
