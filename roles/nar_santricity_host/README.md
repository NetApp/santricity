nar_santricity_host
=========
    Configures storage pools, volumes, hosts, host groups, and port interfaces for NetApp E-Series storage arrays
    using iSCSI, FC, SAS, IB, NVMe protocols.

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
      - name: Ensure NetApp E-Series storage system is properly configured
        import_role:
          name: nar_santricity_host

Example Storage System Inventory File (Discover storage system with proxy)
-------------------------------------
    eseries_system_serial: "012345678901"   # Be sure to quote if the serial is all numbers and begins with zero.
    eseries_system_password: admin_password
    eseries_proxy_api_url: https://192.168.1.100:8443/devmgr/v2/
    eseries_proxy_api_password: admin_password
    eseries_subnet: 192.168.1.0/24
    eseries_prefer_embedded: true
    eseries_validate_certs: false

    eseries_initiator_protocol: iscsi

    # Controller port definitions
    eseries_controller_port_config_method: static
    eseries_controller_port_subnet_mask: 255.255.255.0
    eseries_controller_port:
      controller_a:
        ports:
          - address: 192.168.2.100
          - address: 192.168.2.110
      controller_b:
        ports:
          - address: 192.168.3.100
          - address: 192.168.3.110

    # Storage pool and volume configuration
    eseries_storage_pool_configuration:
      - name: pool[1-2]
        raid_level: raid6
        criteria_drive_count: 10
        volumes:
          - name: "[pool]_volume[A-C]"
            host: server_group
            size: 4096

Example Storage System Inventory File (Without storage system discovery)
-------------------------------------
    eseries_system_api_url: https://192.168.1.200:8443/devmgr/v2/
    eseries_system_password: admin_password
    eseries_validate_certs: false

    (...)   # Same as the previous example

