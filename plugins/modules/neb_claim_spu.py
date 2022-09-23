#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2021, 2022 Nebulon, Inc.
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
module: neb_claim_spu

short_description: To claim or release a SPU
description:
    - This module allows claim or release a SPU.
author:
    - Nebulon Team (@nebulon) <info@nebulon.com>
options:
    spu_serial:
        description: The serial number of the SPU
        type: str
        required: true
    state:
        description: Defines the intendend state for the SPU
        type: str
        choices:
            - present
            - absent
        required: true
extends_documentation_fragment:
    - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: claim a SPU
  nebulon.nebulon_on.neb_claim_spu:
    neb_username: "nebulon_on_user"
    neb_password: "nebulon_on_password"
    spu_serial: "112355D3F69FF16FEE"
    state: "present"

- name: Release a SPU
  nebulon.nebulon_on.neb_claim_spu:
    neb_username: "nebulon_on_user"
    neb_password: "nebulon_on_password"
    spu_serial: "112355D3F69FF16FEE"
    state: "absent"
"""

RETURN = r"""
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    validate_sdk,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)

# safe import of the Nebulon Python SDK
try:
    from nebpyclient import (
        SpuFilter,
        StringFilter,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def spu_exist(client, spu_serial):
    # type: (NebPyClient, str) -> bool
    """Checks SPU existence"""
    spu_list = client.get_spus(
        spu_filter=SpuFilter(
            serial=StringFilter(
                equals=spu_serial
            )
        )
    )
    if len(spu_list.items) > 0:
        return True
    return False


def claim_spu(module, client, spu_serial):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Claim a SPU"""
    try:
        client.claim_spu(
            spu_serial=spu_serial
        )
    except Exception as err:
        module.fail_json(msg=str(err))
    return dict(changed=True)


def release_spu(module, client, spu_serial):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Release a SPU"""
    try:
        client.release_spu(
            spu_serial=spu_serial
        )
    except Exception as err:
        module.fail_json(msg=str(err))
    return dict(changed=True)


def main():
    module_args = dict(
        spu_serial=dict(required=True, type='str'),
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

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    client = get_client(module)

    exist = spu_exist(client, module.params['spu_serial'])

    if module.params['state'] == 'present':
        if not exist:
            result = claim_spu(module, client, module.params['spu_serial'])
    else:
        if exist:
            result = release_spu(module, client, module.params['spu_serial'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
