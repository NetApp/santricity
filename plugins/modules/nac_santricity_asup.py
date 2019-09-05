#!/usr/bin/python

# (c) 2018, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1",
                    "status": ["preview"],
                    "supported_by": "community"}

DOCUMENTATION = """
---
module: nac_santricity_asup
short_description: NetApp E-Series manage auto-support settings
description:
    - Allow the auto-support settings to be configured for an individual E-Series storage-system
version_added: "2.7"
author:
    - Michael Price (@lmprice)
    - Nathan Swartz (@ndswartz)
extends_documentation_fragment:
    - netapp_eseries.santricity.santricity.santricity
options:
    state:
        description:
            - Enable/disable the E-Series auto-support configuration.
            - When this option is enabled, configuration, logs, and other support-related information will be relayed
              to NetApp to help better support your system. No personally identifiable information, passwords, etc, will
              be collected.
        default: enabled
        choices:
            - enabled
            - disabled
        aliases:
            - asup
            - auto_support
            - autosupport
    active:
        description:
            - Enable active/proactive monitoring for ASUP. When a problem is detected by our monitoring systems, it"s
              possible that the bundle did not contain all of the required information at the time of the event.
              Enabling this option allows NetApp support personnel to manually request transmission or re-transmission
              of support data in order ot resolve the problem.
            - Only applicable if I(state=enabled).
        default: yes
        type: bool
    start:
        description:
            - A start hour may be specified in a range from 0 to 23 hours.
            - ASUP bundles will be sent daily between the provided start and end time (UTC).
            - I(start) must be less than I(end).
        aliases:
            - start_time
        default: 0
    end:
        description:
            - An end hour may be specified in a range from 1 to 24 hours.
            - ASUP bundles will be sent daily between the provided start and end time (UTC).
            - I(start) must be less than I(end).
        aliases:
            - end_time
        default: 24
    days:
        description:
            - A list of days of the week that ASUP bundles will be sent. A larger, weekly bundle will be sent on one
              of the provided days.
        choices:
            - monday
            - tuesday
            - wednesday
            - thursday
            - friday
            - saturday
            - sunday
        required: no
        aliases:
            - days_of_week
            - schedule_days
    method:
        description:
            - AutoSupport dispatch delivery method.
        choices:
            - https
            - http
            - email
        type: str
        required: false
        default: https
    routing_type:
        description:
            - AutoSupport routing
            - Required when M(method==https or method==http).
        choices:
            - direct
            - proxy
            - script
        type: str
        default: direct
        required: false
    proxy:
        description:
            - Information particular to the proxy delivery method.
            - Required when M((method==https or method==http) and routing_type==proxy).
        type: dict
        required: false
        suboptions:
            host:
                description:
                    - Proxy host IP address or fully qualified domain name.
                    - Required when M(routing_type==proxy) and M(.
                type: str
                required: false
            port:
                description:
                    - Proxy host port.
                    - Required when M(routing_type==proxy).
                type: str
                required: false
            script:
                description:
                    - Path to the AutoSupport routing script file.
                    - Required when M(routing_type==script) and M(.
                type: str
                required: false
    email:
        description:
            - Information particular to the e-mail delivery method.
            - Uses the SMTP protocol.
            - Required when M(method==email).
        type: dict
        required: false
        suboptions:
            server:
                description:
                    - Mail server's IP address or fully qualified domain name.
                    - Required when M(routing_type==email).
                type: str
                required: false
            sender:
                description:
                    - Sender's email account
                    - Required when M(routing_type==email).
                type: str
                required: false
            test_recipient:
                description:
                    - Test verification email
                    - Required when M(routing_type==email).
                type: str
                required: false
    validate:
        description:
            - Validate ASUP configuration.
        type: bool
        default: false
        required: false
notes:
    - Check mode is supported.
    - Enabling ASUP will allow our support teams to monitor the logs of the storage-system in order to proactively
      respond to issues with the system. It is recommended that all ASUP-related options be enabled, but they may be
      disabled if desired.
    - This API is currently only supported with the Embedded Web Services API v2.0 and higher.
"""

EXAMPLES = """
    - name: Enable ASUP and allow pro-active retrieval of bundles
      nac_santricity_asup:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        state: enabled
        active: yes

    - name: Set the ASUP schedule to only send bundles from 12 AM CST to 3 AM CST.
      nac_santricity_asup:
        ssid: "1"
        api_url: "https://192.168.1.100:8443/devmgr/v2"
        api_username: "admin"
        api_password: "adminpass"
        validate_certs: true
        start: 17
        end: 20
"""

