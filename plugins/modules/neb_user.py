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
module: neb_user
short_description: To create/modify/delete a Nebulon ON user
description:
  - >-
    This module manages the lifecycle (create, modify and delete) a Nebulon ON
    user.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  username:
    description: The name of the user
    type: str
    required: true
  password:
    description: The password of the user
    type: str
    required: false
  note:
    description: An optional note for the user
    type: str
    required: false
  email:
    description: The business email address for the user
    type: str
    required: false
  user_group_name:
    description: Unique identifier of the user group the user shall be part of
    type: str
    required: false
  first_name:
    description: The user's first name
    type: str
    required: false
  last_name:
    description: The user's last name
    type: str
    required: false
  mobile_phone:
    description: The mobile phone number of the user
    type: str
    required: false
  business_phone:
    description: The business phone number of the user
    type: str
    required: false
  inactive:
    description: Indicates if the user is marked as inactive / disabled
    type: bool
    required: false
  policy_uuids:
    description: List of RBAC policies associated with the user
    type: list
    elements: str
    required: false
  state:
    description:
      - Defines the intended state for the user
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new user
  nebulon.nebulon_on.neb_user:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    username: user
    password: password
    note: note
    email: user@domain.com
    user_group_name: Monitor
    first_name: firstname
    last_name: lastname
    mobile_phone: +1 650 123 4567
    business_phone: +1 650 123 4567
    inactive: true
    state: present

- name: Delete existing user
  nebulon.nebulon_on.neb_user:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    username: user
    state: absent

- name: Modify existing user
  nebulon.nebulon_on.neb_user:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    username: user
    password: new_password
    note: new_note
    state: present
"""

RETURN = r"""
user:
  description: A user in nebulon ON
  returned: if present
  type: dict
  contains:
    uuid:
      description: The unique identifier of the user in nebulon ON
      type: str
      returned: always
    name:
      description: The name of the user
      type: str
      returned: always
    note:
      description: An optional note for the user
      type: str
      returned: always
    email:
      description: The business email address for the user
      type: str
      returned: always
    first_name:
      description: The user's first name
      type: str
      returned: always
    last_name:
      description: The user's last name
      type: str
      returned: always
    mobile_phone:
      description: The mobile phone number of the user
      type: str
      returned: always
    business_phone:
      description: The business phone number of the user
      type: str
      returned: always
    inactive:
      description: Indicates if the user is marked as inactive / disabled
      type: bool
      returned: always
    group_uuids:
      description: Unique identifiers of user groups the user is part of
      type: list
      elements: str
      returned: always
    support_contact_id:
      description: The user identifier for support purposes (OEM)
      type: str
      returned: always
    change_password:
      description: Indicates if the user has to change the password during next login
      type: bool
      returned: always
    preferences:
      description: The user's personal preferences
      returned: always
      type: dict
      contains:
        send_notification:
          description: specifies if and the rate at which the user receives notifications
          returned: always
          type: str
        time_zone:
          description: Specifies the time zone of the user
          returned: always
          type: str
        show_base_two:
          description: Specifies if the user wants capacity values displayed in base2
          returned: always
          type: bool
        date_format:
          description: Specifies the user's preferred date and time formatting
          returned: always
          type: str
    policy_uuids:
      description: List of RBAC policies associated with the user
      type: list
      elements: str
      returned: always
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import UserFilter, StringFilter, UserGroupFilter, User, UserGroup


def get_user(module, client, user_name):
    # type: (AnsibleModule, NebPyClient, str) -> User
    """Get the user that matches the specified username"""
    user_list = client.get_users(
        user_filter=UserFilter(
            name=StringFilter(
                equals=user_name
            )
        )
    )
    # module will returns User object only if it finds one user
    if user_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one user with username {user_name}"
        )
    elif user_list.filtered_count == 1:
        return user_list.items[0]


