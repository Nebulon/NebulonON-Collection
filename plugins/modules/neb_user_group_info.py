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
module: neb_user_group_info
short_description: Returns details for user groups
description:
  - >-
    This module returns details for user group objects in Nebulon ON
    organization.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Name of the user group
    type: str
    required: false
  uuid:
    description: UUID of the user group
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Retrive all user groups
  nebulon.nebulon_on.neb_user_group_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password

- name: Retrive user groups by name
  nebulon.nebulon_on.neb_user_group_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name

- name: Retrive all user groups by UUID
  nebulon.nebulon_on.neb_user_group_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    uuid: group_uuid
"""

RETURN = r"""
user_groups:
  description: A list of user groups in nebulon ON
  returned: success
  type: list
  elements: dict
  contains:
    uuid:
      description: The unique identifier of the user group in nebulon ON
      returned: always
      type: str
    name:
      description: The name of the user group
      returned: always
      type: str
    note:
      description: An optional note for the user group
      returned: always
      type: str
    user_uuids:
      description: List of user unique identifiers that are part of the group
      returned: always
      type: list
      elements: str
    policy_uuids:
      description: List of RBAC policies associated with the user group
      returned: always
      type: list
      elements: str
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import UserGroupFilter, UuidFilter, StringFilter, PageInput


def get_user_groups(client, name, uuid):
    # type: (AnsibleModule, NebPyClient, str) -> list[dict]
    user_group_info_list = []
    page_number = 1
    while True:
        user_group_list = client.get_user_groups(
            page=PageInput(page=page_number),
            ug_filter=UserGroupFilter(
                name=StringFilter(
                    equals=name
                ),
                and_filter=UserGroupFilter(
                    uuid=UuidFilter(
                        equals=uuid
                    )
                )
            )
        )
        for i in range(len(user_group_list.items)):
            user_group_info_list.append(to_dict(user_group_list.items[i]))
        if not user_group_list.more:
            break
        page_number += 1
    return user_group_info_list


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

    result['user_groups'] = get_user_groups(
        client,
        module.params['name'],
        module.params['uuid']
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
