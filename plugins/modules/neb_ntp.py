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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: neb_ntp
short_description: Setting NTP configuration for SPU
description:
  - This module sets NTP server configuration for SPU and nPod.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  spu_serial:
    description: The serial number of the services processing unit
    type: str
    required: false
  npod_uuid:
    description: The unique identifier of the nPod
    type: str
    required: false
  ntp_servers:
    description: List of NTP server configurations that shall be applied to an SPU or nPod
    type: list
    required: true
    elements: dict
    suboptions:
      ntp_hostname:
        description: The DNS hostname of the NTP server
        type: str
        required: true
      pool:
        description: Indicates if the specified NTP server hostname is a NTP pool
        type: bool
        required: false
        default: false
      prefer:
        description: Indicates if the specified NTP server is the preferred NTP server
        type: bool
        required: false
        default: false
  ignore_warnings:
    description: >-
        When set to true, warnings in nebulon ON are ignored, otherwise the module will fail
        on warnings
    type: bool
    required: false
    default: false
notes:
  - In the pool option, you can not mix pool with non-pool hostnames in your input otherwise,
    it throws an error.
  - If your hostname is from the NTP pool, the pool flag should be set as True otherwise,
    it throws a warning.
  - The prefer option designates one or more sources as preferred over all others. While the
    rules do not forbid it,
    it is usually not useful to designate more than one source as preferred; however, if more
    than one source is so
    designated, they are used in the order specified in the configuration file.
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Set NTP server configuration for nPod
  nebulon.nebulon_on.neb_ntp:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_uuid: "3f9d4203-2a9e-4592-9038-7b968daac34b"
    ntp_servers:
        - ntp_hostname: "0.pool.ntp.org"
          prefer: true
          pool: true

- name: Set NTP server configuration for SPU
  nebulon.nebulon_on.neb_ntp:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    spu_serial: 012355XXXXXXF16FEE
    ntp_servers:
        - ntp_hostname: "0.pool.ntp.org"
          prefer: true
          pool: true
        - ntp_hostname: "1.pool.ntp.org"
          prefer: false
          pool: true
        - ntp_hostname: "2.pool.ntp.org"
          prefer: false
          pool: true
"""

RETURN = r"""
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    to_dict,
    validate_sdk,
)

# safe import of the Nebulon Python SDK
try:
    from nebpyclient import (
        NebPyClient,
        NTPServer,
        NTPServerInput,
        SetNTPServersInput,
        Spu,
        SpuFilter,
        StringFilter,
        UUIDFilter,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def get_ntp_server_list(module):
    # type: (AnsibleModule) -> list[NTPServerInput]
    """Retrieve the list of NTP server configuration information that will be used on SPUs."""
    ntp_server_list = []
    for server in module.params['ntp_servers']:
        ntp_server_list.append(
            NTPServerInput(
                pool=server['pool'],
                prefer=server['prefer'],
                server_hostname=server['ntp_hostname']
            )
        )
    return ntp_server_list


def check_previous_ntp_config(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """This function checks if the input NTP configurations is already set on SPU"""
    result = dict(
        changed=False
    )
    if module.params['spu_serial'] is not None:
        spu = client.get_spus(
            spu_filter=SpuFilter(
                serial=StringFilter(
                    equals=module.params['spu_serial'],
                )
            )
        )

        if spu.filtered_count > 1:
            module.fail_json(
                msg=f"Found more than one SPU for SPU serial {module.params['spu_serial']}"
            )
        elif spu.filtered_count == 1:
            if len(spu.items[0].ntp_servers) != 0:
                for server in spu.items[0].ntp_servers:
                    if to_dict(server) not in module.params['ntp_servers']:
                        result['changed'] = True
            else:
                result['changed'] = True
    return result


def set_ntp_spu(module, client, spu_serial):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Set NTP server configuration for a SPU"""
    result = dict(
        changed=False
    )
    try:
        result = check_previous_ntp_config(module, client)
        client.set_ntp_servers(
            SetNTPServersInput(
                spu_serial=spu_serial,
                servers=get_ntp_server_list(module)
            ),
            ignore_warnings=module.params['ignore_warnings'],
        )
    except Exception as err:
        module.fail_json(msg=str(err))
    return result


def set_ntp_npod(module, client, npod_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Set NTP server configuration for a nPod"""
    result = dict(
        changed=False
    )
    try:
        client.set_ntp_servers(
            SetNTPServersInput(
                npod_uuid=npod_uuid,
                servers=get_ntp_server_list(module)
            ),
            ignore_warnings=module.params['ignore_warnings'],
        )
    except Exception as err:
        module.fail_json(msg=str(err))
    return result


def main():
    module_args = dict(
        npod_uuid=dict(required=False, type='str'),
        spu_serial=dict(required=False, type='str'),
        ntp_servers=dict(required=True, type='list', elements='dict', options=dict(
            ntp_hostname=dict(required=True, type='str'),
            prefer=dict(required=False, type='bool', default=False),
            pool=dict(required=False, type='bool', default=False),
        )),
        ignore_warnings=dict(required=False, type='bool', default=False),
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    client = get_client(module)

    if module.params['spu_serial'] is not None:
        result = set_ntp_spu(
            module,
            client,
            module.params['spu_serial'],
        )
    else:
        result = set_ntp_npod(
            module,
            client,
            module.params['npod_uuid'],
        )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
