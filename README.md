# Nebulon Collection

The Nebulon Collection consists of modules to manage Nebulon
smartInfrastructure and cloud services.

## Requirements

- Ansible 3.0.0 or higher
- Ansible-core 2.10 or higher
- Python 3.6 or higher
- Internet connectivity to <https://ucapi.nebcloud.nebuloninc.com/> from host where Ansible is executed
- Nebulon Python SDK 2.0.8

## Available modules

- neb_claim_spu - To claim or release a SPU
- neb_clone - To create or delete a volume clone
- neb_lun - To create or delete a LUN
- neb_npod - To create or delete a nPod
- neb_npod_info - To retrieve a list of provisioned nPods
- neb_npod_template - To create or delete a nPod template
- neb_npod_template_info - To query nPod templates
- neb_snapshot - To create or delete a volume snapshot
- neb_snapshot_template - To create or delete a snapshot schedule template
- neb_snapshot_template_info - To query snapshot schedule templates
- neb_spu_info - To query details of Nebulon SPUs
- neb_update - To update SPU firmware
- neb_user - To create, modify or delete a Nebulon ON user
- neb_user_group - To create, modify or delete a Nebulon ON user group
- neb_user_group_info - To query Nebulon ON user groups
- neb_user_info - To query Nebulon ON users
- neb_volume - To create or delete a nPod volume
- neb_volume_info - To query nPod volumes
- neb_npod_group - To create, modify or delete a Nebulon nPod group
- neb_npod_group_info - To query Nebulon ON nPod groups
- neb_host_info - To query information on hosts
- neb_ntp - To set NTP server configuration

### Support for module_defaults

All modules in the Nebulon collections require you to specify a user name and password. These
are provided through the `neb_username` and `neb_password` parameters in each module. To simplify
authoring of playbooks, the module defines the action group `nebulon`, so that you can use the
`module_defaults` functionality. For example:

```yaml
---
- name: Example playbook
  hosts: localhost
  connection: local
  module_defaults:
    group/nebulon.nebulon_on.nebulon:
      neb_username: your_username
      neb_password: your_password

  tasks:
    - name: Step 1
      nebulon.nebulon_on.neb_npod_group:
        name: group_name
        state: present
```

## Getting started

To use the Nebulon Ansible modules, install the collection from Ansible
Galaxy or build and install from source code. The recommended installation procedure
to use Ansible Galaxy

### To Install Nebulon Python SDK

To install the Nebulon Python SDK use the following command:

```bash
python3 -m pip install -r requirements.txt
```

Refer to Nebulon [Python SDK installation](https://nebulon.github.io/nebpyclient/installation.html)
page for more detail.

### Installation of Collections using Ansible Galaxy

The easiest way to get started by use of ansible-galaxy. Use the following
command to install the latest collection:

```shell
ansible-galaxy collection install nebulon.nebulon_on -p ~/.ansible/collections
```

### Building from source

Use the following command to build the Nebulon Collection from source code.

```bash
git clone https://github.com/Nebulon/NebulonON-Collection.git
cd neb-ansible/ansible_collections/nebulon/nebulon_on
ansible-galaxy collection build
```

Then Install the collection from this command:

```bash
ansible-galaxy collection install nebulon-nebulon_on-{version number}.tar.gz
```

To get the latest version number please refer to galaxy.yml in the source code

### Using collections in a Playbook

Once installed, you can reference a collection content by its fully qualified
collection name (FQCN). FQCN for the Nebulon Ansible Collection is: nebulon.nebulon_on

```yaml
tasks:
- name: query volumes
  nebulon.nebulon_on.neb_volume_info:
```

### Tutorial

For more detail information and how to use Nebulon Ansible Collection please refer to
our tutorial page at [Nebulon Ansible Tutorial](https://on.nebulon.com/docs/en-us/tutorials/tutorial-ansible/8041667baadd168c8333f3aa991637c1)

## Changelog

### 1.4.0

- Introduced a new `neb_capacity_info` module that allows automation users to query volumes, SPUs,
  and nPods for capacity information.
- Introduced a new `neb_vcenter` module that allows configuring the vCenter integration for nPods.

### 1.3.0

- Introduced a new `neb_volume_access` module that simplifies the process of managing access to volumes
  by hosts in a nPod. This module replaces the deprecated `neb_lun` module.

- __Deprecated__ the `neb_lun` module. This module will be removed on October 1st 2022.

- Introduced a new `neb_host` module that allows configuration of host (server) properties,
  including host display name and note.

### 1.2.4

- Updated the requirements.txt information to match latest dependencies for the Ansible Collection

### 1.2.3

- Updated formatting of client version string for nebpyclient to better represent the collection version
  information in the nebulon ON audit log.

### 1.2.2

- Added `neb_spu_lookup` lookup plugin that gets SPU configuration information from your inventory and
  converts it to a structure that can be passed to the `neb_npod` module when creating a new nPod

### 1.2.1

- Added support for `module_defaults` using the action group `nebulon.nebulon_on.nebulon` to simplify providing
  credentials to the modules provided by this collection
  
### 1.2.0

Moved Nebulon Ansible collection from Nebulon Python SDK 1.0.15 to 2.0.8

- Added Three more optional filters to module `neb_npod_template_info` for looking up nPod templates.
  - `os` - string type filter based on nPod template operating system name
  - `app` - string type filter based on nPod template application name
  - `only_last_version` - boolean type filter based on their latest version
- Added two more optional inputs to module `neb_user` for adding, deleting and modifying Nebulon users
  - `time_zone` - string type filter based on user's time zone
  - `send_notification` - string type filter based on the user's notification preferences for alerts
    - Choices:
      - `Daily`
      - `Disabled`
      - `Instant`
- Added optional filters to module `neb_volume_info` for looking up nPod volumes
  - `sync_state` - string type filter based on volume synchronization status
    - Choices:
      - `InSync`
      - `NotMirrored`
      - `Syncing`
      - `Unknown`
      - `Unsynced`
      - `All`

### 1.1.2

- Added compatibility check for Nebulon SDK and Python to `login_utils`

### 1.1.1

- Fixed an issue where module `neb_snapshot_template` can properly set arguments (true/false) for the parameter
`ignore_boot_volumes`

### 1.1.0

- Added module `neb_host_info` that returns detailed information for host
- Added module `neb_ntp` that allows configuring SPU NTP server information
- Fixed an issue where module `neb_spu_info` would always default to
  `false` for parameter `not_in_pod` instead of `None`
  
### 1.0.0

- Initial release of the Nebulon Ansible Collection

## License

[GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Authors

This collection was created in 2021 by Sarang Nazari, Sepehr Foroughi Shafiei,
Shayan Namaghi, and Tobias Flitsch on behalf of the Nebulon Cloud Team.
