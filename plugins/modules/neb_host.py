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
module: neb_host
short_description: Manage properties of hosts (servers) in Nebulon ON
description:
  - This module allows managing properties of hosts or servers in Nebulon ON
    including host display name
author:
  - Tobias Flitsch (@tflitsch) <tobias@nebulon.com>
  - Nebulon Team (@nebulon) <info@nebulon.com>
version_added: 1.3.0
options:
  host_name:
    description: >-
        The display name to configure for the host (server). To unset
        the value, provide an empty string C('').
    type: str
    required: false
  note:
    description: >-
        Allows configuring additional contextual information for the host
        (server). To unset the value, provide an empty string C('').
    type: str
    required: false
  host_uuid:
    description: The unique identifier of the host to manage
    type: str
    required: false
  spu_serial:
    description: The serial number of an SPU in the host to manage
    type: str
    required: false
  host_chassis_serial:
    description: The chassis serial number of the host to manage
    type: str
    required: false
  host_board_serial:
    description: The board serial number of the host to manage
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Set the displayed host name of a host by UUID
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    host_uuid: "3f9d4203-2a9e-4592-9038-7b968daac34b"
    host_name: server-05.tme.nebulon.com

- name: Set the displayed host name of a host by SPU
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    spu_serial: 0123F5C62DB49CF4EE
    host_name: server-05.tme.nebulon.com

- name: Set the displayed host name of a host by server chassis serial number
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    host_chassis_serial: SYS1234567890
    host_name: server-05.tme.nebulon.com

- name: Set the displayed host name of a host by server board serial number
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    host_board_serial: SYS1234567890
    host_name: server-05.tme.nebulon.com

- name: Add a note to a host
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    host_board_serial: SYS1234567890
    note: This is an important server

- name: Unset the displayed host name and the note
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    host_board_serial: SYS1234567890
    note: ''
    host_name: ''
"""

RETURN = r"""
host_name:
  description: The hosts' current displayed host name
  returned: always
  type: str
note:
  description: The host's current note
  returned: always
  type: str
