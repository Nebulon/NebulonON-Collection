#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2022 Nebulon, Inc.
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
module: neb_volume_access
short_description: Allows managing host access to volumes
description:
  - This module allows managing host access to a volume using nebulon guidance
    on volume mappings best practices for hosts.
author:
  - Tobias Flitsch (@tflitsch)
version_added: "1.3.0"
options:
  volume_uuid:
    description: >-
       The unique identifier of the volume to manage accessibility for
    type: str
    required: true
  lun_id:
    description: >-
      An optional LUN ID to be deleted. Provide optional single item to export
      volumes with a specific ID when creating lUN
    type: int
    required: false
  host_uuid:
    description: >-
      Unique identifier of the host to manage the volume export for this option
      is parameter is required when the state is set to C(host).
    type: str
    required: false
  state:
    description: >-
      Defines the intended accessibility state for the volume. Using the option
      C(present) or C(all) will cause the volume to be accessible by all hosts
      in the volume's nPod. Using C(host) will allow making the volume
      accessible to an individual host. When setting this option the parameter
      C(host_uuid) must be provided. The option C(local) will make the volume
      available to the host that owns the volume. C(absent) will prevent any
      host from accessing the volume.
    type: str
    choices:
      - present
      - all
      - host
      - local
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Allow access to a volume by a specific host
  nebulon.nebulon_on.neb_volume_access:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    lun_id: 20
    host_uuid: 78adf4fc-8ddc-4c59-9995-c77a2e717955
    state: host

- name: Allow access to a volume by all hosts in the nPod
  nebulon.nebulon_on.neb_volume_access:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    state: present

- name: Allow access to a volume by all hosts in the nPod
  nebulon.nebulon_on.neb_volume_access:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    state: all

- name: Allow access to a volume by its owner
  nebulon.nebulon_on.neb_volume_access:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    state: local

- name: Remove all access to a volume
  nebulon.nebulon_on.neb_volume_access:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 02c3f31a-2f43-4dfe-8153-6231ecd8ebb3
    state: absent
"""

RETURN = r"""
uuid:
  description: The unique identifier of the created LUN
  returned: if present
  type: str
lun_id:
  description: The LUN ID for the created LUN
  returned: if present
  type: int
host_uuids:
  description: The unique identifiers of the host that has access to the volume
  returned: always
  type: list
  elements: str
