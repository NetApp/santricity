#!/usr/bin/python

# (c) 2016, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function #, unicode_literals
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: na_santricity_client_certificate
version_added: "2.9"
short_description: NetApp E-Series manage remote server certificates.
description: Manage NetApp E-Series storage array's remote server certificates.
author: Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity_doc
options:
  state:
    description:
      - Dictates whether remote server certificates should be added to the storage array.
    required: true
    choices: ["present", "absent"]
  alias:
    description:
      - Alias for the supplied remote server certificate
      - A randomly generated alias will be used when an alias is not given.
      - This option may not be available in older versions of NetApp E-Series web services.
    required: false
  certificates:
    description:
      - List of certificate files
      - Each item must include the path to the file
    required: false
note:
  - When I(state=="absent") either I(alias) or I(file_path) must be specified.
  - Use M(ssid=0) to specifically reference SANtricity Web Services Proxy.
'''
EXAMPLES = '''
'''
RETURN = '''
---
msg:
    description: 
    type: string
    returned: always
    sample: ""
'''

import binascii
import os
import re

from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule, create_multipart_formdata
from ansible.module_utils._text import to_native


class NetAppESeriesClientCertificate(NetAppESeriesModule):
    def __init__(self):
        ansible_options = dict(certificates=dict(type="list", required=False))

        super(NetAppESeriesClientCertificate, self).__init__(ansible_options=ansible_options,
                                                             web_services_version="02.00.0000.0000",
                                                             supports_check_mode=True)

        args = self.module.params
        self.certificates = args["certificates"] if args["certificates"] else []

        # Check whether request needs to be forwarded on to the controller web services rest api.
        self.url_path_prefix = ""
        if not self.is_embedded() and self.ssid != 0:
            self.url_path_prefix = "storage-systems/%s/forward/devmgr/v2/" % self.ssid

        self.remove_certificates = list()
        self.add_certificates = list()
        self.certificate_fingerprint_cache = None
        self.certificate_info_cache = None

    def determine_changes(self):
        """Search for remote server certificate that goes by the alias or has a matching fingerprint.

        :returns dict: dictionary containing information about the certificate."""
        rc, current_certificates = self.request(self.url_path_prefix + "certificates/remote-server", ignore_errors=True)

        if rc == 404:   # system down or endpoint does not exist
            rc, current_certificates = self.request(self.url_path_prefix + "sslconfig/ca?useTruststore=true", ignore_errors=True)

            if rc > 299:
                self.module.fail_json(msg="Failed to retrieve remote server certificates. Array [%s]." % self.ssid)

            user_installed_certificates = [certificate for certificate in current_certificates if certificate["isUserInstalled"]]
            existing_certificates = []

            for path in self.certificates:
                for current_certificate in user_installed_certificates:
                    info = self.certificate_info(path)
                    tmp = dict(subject_dn=[re.sub(r".*=", "", item) for item in current_certificate["subjectDN"].split(", ")],
                               issuer_dn=[re.sub(r".*=", "", item) for item in current_certificate["issuerDN"].split(", ")],
                               start_date=datetime.strptime(current_certificate["start"].split(".")[0], "%Y-%m-%dT%H:%M:%S"),
                               expire_date=datetime.strptime(current_certificate["expire"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))

                    if (all([attr in info["subject_dn"] for attr in tmp["subject_dn"]]) and
                            all([attr in info["issuer_dn"] for attr in tmp["issuer_dn"]]) and
                            tmp["start_date"] == info["start_date"] and
                            tmp["expire_date"] == info["expire_date"]):
                        existing_certificates.append(current_certificate)
                        break
                else:
                    self.add_certificates.append(path)
            self.remove_certificates = [certificate for certificate in user_installed_certificates if certificate not in existing_certificates]

        elif rc > 299:
            self.module.fail_json(msg="Failed to retrieve remote server certificates. Array [%s]." % self.ssid)

        else:
            user_installed_certificates = [certificate for certificate in current_certificates if certificate["isUserInstalled"]]
            existing_certificates = []
            for path in self.certificates:
                for current_certificate in user_installed_certificates:
                    fingerprint = self.certificate_fingerprint(path)
                    if current_certificate["sha256Fingerprint"] == fingerprint or current_certificate["shaFingerprint"] == fingerprint:
                        existing_certificates.append(current_certificate)
                        break
                else:
                    self.add_certificates.append(path)
            self.remove_certificates = [certificate for certificate in user_installed_certificates if certificate not in existing_certificates]

    def certificate_info(self, path):
        """Determine the pertinent certificate information: alias, subjectDN, issuerDN, start and expire.

        Note: Use only when certificate/remote-server endpoints do not exist. Used to identify certificates through
        the sslconfig/ca endpoint.
        """
        certificate = None
        with open(path, "rb") as fh:
            data = fh.read()
            try:
                certificate = x509.load_pem_x509_certificate(data, default_backend())
            except Exception as error:
                try:
                    certificate = x509.load_der_x509_certificate(data, default_backend())
                    pass
                except Exception as error:
                    self.module.fail_json(msg="Failed to load certificate. Array [%s]. Error [%s]."
                                              % (self.ssid, to_native(error)))

        if not isinstance(certificate, x509.Certificate):
            self.module.fail_json(msg="Failed to open certificate file or invalid certificate object type. Array [%s]." % self.ssid)

        return dict(start_date=certificate.not_valid_before,
                    expire_date=certificate.not_valid_after,
                    subject_dn=[attr.value for attr in certificate.subject],
                    issuer_dn=[attr.value for attr in certificate.issuer])

    def certificate_fingerprint(self, path):
        """Load x509 certificate that is either encoded DER or PEM encoding and return the certificate fingerprint."""
        certificate = None
        with open(path, "rb") as fh:
            data = fh.read()
            try:
                certificate = x509.load_pem_x509_certificate(data, default_backend())
            except Exception as error:
                try:
                    certificate = x509.load_der_x509_certificate(data, default_backend())
                except Exception as error:
                    self.module.fail_json(msg="Failed to determine certificate fingerprint. File [%s]. Array [%s]. Error [%s]."
                                              % (path, self.ssid, to_native(error)))

        return binascii.hexlify(certificate.fingerprint(certificate.signature_hash_algorithm)).decode("utf-8")

    def upload_certificate(self, path):
        """Add or update remote server certificate to the storage array."""
        file_name = os.path.basename(path)
        headers, data = create_multipart_formdata(files=[("file", file_name, path)])

        rc, resp = self.request(self.url_path_prefix + "certificates/remote-server", method="POST", headers=headers, data=data, ignore_errors=True)

        if rc == 404:
            rc, resp = self.request(self.url_path_prefix + "sslconfig/ca?useTruststore=true", method="POST", headers=headers, data=data, ignore_errors=True)
        if rc > 299:
            self.module.fail_json(msg="Failed to upload certificate. Array [%s]. Error [%s, %s]." % (self.ssid, rc, resp))

    def delete_certificate(self, info):
        """Delete existing remote server certificate in the storage array truststore."""
        rc, resp = self.request(self.url_path_prefix + "certificates/remote-server/%s" % info["alias"], method="DELETE", ignore_errors=True)

        if rc == 404:
            rc, resp = self.request(self.url_path_prefix + "sslconfig/ca/%s?useTruststore=true" % info["alias"], method="DELETE", ignore_errors=True)

        if rc > 204:
            self.module.fail_json(msg="Failed to delete certificate. Alias [%s]. Array [%s]. Error [%s, %s]." % (info["alias"], self.ssid, rc, resp))

    def apply(self):
        """Apply state changes to the storage array's truststore."""
        changed = False

        self.determine_changes()
        if self.remove_certificates or self.add_certificates:
            changed = True

        if changed and not self.module.check_mode:
            for info in self.remove_certificates:
                self.delete_certificate(info)

            for path in self.add_certificates:
                self.upload_certificate(path)

        self.module.exit_json(changed=changed, removed_certificates=self.remove_certificates, add_certificates=self.add_certificates)


def main():
    client_certs = NetAppESeriesClientCertificate()
    client_certs.apply()


if __name__ == '__main__':
    main()
