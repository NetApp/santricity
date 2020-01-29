## [0.1.0] - 2020-02-01
### Added
This release consists of all existing NetApp E-Series Ansible content modified to conform with Ansible collections.

Initial Collection Content:
- Roles:
    - nar_santricity_host: Manages NetApp E-Series storage system's interfaces, storage pools, volumes, hosts, hostgroups, and volume mappings.
    - nar_santricity_management: Manages NetApp E-Series storage system's firmware, management interfaces, security, system, and logging configuration.
        
- Modules:
    - na_santricity_alerts: manage system notification 
    - na_santricity_alerts_syslog: manage syslog servers for system alert notifications
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
    - na_santricity_ib_iser_interface: manage InfiniBand iSER interfaces
    - na_santricity_iscsi_interface: manage iSCSI interfaces
    - na_santricity_iscsi_target: manage iSCSI target configuration
    - na_santricity_ldap: manage LDAP integration to use for authentication
    - na_santricity_lun_mapping: manage lun mappings
    - na_santricity_mgmt_interface: manage management interfaces
    - na_santricity_nvme_interface: manage NVMe interfaces
    - na_santricity_proxy_drive_firmware_upload: manage SANtricity web services proxy available drive firmware
    - na_santricity_proxy_firmware_upload: manage SANtricity web services proxy available firmware
    - na_santricity_proxy_systems: manage SANtricity web services proxy storage systems
    - na_santricity_storagepool: manage storage pools
    - na_santricity_syslog: manage syslog settings
    - na_santricity_volume: manage storage volumes