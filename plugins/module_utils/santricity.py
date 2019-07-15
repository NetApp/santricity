# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) 2017, Sumit Kumar <sumit4@netapp.com>
# Copyright (c) 2017, Michael Price <michael.price@netapp.com>
# Copyright (c) 2017, Nathan Swartz <swartzn@netapp.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import random
import mimetypes

from pprint import pformat
from ansible.module_utils import six
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.urls import open_url
from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils._text import to_native
try:
    from ansible.module_utils.ansible_release import __version__ as ansible_version
except ImportError:
    ansible_version = 'unknown'

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse


def eseries_host_argument_spec():
    """Retrieve a base argument specification common to all NetApp E-Series modules"""
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(dict(
        api_username=dict(type='str', required=True),
        api_password=dict(type='str', required=True, no_log=True),
        api_url=dict(type='str', required=True),
        ssid=dict(type='str', required=False, default='1'),
        validate_certs=dict(type='bool', required=False, default=True)
    ))
    return argument_spec


class NetAppESeriesModule(object):
    """Base class for all NetApp E-Series modules.

    Provides a set of common methods for NetApp E-Series modules, including version checking, mode (proxy, embedded)
    verification, http requests, secure http redirection for embedded web services, and logging setup.

    Be sure to add the following lines in the module's documentation section:
    extends_documentation_fragment:
        - netapp.eseries

    :param dict(dict) ansible_options: dictionary of ansible option definitions
    :param str web_services_version: minimally required web services rest api version (default value: "02.00.0000.0000")
    :param bool supports_check_mode: whether the module will support the check_mode capabilities (default=False)
    :param list(list) mutually_exclusive: list containing list(s) of mutually exclusive options (optional)
    :param list(list) required_if: list containing list(s) containing the option, the option value, and then
    a list of required options. (optional)
    :param list(list) required_one_of: list containing list(s) of options for which at least one is required. (optional)
    :param list(list) required_together: list containing list(s) of options that are required together. (optional)
    :param bool log_requests: controls whether to log each request (default: True)
    """
    DEFAULT_TIMEOUT = 60
    DEFAULT_SECURE_PORT = "8443"
    DEFAULT_REST_API_PATH = "devmgr/v2/"
    DEFAULT_REST_API_ABOUT_PATH = "devmgr/utils/about"
    DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json",
                       "netapp-client-type": "Ansible-%s" % ansible_version}
    HTTP_AGENT = "Ansible / %s" % ansible_version
    SIZE_UNIT_MAP = dict(bytes=1, b=1, kb=1024, mb=1024**2, gb=1024**3, tb=1024**4,
                         pb=1024**5, eb=1024**6, zb=1024**7, yb=1024**8)

    def __init__(self, ansible_options, web_services_version=None, supports_check_mode=False,
                 mutually_exclusive=None, required_if=None, required_one_of=None, required_together=None,
                 log_requests=True):
        argument_spec = eseries_host_argument_spec()
        argument_spec.update(ansible_options)

        self.module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=supports_check_mode,
                                    mutually_exclusive=mutually_exclusive, required_if=required_if,
                                    required_one_of=required_one_of, required_together=required_together)

        args = self.module.params
        self.web_services_version = web_services_version if web_services_version else "02.00.0000.0000"
        self.ssid = args["ssid"]
        self.url = args["api_url"]
        self.log_requests = log_requests
        self.creds = dict(url_username=args["api_username"],
                          url_password=args["api_password"],
                          validate_certs=args["validate_certs"])

        if not self.url.endswith("/"):
            self.url += "/"

        self.is_embedded_mode = None
        self.is_web_services_valid_cache = None

    def _check_web_services_version(self):
        """Verify proxy or embedded web services meets minimum version required for module.

        The minimum required web services version is evaluated against version supplied through the web services rest
        api. AnsibleFailJson exception will be raised when the minimum is not met or exceeded.

        This helper function will update the supplied api url if secure http is not used for embedded web services

        :raise AnsibleFailJson: raised when the contacted api service does not meet the minimum required version.
        """
        if not self.is_web_services_valid_cache:

            url_parts = list(urlparse(self.url))
            if not url_parts[0] or not url_parts[1]:
                self.module.fail_json(msg="Failed to provide valid API URL. Example: https://192.168.1.100:8443/devmgr/v2. URL [%s]." % self.url)

            if url_parts[0] not in ["http", "https"]:
                self.module.fail_json(msg="Protocol must be http or https. URL [%s]." % self.url)

            self.url = "%s://%s/" % (url_parts[0], url_parts[1])
            about_url = self.url + self.DEFAULT_REST_API_ABOUT_PATH
            rc, data = request(about_url, timeout=self.DEFAULT_TIMEOUT, headers=self.DEFAULT_HEADERS, ignore_errors=True, **self.creds)

            if rc != 200:
                self.module.warn("Failed to retrieve web services about information! Retrying with secure ports. Array Id [%s]." % self.ssid)
                self.url = "https://%s:8443/" % url_parts[1].split(":")[0]
                about_url = self.url + self.DEFAULT_REST_API_ABOUT_PATH
                try:
                    rc, data = request(about_url, timeout=self.DEFAULT_TIMEOUT, headers=self.DEFAULT_HEADERS, **self.creds)
                except Exception as error:
                    self.module.fail_json(msg="Failed to retrieve the webservices about information! Array Id [%s]. Error [%s]."
                                              % (self.ssid, to_native(error)))

            major, minor, other, revision = data["version"].split(".")
            minimum_major, minimum_minor, other, minimum_revision = self.web_services_version.split(".")

            if not (major > minimum_major or
                    (major == minimum_major and minor > minimum_minor) or
                    (major == minimum_major and minor == minimum_minor and revision >= minimum_revision)):
                self.module.fail_json(msg="Web services version does not meet minimum version required. Current version: [%s]."
                                          " Version required: [%s]." % (data["version"], self.web_services_version))

            self.module.log("Web services rest api version met the minimum required version.")
            self.is_web_services_valid_cache = True

    def is_embedded(self):
        """Determine whether web services server is the embedded web services.

        If web services about endpoint fails based on an URLError then the request will be attempted again using
        secure http.

        :raise AnsibleFailJson: raised when web services about endpoint failed to be contacted.
        :return bool: whether contacted web services is running from storage array (embedded) or from a proxy.
        """
        self._check_web_services_version()

        if self.is_embedded_mode is None:
            about_url = self.url + self.DEFAULT_REST_API_ABOUT_PATH
            try:
                rc, data = request(about_url, timeout=self.DEFAULT_TIMEOUT, headers=self.DEFAULT_HEADERS, **self.creds)
                self.is_embedded_mode = not data["runningAsProxy"]
            except Exception as error:
                self.module.fail_json(msg="Failed to retrieve the webservices about information! Array Id [%s]. Error [%s]."
                                          % (self.ssid, to_native(error)))

        return self.is_embedded_mode

    def request(self, path, data=None, method='GET', headers=None, ignore_errors=False):
        """Issue an HTTP request to a url, retrieving an optional JSON response.

        :param str path: web services rest api endpoint path (Example: storage-systems/1/graph). Note that when the
        full url path is specified then that will be used without supplying the protocol, hostname, port and rest path.
        :param data: data required for the request (data may be json or any python structured data)
        :param str method: request method such as GET, POST, DELETE.
        :param dict headers: dictionary containing request headers.
        :param bool ignore_errors: forces the request to ignore any raised exceptions.
        """
        self._check_web_services_version()

        if headers is None:
            headers = self.DEFAULT_HEADERS

        if not isinstance(data, str) and headers["Content-Type"] == "application/json":
            data = json.dumps(data)

        if path.startswith("/"):
            path = path[1:]
        request_url = self.url + self.DEFAULT_REST_API_PATH + path

        if self.log_requests or True:
            self.module.log(pformat(dict(url=request_url, data=data, method=method)))

        return request(url=request_url, data=data, method=method, headers=headers, use_proxy=True, force=False, last_mod_time=None,
                       timeout=self.DEFAULT_TIMEOUT, http_agent=self.HTTP_AGENT, force_basic_auth=True, ignore_errors=ignore_errors, **self.creds)


