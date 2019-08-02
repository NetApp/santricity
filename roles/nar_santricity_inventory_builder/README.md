nar_santricity_inventory_builder
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
      gather_facts: false   # Fact gathering should be disabled to avoid gathering unnecessary facts about the control node.
      collection:
        - netapp_eseries.santricity
      tasks:
      - name: Ensure NetApp E-Series storage system is properly configured
        import_role:
          name: nar_santricity_inventory_builder

Example Storage System Inventory File
-------------------------------------
# Exclude .yml extensions from all file names. They will be added during templating
inventory_builder_inventory_file: santricity_inventory
inventory_builder_group_name: scratch_pods
inventory_builder_group_size: 4

# Group information defaults
# --------------------------
inventory_builder_group_defaults:    # List of group key-value pairs included at the group level.

# Storage array defaults
# ----------------------
inventory_builder_array_defaults:    # List of group key-value pairs included at the array level.

# Group inventory list containing specific group inventory information
# --------------------------------------------------------------------
inventory_builder_group_list:
  pod_01:
    test_value1: 1
    test_value2: 2
  pod_02:
    test_value1: 3
    test_value2: 4
  pod_03:
    test_value1: 5
    test_value2: 6

# Array inventory list containing specific array inventory information
# --------------------------------------------------------------------
inventory_builder_array_list:
  array_001:
    eseries_management_interfaces:
      controller_a:
        - address: 192.168.1.100
      controller_b:
        - address: 192.168.1.102
  array_002:
    eseries_management_interfaces:
      controller_a:
        - address: 192.168.1.104
      controller_b:
        - address: 192.168.1.106

License
-------
    BSD

Author Information
------------------
    Nathan Swartz (@ndswartz)
