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
module: neb_snapshot
short_description: To create or delete a volume snapshots
description:
  - This module allows creating or delting volume snapshots.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  volume_uuids:
    description: List of unique identifiers for all volumes for which to create a snapshot
    type: list
    elements: str
    required: true
  name_patterns:
    description:
      - List of naming patterns for volume snapshots
      - >-
        Options of the ``strftime`` function are available to format time and
        the variable `%v` that will be translated to the volume name.
    type: list
    elements: str
    required: false
  expiration_seconds:
    description: >-
      The number of seconds after snapshot creation when the snapshots will be
      automatically deleted
    type: int
    required: false
  retention_seconds:
    description: The number of seconds before a user can delete the snapshots
    type: int
    required: false
  snapshot_uuid:
    description: >-
      The unique identifier of the snapshot to delete,  Used only where 'state'
      is 'absent'
    type: str
    required: false
  state:
    description: Defines the intended state for the snapshot(s)
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new snapshot
  nebulon.nebulon_on.neb_snapshot:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuids:
      - 889d9290-8477-4a7c-a4a1-8528c98d4282
    name_patterns:
      - '%v_%y-%m-%d_%H:%M_ANS'
    expiration_seconds: 3600
    retention_seconds: 3600
    state: present

- name: Delete existing snapshot
  nebulon.nebulon_on.neb_snapshot:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    snapshot_uuid: 6bbc874d-b849-4b04-8354-ff9e2b5ebbb5
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import Volume, VolumeFilter, UUIDFilter


def get_snapshot(module, client, snapshot_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> Volume
    """Get the volume snapshot that matches the specified UUID"""
    snapshot_list = client.get_volumes(
        volume_filter=VolumeFilter(
            uuid=UUIDFilter(
                equals=snapshot_uuid
            )
        )
    )
    if snapshot_list.filtered_count > 1:
        module.fail_json(
            msg="Found more than one snapshot with UUID: '" + str(snapshot_uuid) + "'.")
    elif snapshot_list.filtered_count == 1:
        return snapshot_list.items[0]


def delete_snapshot(module, client, snapshot_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a snapshot"""
    result = dict(
        changed=False
    )
    try:
        client.delete_volume(snapshot_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_snapshot(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating snapshots"""
    result = dict(
        changed=False,
    )
    try:
        client.create_snapshot(
            parent_volume_uuids=module.params['volume_uuids'],
            name_patterns=module.params['name_patterns'],
            expiration_seconds=module.params['expiration_seconds'],
            retention_seconds=module.params['retention_seconds']
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def main():
    module_args = dict(
        volume_uuids=dict(required=True, type='list', elements='str'),
        snapshot_uuid=dict(required=False, type='str'),
        name_patterns=dict(required=False, type='list', elements='str'),
        expiration_seconds=dict(required=False, type='int'),
        retention_seconds=dict(required=False, type='int'),
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

    client = get_client(module)

    if module.params['state'] == 'absent':
        snapshot = get_snapshot(module, client, module.params['snapshot_uuid'])
        if snapshot is not None:
            result = delete_snapshot(
                module, client, module.params['snapshot_uuid'])
    elif module.params['state'] == 'present':
        result = create_snapshot(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
