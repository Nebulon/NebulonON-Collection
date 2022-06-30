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
module: neb_npod_template
short_description: To create or delete a nPod template
description:
  - 'This module allows creating, modifying or deleting a nPod template.'
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: The unique name of the nPod template
    type: str
    required: true
  saving_factor:
    description: Anticipated data saving factor after compression and deduplication
    type: float
    required: false
  mirrored_volume:
    description: Indicates if volumes will be mirrored across SPUs in an nPod
    type: bool
    required: false
  boot_volume:
    description: Indicates if a boot volume for the OS will be provisioned
    type: bool
    required: false
    default: false
  os:
    description: Name of the operating system running on the hosts in the nPod
    type: str
    required: false
  volume_size_bytes:
    description: Volume size in bytes
    type: int
    required: false
  shared_volume:
    description: Indicates if volumes are shared between all hosts in an nPod
    type: bool
    required: false
  boot_volume_size_bytes:
    description: Indicates the boot volume size in bytes
    type: int
    required: false
  boot_image_url:
    description: Allows specifying a URL to an OS image for the boot volume
    type: str
    required: false
  app:
    description: Name of the application running on the hosts in the nPod
    type: str
    required: false
  note:
    description: An optional note for the nPod template
    type: str
    required: false
  snapshot_schedule_template_uuids:
    description: List of associated snapshot schedule templates
    type: list
    elements: str
    required: false
  volume_count:
    description: Indicates how many volumes shall be provisioned by the template
    type: int
    required: false
  state:
    description: Defines the intended state for the nPod volume
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new nPod template
  nebulon.nebulon_on.neb_npod_template:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: npod-temp
    volume_size_bytes: 1000000000
    saving_factor: 3
    mirrored_volume: false
    shared_volume: false
    boot_volume: false
    os: Amazon Linux 2 (64-bit)
    state: present
- name: Modify nPod template
  nebulon.nebulon_on.neb_npod_template:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: npod-temp
    os: Windows
    note: Modified npod template
    state: present
- name: Delete existing nPod template
  nebulon.nebulon_on.neb_npod_template:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: npod_name
    state: absent
"""

RETURN = r"""
npod_template:
  description: The detailed information of a nPod template
  returned: always
  type: dict
  contains:
    parent_uuid:
      description: The unique identifier of the original template if modified
      type: str
      returned: always
    uuid:
      description: The unique identifier of the template
      type: str
      returned: always
    name:
      description: The unique name of the nPod template
      type: str
      returned: always
    volume_size_bytes:
      description: Volume size in bytes
      type: int
      returned: always
    saving_factor:
      description: Anticipated data saving factor after compression and deduplication
      type: float
      returned: always
    mirrored_volume:
      description: Indicates if volumes will be mirrored across SPUs in an nPod
      type: bool
      returned: always
    shared_volume:
      description: Indicates if volumes are shared between all hosts in an nPod
      type: bool
      returned: always
    boot_volume:
      description: Indicates if a boot volume for the OS will be provisioned
      type: bool
      returned: always
    boot_volume_size_bytes:
      description: Indicates the boot volume size in bytes
      type: int
      returned: always
    boot_image_url:
      description: Allows specifying a URL to an OS image for the boot volume
      type: str
      returned: always
    os:
      description: Name of the operating system running on the hosts in the nPod
      type: str
      returned: always
    app:
      description: Name of the application running on the hosts in the nPod
      type: str
      returned: always
    version:
      description: The version of the template. Every update creates a new version
      type: int
      returned: always
    note:
      description: An optional note for the nPod template
      type: str
      returned: always
    nebulon_template:
      description: Indicates if nebulon created the nPod template
      type: bool
      returned: always
    snapshot_schedule_template_uuids:
      description: List of associated snapshot schedule templates
      type: list
      elements: str
      returned: always
    volume_count:
      description: Indicates how many volumes shall be provisioned by the template
      type: int
      returned: always
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import NPodTemplateFilter, NPodTemplate, StringFilter, CreateNPodTemplateInput, UpdateNPodTemplateInput


