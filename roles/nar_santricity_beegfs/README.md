nar_santricity_beegfs
=========

    Configures BeeGFS parallel file system with NetApp E-Series storage systems.

Requirements
------------

    - Ansible 2.5 or later
    - NetApp E-Series E2800 platform or newer or NetApp E-Series SANtricity Web Services Proxy configured for older E-Series Storage arrays.

Instructions
------------
    1) Use the ansible-galaxy command line tool to install nar_santricity_beegfs role on your Ansible management host.

          ansible-galaxy install netapp_eseries.nar_santricity_beegfs

    2) Add your NetApp E-Series storage systems(s) and BeeGFS hosts to the Ansible inventory. Copy and modify the example storage array inventory file below.
       For the full list variables pertaining to this role, review the role variables section below.

    3) Lastly, add the role to your execution playbook. See the example playbook section below.

Example Playbook
----------------
    - hosts: eseries_beegfs_hosts
      tasks:
      - name: Configure BeeGFS on beegfs hosts
        import_role:
          name: netapp_eseries.nar_santricity_beegfs
         
Example Storage System Inventory File
-------------------------------------
    eseries_api_url: https://192.168.1.7:8443/devmgr/v2/    # SANtricity Web Service REST API url
    eseries_api_username: admin                             # Storage system username and password
    eseries_api_password: mypass
    eseries_validate_certs: no                              # Forces SSL certificate certification
          
Example BeeGFS host using E-Series Storage inventory file
---------------------------------------------------------
    beegfs_eseries_group: eseries_arrays        # Ansible inventory group or explicit list of E-Series storage systems.
    beegfs_mgmt_node_ip: 192.168.1.100          # BeeGFS nanagement node address
    beegfs_ntp_enabled: true                    # Forces ntp to be configured. *Note, this will uninstall Chrony if it exists.
    beegfs_connInterfaces:                      # List of beegfs interfaces for beegfs traffic
      - ens192
    beegfs_node_roles:                          # List of beegfs roles. Choices: management, storage, metadata, client
      - management
      - storage
      - metadata
      - client
      
Role Variables
--------------
    # For complete variable list and definitions, see defaults/main.yml file.

    beegfs_eseries_group:           # Ansible inventory group or list that contains E-Series storage systems pertaining to BeeGFS host.

    beegfs_open_firewall_ports:     # Ensures firewall ports are open on all BeeGFS nodes
    beegfs_enable_rdma: False       # Ensures remote direct memory access (RDMA) is enabled on metadata and storage nodes.
    beegfs_ofed_include_path:       # Define path to the infiniband OFED include directory if not using default kernel infiniband modules.
    
    # BeeGFS volume formatting options
    beegfs_segment_size: 128k
    beegfs_stripe_count: 8
    
    # BeeGFS Quota Configuration - WARNING: For existing installations you must manually enable/disable quotas before changing these values (see "Special Considerations" in the README).
    beegfs_enable_quota: False
    beegfs_quota_enable_enforcement: False
    
    beegfs_ntp_enabled: True        # Enables NTP service on all BeeGFS nodes.
    beegfs_ntp_configuration_file:  # NTP.conf location
    beegfs_ntp_server_pools:        # NTP server pools
    beegfs_ntp_restricts:           # List of ip or hostnames to restrict the NTP service from using.
      
    # Below are the BeeGFS rpm and deb repository urls 
    beegfs_repository_rpm_base_url:
    beegfs_repository_rpm_gpgkey:
    beegfs_repository_deb_base_url:
    beegfs_repository_deb_gpgkey:
    
    # BeeGFS service file locations
    beegfs_redhat_service_path:
    beegfs_debian_service_path:
    
    # BeeGFS default configuration directory locations
    beegfs_configuration_directory:
    beegfs_data_directory:
    
Special Considerations
------------
Enabling Quota Support: 
* There are two parameters that control BeeGFS quota functionality, beegfs_enable_quota (quota tracking) and beegfs_quota_enable_enforcement (quota enforcement).
* When initially deploying a new filesystem, these parameters can be used to deploy with quota support enabled.
* When adding support to an existing installation, please follow the official BeeGFS procedures to manually enable quotas (https://www.beegfs.io/wiki/EnableQuota) before toggling these parameters. 
  * After manually enabling quotas on the filesystem, you must toggle one or both parameters to "True" before running the role.
  * During the first run after enabling quota support, you may notice "changed" logged for the following tasks: 
    * The tasks that populate service configuration files due to how Ansible determines changes between files (or subtle difference in the config templates/actual file).
    * The task responsible for mounting BeeGFS storage targets, especially if /etc/fstab was not updated with the new mount options.
    
Enabling NTP:
* Time synchronization is required for BeeGFS to function properly.
* When beegfs_ntp_enabled set to true, nar_santricity_beegfs will ensure NTP service maintains all BeeGFS management, metadata, storage, and clients nodes.
* Chrony will conflict with NTP and will be removed when beegfs_ntp_enabled == True.   
         
License
-------

BSD

Author Information
------------------

Joe McCormick (@iamjoemccormick)
Nathan Swartz (@ndswartz)
