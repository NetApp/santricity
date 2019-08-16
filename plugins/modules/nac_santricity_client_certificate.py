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
module: nac_santricity_client_certificate
version_added: "2.9"
short_description: NetApp E-Series manage remote server certificates.
description: Manage NetApp E-Series storage array's remote server certificates.
author: Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp.eseries
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
  file_path:
    description:
      - Valid path to the remote server certificate
      - Must be specified when I(state=="present")
      - When alias is not known or specified the file can be used to identify existing certificate match.
    required: false
note:
  - When I(state=="absent") either I(alias) or I(file_path) must be specified.
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
import re

from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule, create_multipart_formdata
from ansible.module_utils._text import to_native


class NetAppESeriesClientCertificate(NetAppESeriesModule):
    def __init__(self):
        ansible_options = dict(state=dict(required=True, choices=["present", "absent"]),
                               alias=dict(type="str", required=False),
                               file_path=dict(type="str", required=False))
        required_if = [["state", "present", ["file_path"]]]

        super(NetAppESeriesClientCertificate, self).__init__(ansible_options=ansible_options,
                                                             web_services_version="02.00.0000.0000",
                                                             supports_check_mode=True,
                                                             required_if=required_if)

        args = self.module.params
        self.state = args["state"]
        self.alias = args["alias"]
        self.file_path = args["file_path"]
        self.certificate_cache = dict()
        self.certificate_fingerprint_cache = None
        self.certificate_info_cache = None

        if self.state == "absent" and not (self.alias or self.file_path):
            self.module.fail_json(msg="Either alias or file_path must be specified in order to remove an existing"
                                      " certificate. Array [%s]" % self.ssid)

    @property
    def certificate(self):
        """Search for remote server certificate that goes by the alias or has a matching fingerprint.

        :returns dict: dictionary containing information about the certificate."""
        if not self.certificate_cache:
            rc, certificates = self.request("certificates/remote-server", ignore_errors=True)

            if rc == 404:   # system down or endpoint does not exist
                rc, certificates = self.request("sslconfig/ca", ignore_errors=True)
                if rc > 299:
                    self.module.fail_json(msg="Failed to retrieve remote server certificates. Array [%s]." % self.ssid)

                if self.state == "present" and self.alias:
                    self.module.fail_json(msg="User-defined aliases cannot be used to in this version of NetApp"
                                              " E-Series Web Services. Please upgrade Web Services or just specifying"
                                              " file_path option. Array [%s]." % self.ssid)

                for certificate in certificates:
                    tmp = dict(subject_dn=[re.sub(r".*=", "", item) for item in certificate["subjectDN"].split(", ")],
                               issuer_dn=[re.sub(r".*=", "", item) for item in certificate["issuerDN"].split(", ")],
                               start_date=datetime.strptime(certificate["start"].split(".")[0], "%Y-%m-%dT%H:%M:%S"),
                               expire_date=datetime.strptime(certificate["expire"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))

                    if (all([attr in self.certificate_info["subject_dn"] for attr in tmp["subject_dn"]]) and
                            all([attr in self.certificate_info["issuer_dn"] for attr in tmp["issuer_dn"]]) and
                            tmp["start_date"] == self.certificate_info["start_date"] and
                            tmp["expire_date"] == self.certificate_info["expire_date"]):
                        self.alias = certificate["alias"]
                        self.certificate_cache = tmp
                        break

            elif rc > 299:
                self.module.fail_json(msg="Failed to retrieve remote server certificates. Array [%s]." % self.ssid)
            else:
                for certificate in certificates:
                    if (certificate["alias"] == self.alias or
                            self.certificate_fingerprint == certificate["sha256Fingerprint"] or
                            self.certificate_fingerprint == certificate["shaFingerprint"]):
                        self.certificate_cache = certificate
                        break

            self.module.debug(self.certificate_cache)
        return self.certificate_cache

    @property
    def certificate_info(self):
        """Determine the pertinent certificate information: alias, subjectDN, issuerDN, start and expire.

        Note: Use only when certificate/remote-server endpoints do not exist. Used to identify certificates through
        the sslconfig/ca endpoint.
        """
        if not self.certificate_info_cache:
            certificate = None
            with open(self.file_path, "rb") as fh:
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

            self.certificate_info_cache = dict(start_date=certificate.not_valid_before,
                                               expire_date=certificate.not_valid_after,
                                               subject_dn=[attr.value for attr in certificate.subject],
                                               issuer_dn=[attr.value for attr in certificate.issuer])

        return self.certificate_info_cache

    @property
    def certificate_fingerprint(self):
        """Load x509 certificate that is either encoded DER or PEM encoding and return the certificate fingerprint."""
        certificate = None
        if not self.certificate_fingerprint_cache:
            with open(self.file_path, "rb") as fh:
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
            self.certificate_fingerprint_cache = binascii.hexlify(
                certificate.fingerprint(certificate.signature_hash_algorithm))

        return self.certificate_fingerprint_cache

    def certificate_match(self):
        """Determine whether the certificate is different than the existing certificate in the truststore."""

        if all([key in ["subject_dn", "issuer_dn", "start_date", "expire_date"] for key in self.certificate.keys()]):
            if (all([attr in self.certificate_info["subject_dn"] for attr in self.certificate["subject_dn"]]) and
                    all([attr in self.certificate_info["issuer_dn"] for attr in self.certificate["issuer_dn"]]) and
                    self.certificate["start_date"] == self.certificate_info["start_date"] and
                    self.certificate["expire_date"] == self.certificate_info["expire_date"]):
                return True

        elif any([key in ["sha256Fingerprint", "shaFingerprint"] for key in self.certificate.keys()]):
            if (self.certificate_fingerprint == self.certificate["sha256Fingerprint"] or
                    self.certificate_fingerprint == self.certificate["shaFingerprint"]):
                return True

        return False

    def upload_certificate(self):
        """Add or update remote server certificate to the storage array."""
        url = "certificates/remote-server?alias=%s" % self.alias if self.alias else "certificates/remote-server"
        headers, data = create_multipart_formdata(files=[("file", self.file_path)])
        rc, resp = self.request(url, method="POST", headers=headers, data=data, ignore_errors=True)
        if rc == 404:
            rc, resp = self.request("sslconfig/ca", method="POST", headers=headers, data=data, ignore_errors=True)

        if rc > 299:
            self.module.fail_json(msg="Failed to upload certificate. Array [%s]. Error [%s, %s]." % (self.ssid, rc, resp))

    def delete_certificate(self):
        """Delete existing remote server certificate in the storage array truststore."""
        rc, resp = self.request("certificates/remote-server/%s" % self.alias, method="DELETE", ignore_errors=True)
        if rc == 404:
            rc, resp = self.request("sslconfig/ca/%s" % self.alias, method="DELETE", ignore_errors=True)

        if rc > 204:
            self.module.fail_json(msg="Failed to delete certificate. Alias [%s]. Array [%s]. Error [%s, %s]." % (self.alias, self.ssid, rc, resp))

    def apply(self):
        """Apply state changes to the storage array's truststore."""
        change_required = False
        message = "No changes were required. Array [%s]." % self.ssid

        if self.state == "present":
            if self.certificate:
                if not self.certificate_match():
                    change_required = True
            else:
                change_required = True
        elif self.certificate:
            change_required = True

        if change_required and not self.module.check_mode:
            if self.state == "present":
                self.upload_certificate()
                if self.certificate:
                    message = "Certificate [%s] was successfully modified. Array [%s]." % (self.alias, self.ssid)
                else:
                    message = "Certificate [%s] was successfully uploaded. Array [%s]." % (self.alias, self.ssid)
            elif self.certificate:
                self.delete_certificate()
                message = "Certificate [%s] was successfully removed. Array [%s]." % (self.alias, self.ssid)

        self.module.exit_json(msg=message, changed=change_required)


def main():
    client_certs = NetAppESeriesClientCertificate()
    client_certs.apply()


if __name__ == '__main__':
    main()
