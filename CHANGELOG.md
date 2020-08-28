## [1.0.1] - 2020-03-016
### Added
This release consists of all existing NetApp E-Series Ansible content modified to conform with Ansible collections.

Initial Collection Content:
 - Roles:
    - nar_santricity_common: Discover NetApp E-Series storage systems and configures SANtricity Web Services Proxy.
    - nar_santricity_host: Configure storage pools, volumes, hosts, host groups, and port interfaces. (nar_santricity_common is called at the beginning)
    - nar_santricity_management: Manage storage system's name, management interfaces, alerts, syslog, auditlog, asup, ldap, certificates, drive firmware and
        controller firmware. (nar_santricity_common is called at the beginning)
 - Modules:
    - na_santricity_alerts: Manage email alert notification settings
    - na_santricity_alerts_syslog: Manage syslog servers receiving storage system alerts
    - na_santricity_asup: Manage auto-support settings
    - na_santricity_auditlog: Manage audit-log configuration
    - na_santricity_auth: Set or update the password for a storage array
    - na_santricity_client_certificate: Manage remote server certificates
    - na_santricity_discover: Discover E-Series storage systems on a subnet
    - na_santricity_drive_firmware: Manage drive firmware
    - na_santricity_facts: Retrieve facts about NetApp E-Series storage arrays
    - na_santricity_firmware: Manage firmware
    - na_santricity_global: Manage global settings configuration
    - na_santricity_host: Manage eseries hosts
    - na_santricity_hostgroup: Manage array host groups
    - na_santricity_iscsi_interface: Manage iSCSI interface configuration
    - na_santricity_iscsi_target: Manage iSCSI target configuration
    - na_santricity_ldap: Manage LDAP integration to use for authentication
    - na_santricity_lun_mapping: Manage lun mappings
    - na_santricity_mgmt_interface: Manage management interface configuration
    - na_santricity_storage_system: Manage SANtricity web services proxy storage arrays
    - na_santricity_storagepool: Manage volume groups and disk pools
    - na_santricity_syslog: Manage syslog settings
    - na_santricity_volume: Manage storage volumes
 - Deprecated Modules:
    - netapp_e_alerts: Manage email notification settings
    - netapp_e_amg: Create, remove, and update asynchronous mirror groups
    - netapp_e_amg_role: Update the role of a storage array within an Asynchronous Mirror Group (AMG)
    - netapp_e_amg_sync: Conduct synchronization actions on asynchronous mirror groups
    - netapp_e_asup: Manage auto-support settings
    - netapp_e_auditlog: Manage audit-log configuration
    - netapp_e_auth: Set or update the password for a storage array
    - netapp_e_drive_firmware: Manage drive firmware
    - netapp_e_facts: Retrieve facts about NetApp E-Series storage arrays
    - netapp_e_firmware: Manage firmware
    - netapp_e_flashcache: Manage SSD caches
    - netapp_e_global: Manage global settings configuration
    - netapp_e_hostgroup: Manage eseries hosts
    - netapp_e_host: Manage array host groups
    - netapp_e_iscsi_interface: Manage iSCSI interface configuration
    - netapp_e_iscsi_target: Manage iSCSI target configuration
    - netapp_e_ldap: Manage LDAP integration to use for authentication
    - netapp_e_lun_mapping: Create, delete, or modify lun mappings
    - netapp_e_mgmt_interface: Manage management interface configuration
    - netapp_e_snapshot_group: Manage snapshot groups
    - netapp_e_snapshot_images: Create and delete snapshot images
    - netapp_e_snapshot_volume: Manage snapshot volumes
    - netapp_e_storagepool: Manage volume groups and disk pools
    - netapp_e_storage_system: Manage Web Services Proxy manage storage arrays
    - netapp_e_syslog: Manage syslog settings
    - netapp_e_volume_copy: Create volume copy pairs
