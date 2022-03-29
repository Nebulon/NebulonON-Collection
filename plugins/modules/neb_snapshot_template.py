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
module: neb_snapshot_template
short_description: Allows creation of a new snapshot schedule template
description:
  - >-
    This playbook manages the lifecycle (create, modify and delete) a snapshot
    schedule templates.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Name for the snapshot schedule template
    type: str
    required: true
  snapshot_name_pattern:
    description: A naming pattern for the snapshots created by the schedule
    type: str
    required: false
  schedule_period:
    description: The schedule in which snapshots will be created
    type: dict
    required: false
    suboptions:
      hours:
        description: Hours of the day
        type: list
        elements: int
        required: false
      minutes:
        description: Minutes past the hour
        type: list
        elements: int
        required: false
      days_of_week:
        description: Days of the week
        type: list
        elements: int
        required: false
      days_of_month:
        description: Days of the month
        type: list
        elements: int
        required: false
      months:
        description: Months of year
        type: list
        elements: int
        required: false
  expiration_time:
    description: Time when snapshots will be automatically deleted
    type: dict
    required: false
    suboptions:
      weeks:
        description: Number of weeks when snapshots will be automatically deleted
        type: int
        required: false
      days:
        description: Number of days when snapshots will be automatically deleted
        type: int
        required: false
      hours:
        description: Number of hours weeks when snapshots will be automatically deleted
        type: int
        required: false
  retention_time:
    description: Time that prevents users from deleting snapshots
    type: dict
    required: false
    suboptions:
      weeks:
        description: Number of weeks that prevents users from deleting snapshots
        type: int
        required: false
      days:
        description: Number of days that prevents users from deleting snapshots
        type: int
        required: false
      hours:
        description: Number of hours that prevents users from deleting snapshots
        type: int
        required: false
  include_boot_volume:
    description: Specifies if boot volumes are ignored by the schedule or included
    type: bool
    default: false
    required: false
  state:
    description: Defines the intended state for the snapshot schedule template
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create Snapshot Schedule Template
  nebulon.nebulon_on.neb_snapshot_template:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: AnsibleTemplate
    snapshot_name_pattern: NamePattern
    schedule_period:
      minutes: 2
      hours: 1
      days_of_week: 1
      days_of_month: 1
      months: 1
    expiration_time:
      weeks: 2
      days: 2
      hours: 2
    retention_time:
      weeks: 2
      days: 1
      hours: 1
    include_boot_volume: false
    state: present

- name: Delete existing Snapshot Schedule Template
  nebulon.nebulon_on.neb_snapshot_template:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: AnsibleTemplate
    state: absent

- name: Modify existing Snapshot Schedule Template
  nebulon.nebulon_on.neb_snapshot_template:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: AnsibleTemplate
    snapshot_name_pattern: NewNamePattern
    schedule_period:
      minutes: 2
      hours: 1
      days_of_week: 1
      days_of_month: 1
      months: 1
    expiration_time:
      weeks: 2
      days: 2
      hours: 2
    retention_time:
      weeks: 2
      days: 1
      hours: 1
    include_boot_volume: false
    state: present
"""

RETURN = r"""
snapshot_schedule:
  description: The detailed information of a snapshot schedule template in nebulon ON
  returned: success
  type: dict
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
        hour:
          description: Hour of the day
          type: list
          elements: int
          returned: always
        minute:
          description: Minutes past the hour
          type: list
          elements: int
          returned: always
        day_of_week:
          description: Days of the week
          type: list
          elements: int
          returned: always
        day_of_month:
          description: Days of the month
          type: list
          elements: int
          returned: always
        month:
          description: Months of year
          type: list
          elements: int
          returned: always
    expiration_seconds:
      description: Time in seconds when snapshots will be automatically deleted
      type: int
      returned: always
    expiration_time:
      description: Time when snapshots will be automatically deleted
      type: dict
      returned: always
      contains:
        weeks:
          description: Number of weeks when snapshots will be automatically deleted
          type: int
          returned: always
        days:
          description: Number of days when snapshots will be automatically deleted
          type: int
          returned: always
        hours:
          description: Number of hours weeks when snapshots will be automatically deleted
          type: int
          returned: always
    retention_seconds:
      description: Time in seconds that prevents users from deleting snapshots
      type: int
      returned: always
    retention_time:
      description: Time that prevents users from deleting snapshots
      type: dict
      returned: always
      contains:
        weeks:
          description: Number of weeks that prevents users from deleting snapshots
          type: int
          returned: always
        days:
          description: Number of days that prevents users from deleting snapshots
          type: int
          returned: always
        hours:
          description: Number of hours that prevents users from deleting snapshots
          type: int
          returned: always
    consistency_level:
      description: Snapshot consistency level
      type: str
      returned: always
    ignore_boot_volumes:
      description: Specifies if boot volumes are ignored by the schedule or included
      type: bool
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from nebpyclient import SnapshotScheduleTemplate, SnapshotScheduleTemplateFilter, ScheduleInput, StringFilter


