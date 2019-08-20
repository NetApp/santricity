nar_santricity_management
=========

    Manages NetApp E-Series storage system's name, management interfaces, alerts, syslog, auditlog, asup, ldap, certificates, drive firmware and controller firmware.

Requirements
------------
    - Ansible 2.8 or later
    - NetApp E-Series E2800 platform or newer or NetApp E-Series SANtricity Web Services Proxy configured for older E-Series storage systems.

Instructions
------------
    1) Use the ansible-galaxy command line tool to install nar_santricity_management role on your Ansible management host.

        Using Mazer (Ansible 2.8 or later, experimental):
            mazer install netapp_eseries.santricity

        Using ansible-galaxy (Ansible 2.9 or later):
            ansible-galaxy install netapp_eseries.santricity

    2) Add your NetApp E-Series storage systems(s) to the Ansible inventory. Copy and modify the example storage array inventory file below or see the example
       inventory files found in this roles examples directory. For the full list variables pertaining to this role, review the role variables section below.

    3) Lastly, add the role to your execution playbook. See the example playbook section below.

Example Playbook
----------------
    - hosts: eseries_storage_systems
      gather_facts: false             # Fact gathering should be disabled to avoid gathering unnecessary facts about the control node.
      collection:
        - netapp_eseries.santricity
      tasks:
        - name: Ensure NetApp E-Series storage system is properly configured
          import_role:
            name: nar_santricity_management

Example Storage System Inventory File
-------------------------------------
    eseries_ssid: 1
    eseries_api_url: https://192.168.1.7:8443/devmgr/v2
    eseries_api_username: admin
    eseries_api_password: adminpass
    eseries_validate_certs: false

    eseries_system_name: my_eseries_array

    eseries_asup_state: enabled
    eseries_asup_active: true
    eseries_asup_days:
      - sunday
    eseries_asup_start: 17
    eseries_asup_end: 24
    eseries_asup_validate: false
    eseries_asup_method: email
    eseries_asup_email:
      server: smtp.example.com
      sender: noreply@example.com

    eseries_auditlog_enforce_policy: false
    eseries_auditlog_force: true
    eseries_auditlog_full_policy: overWrite
    eseries_auditlog_log_level: writeOnly
    eseries_auditlog_max_records: 10000
    eseries_auditlog_threshold: 80

    eseries_firmware_firmware: "/home/user/Downloads/RCB_11.40.5_280x_5ceef00e.dlp"
    eseries_firmware_nvsram: "/home/user/Downloads/N280X-842834-D02.dlp"
    eseries_drive_firmware_firmware_list:
      - "/home/user/Downloads/drive firmware/D_PX04SVQ160_30603183_MS00_6600_001.dlp"
      - "/home/user/Downloads/drive firmware/D_ST1200MM0017_30602214_MS02_5600_002.dlp"

    eseries_ldap_state: present
    eseries_ldap_bind_username:
    eseries_ldap_bind_password:
    eseries_ldap_server:
    eseries_ldap_search_base:
    eseries_ldap_role_mappings:
      ".*":
        - storage.admin
        - storage.monitor
        - support.admin
        - security.admin

    eseries_management_interfaces:
      config_method: static
      subnet_mask: 255.255.255.0
      gateway: 192.168.1.1
      dns_config_method: static
      dns_address: 192.168.1.253
      dns_address_backup:  192.168.1.254
      ssh: true
      ntp_config_method: static
      ntp_address: 192.168.1.200
      ntp_address_backup: 192.168.1.201
      controller_a:
        - address: 192.168.1.100
        - address: 192.168.1.101
      controller_b:
        - address: 192.168.1.102
        - address: 192.168.1.103

    eseries_syslog_state: present
    eseries_syslog_address: 192.168.1.150
    eseries_syslog_protocol: udp
    eseries_syslog_port: 514

