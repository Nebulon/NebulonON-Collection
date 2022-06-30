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
module: neb_lun
short_description: To create or delete LUNs
description:
  - This module allows creating or deleting LUN(s).
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  volume_uuid:
    description: The unique identifier of the volume that shall be made available to a host
    type: str
    required: false
  lun_id:
    description: >-
      An optional LUN ID to be deleted. Provide optional single item to export
      volumes with a specific ID when creating lUN
    type: int
    required: false
  lun_uuids:
    description: List of LUN UUIDs used only for deleteing LUNs.
    type: list
    elements: str
    required: false
  host_uuids:
    description: >-
      List of host UUIDs that identify the hosts the volume shall be exported
      to. This must be provided if 'spu_serials' is not provided
    type: list
    elements: str
    required: false
  spu_serials:
    description: >-
      List of SPU serials that identify the serials the volume shall be exported
      to. This must be provided if 'host_uuids' is not provided.
    type: list
    elements: str
    required: false
  local:
    description: If provided and set to 'True' then the volume will be exported with ALUA
    type: bool
    default: false
    required: false
  state:
    description: Defines the intended state for the LUN(s)
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new LUN exported to SPU
  nebulon.nebulon_on.neb_lun:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    lun_id:
      - '123'
    spu_serials:
      - 0123F5C62DB49CF4EE
    local: true
    state: present

- name: Create new LUN exported to host
  nebulon.nebulon_on.neb_lun:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    host_uuids:
      - 78adf4fc-8ddc-4c59-9995-c77a2e717955
    local: true
    state: present

- name: Delete existing LUNs
  nebulon.nebulon_on.neb_lun:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    host_uuids:
      - 78adf4fc-8ddc-4c59-9995-c77a2e717955
    lun_uuids:
      - ab94975d-9fc8-404d-a4a0-4e7b58c9f210
    state: absent
"""

RETURN = r"""
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import VolumeFilter, UUIDFilter, HostFilter, LUNFilter, StringFilter, CreateLUNInput


def delete_luns(module, client) -> dict:
    """Removes all exports matching a provided criteria"""

    result = dict(
        changed=False
    )
    volume_uuid = module.params['volume_uuid']
    spu_serials = module.params['spu_serials']
    lun_id = module.params['lun_id']
    host_uuids = module.params['host_uuids']
    lun_uuids = module.params['lun_uuids']

    lun_list = client.get_luns(
        lun_filter=LUNFilter(
            uuid=UUIDFilter(
                in_filter=lun_uuids
            )
        )
    )

    if lun_list.filtered_count == 0:
        result['changed'] = False
        return result

    try:
        for lun in lun_list.items:
            client.delete_lun(
                lun_uuid=lun.uuid
            )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_luns(module, client):
    """Creates LUNs for matching criteria"""

    result = dict(
        changed=False
    )
    volume_uuid = module.params['volume_uuid']
    spu_serials = module.params['spu_serials']
    lun_id = module.params['lun_id']
    host_uuids = module.params['host_uuids']

    volume_list = client.get_volumes(
        volume_filter=VolumeFilter(
            uuid=UUIDFilter(
                equals=volume_uuid
            )
        )
    )

    if volume_list.filtered_count == 0:
        module.fail_json(msg="Volume does not exist")
        return

    # get all relevant spu serials
    # TODO: This will not work with 2 SPUs in one server
    if len(host_uuids) > 0:
        host_list = client.get_hosts(
            host_filter=HostFilter(
                uuid=StringFilter(
                    in_list=host_uuids
                )
            )
        )

        for host in host_list.items:
            for spu_serial in host.spu_serials:
                if spu_serial not in spu_serials:
                    spu_serials.append(spu_serial)

    lun_list = client.get_luns(
        lun_filter=LUNFilter(
            volume_uuid=UUIDFilter(
                equals=volume_uuid
            )
        )
    )

    for lun in lun_list.items:
        if lun.spu_serial in spu_serials:
            spu_serials.remove(lun.spu_serial)

    # if spu_serials length is 0, all of the exports exist
    # TODO: they could exist with a different LUN ID, but it is unsafe to change

    if len(spu_serials) == 0:
        return result

    try:
        client.create_lun(
            lun_input=CreateLUNInput(
                volume_uuid=volume_uuid,
                lun_id=lun_id,
                spu_serials=spu_serials,
                local=module.params['local'],
                host_uuids=module.params['host_uuids']
            )
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def main():
    module_args = dict(
        volume_uuid=dict(required=False, type='str'),
        lun_id=dict(required=False, type='int'),
        lun_uuids=dict(required=False, type='list', elements='str', default=[]),
        host_uuids=dict(required=False, type='list', elements='str', default=[]),
        spu_serials=dict(required=False, type='list', elements='str', default=[]),
        local=dict(required=False, type='bool', default=False),
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
        result = delete_luns(module, client)
    elif module.params['state'] == 'present':
        result = create_luns(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
