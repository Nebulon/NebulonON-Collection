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
module: neb_npod_group
short_description: To create/modify/delete a Nebulon ON nPod group
description:
  - >-
    This module manages the lifecycle (create, modify and delete) a Nebulon ON
    nPod group.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: The name of the new nPod group
    type: str
    required: true
  note:
    description: An optional note for the nPod group
    type: str
    required: false
  state:
    description: Defines the intended state for the nPod group
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new nPod group
  nebulon.nebulon_on.neb_npod_group:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
    note: note
    state: present

- name: Delete existing nPod group
  nebulon.nebulon_on.neb_npod_group:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
    state: absent

- name: Modify existing nPod group
  nebulon.nebulon_on.neb_npod_group:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
    note: new_note
    state: present

"""

RETURN = r"""
npod_group:
    description: The detailed information of a nPod group
    returned: if present
    type: dict
    contains:
        uuid:
            description: The unique identifier of the nPod group
            type: str
            returned: always
        name:
            description: The name of the nPod group
            type: str
            returned: always
        note:
            description: An optional note for the nPod group
            type: str
            returned: always
        npod_uuids:
            description: List of nPod unique identifiers in this nPod group
            type: list
            elements: str
            returned: always
        npod_count:
            description: Number of nPods in this nPod group
            type: int
            returned: always
        host_count:
            description: Number of hosts (servers) in this nPod group
            type: int
            returned: always
        spu_count:
            description: Number of services processing units in this nPod group
            type: int
            returned: always
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import NPodGroup, NPodGroupFilter, StringFilter, CreateNPodGroupInput, UpdateNPodGroupInput


def get_npod_group(module, client, group_name):
    # type: (AnsibleModule, NebPyClient, str) -> NPodGroup
    """Get the nPod group that match the specified npod group name"""
    npod_group_list = client.get_npod_groups(
        npod_group_filter=NPodGroupFilter(
            name=StringFilter(
                equals=group_name
            )
        )
    )
    if npod_group_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one npod group with group name {group_name}."
        )
    if npod_group_list.filtered_count == 1:
        return npod_group_list.items[0]


def delete_npod_group(module, client, npod_group_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a nPod group"""
    result = dict(
        changed=False
    )
    try:
        client.delete_npod_group(npod_group_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_npod_group(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating a new nPod group"""
    result = dict(
        changed=False
    )
    try:
        new_npod_group = client.create_npod_group(
            create_npod_group_input=CreateNPodGroupInput(
                name=module.params['name'],
                note=module.params['note']
            )
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['npod_group'] = to_dict(new_npod_group)
    return result


def modify_npod_group(module, client, npod_group):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows modifying a nPod group"""
    result = dict(
        changed=False
    )
    should_update = False
    for key in module.params:
        try:
            if module.params[key] is None:
                continue
            should_update = getattr(npod_group, key) != module.params[key]
            if should_update:
                break
        except AttributeError:
            should_update = False

    if should_update:
        try:
            modified_npod_group = client.update_npod_group(
                uuid=npod_group.uuid,
                update_npod_group_input=UpdateNPodGroupInput(
                    name=module.params['name'],
                    note=module.params['note'],
                )
            )
        except Exception as err:
            module.fail_json(msg=str(err))

        result['changed'] = True
        result['npod_group'] = to_dict(modified_npod_group)
        return result

    else:
        result['changed'] = False
        result['npod_group'] = to_dict(npod_group)
        return result


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        note=dict(required=False, type='str'),
        state=dict(required=True, choices=['present', 'absent'])
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(
        changed=False,
    )

    client = get_client(module)

    npod_group = get_npod_group(module, client, module.params['name'])

    if module.params['state'] == 'absent':
        if npod_group is not None:
            result = delete_npod_group(module, client, npod_group.uuid)
    elif module.params['state'] == 'present':
        if npod_group is None:
            result = create_npod_group(module, client)
        else:
            result = modify_npod_group(module, client, npod_group)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
