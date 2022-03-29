# Nebulon Collection
The Nebulon Collection consists of modules to manage Nebulon
smartInfrastructure and cloud services.

## Requirements
- Ansible 3.0.0 or higher
- Ansible-core 2.10 or higher
- Python 3.6 or higher
- Internet connectivity to https://ucapi.nebcloud.nebuloninc.com/ from host where Ansible is executed
- Nebulon Python SDK 1.0.15

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


## Getting started
To use the Nebulon Ansible modules, install the collection from Ansible
Galaxy or build and install from source code. The recommended installation procedure
to use Ansible Galaxy

### To Install Nebulon Python SDK:
To install the Nebulon Python SDK use the following command:

```
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

```
git clone https://github.com/Nebulon/NebulonON-Collection.git
cd neb-ansible/ansible_collections/nebulon/nebulon_on
ansible-galaxy collection build
```

Then Install the collection from this command:

```
ansible-galaxy collection install nebulon-nebulon_on-{version number}.tar.gz
```
To get the latest version number please refer to galaxy.yml in the source code

### Using collections in a Playbook
Once installed, you can reference a collection content by its fully qualified 
collection name (FQCN). FQCN for the Nebulon Ansible Collection is: nebulon.nebulon_on

```
tasks:
- name: query volumes
  nebulon.nebulon_on.neb_volume_info:
```

## Changelog

### 1.1.1

* Fixed an issue where module `neb_snapshot_template` can properly set arguments (true/false) for the parameter
`ignore_boot_volumes`

### 1.1.0

* Added module `neb_host_info` that returns detailed information for host
* Added module `neb_ntp` that allows configuring SPU NTP server information
* Fixed an issue where module `neb_spu_info` would always default to 
  `false` for parameter `not_in_pod` instead of `None`
  
### 1.0.0 

* Initial release of the Nebulon Ansible Collection

## License
[GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Authors
This collection was created in 2021 by Sarang Nazari, Sepehr Foroughi Shafiei
and Shayan Namaghi and on behalf of, the Nebulon Cloud Team.
