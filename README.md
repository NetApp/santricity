NetApp SANtricity Collection
=========

    The NetApp SANtricity collection consist of the latest available versions of the SANtricity modules and roles.
    
    Roles:
        - nar_santricity_host: configures storage pools, volumes, hosts, host groups, and port interfaces
        - nar_santricity_management: manages storage system's name, management interfaces, alerts, syslog, auditlog, asup, ldap, certificates, drive firmware and controller firmware.
            
     Modules:
        - nac_santricity_alerts: manage email notification settings
        - nac_santricity_asup: manage auto-support settings
        - nac_santricity_auditlog: manage audit-log configuration
        - nac_santricity_auth: set or update the password for a storage array
        - nac_santricity_client_certificate: manage remote server certificates
        - nac_santricity_drive_firmware: manage drive firmware
        - nac_santricity_facts: retrieve facts about NetApp E-Series storage arrays
        - nac_santricity_firmware: manage firmware
        - nac_santricity_global: manage global settings configuration
        - nac_santricity_host: manage eseries hosts
        - nac_santricity_hostgroup: manage array host groups
        - nac_santricity_iscsi_interface: manage iSCSI interface configuration
        - nac_santricity_iscsi_target: manage iSCSI target configuration
        - nac_santricity_ldap: manage LDAP integration to use for authentication
        - nac_santricity_lun_mapping: manage lun mappings
        - nac_santricity_mgmt_interface: manage management interface configuration
        - nac_santricity_storage_system: manage SANtricity web services proxy storage arrays
        - nac_santricity_storagepool: manage volume groups and disk pools
        - nac_santricity_syslog: manage syslog settings
        - nac_santricity_volume: manage storage volumes

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