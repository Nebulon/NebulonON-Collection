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
module: neb_host_info
short_description: returns details for a host
description:
  - This module returns details for a host.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  host_uuid:
    description: Filter based on host unique identifier
    type: str
    required: false
  host_name:
    description: Filter based on host name
    type: str
    required: false
  host_model:
    description: Filter based on host model name
    type: str
    required: false
  host_manufacturer:
    description: Filter based on host manufacturer name
    type: str
    required: false
  host_chassis_serial:
    description: Filter based on host chassis serial number
    type: str
    required: false
  host_board_serial:
    description: Filter based on board serial number
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Get Host info
  nebulon.nebulon_on.neb_host_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    host_uuid: "3f9d4203-2a9e-4592-9038-7b968daac34b"
"""

RETURN = r"""
hosts:
  description: Information of hosts.
  returned: always
  type: list
  elements: dict
  contains:
    uuid:
      description: Unique identifier of the host
      returned: always
      type: str
    chassis_serial:
      description: Chassis serial number of the host
      returned: always
      type: str
    board_serial:
      description: Board serial number of the host
      returned: always
      type: str
    name:
      description: Name of the host
      returned: always
      type: str
    model:
      description: Model of the host
      returned: always
      type: str
    note:
      description: Optional note for the host
      returned: always
      type: str
    npod_uuid:
      description: The unique identifier of the nPod this host is part of
      returned: always
      type: str
    spu_serials:
      description: List of SPU serial numbers that are installed in this host
      type: list
      elements: str
      returned: always
    spu_count:
      description: Number of SPUs installed in this host
      returned: always
      type: int
    rack_uuid:
      description: Unique identifier associated with this host
      returned: always
      type: str
    manufacturer:
      description: Manufacturer name for this host
      returned: always
      type: str
    cpu_count:
      description: Number of installed CPUs in this host
      returned: always
      type: int
    cpu_type:
      description: CPU type of the CPUs installed in this host
      returned: always
      type: str
    cpu_manufacturer:
      description: CPU manufacturer of the CPUs installed in this host
      returned: always
      type: str
    cpu_core_count:
      description: Number of cores of the installed CPUs
      returned: always
      type: int
    cpu_thread_count:
      description: Number of threads of the installed CPUs
      returned: always
      type: int
    cpu_speed:
      description: CPU clock speed
      returned: always
      type: int
    dimm_count:
      description: Number of DIMMs installed in this host
      returned: always
      type: int
    dimms:
      description: List of DIMMs installed in this host
      type: list
      elements: str
      returned: always
    memory_bytes:
      description: Total memory installed in the server in bytes
      returned: always
      type: int
    lom_hostname:
      description: Hostname of the lights out management address of the host
      returned: always
      type: str
    lom_address:
      description: IP address of the lights out management address of the host
      returned: always
      type: str
    boot_time:
      description: Date and time when the host booted
      returned: always
      type: str
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    to_dict,
    validate_sdk,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)

# safe import of the Nebulon Python SDK
try:
    from nebpyclient import (
        NebPyClient,
        HostFilter,
        StringFilter,
        PageInput,
        UUIDFilter,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def get_host_info_list(module, client):
    # type: (AnsibleModule, NebPyClient) -> list[dict]
    """Retrieves a list of hosts"""
    host_info_list = []
    page_number = 1
    while True:
        host_list = client.get_hosts(
            page=PageInput(page=page_number),
            host_filter=HostFilter(
                uuid=StringFilter(
                    equals=module.params['host_uuid']
                ),
                and_filter=HostFilter(
                    name=StringFilter(
                        equals=module.params['host_name']
                    ),
                    and_filter=HostFilter(
                        model=StringFilter(
                            equals=module.params['host_model']
                        ),
                        and_filter=HostFilter(
                            manufacturer=StringFilter(
                                equals=module.params['host_manufacturer']
                            ),
                            and_filter=HostFilter(
                                chassis_serial=StringFilter(
                                    equals=module.params['host_chassis_serial']
                                ),
                                and_filter=HostFilter(
                                    board_serial=StringFilter(
                                        equals=module.params['host_board_serial']
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
        for host in host_list.items:
            host_info_list.append(to_dict(host))
        if not host_list.more:
            break
        page_number += 1

    return host_info_list


def main():
    module_args = dict(
        host_uuid=dict(required=False, type='str'),
        host_name=dict(required=False, type='str'),
        host_model=dict(required=False, type='str'),
        host_manufacturer=dict(required=False, type='str'),
        host_chassis_serial=dict(required=False, type='str'),
        host_board_serial=dict(required=False, type='str'),
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    result = dict(
        hosts=[]
    )

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    client = get_client(module)

    result['hosts'] = get_host_info_list(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