def seconds_as_dict(seconds):
    # type: (int) -> dict
    """splits seconds into weeks, days and hours"""
    week_seconds = 7 * 24 * 3600
    day_seconds = 24 * 3600
    hour_seconds = 3600
    weeks = seconds // week_seconds
    seconds = seconds % week_seconds
    days = seconds // day_seconds
    seconds = seconds % day_seconds
    hours = seconds // hour_seconds
    return dict(
        weeks=weeks,
        days=days,
        hours=hours,
    )


def get_snapshot_schedule_template_as_dict(schedule_template):
    # type: (SnapshotScheduleTemplate) -> dict
    """returns SnapshotScheduleTemplate object as a dict"""
    schedule_template_dict = to_dict(schedule_template)
    schedule_template_dict['retention_time'] = seconds_as_dict(
        schedule_template.retention_seconds)
    schedule_template_dict['expiration_time'] = seconds_as_dict(
        schedule_template.expiration_seconds)
    return schedule_template_dict


def get_snapshot_schedule_template(module, client, name):
    # type: (AnsibleModule, NebPyClient, str) -> SnapshotScheduleTemplate
    """"Retrieves a snapshot schedule template objects that matches the specified name"""
    schedule_list = client.get_snapshot_schedule_templates(
        template_filter=SnapshotScheduleTemplateFilter(
            name=StringFilter(
                equals=name
            )
        )
    )
    if schedule_list.filtered_count > 1:
        module.fail_json(
            msg="Found more than one snapshot schedule template with name: '" + name + "'.")
    elif schedule_list.filtered_count == 1:
        return schedule_list.items[0]


