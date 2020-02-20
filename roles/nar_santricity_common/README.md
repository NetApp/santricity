nar_santricity_common
=====================
    Discover NetApp E-Series storage systems and configures SANtricity Web Services Proxy.

    The following variables with be added to the runtime host inventory.
        current_eseries_api_url:            # Web Services REST API URL
        current_eseries_api_username:       # Web Services REST API username
        current_eseries_api_password:       # Web Services REST API password
        current_eseries_ssid:               # Arbitrary string for the proxy to represent the storage system.
        current_eseries_validate_certs:     # Indicates whether SSL certificates should be verified.
        current_eseries_api_is_proxy:       # Indicates whether Web Services REST API is running on a proxy.

Requirements
------------
    - Ansible 2.9 or later
    - NetApp E-Series E2800 platform or newer or NetApp E-Series SANtricity Web Services Proxy configured for older E-Series storage systems.

Example Playbook
----------------
    - hosts: eseries_storage_systems
      gather_facts: false
      collection:
        - netapp_eseries.santricity
      tasks:
        - name: Configure SANtricity Web Services and discover storage systems 
          import_role:
            name: nar_santricity_common

Example Inventory Host file using discovery
-------------------------------------------
    eseries_subnet: 192.168.1.0/24
    eseries_validate_certs: false
    eseries_system_serial: "012345678901"   # Be sure to quote if the serial is all numbers and begins with zero.
    eseries_system_password: admin_password
    eseries_proxy_api_url: https://192.168.1.100:8443/devmgr/v2/
    eseries_proxy_api_password: admin_password

Example Inventory Host file without using discovery
---------------------------------------------------
    eseries_system_api_url: https://192.168.1.200:8443/devmgr/v2/
    eseries_system_password: admin_password
    eseries_validate_certs: false

Role Variables
--------------
    eseries_subnet:                       # Network subnet to search for the storage system specified in CIDR form. Example: 192.168.1.0/24
    eseries_template_api_url:             # Template for the web services api url. Default: https://0.0.0.0:8443/devmgr/v2/
    eseries_validate_certs:               # Indicates Whether SSL certificates should be verified. Used for both embedded and proxy. Choices: true, false

    # Storage system specific variables
    eseries_proxy_ssid:                   # Arbitrary string for the proxy to represent the storage system. eseries_system_serial will be used when not defined.
    eseries_system_serial:                # Storage system serial number. Be sure to quote if the serial is all numbers and begins with zero. (This is located on a label at the top-left towards the front on the device)
    eseries_system_addresses:             # Storage system management IP addresses. Only required when eseries_system_serial or eseries_system_api_url are not defined. When not specified, addresses will be populated with eseries_management_interfaces controller addresses.
    eseries_system_api_url:               # Url for the storage system's for embedded web services rest api. Example: https://192.168.10.100/devmgr/v2
    eseries_system_username:              # Username for the storage system's for embedded web services rest api
    eseries_system_password:              # Password for the storage system's for embedded web services rest api and when the admin password has not been set eseries_system_password will be used to set it.
    eseries_system_tags:                  # Meta tags to associate with storage system when added to the proxy.

    # Storage system management interface information
        Note: eseries_management_interfaces will be used when eseries_system_serial, eseries_system_api_url, or eseries_system_addresses are not defined.
    eseries_management_interfaces:        # Subset of the eseries_management_interface variable found in the nar_santricity_management role
      controller_a:
        - address:                        # Controller A port 1's IP address
        - address:                        # Controller A port 2's IP address
      controller_b:
        - address:                        # Controller B port 1's IP address
        - address:                        # Controller B port 2's IP address

    # Web Services Proxy specific variable
        Note: eseries_proxy_* variables are required to discover storage systems prior to SANtricity OS version 11.60.2.
    eseries_proxy_api_url:                # Url for the storage system's for proxy web services rest api. Example: https://192.168.10.100/devmgr/v2
    eseries_proxy_api_username:           # Username for the storage system's for proxy web services rest api.
    eseries_proxy_api_password:           # Password for the storage system's for proxy web services rest api and when the admin password has not been set eseries_proxy_api_password will be used to set it.
    eseries_proxy_monitor_password:       # Proxy password for the monitor username
    eseries_proxy_security_password:      # Proxy password for the security username
    eseries_proxy_storage_password:       # Proxy password for the monitor username
    eseries_proxy_support_password:       # Proxy password for the support username
    eseries_proxy_accept_certifications:  # Force automatic acceptance of all storage system's certificate
    eseries_proxy_default_system_tags:    # Default meta tags to associate with all storage systems
    eseries_proxy_default_password:       # Default password to associate with all storage systems. This is overridden by eseries_system_password.

License
-------
    BSD-3-Clause

Author Information
------------------
    Nathan Swartz (@ndswartz)