def create_multipart_formdata(files, fields=None, send_8kb=False):
    """Create the data for a multipart/form request."""
    boundary = "---------------------------" + "".join([str(random.randint(0, 9)) for x in range(27)])
    data_parts = list()
    data = None

    if six.PY2:  # Generate payload for Python 2
        newline = "\r\n"
        if fields is not None:
            for key, value in fields:
                data_parts.extend(["--%s" % boundary,
                                   'Content-Disposition: form-data; name="%s"' % key,
                                   "",
                                   value])

        for name, filename, path in files:
            with open(path, "rb") as fh:
                value = fh.read(8192) if send_8kb else fh.read()

                data_parts.extend(["--%s" % boundary,
                                   'Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename),
                                   "Content-Type: %s" % (mimetypes.guess_type(path)[0] or "application/octet-stream"),
                                   "",
                                   value])
        data_parts.extend(["--%s--" % boundary, ""])
        data = newline.join(data_parts)

    else:
        newline = six.b("\r\n")
        if fields is not None:
            for key, value in fields:
                data_parts.extend([six.b("--%s" % boundary),
                                   six.b('Content-Disposition: form-data; name="%s"' % key),
                                   six.b(""),
                                   six.b(value)])

        for name, filename, path in files:
            with open(path, "rb") as fh:
                value = fh.read(8192) if send_8kb else fh.read()

                data_parts.extend([six.b("--%s" % boundary),
                                   six.b('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename)),
                                   six.b("Content-Type: %s" % (mimetypes.guess_type(path)[0] or "application/octet-stream")),
                                   six.b(""),
                                   value])
        data_parts.extend([six.b("--%s--" % boundary), b""])
        data = newline.join(data_parts)

    headers = {
        "Content-Type": "multipart/form-data; boundary=%s" % boundary,
        "Content-Length": str(len(data))}

    return headers, data


def request(url, data=None, headers=None, method='GET', use_proxy=True,
            force=False, last_mod_time=None, timeout=10, validate_certs=True,
            url_username=None, url_password=None, http_agent=None, force_basic_auth=True, ignore_errors=False):
    """Issue an HTTP request to a url, retrieving an optional JSON response."""

    if headers is None:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers.update({"netapp-client-type": "Ansible-%s" % ansible_version})

    if not http_agent:
        http_agent = "Ansible / %s" % ansible_version

    try:
        r = open_url(url=url, data=data, headers=headers, method=method, use_proxy=use_proxy,
                     force=force, last_mod_time=last_mod_time, timeout=timeout, validate_certs=validate_certs,
                     url_username=url_username, url_password=url_password, http_agent=http_agent,
                     force_basic_auth=force_basic_auth)
    except HTTPError as err:
        r = err.fp

    try:
        raw_data = r.read()
        if raw_data:
            data = json.loads(raw_data)
        else:
            raw_data = None
    except Exception:
        if ignore_errors:
            pass
        else:
            raise Exception(raw_data)

    resp_code = r.getcode()

    if resp_code >= 400 and not ignore_errors:
        raise Exception(resp_code, data)
    else:
        return resp_code, data
