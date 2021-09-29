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
module: neb_user_info
short_description: Returns details for users
description:
  - This module returns details for user objects in Nebulon ON organization.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Name of the user
    type: str
    required: false
  uuid:
    description: UUID of the user
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Retrive all users
  nebulon.nebulon_on.neb_user_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password

- name: Retrive user by name
  nebulon.nebulon_on.neb_user_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: user_name

- name: Retrive user by uuid
  nebulon.nebulon_on.neb_user_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    uuid: user_uuid
"""

RETURN = r"""
users:
  description: A list of users in nebulon ON
  returned: always
  type: list
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
from nebpyclient import UserFilter, UuidFilter, StringFilter, PageInput


def get_users(client, name, uuid):
    # type: (AnsibleModule, NebPyClient, str) -> list[dict]
    users_info_list = []
    page_number = 1
    while True:
        users_list = client.get_users(
            page=PageInput(page=page_number),
            user_filter=UserFilter(
                name=StringFilter(
                    equals=name
                ),
                and_filter=UserFilter(
                    uuid=UuidFilter(
                        equals=uuid
                    )
                )
            )
        )
        for i in range(len(users_list.items)):
            users_info_list.append(to_dict(users_list.items[i]))
        if not users_list.more:
            break
        page_number += 1
    return users_info_list


def main():
    module_args = dict(
        name=dict(required=False, type='str'),
        uuid=dict(required=False, type='str'),
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(
        users=[],
        user_groups=[]
    )

    client = get_client(module)

    result['users'] = get_users(
        client,
        module.params['name'],
        module.params['uuid']
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
