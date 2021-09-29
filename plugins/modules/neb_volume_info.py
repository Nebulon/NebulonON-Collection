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
module: neb_volume_info
short_description: To query nPod volumes
description:
  - This module allows querying multiple nPod volumes.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  volume_name:
    description: Filter based on volume name
    type: str
    required: false
  volume_uuid:
    description: Filter based on volume unique identifier
    type: str
    required: false
  npod_uuid:
    description: Filter based on nPod unique identifier
    type: str
    required: false
  volume_wwn:
    description: Filter based on volume WWN
    type: str
    required: false
  parent_volume_uuid:
    description: Filter based on volume parent uuid
    type: str
    required: false
  base_only:
    description: Filter for only base volumes
    type: bool
    required: false
    default: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Get volume by UUID
  nebulon.nebulon_on.neb_volume_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 4dd60e86-3a8c-47e4-9ca3-0d0364784525
    base_only: true

- name: Get nPod volumes
  nebulon.nebulon_on.neb_volume_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_uuid: 3b79fcc8-ba82-4374-b342-f2ca93641a74

"""

RETURN = r"""
volume:
  description: The detailed information of nPod volumes
  returned: always
  type: list
  elements: dict
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

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import VolumeFilter, StringFilter, UuidFilter, PageInput


def get_volumes(module, client):
    # type: (AnsibleModule, NebPyClient) -> list[dict]
    """Get the nPod volumes that matche the specified filter options"""
    volume_info_list = []
    page_number = 1
    while True:
        volume_list = client.get_volumes(
            page=PageInput(page=page_number),
            volume_filter=VolumeFilter(
                name=StringFilter(
                    equals=module.params['volume_name']
                ),
                and_filter=VolumeFilter(
                    uuid=UuidFilter(
                        equals=module.params['volume_uuid']
                    ),
                    and_filter=VolumeFilter(
                        wwn=StringFilter(
                            equals=module.params['volume_wwn']
                        ),
                        and_filter=VolumeFilter(
                            npod_uuid=UuidFilter(
                                equals=module.params['npod_uuid']
                            ),
                            and_filter=VolumeFilter(
                                parent_uuid=UuidFilter(
                                    equals=module.params['parent_volume_uuid']
                                ),
                                and_filter=VolumeFilter(
                                    base_only=module.params['base_only']
                                )
                            )
                        )
                    )
                )

            )
        )
        for i in range(len(volume_list.items)):
            volume_info_list.append(to_dict(volume_list.items[i]))
        if not volume_list.more:
            break
        page_number += 1
    return volume_info_list


def main():
    module_args = dict(
        npod_uuid=dict(required=False, type='str'),
        volume_name=dict(required=False, type='str'),
        volume_uuid=dict(required=False, type='str'),
        volume_wwn=dict(required=False, type='str'),
        parent_volume_uuid=dict(required=False, type='str'),
        base_only=dict(required=False, type='bool', default=False),
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(
        volumes=[]
    )

    client = get_client(module)

    result['volumes'] = get_volumes(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
