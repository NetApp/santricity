## [1.0.0] - 2019-09-01
### Added
This release consists of all existing NetApp E-Series Ansible content modified to conform with Ansible collections.

Notes:
- nar_santricity prefix indicates Ansible roles
- na_santricity prefix indicates Ansible community supported
- All modules will be treated as new modules, although core functionality will be consistent with the existing netapp_e modules.

Initial Collection Content:
- Roles:
    - nar_santricity_host: configures storage pools, volumes, hosts, host groups, and port interfaces
    - nar_santricity_management: manages storage system's name, management interfaces, alerts, syslog, auditlog, asup, ldap, certificates, drive firmware
      and controller firmware.
        
- Modules:
    - na_santricity_alerts: manage email notification settings
    - na_santricity_asup: manage auto-support settings
    - na_santricity_auditlog: manage audit-log configuration
    - na_santricity_auth: set or update the password for a storage array
    - na_santricity_client_certificate: manage remote server certificates
    - na_santricity_drive_firmware: manage drive firmware
    - na_santricity_facts: retrieve facts about NetApp E-Series storage arrays
    - na_santricity_firmware: manage firmware
    - na_santricity_global: manage global settings configuration
    - na_santricity_host: manage eseries hosts
    - na_santricity_hostgroup: manage array host groups
    - na_santricity_iscsi_interface: manage iSCSI interface configuration
    - na_santricity_iscsi_target: manage iSCSI target configuration
    - na_santricity_ldap: manage LDAP integration to use for authentication
    - na_santricity_lun_mapping: manage lun mappings
    - na_santricity_mgmt_interface: manage management interface configuration
    - na_santricity_storage_system: manage SANtricity web services proxy storage arrays
    - na_santricity_storagepool: manage volume groups and disk pools
    - na_santricity_syslog: manage syslog settings
    - na_santricity_volume: manage storage volumes