def delete_snapshot_template(module, client, uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a Snapshot Schedule Template"""
    result = dict(
        changed=False,
    )
    try:
        client.delete_snapshot_schedule_template(uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_snapshot_template(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Create new instance of Snapshot Schedule Template"""
    result = dict(
        changed=False,
        snapshot_schedule_template=None
    )
    ignore_boot_volume = True
    if module.params['include_boot_volume']:
        ignore_boot_volume = False
    try:
        new_snapshot_template = client.create_snapshot_schedule_template(
            name=module.params['name'],
            name_pattern=module.params['snapshot_name_pattern'],
            schedule=ScheduleInput(
                minute=module.params['schedule_period']['minutes'],
                hour=module.params['schedule_period']['hours'],
                day_of_week=module.params['schedule_period']['days_of_week'],
                day_of_month=module.params['schedule_period']['days_of_month'],
                month=module.params['schedule_period']['months']
            ),
            expiration_seconds=get_seconds(module.params['expiration_time']['weeks'],
                                           module.params['expiration_time']['days'],
                                           module.params['expiration_time']['hours']),
            retention_seconds=get_seconds(module.params['retention_time']['weeks'],
                                          module.params['retention_time']['days'],
                                          module.params['retention_time']['hours']),
            ignore_boot_volumes=ignore_boot_volume
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['snapshot_schedule_template'] = get_snapshot_schedule_template_as_dict(
        new_snapshot_template)
    return result


def modify_snapshot_template(module, client, schedule_template):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows modifying a Snapshot Schedule Template"""
    result = dict(
        changed=False,
        snapshot_schedule_template=None
    )
    should_update = False
    if ((module.params['name'] is not None and schedule_template.name !=
         module.params['name'])
        or (module.params['snapshot_name_pattern'] is not None
            and schedule_template.name_pattern != module.params['snapshot_name_pattern'])
        or (module.params['schedule_period']['minutes'] is not None
            and schedule_template.schedule.minute != module.params['schedule_period']['minutes'])
        or (module.params['schedule_period']['hours'] is not None
            and schedule_template.schedule.hour != module.params['schedule_period']['hours'])
        or (module.params['schedule_period']['days_of_week'] is not None
            and schedule_template.schedule.day_of_week != module.params['schedule_period']['days_of_week'])
        or (module.params['schedule_period']['days_of_month'] is not None
            and schedule_template.schedule.day_of_month != module.params['schedule_period']['days_of_month'])
        or (module.params['schedule_period']['months'] is not None
            and schedule_template.schedule.month != module.params['schedule_period']['months'])
        or (module.params['expiration_time']['weeks'] is not None
            and module.params['expiration_time']['days'] is not None
            and module.params['expiration_time']['hours'] is not None
            and schedule_template.expiration_seconds != get_seconds(module.params['expiration_time']['weeks'],
                                                                    module.params['expiration_time']['days'],
                                                                    module.params['expiration_time']['hours']))
        or (module.params['retention_time']['weeks'] is not None
            and module.params['retention_time']['days'] is not None
            and module.params['retention_time']['hours'] is not None
            and schedule_template.retention_seconds != get_seconds(module.params['retention_time']['weeks'],
                                                                   module.params['retention_time']['days'],
                                                                   module.params['retention_time']['hours']))):
        should_update = True

    if should_update:
        try:
            modified_snapshot_template = client.update_snapshot_schedule_template(
                uuid=schedule_template.uuid,
                name=module.params['name'],
                name_pattern=module.params['snapshot_name_pattern'],
                schedule=ScheduleInput(
                    minute=module.params['schedule_period']['minutes'],
                    hour=module.params['schedule_period']['hours'],
                    day_of_week=module.params['schedule_period']['days_of_week'],
                    day_of_month=module.params['schedule_period']['days_of_month'],
                    month=module.params['schedule_period']['months']
                ),
                expiration_seconds=get_seconds(module.params['expiration_time']['weeks'],
                                               module.params['expiration_time']['days'],
                                               module.params['expiration_time']['hours']),
                retention_seconds=get_seconds(module.params['retention_time']['weeks'],
                                              module.params['retention_time']['days'],
                                              module.params['retention_time']['hours']),
            )
        except Exception as err:
            module.fail_json(msg=str(err))

        result['changed'] = True
        result['snapshot_schedule_template'] = get_snapshot_schedule_template_as_dict(
            modified_snapshot_template)
        return result
    else:
        result['changed'] = False
        result['snapshot_schedule_template'] = get_snapshot_schedule_template_as_dict(
            schedule_template)
        return result


def get_seconds(weeks, days, hours):
    # type: (int, int, int) -> int
    return ((((weeks * 7) + days) * 24) + hours) * 60 * 60


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        snapshot_name_pattern=dict(required=False, type='str'),
        schedule_period=dict(required=False, type='dict', options=dict(
            minutes=dict(required=False, type='list', elements='int'),
            hours=dict(required=False, type='list', elements='int'),
            days_of_week=dict(required=False, type='list', elements='int'),
            days_of_month=dict(required=False, type='list', elements='int'),
            months=dict(required=False, type='list', elements='int'))),
        expiration_time=dict(required=False, type='dict', options=dict(
            weeks=dict(required=False, type='int'),
            days=dict(required=False, type='int'),
            hours=dict(required=False, type='int'))),
        retention_time=dict(required=False, type='dict', options=dict(
            weeks=dict(required=False, type='int'),
            days=dict(required=False, type='int'),
            hours=dict(required=False, type='int'))),
        include_boot_volume=dict(required=False, type='bool', default='False'),
        state=dict(required=True, choices=['present', 'absent'])
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result = dict(
        changed=False,
    )

    client = get_client(module)

    schedule_template = get_snapshot_schedule_template(
        module, client, module.params['name'])

    if module.params['state'] == 'absent':
        if schedule_template is not None:
            result = delete_snapshot_template(
                module, client, schedule_template.uuid)
    elif module.params['state'] == 'present':
        if schedule_template is None:
            result = create_snapshot_template(module, client)
        else:
            result = modify_snapshot_template(
                module, client, schedule_template)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
