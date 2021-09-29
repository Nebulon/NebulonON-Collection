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
module: neb_clone
short_description: To create or delete a volume clone
description:
  - This module allows creating or delting volume clones.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  volume_uuid:
    description: >-
      The unique identifier for the volume or snapshot from which to create the
      clone
    type: str
    required: true
  name:
    description: The human readable name for the volume clone
    type: str
    required: true
  state:
    description: Defines the intended state for the clone
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new clone
  nebulon.nebulon_on.neb_clone:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 889d9290-8477-4a7c-a4a1-8528c98d4282
    name: my_volume_clone
    state: present

- name: Delete existing clone
  nebulon.nebulon_on.neb_clone:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 889d9290-8477-4a7c-a4a1-8528c98d4282
    name: my_volume_clone
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import Volume, VolumeFilter, StringFilter, UuidFilter


def get_clone(module, client, clone_name, parent_volume_uuid):
    # type: (AnsibleModule, NebPyClient, str, str) -> Volume
    """Get the volume clone that matches the specified name and parent volume UUID"""
    volume_list = client.get_volumes(
        volume_filter=VolumeFilter(
            uuid=UuidFilter(
                equals=parent_volume_uuid
            )
        )
    )
    if volume_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one volume with UUID: {parent_volume_uuid}'.")
    elif volume_list.filtered_count == 0:
        module.fail_json(
            msg=f"Could not find volume with UUID: {parent_volume_uuid}'.")

    parent_volume = volume_list.items[0]

    clone_list = client.get_volumes(
        volume_filter=VolumeFilter(
            name=StringFilter(
                equals=clone_name
            ),
            and_filter=VolumeFilter(
                npod_uuid=UuidFilter(
                    equals=parent_volume.npod_uuid
                )
            )
        )
    )
    if clone_list.filtered_count > 1:
        module.fail_json(msg=f"Found more than one clone with name {clone_name} for volume {parent_volume_uuid}")
    elif clone_list.filtered_count == 1:
        return clone_list.items[0]


def delete_clone(module, client, clone_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a clone"""

    result = dict(
        changed=False
    )
    try:
        client.delete_volume(clone_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_clone(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating volume clone"""
    result = dict(
        changed=False,
    )
    try:
        client.create_clone(
            name=module.params['name'],
            volume_uuid=module.params['volume_uuid']
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        volume_uuid=dict(required=True, type='str'),
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

    clone = get_clone(
        module, client, module.params['name'], module.params['volume_uuid'])

    if module.params['state'] == 'absent':
        if clone is not None:
            result = delete_clone(module, client, clone.uuid)
    elif module.params['state'] == 'present':
        if clone is None:
            result = create_clone(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
