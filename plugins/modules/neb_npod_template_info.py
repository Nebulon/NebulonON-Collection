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
module: neb_npod_template_info
short_description: Retrieve a list of provisioned nPod templates
description:
  - This module allows retrieving a list of provisioned nPod templates.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Retrive a nPod template based on nPod template name
    type: str
    required: false
  uuid:
    description: >-
      Retrive a nPod template based on nPod template unique identifier. If
      provided all other input parameters will be ignored
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Retrive nPod template by UUID
  nebulon.nebulon_on.neb_npod_template_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    uuid: 041e6d6e-5e45-4881-859d-98bda749c173

- name: Retrive all of nPod templates
  nebulon.nebulon_on.neb_npod_template_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
"""

RETURN = r"""
npod_templates:
  description: The detailed information of a nPod template
  returned: always
  type: list
  elements: dict
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
from nebpyclient import NPodTemplateFilter, UuidFilter, StringFilter, PageInput


def get_npod_template_by_uuid(module, client, npod_template_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> list[dict]
    """Get the nPod template that matches the specified UUID"""
    template_list = client.get_npod_templates(
        template_filter=NPodTemplateFilter(
            uuid=UuidFilter(
                equals=npod_template_uuid
            )
        )
    )
    if template_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one nPod template with uuid {npod_template_uuid}."
        )
    elif template_list.filtered_count == 1:
        return [to_dict(template_list.items[0])]


def get_npod_template(client, npod_template_name):
    # type: (NebPyClient, str, bool) -> list
    """Get the nPod template that matches the specified UUID"""
    templates = []
    page_number = 1
    while True:
        template_list = client.get_npod_templates(
            page=PageInput(page=page_number),
            template_filter=NPodTemplateFilter(
                name=StringFilter(
                    equals=npod_template_name
                )
            )
        )
        for i in range(len(template_list.items)):
            templates.append(to_dict(template_list.items[i]))
        if not template_list.more:
            break
        page_number += 1

    return templates


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
        changed=False
    )

    client = get_client(module)

    if module.params['uuid'] is not None:
        result['npod_templates'] = get_npod_template_by_uuid(
            module, client, module.params['uuid'])
    else:
        result['npod_templates'] = get_npod_template(
            client, module.params['name'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