Role Variables
--------------
    # Default storage array credentials for interacting with web services api
    -------------------------------------------------------------------------
    eseries_ssid:               # Storage array identifier. This value will be 1 when interacting with the embedded web services, otherwise the identifier will be
                                     defined on the web services proxy.
    eseries_api_url:            # Url for the web services api. Example: https://192.168.10.100/devmgr/v2
    eseries_api_username:       # Username for the web services api.
    eseries_api_password:       # Password for the web services api.
    eseries_validate_certs:     # Whether the SSL certificates should be verified. (boolean)

    Storage system defaults
    -----------------------------
    eseries_system_name:    # Name of the storage system.

    Storage management interface defaults
    -------------------------------------
    eseries_management_interfaces:
      update_santricity_web_services_proxy:   # Forces the url to be updated in the web services proxy
      config_method:
      subnet_mask:
      gateway_mask:
      dns_config_method:
      dns_address:
      dns_address_backup:
      ntp_config_method:
      ntp_address:
      ntp_address_backup:
      ssh
      controller_a:
        - update_proxy                        # Forces the url to be updated in the web services proxy
          update_inventory_url:               # Forces a dynamic change to the inventory url. Use set_fact and then update line in file???
          config_method:
          address:
          subnet_mask:
          gateway:
          dns_config_method:
          dns_address:
          dns_address_backup:
          ntp_config_method:
          ntp_address:
          ntp_address_backup:
          ssh:
      controller_b:

    # Alerts configuration defaults
    # -----------------------------
    eseries_alerts_state:        # Whether to enable storage system alerts. Choices: enabled, disabled
    eseries_alerts_contact:      # This allows owner to specify free-form contact information such as email or phone number.
    eseries_alerts_recipients:   # List containing e-mails that should be sent notifications when alerts are issued.
    eseries_alerts_sender:       # Sender email. This does not necessarily need to be a valid e-mail.
    eseries_alerts_server:       # Fully qualified domain name, IPv4 address, or IPv6 address of the mail server.
    eseries_alerts_test: false    # When changes are made to the storage system alert configuration a test e-mail will be sent. Choices: true, false

    # LDAP configuration defaults
    # ---------------------------
    eseries_ldap_state:                           # Whether LDAP should be configured
    eseries_ldap_identifier: memberOf             # The user attributes that should be considered for the group to role mapping
    eseries_ldap_user_attribute: sAMAccountName   # Attribute used to the provided username during authentication.
    eseries_ldap_bind_username:                   # User account that will be used for querying the LDAP server.
    eseries_ldap_bind_password:                   # Password for the bind user account
    eseries_ldap_server:                          # LDAP server URL.
    eseries_ldap_search_base:                     # Search base used for find user's group membership
    eseries_ldap_role_mappings:                   # Dictionary of user groups, each containing the list of access roles.
                                                  #     Role choices: storage.admin - allows users full read/writes access to storage objects and operations.
                                                  #                   storage.monitor - allows users read-only access to storage objects and operations.
                                                  #                   storage.admin - allows users access to hardware, diagnostic information, major event logs,
                                                  #                       and other critical support-related functionality, but not the sorage configuration.
                                                  #                   security.admin - allows users access to authentication/authorization configuration, as
                                                  #                       well as the audit log configuration, adn certification management.

    # Drive firmware defaults
    # -----------------------
    eseries_drive_firmware_firmware_list:                     # Local path list for drive firmware.
    eseries_drive_firmware_wait_for_completion: true          # Forces drive firmware upgrades to wait for all associated tasks to complete. Choices: true, false
    eseries_drive_firmware_ignore_inaccessible_drives: false  # Forces drive firmware upgrades to ignore any inaccessible drives. Choices: true, false
    eseries_drive_firmware_upgrade_drives_online: true        # Forces drive firmware upgrades to be performed while I/Os are accepted. Choices: true, false

    # Controller firmware defaults
    # ----------------------------
    eseries_firmware_nvsram:                      # Local path for NVSRAM file.
    eseries_firmware_firmware:                    # Local path for controller firmware file.
    eseries_firmware_wait_for_completion: true    # Forces controller firmware upgrade to wait until upgrade has completed before continuing. Choices: true, false
    eseries_firmware_ignore_health_check: false   # Forces firmware upgrade to be attempted regardless of the health check results. Choices: true, false

    # ASUP configuration defaults
    # ---------------------------
    eseries_asup_state:          # Whether auto support (ASUP) should be enabled. Choices: enabled, disabled
    eseries_asup_active: true    # Enables active monitoring which allows NetApp support personnel to request support data to resolve issues. Choices: true, false
    eseries_asup_days:           # List of days of the week. Choices: monday, tuesday, wednesday, thursday, friday, saturday, sunday
    eseries_asup_start: 0        # Hour of the day(s) to start ASUP bundle transmissions. Start time must be less than end time. Choices: 0-23
    eseries_asup_end: 24         # Hour of the day(s) to end ASUP bundle transmissions. Start time must be less than end time. Choices: 1-24
    eseries_asup_method:         # ASUP delivery method. Choices https, http, email (default: https)
    eseries_asup_routing_type:   # ASUP delivery routing type for https or http. Choices: direct, proxy, script (default: direct)
    eseries_asup_proxy:          # ASUP proxy delivery method information.
      host:                      # ASUP proxy host IP address or FQDN. When eseries_asup_routing_type==proxy this must be specified.
      port:                      # ASUP proxy host port. When eseries_asup_routing_type==proxy this must be specified.
      script:                    # ASUP proxy host script.
    eseries_asup_email:          # ASUP email delivery configuration information
      server:                    # ASUP email server
      sender:                    # ASUP email sender
      test_recipient:            # ASUP configuration mail test recipient
    eseries_asup_validate:       # Verify ASUP configuration prior to applying changes.

    # Audit-log configuration defaults
    # --------------------------------
    eseries_auditlog_enforce_policy: false    # Whether to make audit-log policy changes. Choices: true, false
    eseries_auditlog_force: false             # Forces audit-log to delete log messages when fullness threshold has been exceeded.
                                              #     Applicable when eseries_auditlog_full_policy=preventSystemAccess. Choices: true, false
    eseries_auditlog_full_policy: overWrite   # Policy for what to do when record limit has been reached. Choices: overWrite, preventSystemAccess
    eseries_auditlog_log_level: writeOnly     # Filters logs based on the specified level. Choices: all, writeOnly
    eseries_auditlog_max_records: 50000       # Maximum number of audit-log messages retained. Choices: 100-50000.
    eseries_auditlog_threshold: 90            # Memory full percentage threshold that audit-log will start issuing warning messages. Choices: 60-90

    # Syslog configuration defaults
    # -----------------------------
    eseries_syslog_state:                     # Whether syslog servers should be added or removed from storage system. Choices: present, absent
    eseries_syslog_address:                   # Syslog server IPv4 address or fully qualified hostname.
    eseries_syslog_test: false                # Whether a test messages should be sent to syslog server when added to the storage system. Choices: true, false
    eseries_syslog_protocol: udp              # Protocol to be used when transmitting log messages to syslog server. Choices: udp, tc, tls
    eseries_syslog_port: 514                  # Port to be used when transmitting log messages to syslog server.
    eseries_syslog_components: ["auditLog"]   # List of components log to syslog server. Choices: auditLog, (others may be available)

License
-------
    BSD

Author Information
------------------
    Nathan Swartz (@ndswartz)