def get_user_group(module, client, group_name):
    # type: (AnsibleModule, NebPyClient, str) -> UserGroup
    """Get the user group that matches the specified user group name"""
    user_group_list = client.get_user_groups(
        ug_filter=UserGroupFilter(
            name=StringFilter(
                equals=group_name
            )
        )
    )
    # module will returns UserGroup object if it finds oly one user group
    if user_group_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one user group with group name {group_name}"
        )
    elif user_group_list.filtered_count == 1:
        return user_group_list.items[0]


def delete_user(module, client, user_uuid, result):
    # type: (AnsibleModule, NebPyClient, str, dict) -> None
    """Allows deletion of a user account"""
    try:
        client.delete_user(user_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True


def add_user(module, client, result):
    # type: (AnsibleModule, NebPyClient, dict) -> None
    """Allow creating a new user in nebulon ON"""
    new_user_group = get_user_group(
        module, client, module.params['user_group_name'])
    if new_user_group is None:
        module.fail_json(
            msg=f"User Group {module.params['user_group_name']} does not exist"
        )
    try:
        new_user = client.create_user(
            name=module.params['username'],
            password=module.params['password'],
            email=module.params['email'],
            user_group_uuid=new_user_group.uuid,
            first_name=module.params['first_name'],
            last_name=module.params['last_name'],
            note=module.params['note'],
            mobile_phone=module.params['mobile_phone'],
            business_phone=module.params['business_phone'],
            inactive=module.params['inactive'],
            policy_uuids=module.params['policy_uuids']
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['user'] = to_dict(new_user)


def modify_user(module, client, user, result):
    # type: (AnsibleModule, NebPyClient, str, dict) -> None
    """Allow updating properties of an existing user"""
    should_update = False
    for key in module.params:
        try:
            if module.params[key] is None:
                continue
            # update if the values don't match
            should_update = getattr(user, key) != module.params[key]
            if should_update:
                break
        except AttributeError:
            should_update = False

    # we assume password change is requested if password is passed to the module. we can not read password from User
    # object and for that reason we can not determine if the new password is the same as stored password
    if module.params['password'] is not None:
        should_update = True

    user_group_uuids = user.group_uuids
    if module.params['user_group_name'] is not None:
        new_user_group = get_user_group(
            module, client, module.params['user_group_name'])
        if new_user_group is None:
            module.fail_json(
                msg=f"User Group {module.params['user_group_name']} does not exist"
            )
        else:
            if new_user_group.uuid not in user.group_uuids:
                # If a new user group passed, it will replace user groups with the new group
                user_group_uuids = [new_user_group.uuid]
                should_update = True

    if should_update:
        try:
            modified_user = client.update_user(
                uuid=user.uuid,
                name=module.params['username'],
                password=module.params['password'],
                email=module.params['email'],
                user_group_uuids=user_group_uuids,
                first_name=module.params['first_name'],
                last_name=module.params['last_name'],
                note=module.params['note'],
                mobile_phone=module.params['mobile_phone'],
                business_phone=module.params['business_phone'],
                inactive=module.params['inactive'],
                policy_uuids=module.params['policy_uuids']
            )
        except Exception as err:
            module.fail_json(msg=str(err))

        result['changed'] = True
        result['user'] = to_dict(modified_user)
    else:
        result['changed'] = False
        result['user'] = to_dict(user)


def main():
    module_args = dict(
        username=dict(required=True, type='str'),
        password=dict(required=False, type='str', no_log=True),
        note=dict(required=False, type='str'),
        email=dict(required=False, type='str'),
        user_group_name=dict(required=False, type='str'),
        first_name=dict(required=False, type='str'),
        last_name=dict(required=False, type='str'),
        mobile_phone=dict(required=False, type='str'),
        business_phone=dict(required=False, type='str'),
        inactive=dict(required=False, type='bool'),
        policy_uuids=dict(required=False, type='list', elements='str'),
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

    user = get_user(module, client, module.params['username'])

    if module.params['state'] == 'absent':
        if user is not None:
            delete_user(module, client, user.uuid, result)
    elif module.params['state'] == 'present':
        if user is None:
            add_user(module, client, result)
        else:
            modify_user(module, client, user, result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
