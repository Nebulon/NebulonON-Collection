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
module: neb_user_group
short_description: To create/modify/delete a Nebulon ON user group
description:
  - >-
    This module manages the lifecycle (create, modify and delete) a Nebulon ON
    user group.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: The name of the user group
    type: str
    required: true
  policy_uuids:
    description: List of RBAC policies associated with the user group
    type: list
    elements: str
    required: false
  note:
    description: An optional note for the user group
    type: str
    required: false
  state:
    description: Defines the intended state for the user group
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new user group
  nebulon.nebulon_on.neb_user_group:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
    policy_uuids:
      - 041e6d6e-5e45-4881-859d-98bda749c173
    note: note
    state: present

- name: Delete existing user group
  nebulon.nebulon_on.neb_user_group:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
    state: absent

- name: Modify existing user group
  nebulon.nebulon_on.neb_user_group:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
    note: new_note
    state: present
"""

RETURN = r"""
user_group:
  description: The detailed information of a user group
  returned: if present
  type: dict
  contains:
    uuid:
      description: The unique identifier of the user group in nebulon ON
      type: str
      returned: always
    name:
      description: The name of the user group
      type: str
      returned: always
    note:
      description: An optional note for the  user group
      type: str
      returned: always
    user_uuids:
      description: List of user unique identifiers that are part of the group
      type: list
      elements: str
      returned: always
    policy_uuids:
      description: List of RBAC policies associated with the user group
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
        UserGroup,
        UserGroupFilter,
        StringFilter,
        CreateUserGroupInput,
        UpdateUserGroupInput,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def get_user_group(module, client, group_name):
    # type: (AnsibleModule, NebPyClient, str) -> UserGroup
    """Get the user group that match the specified user group name"""
    user_group_list = client.get_user_groups(
        user_group_filter=UserGroupFilter(
            name=StringFilter(
                equals=group_name
            )
        )
    )
    if user_group_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one user group with group name: {group_name}"
        )
    if user_group_list.filtered_count == 1:
        return user_group_list.items[0]


def delete_user_group(module, client, user_group_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a user group"""
    result = dict(
        changed=False
    )
    try:
        result['changed'] = client.delete_user_group(user_group_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    return result


def add_user_group(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating a new user group in Nebulon ON"""
    result = dict(
        changed=False
    )
    try:
        new_user_group = client.create_user_group(
            create_user_group_input=CreateUserGroupInput(
                name=module.params['name'],
                policy_uuids=module.params['policy_uuids'],
                note=module.params['note']
            )
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['user_group'] = to_dict(new_user_group)
    return result


def modify_user_group(module, client, user_group):
    # type: (AnsibleModule, NebPyClient, UserGroup) -> dict
    """Allows modifying a user group in Nebulon ON"""
    result = dict(
        changed=False
    )
    should_update = False
    for key in module.params:
        try:
            if module.params[key] is None:
                continue
            should_update = getattr(user_group, key) != module.params[key]
            if should_update:
                break
        except AttributeError:
            should_update = False

    if should_update:
        try:
            modified_user_group = client.update_user_group(
                update_user_group_input=UpdateUserGroupInput(
                    name=module.params['name'],
                    policy_uuids=module.params['policy_uuids'],
                    note=module.params['note'],
                )
            )
        except Exception as err:
            module.fail_json(msg=str(err))

        result['changed'] = True
        result['user_group'] = to_dict(modified_user_group)
        return result

    else:
        result['changed'] = False
        result['user_group'] = to_dict(user_group)
        return result


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        policy_uuids=dict(required=False, type='list', elements='str'),
        note=dict(required=False, type='str'),
        state=dict(required=True, choices=['present', 'absent']),
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(
        changed=False,
    )

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    client = get_client(module)

    user_group = get_user_group(module, client, module.params['name'])

    if module.params['state'] == 'absent':
        if user_group is not None:
            result = delete_user_group(module, client, user_group.uuid)
    elif module.params['state'] == 'present':
        if user_group is None:
            result = add_user_group(module, client)
        else:
            result = modify_user_group(module, client, user_group)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
