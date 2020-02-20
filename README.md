NetApp SANtricity Collection
=========

    The NetApp SANtricity collection consist of the latest available versions of the SANtricity modules and roles.
    
    Roles:
        - nar_santricity_common: Discover NetApp E-Series storage systems and configures SANtricity Web Services Proxy.
        - nar_santricity_host: Configure storage pools, volumes, hosts, host groups, and port interfaces
        - nar_santricity_management: Manage storage system's name, management interfaces, alerts, syslog, auditlog, asup, ldap, certificates, drive firmware and controller firmware.
            
     Modules:
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

Requirements
------------
    - Ansible 2.9 or later
    - NetApp E-Series E2800 platform or newer or NetApp E-Series SANtricity Web Services Proxy configured for older E-Series Storage arrays.

Example Playbook
----------------
    - hosts: eseries_storage_systems
      gather_facts: false
      collection:
        - netapp_eseries.santricity
      tasks:
        - name: Ensure all management related policies are enforced
          import_role:
            name: nar_santricity_management
        - name: Ensure all host related policies are enforced
          import_role:
            name: nar_santricity_host

License
-------
    BSD-3-Clause

Author Information
------------------
    Nathan Swartz (@ndswartz)
