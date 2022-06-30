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
module: neb_snapshot_template_info
short_description: To query snapshot schedule templates
description:
  - This module allows querying snapshot schedule templates.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Filter based on snapshot schedule template name
    type: str
    required: false
  uuid:
    description: The unique identifier of the snapshot schedule template
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Get a snapshot template by name
  neb_snapshot_template_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: template_name

- name: Get all available snapshot templates
  neb_snapshot_template_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
"""

RETURN = r"""
snapshot_schedule_templates:
  description: The detailed information of snapshot schedule templates
  returned: always
  type: list
  elements: dict
  contains:
    uuid:
      description: The unique identifier of the snapshot schedule template
      type: str
      returned: always
    name:
      description: Name for the snapshot schedule template
      type: str
      returned: always
    name_pattern:
      description: A naming pattern for the snapshots created by the schedule
      type: str
      returned: always
    schedule:
      description: The schedule in which snapshots will be created
      type: dict
      returned: always
      contains:
        hours:
          description: Hour of the day
          type: list
          elements: int
          returned: always
        minutes:
          description: Minutes past the hour
          type: list
          elements: int
          returned: always
        days_of_week:
          description: Days of the week
          type: list
          elements: int
          returned: always
        days_of_month:
          description: Days of the month
          type: list
          elements: int
          returned: always
        months:
          description: Months of year
          type: list
          elements: int
          returned: always
    expiration_seconds:
      description: Time in seconds when snapshots will be automatically deleted
      type: int
      returned: always
    retention_seconds:
      description: Time in seconds that prevents users from deleting snapshots
      type: int
      returned: always
    consistency_level:
      description: Snapshot consistency level
      type: str
      returned: always
    associated_npod_template_count:
      description: The number of nPod templates that make use of this template
      type: int
      returned: always
    associated_schedule_count:
      description: The number of provisioned snapshot schedules from this template
      type: int
      returned: always
 """

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import StringFilter, PageInput, SnapshotScheduleTemplateFilter, UUIDFilter


def get_snapshot_templates(client, name, uuid):
    # type: (NebPyClient, str) -> list
    """Get snapshot schedule templates that matche the specified filter options"""
    template_info_list = []
    page_number = 1
    while True:
        template_list = client.get_snapshot_schedule_templates(
            page=PageInput(page=page_number),
            template_filter=SnapshotScheduleTemplateFilter(
                name=StringFilter(
                    equals=name
                )
            )
        )
        for i in range(len(template_list.items)):
            template_info_list.append(to_dict(template_list.items[i]))
        if not template_list.more:
            break
        page_number += 1
    return template_info_list


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
        snapshot_schedule_templates=[]
    )

    client = get_client(module)

    result['snapshot_schedule_templates'] = get_snapshot_templates(
        client,
        module.params['name'], module.params['uuid']
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