RETURN = """
msg:
    description: Success message
    returned: on success
    type: str
    sample: The settings have been updated.
asup:
    description:
        - True if ASUP is enabled.
    returned: on success
    sample: True
    type: bool
active:
    description:
        - True if the active option has been enabled.
    returned: on success
    sample: True
    type: bool
cfg:
    description:
        - Provide the full ASUP configuration.
    returned: on success
    type: complex
    contains:
        asupEnabled:
            description:
                    - True if ASUP has been enabled.
            type: bool
        onDemandEnabled:
            description:
                    - True if ASUP active monitoring has been enabled.
            type: bool
        daysOfWeek:
            description:
                - The days of the week that ASUP bundles will be sent.
            type: list
"""
from ansible_collections.netapp_eseries.santricity.plugins.module_utils.santricity import NetAppESeriesModule
from ansible.module_utils._text import to_native


class NetAppESeriesAsup(NetAppESeriesModule):
    DAYS_OPTIONS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    def __init__(self):
        ansible_options = dict(
            state=dict(type="str", required=False, default="enabled", aliases=["asup", "auto_support", "autosupport"], choices=["enabled", "disabled"]),
            active=dict(type="bool", required=False, default=True, ),
            days=dict(type="list", required=False, aliases=["schedule_days", "days_of_week"], choices=self.DAYS_OPTIONS),
            start=dict(type="int", required=False, default=0, aliases=["start_time"]),
            end=dict(type="int", required=False, default=24, aliases=["end_time"]),
            method=dict(type="str", required=False, choices=["https", "http", "email"], default="https"),
            routing_type=dict(type="str", required=False, choices=["direct", "proxy", "script"], default="direct"),
            proxy=dict(type="dict", required=False, options=dict(host=dict(type="str", required=False),
                                                                 port=dict(type="str", required=False),
                                                                 script=dict(type="str", required=False))),
            email=dict(type="dict", required=False, options=dict(server=dict(type="str", required=False),
                                                                 sender=dict(type="str", required=False),
                                                                 test_recipient=dict(type="str", required=False))),
            validate=dict(type="bool", require=False, default=False))

        mutually_exclusive = [["host", "script"],
                              ["port", "script"]]

        required_if = [["method", "https", ["routing_type"]],
                       ["method", "http", ["routing_type"]],
                       ["method", "email", ["email"]]]

        super(NetAppESeriesAsup, self).__init__(ansible_options=ansible_options,
                                                web_services_version="02.00.0000.0000",
                                                mutually_exclusive=mutually_exclusive,
                                                required_if=required_if,
                                                supports_check_mode=True)

        args = self.module.params
        self.asup = args["state"] == "enabled"
        self.active = args["active"]
        self.days = args["days"]
        self.start = args["start"]
        self.end = args["end"]

        self.method = args["method"]
        self.routing_type = args["routing_type"] if args["routing_type"] else "none"
        self.proxy = args["proxy"]
        self.email = args["email"]
        self.validate = args["validate"]

        if self.validate and self.email and "test_recipient" not in self.email.keys():
            self.module.fail_json(msg="test_recipient must be provided for validating email delivery method. Array [%s]" % self.ssid)

        self.check_mode = self.module.check_mode

        if self.start >= self.end:
            self.module.fail_json(msg="The value provided for the start time is invalid."
                                      " It must be less than the end time.")
        if self.start < 0 or self.start > 23:
            self.module.fail_json(msg="The value provided for the start time is invalid. It must be between 0 and 23.")
        else:
            self.start = self.start * 60
        if self.end < 1 or self.end > 24:
            self.module.fail_json(msg="The value provided for the end time is invalid. It must be between 1 and 24.")
        else:
            self.end = min(self.end * 60, 1439)

        if not self.days:
            self.days = self.DAYS_OPTIONS

        # Check whether request needs to be forwarded on to the controller web services rest api.
        self.url_path_prefix = ""
        if not self.is_embedded() and self.ssid != 0:
            self.url_path_prefix = "storage-systems/%s/forward/devmgr/v2/" % self.ssid

    def get_configuration(self):
        try:
            (rc, result) = self.request(self.url_path_prefix + "device-asup")

            if not (result["asupCapable"] and result["onDemandCapable"]):
                self.module.fail_json(msg="ASUP is not supported on this device. Array Id [%s]." % self.ssid)
            return result

        except Exception as err:
            self.module.fail_json(msg="Failed to retrieve ASUP configuration! Array Id [%s]. Error [%s]." % (self.ssid, to_native(err)))

    def update_configuration(self):
        config = self.get_configuration()
        update = False
        body = dict()

        if self.asup:
            body = dict(asupEnabled=True)
            if not config["asupEnabled"]:
                update = True

            if (config["onDemandEnabled"] and config["remoteDiagsEnabled"]) != self.active:
                update = True
                body.update(dict(onDemandEnabled=self.active,
                                 remoteDiagsEnabled=self.active))
            self.days.sort()
            config["schedule"]["daysOfWeek"].sort()

            body["schedule"] = dict(daysOfWeek=self.days,
                                    dailyMinTime=self.start,
                                    dailyMaxTime=self.end,
                                    weeklyMinTime=self.start,
                                    weeklyMaxTime=self.end)

            if self.days != config["schedule"]["daysOfWeek"]:
                update = True
            if self.start != config["schedule"]["dailyMinTime"] or self.start != config["schedule"]["weeklyMinTime"]:
                update = True
            elif self.end != config["schedule"]["dailyMaxTime"] or self.end != config["schedule"]["weeklyMaxTime"]:
                update = True

            if self.method in ["https", "http"]:
                if self.routing_type == "direct":
                    body["delivery"] = dict(method=self.method,
                                            routingType="direct")
                elif self.routing_type == "proxy":
                    body["delivery"] = dict(method=self.method,
                                            proxyHost=self.proxy["host"],
                                            proxyPort=self.proxy["port"],
                                            routingType="proxyServer")
                elif self.routing_type == "script":
                    body["delivery"] = dict(method=self.method,
                                            proxyScript=self.proxy["script"],
                                            routingType="proxyScript")

            else:
                body["delivery"] = dict(method="smtp",
                                        mailRelayServer=self.email["server"],
                                        mailSenderAddress=self.email["sender"],
                                        routingType="none")

            if config["delivery"]["method"] != body["delivery"]["method"]:
                update = True
            elif config["delivery"]["method"] in ["https", "http"]:
                if config["delivery"]["routingType"] != body["delivery"]["routingType"]:
                    update = True
                elif (config["delivery"]["routingType"] == "proxy" and
                      config["delivery"]["proxyHost"] != body["delivery"]["proxyHost"] and
                      config["delivery"]["proxyPort"] != body["delivery"]["proxyPort"]):
                    update = True
                elif config["delivery"]["routingType"] == "script" and config["delivery"]["proxyScript"] != body["delivery"]["proxyScript"]:
                    update = True
            elif (config["delivery"]["method"] == "smtp" and
                  config["delivery"]["mailRelayServer"] != body["delivery"]["mailRelayServer"] and
                  config["delivery"]["mailSenderAddress"] != body["delivery"]["mailSenderAddress"]):
                update = True

        elif config["asupEnabled"]:     # Disable asupEnable is asup is disabled.
            body = dict(asupEnabled=False)
            update = True

        if update and not self.check_mode:

            if body["asupEnabled"] and self.validate:
                validate_body = dict(delivery=body["delivery"])
                if self.email:
                    validate_body["mailReplyAddress"] = self.email["test_recipient"]

                try:
                    rc, response = self.request(self.url_path_prefix + "device-asup/verify-config", method="POST", data=validate_body)
                except Exception as err:
                    self.module.fail_json(msg="We failed to verify ASUP configuration! Array Id [%s]. Error [%s]."
                                              % (self.ssid, to_native(err)))

            try:
                rc, response = self.request(self.url_path_prefix + "device-asup", method="POST", data=body)
            # This is going to catch cases like a connection failure
            except Exception as err:
                self.module.fail_json(msg="We failed to set the storage-system name! Array Id [%s]. Error [%s]." % (self.ssid, to_native(err)))

        return update

    def apply(self):
        update = self.update_configuration()
        cfg = self.get_configuration()

        if update:
            self.module.exit_json(msg="The ASUP settings have been updated.", changed=update, asup=cfg["asupEnabled"], active=cfg["onDemandEnabled"], cfg=cfg)
        else:
            self.module.exit_json(msg="No ASUP changes required.", changed=update, asup=cfg["asupEnabled"], active=cfg["onDemandEnabled"], cfg=cfg)


if __name__ == "__main__":
    asup = NetAppESeriesAsup()
    asup.apply()
