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
module: neb_npod_group_info
short_description: Returns details for nPod groups
description:
  - This module returns details for nPod group objects.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Name of the nPod group
    type: str
    required: false
  uuid:
    description: The unique identifier of the nPod group
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Retrive all nPod groups
  nebulon.nebulon_on.neb_npod_group_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
- name: Retrive nPod groups by name
  nebulon.nebulon_on.neb_npod_group_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: group_name
- name: Retrive nPod group by UUID
  nebulon.nebulon_on.neb_npod_group_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    uuid: group_uuid

"""

RETURN = r"""
npod_groups:
  description: A list of nPod groups in nebulon ON
  returned: success
  type: list
  elements: dict
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
from nebpyclient import NPodGroupFilter, UuidFilter, StringFilter, PageInput


def get_npod_groups(client, name, uuid):
    # type: (NebPyClient, str, str) -> list
    npod_group_info_list = []
    page_number = 1
    while True:
        npod_group_list = client.get_npod_groups(
            page=PageInput(page=page_number),
            npod_group_filter=NPodGroupFilter(
                name=StringFilter(
                    equals=name
                ),
                and_filter=NPodGroupFilter(
                    uuid=UuidFilter(
                        equals=uuid
                    )
                )
            )
        )
        for i in range(len(npod_group_list.items)):
            npod_group_info_list.append(to_dict(npod_group_list.items[i]))
        if not npod_group_list.more:
            break
        page_number += 1
    return npod_group_info_list


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
        npod_groups=[]
    )

    client = get_client(module)

    result['npod_groups'] = get_npod_groups(
        client, module.params['name'], module.params['uuid'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
