NetApp SANtricity Collection
=========

    The NetApp SANtricity collection consist of the latest available versions of the SANtricity modules and roles.
    
    Roles:
        - nar_santricity_host: configures storage pools, volumes, hosts, host groups, and port interfaces
        - nar_santricity_management: manages storage system's name, management interfaces, alerts, syslog, auditlog, asup, ldap, certificates, drive firmware and controller firmware.
            
     Modules:
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

Requirements
------------
    - Ansible 2.8 or later
    - NetApp E-Series E2800 platform or newer or NetApp E-Series SANtricity Web Services Proxy configured for older E-Series Storage arrays.

Instructions
------------
    Install NetApp SANtricity collection on your Ansible management host.

        Using Mazer (Ansible 2.8 or later, experimental):
            mazer install netapp_eseries.santricity

        Using ansible-galaxy (Ansible 2.9 or later):
            ansible-galaxy install netapp_eseries.santricity

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
    BSD

Author Information
------------------
    Nathan Swartz (@ndswartz)