"""


# pylint: disable=wrong-import-position,no-name-in-module,import-error
import traceback
import time
from typing import List
from ansible.module_utils.basic import (
    AnsibleModule,
    missing_required_lib,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    get_volume,
    get_npod,
)

try:
    from nebpyclient import (
        NebPyClient,
        # BatchDeleteLUNInput,
        UUIDFilter,
        LUNFilter,
        CreateLUNInput,
        LUN,
        Volume,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def delete_luns(client, volume, lun_uuids=None):
    # type: (NebPyClient, Volume, List[str]) -> None
    """Removes all exports matching a provided criteria"""

    if lun_uuids is not None and len(lun_uuids) > 0:
        # make sure that the LUN definition UUIDs are unique
        lun_definition_uuids = []
        for lun_uuid in lun_uuids:
            if lun_uuid not in lun_definition_uuids:
                lun_definition_uuids.append(lun_uuid)

        # we need to delete explicit LUNs from the volume
        # TODO: There is currently a bug in the SDK version 2.0.8 that
        # doesn't allow the use of batch delete.
        #
        # client.delete_luns(
        #     batch_delete_lun_input=BatchDeleteLUNInput(
        #         volume_uuid=volume.uuid,
        #         lun_uuids=lun_definition_uuids,
        #     )
        # )
        for lun_uuid in lun_definition_uuids:
            client.delete_lun(lun_uuid=lun_uuid)

    else:

        # TODO: the bug mentioned above requires us to delete LUNs explicitly
        # this bug is found in SDK version 2.0.8
        #
        # delete all LUNs for the the provided volume
        # client.delete_luns(
        #     batch_delete_lun_input=BatchDeleteLUNInput(
        #         volume_uuid=volume.uuid,
        #     )
        # )
        existing_luns = get_existing_luns(client, volume)
        lun_definition_uuids = []
        for existing_lun in existing_luns:
            if existing_lun.definition_uuid not in lun_definition_uuids:
                lun_definition_uuids.append(existing_lun.definition_uuid)

        for lun_uuid in lun_definition_uuids:
            client.delete_lun(lun_uuid=lun_uuid)

    # TODO: there is another issue in the python SDK where the called function
    # is async. However, we cannot continue until the LUNs are gone
    _wait_for_lun_deletion(client, lun_definition_uuids)


def _wait_for_lun_deletion(client, lun_uuids):
    # type: (NebPyClient, List[str]) -> None
    for nap_time in (1, 1, 2, 3, 5, 8, 11):
        time.sleep(nap_time)

        lun_list = client.get_luns(
            lun_filter=LUNFilter(
                uuid=UUIDFilter(
                    in_filter=lun_uuids
                )
            )
        )

        if lun_list.filtered_count == 0:
            return


def get_existing_luns(client, volume):
    # type: (NebPyClient, Volume) -> List[LUN]
    """Gets the list of existing LUNs for a volume"""

    # get the list of existing LUNs for the provided volume
    lun_list = client.get_luns(
        lun_filter=LUNFilter(
            volume_uuid=UUIDFilter(
                equals=volume.uuid,
            ),
        )
    )

    return lun_list.items


def create_npod_lun(client, volume, lun_id=None):
    # type: (NebPyClient, Volume, int) -> LUN
    """Export a volume to all hosts in an nPod"""

    lun = client.create_lun(
        lun_input=CreateLUNInput(
            npod_lun=True,
            volume_uuid=volume.uuid,
            lun_id=lun_id,
        )
    )

    return lun


def create_local_lun(client, volume, lun_id=None):
    # type: (NebPyClient, Volume, int) -> LUN
    """Export a volume to its owner host"""

    lun = client.create_lun(
        lun_input=CreateLUNInput(
            local=True,
            volume_uuid=volume.uuid,
            host_uuids=[volume.natural_owner_host_uuid],
            lun_id=lun_id,
        )
    )

    return lun


def create_host_lun(client, volume, host_uuid, lun_id=None):
    # type: (NebPyClient, Volume, str, int) -> LUN
    """Export a volume to a specific host"""

    lun = client.create_lun(
        lun_input=CreateLUNInput(
            local=True,
            volume_uuid=volume.uuid,
            host_uuids=[host_uuid],
            lun_id=lun_id,
        )
    )

    return lun


def main():
    """Main entry point"""

    # setup the Ansible module arguments
    module_args = dict(
        volume_uuid=dict(
            required=True,
            type='str',
        ),
        lun_id=dict(
            required=False,
            type='int',
            default=None,
        ),
        host_uuid=dict(
            required=False,
            type='str',
            default=None,
            required_if=[
                ('state', 'host', ('path', 'content'), True),
            ],
        ),
        state=dict(
            required=True,
            choices=['present', 'all', 'host', 'local', 'absent'],
        )
    )
    # append the standard login arguments to the module
    module_args.update(get_login_arguments())

    # setup the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_if=[
            ('state', 'host', ['host_uuid'], True),
        ]
    )

    # check if SDK is loaded
    if NEBULON_SDK_VERSION is None:
        module.fail_json(
            msg=missing_required_lib("nebpyclient"),
            error_details=str(NEBULON_IMPORT_ERROR),
            error_class=type(NEBULON_IMPORT_ERROR).__name__,
        )

    # initialize the result
    result = dict(
        changed=False,
    )

    try:
        # login and connect to nebulon ON client
        client = get_client(module)

        # read module parameters
        volume_uuid = module.params['volume_uuid']
        host_uuid = module.params['host_uuid']
        lun_id = module.params['lun_id']
        desired_state = module.params['state']

        # try to find the volume and its LUNs for the user-provided UUID. This
        # will throw an exception if the volume is not found
        volume = get_volume(client=client, volume_uuid=volume_uuid)
        existing_luns = get_existing_luns(client, volume)

        if desired_state == 'absent':
            # the volume should not be exported to any hosts and therefore
            # we should delete all LUNs that currently exist for the volume
            # If there are none, this criteria is already met
            if len(existing_luns) == 0:
                result['changed'] = False
                result['host_uuids'] = []
                module.exit_json(**result)

            # if there are existing LUNs, we need to remove them all
            delete_luns(
                client=client,
                volume=volume,
            )

            result['changed'] = True
            result['host_uuids'] = []
            module.exit_json(**result)

        if desired_state in ['all', 'present']:
            # the volume should be exported to all hosts in the nPod

            # if there are any existing LUNs where the LUN ID does not match
            # we unfortunately need to delete them first. This also takes care
            # of the case where a volume is exported with different LUN IDs
            # to different hosts
            unwanted_lun_uuids = []
            desired_lun_id = lun_id if lun_id is not None else -1
            existing_host_uuids = []

            for existing_lun in existing_luns:
                if desired_lun_id == -1:
                    desired_lun_id = existing_lun.lun_id
                if existing_lun.lun_id != desired_lun_id:
                    unwanted_lun_uuids.append(existing_lun.definition_uuid)
                else:
                    existing_host_uuids.append(existing_lun.host_uuid)

            if len(unwanted_lun_uuids) > 0:
                module.warn("Unexporting volume from some hosts")
                delete_luns(
                    client=client,
                    volume=volume,
                    lun_uuids=unwanted_lun_uuids,
                )

            # check if the LUN is exported to all hosts in the nPod
            lun_exported_to_all_hosts = True
            npod = get_npod(
                client=client,
                npod_uuid=volume.npod_uuid,
            )
            for npod_host_uuid in npod.host_uuids:
                if npod_host_uuid not in existing_host_uuids:
                    lun_exported_to_all_hosts = False

            if lun_exported_to_all_hosts:
                result['changed'] = False
                result['host_uuids'] = npod.host_uuids
                result['lun_id'] = desired_lun_id
                module.exit_json(**result)

            # create a nPod LUN
            if desired_lun_id == -1:
                lun = create_npod_lun(
                    client=client,
                    volume=volume,
                )
            else:
                lun = create_npod_lun(
                    client=client,
                    volume=volume,
                    lun_id=desired_lun_id
                )

            result['changed'] = True
            result['uuid'] = lun.definition_uuid
            result['lun_id'] = lun.lun_id
            result['host_uuids'] = npod.host_uuids

        if desired_state in ['local', 'host']:
            # the volume should only be exported to a specific host. The
            # host is either the volume owner or the one specified via
            # the module parameter
            if desired_state == 'host':
                target_host_uuid = host_uuid
            else:
                target_host_uuid = volume.natural_owner_host_uuid

            # if there are any existing LUNs where the LUN ID does not match
            # or that are exported to the wrong host, we need to remove those
            unwanted_lun_uuids = []
            lun_exported_to_host = False

            for existing_lun in existing_luns:
                if existing_lun.host_uuid == target_host_uuid:
                    # make sure that the volume is exported to with the
                    # correct LUN ID to the host. If it is using an ID
                    # that is not what the user wants we need to remove it
                    if lun_id is not None and existing_lun.lun_id != lun_id:
                        unwanted_lun_uuids.append(existing_lun.definition_uuid)
                        continue

                    # the volume is already exported to the host with the
                    # right LUN ID or the user doesn't care about it
                    lun_exported_to_host = True
                    continue

                # this volume is exported to a host that is not the
                # owner of the volume. We need to delete this LUN
                unwanted_lun_uuids.append(existing_lun.definition_uuid)

            # delete any LUNs that are not supposed to be there
            if len(unwanted_lun_uuids) > 0:
                module.warn("Volume export removed for some hosts")
                result['changed'] = True
                delete_luns(
                    client=client,
                    volume=volume,
                    lun_uuids=unwanted_lun_uuids,
                )

            # it could be that a nPod LUN was deleted and that the LUN is no
            # longer exported to the host
            existing_luns = get_existing_luns(client, volume)
            if lun_exported_to_host and len(existing_luns) == 0:
                module.warn("Volume export deleted for target host during change")
                lun_exported_to_host = False

            # create the desired LUN if it is not there
            if not lun_exported_to_host:
                if desired_state == 'local':
                    lun = create_local_lun(
                        client=client,
                        volume=volume,
                        lun_id=lun_id
                    )
                else:
                    lun = create_host_lun(
                        client=client,
                        volume=volume,
                        host_uuid=target_host_uuid,
                        lun_id=lun_id,
                    )

                result['changed'] = True
                result['uuid'] = lun.definition_uuid
                result['lun_id'] = lun.lun_id
                result['host_uuids'] = [lun.host_uuid]

            else:
                if len(existing_luns) != 1:
                    # this should not happen
                    raise Exception("Unknown error occurred")

                existing_lun = existing_luns[0]
                result['uuid'] = existing_lun.definition_uuid
                result['lun_id'] = existing_lun.lun_id
                result['host_uuids'] = [existing_lun.host_uuid]

        module.exit_json(**result)

    # pylint: disable=broad-except
    except Exception as err:
        module.fail_json(msg=str(err), **result)


if __name__ == '__main__':
    main()