"""

# pylint: disable=wrong-import-position,no-name-in-module,import-error
import traceback
from ansible.module_utils.basic import (
    AnsibleModule,
    missing_required_lib,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)

try:
    from nebpyclient import (
        NebPyClient,
        HostFilter,
        Host,
        UpdateHostInput,
        StringFilter,
        SpuFilter,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def get_host_with_filter(client, host_filter):
    # type: (NebPyClient, HostFilter) -> Host
    """Get host data via a filter"""

    if filter is None:
        raise ValueError("Please provide a valid host filter")

    host_list = client.get_hosts(
        host_filter=host_filter,
    )

    if host_list.filtered_count != 1:
        raise Exception("Host could not be identified")

    return host_list.items[0]


def get_host_by_uuid(client, host_uuid):
    # type: (NebPyClient, str) -> Host
    """Get host data via host UUID"""

    if host_uuid is None:
        raise ValueError("Please provide a valid host identifier")

    host_filter = HostFilter(
        uuid=StringFilter(
            equals=host_uuid
        )
    )

    return get_host_with_filter(
        client=client,
        host_filter=host_filter,
    )


def get_host_by_spu_serial(client, spu_serial):
    # type: (NebPyClient, str) -> Host
    """Get host data via host UUID"""

    if spu_serial is None:
        raise ValueError("Please provide a valid SPU serial number")

    spu_list = client.get_spus(
        spu_filter=SpuFilter(
            serial=StringFilter(
                equals=spu_serial
            )
        )
    )

    if spu_list.filtered_count == 1:
        host_filter = HostFilter(
            uuid=StringFilter(
                equals=spu_list.items[0].host_uuid
            )
        )

        return get_host_with_filter(
            client=client,
            host_filter=host_filter,
        )

    raise Exception("Host could not be identified")


def get_host_by_chassis_serial(client, host_chassis_serial):
    # type: (NebPyClient, str) -> Host
    """Get host data via host chassis serial number"""

    if host_chassis_serial is None:
        raise ValueError("Please provide a valid chassis serial number")

    host_filter = HostFilter(
        chassis_serial=StringFilter(
            equals=host_chassis_serial
        )
    )

    return get_host_with_filter(
        client=client,
        host_filter=host_filter,
    )


def get_host_by_board_serial(client, host_board_serial):
    # type: (NebPyClient, str) -> Host
    """Get host data via host board serial number"""

    if host_board_serial is None:
        raise ValueError("Please provide a valid board serial number")

    host_filter = HostFilter(
        board_serial=StringFilter(
            equals=host_board_serial
        )
    )

    return get_host_with_filter(
        client=client,
        host_filter=host_filter,
    )


def update_host(client, host_uuid, host_name=None, note=None):
    # type: (NebPyClient, str, str, str) -> Host
    """Update the properties of a host"""

    host = client.update_host(
        uuid=host_uuid,
        host_input=UpdateHostInput(
            name=host_name,
            note=note,
        )
    )

    return host


def main():
    """Main entry point"""

    # setup the Ansible module arguments
    module_args = dict(
        host_uuid=dict(
            required=False,
            type='str',
        ),
        spu_serial=dict(
            required=False,
            type='str',
        ),
        host_chassis_serial=dict(
            required=False,
            type='str',
        ),
        host_board_serial=dict(
            required=False,
            type='str',
        ),
        host_name=dict(
            required=False,
            type='str',
            default=None,
        ),
        note=dict(
            required=False,
            type='str',
            default=None,
        ),
    )
    # append the standard login arguments to the module
    module_args.update(get_login_arguments())

    # set up the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ('host_uuid', 'spu_serial', 'host_chassis_serial', 'host_board_serial'),
        ],
        required_one_of=[
            ('host_uuid', 'spu_serial', 'host_chassis_serial', 'host_board_serial'),
        ],
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
        host_uuid = module.params['host_uuid']
        spu_serial = module.params['spu_serial']
        host_chassis_serial = module.params['host_chassis_serial']
        host_board_serial = module.params['host_board_serial']
        host_name = module.params['host_name']
        note = module.params['note']

        # find the current host properties of the server to check if we need to
        # change it
        if host_uuid is not None:
            host = get_host_by_uuid(
                client=client,
                host_uuid=host_uuid,
            )
        elif spu_serial is not None:
            host = get_host_by_spu_serial(
                client=client,
                spu_serial=spu_serial,
            )
        elif host_chassis_serial is not None:
            host = get_host_by_chassis_serial(
                client=client,
                host_chassis_serial=host_chassis_serial,
            )
        elif host_board_serial is not None:
            host = get_host_by_board_serial(
                client=client,
                host_board_serial=host_board_serial,
            )
        else:
            # this branch is never reached as the other functions will raise
            # an Exception when the host is not found, but keeping this to
            # keep IDEs from complaining
            host = None

        # check if we need to make changes
        change_hostname = host_name is not None and host_name != host.name
        change_note = note is not None and note != host.note

        # handle check mode
        if module.check_mode:
            if change_hostname and change_note:
                result['changed'] = True
                result['msg'] = "Would change the host display name and note"
                module.exit_json(**result)

            if change_hostname:
                result['changed'] = True
                result['msg'] = f"Would change host display name to {host_name}"
                module.exit_json(**result)

            if change_note:
                result['changed'] = True
                result['msg'] = f"Would change note to {note}"
                module.exit_json(**result)

            result['changed'] = False
            result['msg'] = "No changes"
            module.exit_json(**result)

        # make any changes if necessary
        if change_hostname or change_note:

            # we can send both properties to this function as the provided
            # values are either None (ignored by the API) or set to a value
            # that must be set as an idempotent call.
            updated_host = update_host(
                client=client,
                host_uuid=host.uuid,
                host_name=host_name,
                note=note,
            )

            result['changed'] = True
            result['host_name'] = updated_host.name
            result['note'] = updated_host.note
            module.exit_json(**result)

        # no changes needed
        result['changed'] = False
        result['host_name'] = host.name
        result['note'] = host.note
        module.exit_json(**result)

    # pylint: disable=broad-except
    except Exception as err:
        module.fail_json(msg=str(err), **result)


if __name__ == '__main__':
    main()
