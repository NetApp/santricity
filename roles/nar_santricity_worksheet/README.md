nar_santricity_worksheet
=========

    Generates working NetApp E-Series storage systems inventory structure.

    Items in inventory_builder_arrays_list maybe used to embedded values into strings. For example:
        inventory_builder_array_defaults:
          eseries_api_url: "https://{{ inventory_builder_arrays_list[item]['eseries_management_interfaces']['controller_a'][0]['address'] }}:8443/devmgr/v2"

Requirements
------------
    - Ansible 2.8 or later

Instructions
------------
    1) Use the ansible-galaxy command line tool to install nar_santricity_host role on your Ansible management host.

        Using Mazer (Ansible 2.8 or later, experimental):
            mazer install netapp_eseries.santricity

        Using ansible-galaxy (Ansible 2.9 or later):
            ansible-galaxy install netapp_eseries.santricity

    2) Add your NetApp E-Series storage systems(s) to the Ansible inventory. Copy and modify the example storage array inventory file below or see the example
       inventory files found in this roles examples directory. For the full list variables pertaining to this role, review the role variables section below.

    3) Lastly, add the role to your execution playbook. See the example playbook section below.

Example Playbook
----------------
- hosts: localhost
  gather_facts: false
  collections:
    - netapp_eseries.santricity
  tasks:
    - import_role:
        name: nar_santricity_worksheet
  vars:
    eseries_inventory_file: santricity_inventory
    eseries_playbook_file: santricity_playbook
    eseries_group_name: scratch_pods
    eseries_group_size: 4

    eseries_group_defaults:   # Any common value that should be specified at the top-level E-Series storage array group level.
      eseries_api_url: https://10.113.1.117
      eseries_api_username: admin
      eseries_api_password: admin
      eseries_validate_certs: false
      eseries_ssid: 1

      eseries_asup_state: enabled
      eseries_asup_active: true
      eseries_asup_days:
        - friday
        - saturday
        - sunday
      eseries_asup_start: 17
      eseries_asup_end: 24
      eseries_asup_validate: false
      eseries_asup_method: https
      eseries_asup_routing_type: direct

      eseries_auditlog_enforce_policy: false
      eseries_auditlog_force: true
      eseries_auditlog_full_policy: overWrite
      eseries_auditlog_log_level: writeOnly
      eseries_auditlog_max_records: 10000
      eseries_auditlog_threshold: 80

      eseries_syslog_state: present
      eseries_syslog_address: 10.113.1.117
      eseries_syslog_protocol: udp
      eseries_syslog_port: 514

      #eseries_ldap_state: present
      #eseries_ldap_bind_username: "cn=admin,dc=practice,dc=local"
      #eseries_ldap_bind_password: "admin"
      #eseries_ldap_server: "ldap://10.113.1.254:389"
      #eseries_ldap_search_base: "ou=developers,dc=practice,dc=local"
      #eseries_ldap_role_mappings:
      #  ".*":
      #    - storage.admin
      #    - storage.monitor
      #    - support.admin
      #    - security.admin

      eseries_initiator_protocol: iscsi

      eseries_management_config_method: static
      eseries_management_subnet_mask: 255.255.255.0
      eseries_management_gateway_mask: 10.113.1.1
      eseries_management_dns_config_method: static
      eseries_management_dns_address: 10.192.0.250
      eseries_management_dns_address_backup: 10.193.0.250
      eseries_management_ntp_config_method: static
      eseries_management_ntp_address: 216.239.35.0
      eseries_management_ntp_address_backup: 216.239.35.4
      eseries_management_ssh: true

      eseries_storage_pool_configuration:
        - name: beegfs_storage_vg
          raid_level: raid6
          criteria_drive_count: 10
          criterria_drive_min_size: 500
          criteria_drive_type: hdd
          volumes:
            - name: beegfs_storage_01_[1-4]
              host: beegfs_storage1
              size: 100
              size_unit: gb
              thin_provision: false
              read_cache_enable: false
              read_ahead_enable: true
              write_cache_enable: true
              cache_without_batteries: false
              owning_controller: A
        - name: beegfs_metadata_vg
          raid_level: raid1
          criteria_drive_count: 4
          criteria_drive_type: ssd
          common_volume_configuration:
            workload_name: beegfs_metadata
          volumes:
            - name: beegfs_metadata_01
              host: beegfs_metadata1
              size: 100

      eseries_firmware_firmware: "/home/swartzn/Downloads/RCB_11.40.3R2_280x_5c7d81b3.dlp"
      eseries_firmware_nvsram: "/home/swartzn/Downloads/N280X-842834-D02.dlp"
      eseries_drive_firmware_firmware_list:
        - "/home/swartzn/Downloads/drive firmware/D_PX04SVQ160_DOWNGRADE_MS00toMSB6_801.dlp"
        - "/home/swartzn/Downloads/drive firmware/D_ST1200MM0017_DNGRADE_MS02toMS00_6600_802.dlp"

    eseries_groups:    # List of array group specific values. The dictionary key should be the group name.
      pod_01:
        eseries_group_name: pod_01
      pod_02:
        eseries_group_name: pod_02
      pod_03:
        eseries_group_name: pod_03
      pod_04:
        eseries_group_name: pod_04

    eseries_arrays:    # List of array specific values. The dictionary key should be the array name.
      array_001:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.192
          controller_b:
            - address: 10.113.1.193
      array_002:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.11
          controller_b:
            - address: 10.113.1.12
      array_003:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.184
          controller_b:
            - address: 10.113.1.195
      array_004:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_005:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_006:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_007:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_008:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_009:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_010:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_011:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_012:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29
      array_013:
        eseries_management_interfaces:
          controller_a:
            - address: 10.113.1.28
          controller_b:
            - address: 10.113.1.29

License
-------
    BSD

Author Information
------------------
    Nathan Swartz (@ndswartz)