def get_npod_template(client, name):
    # type: (NebPyClient, str) -> NPodTemplate
    """Get the nPod template that matches the specified name"""
    template_list = client.get_npod_templates(
        template_filter=NPodTemplateFilter(
            name=StringFilter(
                equals=name
            )
        )
    )
    npod_template = None
    if template_list.filtered_count > 0:
        npod_template = template_list.items[0]
    # TODO: To be removed once the SDK accepts the lastVersion flag to retrieve the last version of the template.
    for i in range(1, template_list.filtered_count):
        if template_list.items[i].version > npod_template.version:
            npod_template = template_list.items[i]
    return npod_template


def delete_npod_template(module, client, parent_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a nPod template"""
    result = dict(
        changed=False
    )
    try:
        client.delete_npod_template(parent_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_npod_template(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating a new npod_template"""
    result = dict(
        changed=False,
        npod_template=None,
    )
    try:
        new_npod_template = client.create_npod_template(
            create_npod_template_input=CreateNPodTemplateInput(
                name=module.params['name'],
                saving_factor=module.params['saving_factor'],
                mirrored_volume=module.params['mirrored_volume'],
                boot_volume=module.params['boot_volume'],
                os=module.params['os'],
                volume_size_bytes=module.params['volume_size_bytes'],
                shared_lun=module.params['shared_volume'],
                boot_volume_size_bytes=module.params['boot_volume_size_bytes'],
                boot_image_url=module.params['boot_image_url'],
                app=module.params['app'],
                note=module.params['note'],
                snapshot_schedule_template_uuids=module.params['snapshot_schedule_template_uuids'],
                volume_count=module.params['volume_count'],
            )
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['npod_template'] = to_dict(new_npod_template)
    return result


def modify_npod_template(module, client, npod_template):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows modifying a npod_template"""
    result = dict(
        changed=False,
        npod_template=None,
    )
    should_update = False
    for key in module.params:
        try:
            if module.params[key] is None:
                continue
            should_update = getattr(npod_template, key) != module.params[key]
            if should_update:
                break
        except AttributeError:
            should_update = False

    if should_update:
        try:
            modified_npod_template = client.update_npod_template(
                update_npod_template_input=UpdateNPodTemplateInput(
                    name=module.params['name'],
                    saving_factor=module.params['saving_factor'],
                    mirrored_volume=module.params['mirrored_volume'],
                    boot_volume=module.params['boot_volume'],
                    os=module.params['os'],
                    volume_size_bytes=module.params['volume_size_bytes'],
                    shared_lun=module.params['shared_volume'],
                    boot_volume_size_bytes=module.params['boot_volume_size_bytes'],
                    boot_image_url=module.params['boot_image_url'],
                    app=module.params['app'],
                    note=module.params['note'],
                    snapshot_schedule_template_uuids=module.params['snapshot_schedule_template_uuids'],
                    volume_count=module.params['volume_count']
                )
            )
        except Exception as err:
            module.fail_json(msg=str(err))

        result['changed'] = True
        result['npod_template'] = to_dict(modified_npod_template)

    else:
        result['changed'] = False
        result['npod_template'] = to_dict(npod_template)

    return result


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        saving_factor=dict(required=False, type='float'),
        mirrored_volume=dict(required=False, type='bool'),
        boot_volume=dict(required=False, type='bool', default=False),
        os=dict(required=False, type='str'),
        volume_size_bytes=dict(required=False, type='int'),
        shared_volume=dict(required=False, type='bool'),
        boot_volume_size_bytes=dict(required=False, type='int'),
        boot_image_url=dict(required=False, type='str'),
        app=dict(required=False, type='str'),
        note=dict(required=False, type='str'),
        snapshot_schedule_template_uuids=dict(
            required=False, type='list', elements='str'),
        volume_count=dict(required=False, type='int'),
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
    npod_template = get_npod_template(client, module.params['name'])

    if module.params['state'] == 'absent':
        if npod_template is not None:
            result = delete_npod_template(
                module, client, npod_template.parent_uuid)
    elif module.params['state'] == 'present':
        if npod_template is None:
            result = create_npod_template(module, client)
        else:
            result = modify_npod_template(module, client, npod_template)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
