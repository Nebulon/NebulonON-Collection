#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2021 Nebulon, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: neb_volume
short_description: To create or delete a nPod volume
description:
  - This module allows creating or deleting a nPod volume.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: The name for the volume
    type: str
    required: true
  npod_uuid:
    description: The uuid of the nPod in which to create the volume
    type: str
    required: true
  size:
    description: The size of the volume in bytes
    type: int
    required: false
  mirrored:
    description: Indicates if the volume shall be created with high availability
    type: bool
    default: true
    required: false
  owner_spu_serial:
    description: Create the volume on the SPU indicated with this serial number
    type: str
    required: false
  backup_spu_serial:
    description: 'If the volume is mirrored, create a mirror on the specified SPU'
    type: str
    required: false
  force:
    description: Forces the creation of the volume and ignores any warnings
    type: bool
    default: false
    required: false
  state:
    description: Defines the intended state for the nPod volume
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new volume
  nebulon.nebulon_on.neb_volume:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: volume_name
    npod_uuid: c481d4e0-e00d-474b-9d5e-abfb1adcd59e
    size: 1000000000000
    mirrored: false
    owner_spu_serial: 01234567890
    state: present

- name: Create a new mirrored volume
  nebulon.nebulon_on.neb_volume:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: volume_name
    npod_uuid: c481d4e0-e00d-474b-9d5e-abfb1adcd59e
    size: 1000000000000
    mirrored: true
    owner_spu_serial: 01234567890
    backup_spu_serial: 01234567891
    force: false
    state: present

- name: Delete existing volume
  nebulon.nebulon_on.neb_volume:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: volume_name
    npod_uuid: c481d4e0-e00d-474b-9d5e-abfb1adcd59e
    state: absent
"""

RETURN = r"""
volume:
  description: The detailed information of a nPod Volume
  returned: always
  type: dict
  contains:
    uuid:
      description: The unique identifier of the volume
      type: str
      returned: always
    npod_uuid:
      description: The unique identifier of the nPod for this volume
      type: str
      returned: always
    wwn:
      description: The world wide name of the volume
      type: str
      returned: always
    name:
      description: The name for the volume
      type: str
      returned: always
    size_bytes:
      description: The size of the volume in bytes
      type: int
      returned: always
    creation_time:
      description: Date and time when the volume was created
      type: str
      returned: always
    expiration_time:
      description: Date and time when the snapshot is automatically deleted
      type: str
      returned: always
    read_only_snapshot:
      description: Indicates if the volume is a read-only snapshot
      type: bool
      returned: always
    snapshot_parent_uuid:
      description: Indicates the parent volume of a snapshot
      type: str
      returned: always
    snapshot_uuids:
      description: List of unique identifiers or snapshots from this volume
      type: list
      elements: str
      returned: always
    natural_owner_host_uuid:
      description: The uuid of the current host / server owner of a volume
      type: str
      returned: always
    natural_backup_host_uuid:
      description: The uuid of the host / server that is the natural backup
      type: str
      returned: always
    natural_owner_spu_serial:
      description: The serial number of the SPU that is the natural owner
      type: str
      returned: always
    natural_backup_spu_serial:
      description: The serial number of the SPU that is the natural backup
      type: str
      returned: always
    current_owner_host_uuid:
      description: The uuid of the current host / server owner of a volume
      type: str
      returned: always
    accessible_by_host_uuids:
      description: List of host / server uuids that have access to the volume
      type: list
      elements: str
      returned: always
    sync_state:
      description: Indicates the health and sync state of the volume
      type: str
      returned: always
    boot:
      description: Indicates if the volume is a boot volume
      type: str
      returned: always
    lun_uuids:
      description: List of uuids for all LUNs created for the volume
      type: list
      elements: str
      returned: always
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    to_dict,
    validate_sdk,
)

# safe import of the Nebulon Python SDK
try:
    from nebpyclient import (
        NebPyClient,
        Volume,
        VolumeFilter,
        StringFilter,
        UUIDFilter,
        CreateVolumeInput,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def get_volume(module, client, volume_name, npod_uuid):
    # type: (AnsibleModule, NebPyClient, str, str) -> Volume
    """Get the nPod volume that matches the specified name and npod UUID"""
    volume_list = client.get_volumes(
        volume_filter=VolumeFilter(
            name=StringFilter(
                equals=volume_name
            ),
            and_filter=VolumeFilter(
                npod_uuid=UUIDFilter(
                    equals=npod_uuid
                )
            )
        )
    )
    if volume_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one volume with name {volume_name}"
        )
    elif volume_list.filtered_count == 1:
        return volume_list.items[0]


def delete_volume(module, client, volume_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a volume"""
    result = dict(
        changed=False
    )
    try:
        client.delete_volume(volume_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_volume(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating a new volume"""
    result = dict(
        changed=False,
        volume=None,
    )
    try:
        new_volume = client.create_volume(
            create_volume_input=CreateVolumeInput(
                name=module.params['name'],
                size_bytes=module.params['size'],
                npod_uuid=module.params['npod_uuid'],
                mirrored=module.params['mirrored'],
                owner_spu_serial=module.params['owner_spu_serial'],
                backup_spu_serial=module.params['backup_spu_serial'],
                force=module.params['force'],
            )
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['volume'] = to_dict(new_volume)
    return result


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        npod_uuid=dict(required=True, type='str'),
        size=dict(required=False, type='int'),
        mirrored=dict(required=False, type='bool', default=True),
        owner_spu_serial=dict(required=False, type='str'),
        backup_spu_serial=dict(required=False, type='str'),
        force=dict(required=False, type='bool', default=False),
        state=dict(required=True, choices=['present', 'absent'])
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(
        changed=False
    )

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    client = get_client(module)

    volume = get_volume(
        module,
        client,
        module.params['name'],
        module.params['npod_uuid']
    )

    if module.params['state'] == 'absent':
        if volume is not None:
            result = delete_volume(module, client, volume.uuid)
    elif module.params['state'] == 'present':
        if volume is None:
            result = create_volume(module, client)
        else:
            result['volume'] = to_dict(volume)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