Role Variables
--------------
**Note that when values are specified below, they indicate the default value.**

    # Web Services Embedded information
    eseries_subnet:                   # Network subnet to search for the storage system specified in CIDR form. Example: 192.168.1.0/24
    eseries_system_serial:            # Storage system serial number. Be sure to quote if the serial is all numbers and begins with zero. (This is located
                                      #     on a label at the top-left towards the front on the device)
    eseries_system_addresses:         # Storage system management IP addresses. Only required when eseries_system_serial or eseries_system_api_url are not
                                      #     defined. When not specified, addresses will be populated with eseries_management_interfaces controller addresses.
    eseries_system_api_url:           # Url for the storage system's for embedded web services rest api. Example: https://192.168.10.100/devmgr/v2
    eseries_system_username: admin    # Username for the storage system's for embedded web services rest api
    eseries_system_password:          # Password for the storage system's for embedded web services rest api and when the admin password has not been set
                                      #     eseries_system_password will be used to set it.
    eseries_proxy_ssid:               # Arbitrary string for the proxy to represent the storage system. eseries_system_serial will be used when not defined.
    eseries_template_api_url:         # Template for the web services api url. Default: https://0.0.0.0:8443/devmgr/v2/
    eseries_prefer_embedded: false    # Overrides the default behavior of using Web Services Proxy when eseries_proxy_api_url is defined. This will only effect storage systems that have Embedded Web Services.
    eseries_validate_certs: true      # Indicates Whether SSL certificates should be verified. Used for both embedded and proxy. Choices: true, false

    # Web Services Proxy information
        Note: eseries_proxy_* variables are required to discover storage systems prior to SANtricity OS version 11.60.2.
    eseries_proxy_api_url:         # Url for the storage system's for proxy web services rest api. Example: https://192.168.10.100/devmgr/v2
    eseries_proxy_api_username:    # Username for the storage system's for proxy web services rest api.
    eseries_proxy_api_password:    # Password for the storage system's for proxy web services rest api and when the admin password has not been set
                                   #     eseries_proxy_api_password will be used to set it.

    # Controller iSCSI Interface Port Default Policy Specifications
    eseries_controller_iscsi_port_state: enabled         # Generally specifies whether a controller port definition should be applied Choices: enabled, disabled
    eseries_controller_iscsi_port_config_method: dhcp    # General port configuration method definition for both controllers. Choices: static, dhcp
    eseries_controller_iscsi_port_gateway:               # General port IPv4 gateway for both controllers.
    eseries_controller_iscsi_port_subnet_mask:           # General port IPv4 subnet mask for both controllers.
    eseries_controller_iscsi_port_mtu: 9000              # General port maximum transfer units (MTU) for both controllers. Any value greater than 1500 (bytes).
    eseries_controller_iscsi_port:
      controller_a:         # Ordered list of controller A channel definition.
        - state:            # Whether the port should be enabled. Choices: enabled, disabled
          config_method:    # Port configuration method Choices: static, dhcp
          address:          # Port IPv4 address
          gateway:          # Port IPv4 gateway
          subnet_mask:      # Port IPv4 subnet_mask
          mtu:              # Port IPv4 mtu
      controller_b:         # Ordered list of controller B channel definition.
        - (...)             # Same as controller A but for controller B

    # Controller InfiniBand iSER Interface Channel
    eseries_controller_ib_iser_port:
      controller_a:    # Ordered list of controller A channel address definition.
        -              # Port IPv4 address for channel 1
        - (...)        # So on and so forth
      controller_b:    # Ordered list of controller B channel address definition.

    # Controller NVMe over InfiniBand Interface Channel
    eseries_controller_nvme_ib_port:
      controller_a:    # Ordered list of controller A channel address definition.
        -              # Port IPv4 address for channel 1
        - (...)        # So on and so forth
      controller_b:    # Ordered list of controller B channel address definition.

    # Controller NVMe RoCE Interface Port Default Policy Specifications
    eseries_controller_nvme_roce_port_state: enabled         # Generally specifies whether a controller port definition should be applied Choices: enabled, disabled
    eseries_controller_nvme_roce_port_config_method: dhcp    # General port configuration method definition for both controllers. Choices: static, dhcp
    eseries_controller_nvme_roce_port_gateway:               # General port IPv4 gateway for both controllers.
    eseries_controller_nvme_roce_port_subnet_mask:           # General port IPv4 subnet mask for both controllers.
    eseries_controller_nvme_roce_port_mtu: 9000              # General port maximum transfer units (MTU). Any value greater than 1500 (bytes).
    eseries_controller_nvme_roce_port_speed: auto            # General interface speed. Value must be a supported speed or auto for automatically negotiating the speed with the port.
    eseries_controller_nvme_roce_port:
      controller_a:         # Ordered list of controller A channel definition.
        - state:            # Whether the port should be enabled.
          config_method:    # Port configuration method Choices: static, dhcp
          address:          # Port IPv4 address
          subnet_mask:      # Port IPv4 subnet_mask
          gateway:          # Port IPv4 gateway
          mtu:              # Port IPv4 mtu
          speed:            # Port IPv4 speed
      controller_b:         # Ordered list of controller B channel definition.
        - (...)             # Same as controller A but for controller B

    # Target discovery specifications
        Note: add the following to ansible-playbook command to update the chap secret: --extra-vars "eseries_target_chap_secret_update=True
    eseries_target_name:                        # iSCSI target name that will be seen by the initiator
    eseries_target_ping: True                   # Enables ICMP ping response from the configured iSCSI ports (boolean)
    eseries_target_unnamed_discovery: True      # Whether the iSCSI target iqn should be returned when an initiator performs a discovery session.
    eseries_target_chap_secret:                 # iSCSI chap secret. When left blank, the chap secret will be removed from the storage system.
    eseries_target_chap_secret_update: False    # DO NOT REMOVE! Since na_santricity_iscsi_target cannot compare the chap secret with the current and chooses to always
                                                #     return changed=True, this flag is used to force the module to update the chap secret. It is preferable to
                                                #     leave this value False and to add the --extra-vars "eseries_target_chap_secret_update=True".

    # Storage Pool Default Policy Specifications
    eseries_storage_pool_state: present                   # Default storage pool state. Choices: present, absent
    eseries_storage_pool_raid_level: raidDiskPool         # Default volume raid level. Choices: raid0, raid1, raid5, raid6, raidDiskPool
    eseries_storage_pool_secure_pool: false               # Default for storage pool drive security. This flag will enable the security at rest feature. There
                                                          #    must be sufficient FDE or FIPS security capable drives. Choices: true, false
    eseries_storage_pool_criteria_drive_count:            # Default storage pool drive count.
    eseries_storage_pool_reserve_drive_count:             # Default reserve drive count for drive reconstruction for storage pools using dynamic disk pool and
                                                          #    the raid level must be set for raidDiskPool.
    eseries_storage_pool_criteria_min_usable_capacity:    # Default minimum required capacity for storage pools.
    eseries_storage_pool_criteria_drive_type:             # Default drive type for storage pools. Choices: hdd, ssd
    eseries_storage_pool_criteria_size_unit: gb           # Default unit size for all storage pool related sizing.
                                                          #    Choices: bytes, b, kb, mb, gb, tb, pb, eb, zb, yb
    eseries_storage_pool_criteria_drive_min_size:         # Default minimum drive size for storage pools.
    eseries_storage_pool_criteria_drive_require_da:       # Default for whether storage pools are required to have data assurance (DA) compatible drives.
                                                          #    Choices: true, false
    eseries_storage_pool_criteria_drive_require_fde:      # Default for whether storage pools are required to have drive security compatible drives.
                                                          #    Choices: true, false
    eseries_storage_pool_remove_volumes:                  # Default policy for deleting volumes prior to removing storage pools.
    eseries_storage_pool_erase_secured_drives:            # Default policy for erasing the content drives during create and delete storage pool operations.
                                                          #    Choices: true, false

    # Volume Default Policy Specifications
    eseries_volume_state: present                         # Default volume state. Choices: present, absent
    eseries_volume_size_unit: gb                          # Default unit size for all volume sizing options.
    eseries_volume_size:                                  # Default volume size or the presented size for thinly provisioned volumes.
    eseries_volume_data_assurance_enabled:                # Default for whether data assurance(DA) is required to be enabled.
    eseries_volume_segment_size_kb:                       # Default segment size measured in kib.
    eseries_volume_read_cache_enable:                     # Default for read caching which will cache all read requests.
    eseries_volume_read_ahead_enable:                     # Default for read ahead caching; this is good for sequential workloads to cache subsequent blocks.
    eseries_volume_write_cache_enable:                    # Default for write caching which will cache all writes.
    eseries_volume_cache_without_batteries:               # Default for allowing caching when batteries are not present.
    eseries_volume_thin_provision:                        # Default for whether volumes should be thinly provisioned.
    eseries_volume_thin_volume_repo_size:                 # Default for actually allocated space for thinly provisioned volumes.
    eseries_volume_thin_volume_max_repo_size:             # Default for the maximum allocated space allowed for thinly provisioned volumes.
    eseries_volume_thin_volume_expansion_policy:          # Default thin volume expansion policy. Choices: automatic, manual
    eseries_volume_thin_volume_growth_alert_threshold:    # Default thin volume growth alert threshold; this is the threshold for when the thin volume expansion
                                                          #    policy will be enacted. Allowable values are between and including 10% and 99%
    eseries_volume_ssd_cache_enabled:                     # Default for ssd cache which will enable the volume to use an existing SSD cache on the storage array.
    eseries_volume_host:                                  # Default host for all volumes; the value can be any host from the Ansible inventory. Any initiator may be
                                                          #    used whether connected or not since the storage array does not require connectivity in order to create
                                                          #    host objects.
    eseries_volume_workload_name:                         # Default workload tag name
    eseries_volume_metadata:                              # Default metadata
    eseries_volume_owning_controller                      # Default preferred owning controller
    eseries_volume_wait_for_initialization: false         # Default for whether volume creation with wait for initialization to complete

    # Storage Pool-Volume Mapping Default Policy Specifications
    # ---------------------------------------------------------
    eseries_lun_mapping_state: present    # Generally specifies whether a LUN mapping should be present. This is useful when adding a default host for all
                                          #    volumes. Choices: present, absent
    eseries_lun_mapping_host:             # Default host for all volumes not specifically give a host either in common_volume_configuration or in
                                          #    eseries_storage_pool_configuration.

    # Storage Pool-Volume Default Policy Specifications
       Name schemes: Storage pool and volume names can be used to specify a naming scheme to produce a list of storage pools and volumes. The scheme are defined by
                     brackets and can be used to specify a range of lowercase letters, uppercase letters, range of single digit numbers, any top-level inventory
                     variables, and the current defined storage pool (volume only).
    eseries_storage_pool_configuration:
      - name:                                      # Name or name scheme (see above) for the storage pool.
        state:                                     # Specifies whether the storage pool should exist (present, absent). When removing an existing storage array all of the
                                                   #    volumes must be defined with state=absent.
        raid_level                                 # Volume group raid level. Choices: raid0, raid1, raid5, raid6, raidDiskPool (Default: raidDiskPool)
        secure_pool:                               # Default for storage pool drive security. This flag will enable the security at rest feature. There must be sufficient FDE
                                                   #    or FIPS security capable drives. Choices: true, false
        criteria_drive_count:                      # Default storage pool drive count.
        reserve_drive_count:                       # Default reserve drive count for drive reconstruction for storage pools using dynamic disk pool and the raid level must be
                                                   #    set for raidDiskPool.
        criteria_min_usable_capacity:              # Default minimum required capacity for storage pools.
        criteria_drive_type:                       # Default drive type for storage pools. Choices: hdd, ssd
        criteria_size_unit:                        # Default unit size for all storage pool related sizing. Choices: bytes, b, kb, mb, gb, tb, pb, eb, zb, yb
        criteria_drive_min_size:                   # Default minimum drive size for storage pools.
        criteria_drive_require_da:                 # Default for whether storage pools are required to have data assurance (DA) compatible drives. Choices: true, false
        criteria_drive_require_fde:                # Default for whether storage pools are required to have drive security compatible drives. Choices: true, false
        remove_volumes:                            # Default policy for deleting volumes prior to removing storage pools.
        erase_secured_drives:                      # Default policy for erasing the content drives during create and delete storage pool operations. Choices: true, false
        common_volume_configuration:               # Any option that can be specified at the volume level can be generalized here at the storage pool level. This is useful when
                                                   #    all volumes share common configuration definitions.
        volumes:                                   # List of volumes associated the storage pool.
          - state:                                 # Specifies whether the volume should exist (present, absent)
            name:                                  # (required) Name or name scheme (see above) for the volume(s) to be created in the storage pool(s)
            host:                                  # host or host group for the volume should be mapped to.
            host_type:                             # Only required when using something other than Linux kernel 3.10 or later with DM-MP (Linux DM-MP),
                                                   #     non-clustered Windows (Windows), or the storage system default host type is incorrect. Common definitions below:
                                                   #     - AIX MPIO: The Advanced Interactive Executive (AIX) OS and the native MPIO driver
                                                   #     - AVT 4M: Silicon Graphics, Inc. (SGI) proprietary multipath driver; refer to the SGI installation documentation for more information
                                                   #     - HP-UX: The HP-UX OS with native multipath driver
                                                   #     - Linux ATTO: The Linux OS and the ATTO Technology, Inc. driver (must use ATTO FC HBAs)
                                                   #     - Linux DM-MP: The Linux OS and the native DM-MP driver
                                                   #     - Linux Pathmanager: The Linux OS and the SGI proprietary multipath driver; refer to the SGI installation documentation for more information
                                                   #     - Mac: The Mac OS and the ATTO Technology, Inc. driver
                                                   #     - ONTAP: FlexArray
                                                   #     - Solaris 11 or later: The Solaris 11 or later OS and the native MPxIO driver
                                                   #     - Solaris 10 or earlier: The Solaris 10 or earlier OS and the native MPxIO driver
                                                   #     - SVC: IBM SAN Volume Controller
                                                   #     - VMware: ESXi OS
                                                   #     - Windows: Windows Server OS and Windows MPIO with a DSM driver
                                                   #     - Windows Clustered: Clustered Windows Server OS and Windows MPIO with a DSM driver
                                                   #     - Windows ATTO: Windows OS and the ATTO Technology, Inc. driver
            size:                                  # Size of the volume or presented size of the thinly provisioned volume.
            size_unit:                             # Unit size for the size, thin_volume_repo_size, and thin_volume_max_repo_size
                                                   #    Choices: bytes, b, kb, mb, gb, tb, pb, eb, zb, yb
            segment_size_kb:                       # Indicates the amount of data stored on a drive before moving on to the next drive in the volume group. Does not apply to pool volumes.
            thin_provision:                        # Whether volumes should be thinly provisioned.
            thin_volume_repo_size:                 # Actually allocated space for thinly provisioned volumes.
            thin_volume_max_repo_size:             # Maximum allocated space allowed for thinly provisioned volumes.
            thin_volume_expansion_policy:          # Thin volume expansion policy. Choices: automatic, manual
            thin_volume_growth_alert_threshold:    # Thin volume growth alert threshold; this is the threshold for when the thin volume expansion
                                                   #    policy will be enacted. Allowable values are between and including 10% and 99%
            ssd_cache_enabled:                     # Enables ssd cache which will enable the volume to use an existing SSD cache on the storage array.
            data_assurance_enabled:                # Enables whether data assurance(DA) is required to be enabled.
            read_cache_enable:                     # Enables read caching which will cache all read requests.
            read_ahead_enable:                     # Enables read ahead caching; this is good for sequential workloads to cache subsequent blocks.
            write_cache_enable:                    # Enables write caching which will cache all writes.
            workload_name:                         # Name of the volume's workload. This can be defined using the metadata option or, if already defined, specify one already
                                                   #    created on the storage array.
            metadata:                              # Dictionary containing arbitrary entries normally used for defining the volume(s) workload.
            wait_for_initialization:               # Whether volume creation with wait for initialization to complete

    # Initiator-Target Protocol Variable Defaults
        Note that the following commands need to produce a unique list of IQNs or WWNs of the interfaces used, line separated. Overwrite as necessary.
    eseries_initiator_protocol: fc     # This variable defines which protocol the storage array will use. Choices: fc, iscsi, sas, ib_iser, ib_srp, nvme_ib, nvme_roce
    eseries_initiator_command:
      fc:
        linux: "systool -c fc_host -v | grep port_name | cut -d '\"' -f 2 | cut -d 'x' -f 2 | sort | uniq"
        windows: "(Get-InitiatorPort | Where-Object -P ConnectionType -EQ 'Fibre Channel' | Select-Object -Property PortAddress |
                   Format-Table -AutoSize -HideTableHeaders | Out-String).trim()"
      iscsi:
        linux: "grep -o iqn.* /etc/iscsi/initiatorname.iscsi"
        windows: "(get-initiatorPort | select-object -property nodeaddress | sort-object | get-unique | ft -autoSize | out-string -stream |
                   select-string iqn | out-string).trim()"
      sas:
        # NetApp IMT for SAS attached E-Series SAN hosts recommends adding all possible SAS addresses with the base address
        # starting at 0, and the last address ending in 3 for single port HBAs, or 7 for dual port HBAs. Since determining
        # single vs . dual port HBAs adds complexity, we always add all 8 possible permutations of the SAS address.
        linux: "systool -c scsi_host -v | grep host_sas_address | cut -d '\"' -f 2 | cut -d 'x' -f 2 | sort | uniq"
        windows: "(Get-InitiatorPort | Where-Object -P ConnectionType -EQ 'SAS' | Select-Object -Property PortAddress |
                   Format-Table -AutoSize -HideTableHeaders | Out-String).trim()"
      ib_iser:
        linux: "grep -o iqn.* /etc/iscsi/initiatorname.iscsi"
        windows: ""   # add windows command for determining host iqn address(es)
      ib_srp:
        linux: "ibstat -p"
        windows: ""     # Add Windows command for determining host guid
      nvme_ib:
        linux: ""       # Add Linux command for determining host nqn address(es)
        windows: ""     # Add Windows command for determining host nqn address(es)
      nvme_roce:
        linux: ""       # Add Linux command for determining host nqn address(es)
        windows: ""     # Add Windows command for determining host nqn address(es)

    # Manual host definitions, Linux and Windows systems can be automatically populated based on host mappings found in eseries_storage_pool_configuration
    eseries_host_force_port: true                 # Default for whether ports are to be allowed to be re-assigned (boolean)
    eseries_host_remove_unused_hostgroup: true    # Forces any unused groups to be removed
    eseries_host_object:
      - name:         # Host label as referenced by the storage array.
        state:        # Specifies whether host definition should be exist. Choices: present, absent
        ports:        # List of port definitions
          - type:     # Port protocol definition (iscsi, fc, sas, ib, nvme). Note that you should use 'iscsi' prior to Santricity version 11.60 for IB iSER.
            label:    # Arbitrary port label
            port:     # Port initiator (iqn, wwn, etc)
        group:        # Host's host group
        host_type:    # Only required when using something other than Linux kernel 3.10 or later with DM-MP (Linux DM-MP),
                      #     non-clustered Windows (Windows), or the storage system default host type is incorrect. Common definitions below:
                      #     - AIX MPIO: The Advanced Interactive Executive (AIX) OS and the native MPIO driver
                      #     - AVT 4M: Silicon Graphics, Inc. (SGI) proprietary multipath driver; refer to the SGI installation documentation for more information
                      #     - HP-UX: The HP-UX OS with native multipath driver
                      #     - Linux ATTO: The Linux OS and the ATTO Technology, Inc. driver (must use ATTO FC HBAs)
                      #     - Linux DM-MP: The Linux OS and the native DM-MP driver
                      #     - Linux Pathmanager: The Linux OS and the SGI proprietary multipath driver; refer to the SGI installation documentation for more information
                      #     - Mac: The Mac OS and the ATTO Technology, Inc. driver
                      #     - ONTAP: FlexArray
                      #     - Solaris 11 or later: The Solaris 11 or later OS and the native MPxIO driver
                      #     - Solaris 10 or earlier: The Solaris 10 or earlier OS and the native MPxIO driver
                      #     - SVC: IBM SAN Volume Controller
                      #     - VMware: ESXi OS
                      #     - Windows: Windows Server OS and Windows MPIO with a DSM driver
                      #     - Windows Clustered: Clustered Windows Server OS and Windows MPIO with a DSM driver
                      #     - Windows ATTO: Windows OS and the ATTO Technology, Inc. driver

License
-------
    BSD-3-Clause

Author Information
------------------
    Nathan Swartz (@ndswartz)
