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
module: neb_update
short_description: To update SPU firmware
description:
  - >-
    This module allows updating SPU firmware for a single SPU or all SPUs in a
    nPod.
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  npod_uuid:
    description: The unique identifier of the nPod to update
    type: str
    required: false
  spu_serial:
    description: The serial number of the SPU to update
    type: str
    required: false
  package_name:
    description: The name of the update package to install
    type: str
    required: true
  ignore_warning:
    description: If set to ``True`` the update will bypass any safeguards
    type: bool
    required: false
    default: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Update a SPU
  nebulon.nebulon_on.neb_update:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    spu_serial: 012355D3F69FF16FEF
    package_name: '1.1.4'

- name: Update nPod
  nebulon.nebulon_on.neb_update:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_uuid: c481d4e0-e00d-474b-9d5e-abfb1adcd59e
    package_name: '1.1.4'
    ignore_warning: true
"""

RETURN = r"""
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule


def update_spu(module, client, spu_serial, package_name, force):
    # type: (AnsibleModule, NebPyClient, str, str, bool) -> dict
    """Update SPU firmware"""
    try:
        client.update_spu_firmware(
            spu_serial=spu_serial,
            package_name=package_name,
            force=force
        )
    except Exception as err:
        module.fail_json(msg=str(err))
    return dict(changed=True)


def update_npod(module, client, npod_uuid, package_name, ignore_warning):
    # type: (AnsibleModule, NebPyClient, str, str, bool) -> dict
    """Update nPod"""
    try:
        client.update_npod_firmware(
            npod_uuid=npod_uuid,
            package_name=package_name,
            ignore_warnings=ignore_warning
        )
    except Exception as err:
        module.fail_json(msg=str(err))
    return dict(changed=True)


def main():
    module_args = dict(
        spu_serial=dict(required=False, type='str'),
        npod_uuid=dict(required=False, type='str'),
        package_name=dict(required=True, type='str'),
        ignore_warning=dict(required=False, type='bool', default=False),
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

    if module.params['npod_uuid'] is not None:
        result = update_npod(
            module,
            client,
            module.params['npod_uuid'],
            module.params['package_name'],
            module.params['ignore_warning']
        )
    elif module.params['spu_serial'] is not None:
        result = update_spu(
            module,
            client,
            module.params['spu_serial'],
            module.params['package_name'],
            module.params['ignore_warning']
        )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
