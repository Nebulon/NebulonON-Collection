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
module: neb_npod_info
short_description: Retrieve a list of provisioned nPods
description:
  - This module allows retrieving a list of provisioned nPods.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Name of the nPod
    type: str
    required: false
  uuid:
    description: The unique identifier of the nPod
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options

"""

EXAMPLES = r"""
- name: Retrieve nPod by name
  nebulon.nebulon_on.neb_npod_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: my_pod

- name: Retrieves list of all nPods in the org
  nebulon.nebulon_on.neb_npod_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password

"""

RETURN = r"""
npods:
  description: The detailed information of a nPod
  returned: always
  type: list
  elements: dict
  contains:
    uuid:
      description: The unique identifier of the nPod
      type: str
      returned: always
    name:
      description: The name for the nPod
      type: str
      returned: always
    npod_group_uuid:
      description: The unique identifier of the nPod group this nPod belongs to
      type: str
      returned: always
    note:
      description: An optional note for the nPod
      type: str
      returned: always
    volume_uuids:
      description: List of volume identifiers defined in this nPod
      type: list
      elements: str
      returned: always
    volume_count:
      description: Number of volumes defined in this nPod
      type: int
      returned: always
    host_uuids:
      description: List of host identifiers part of this nPod
      type: list
      elements: str
      returned: always
    host_count:
      description: Number of hosts part of this nPod
      type: int
      returned: always
    spu_serials:
      description: List of serial numbers part of this nPod
      type: list
      elements: str
      returned: always
    spu_count:
      description: Number of spus part of this nPod
      type: int
      returned: always
    snapshot_uuids:
      description: List of snapshot identifiers defined in this nPod
      type: list
      elements: str
      returned: always
    update_history:
      description: List of updates performed on this nPod
      type: list
      elements: dict
      returned: always
      contains:
        update_id:
          description: The identifier of the update
          type: str
        packageName:
          description: The name of the package that is installed
          type: str
        start:
          description: Date and time when the update started
          type: str
        finish:
          description: Date and time when the update complete
          type: str
        success:
          description: Indicates if the update completed successfully
          type: bool
    npod_template_uuid:
      description: Unique identifier for the nPod template used during nPod creation
      type: str
      returned: always
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import NPodFilter, StringFilter, UUIDFilter


def get_npod_list(module, client):
    # type: (AnsibleModule, NebPyClient) -> list
    """Retrieves a list of nPods that matches the specified filter"""
    npods = []
    page_number = 1
    while True:
        npod_list = client.get_npods(
            npod_filter=NPodFilter(
                name=StringFilter(
                    equals=module.params['name']
                ),
                and_filter=NPodFilter(
                    uuid=UUIDFilter(
                        equals=module.params['uuid']
                    )
                )
            )
        )
        for i in range(len(npod_list.items)):
            npods.append(to_dict(npod_list.items[i]))
        if not npod_list.more:
            break
        page_number += 1

    return npods


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
        npods=[]
    )

    client = get_client(module)

    result['npods'] = get_npod_list(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
