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
module: neb_capacity_info
short_description: Provides capacity information for volumes, SPUs, and nPods
description:
  - This module provides users with capacity information for a selected resource in Nebulon ON.
    These resources can either be volumes, SPUs, or nPods. Depending on the provided input
    parameter the relevant capacity metrics are provided.
author:
  - Tobias Flitsch (@tflitsch)
version_added: "1.4.0"
options:
  spu_serial:
    description: The serial number of an SPU for which to provide capacity information
    type: str
    required: false
  npod_uuid:
    description: The unique identified of an nPod for which to provide capacity information
    type: str
    required: false
  volume_uuid:
    description: The unique identifier of a volume for which to provide capacity information
    type: str
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Get capacity utilization for a SPU
  nebulon.nebulon_on.neb_capacity_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    spu_serial: 012355D3F69FF16FEE

- name: Get capacity utilization for a volume
  nebulon.nebulon_on.neb_capacity_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    volume_uuid: 36d87b9b-ac5e-4500-9a04-3e0640c222e6

- name: Get capacity utilization for a nPod
  nebulon.nebulon_on.neb_capacity_info:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_uuid: 9234f0e1-e8a2-42f3-a04d-6ee9da0397e1
"""

RETURN = r"""
spu_consumed_bytes:
  description: >-
      Total capacity stored on drives that is user data after compression, deduplication,
      and encryption.
  type: float
  returned: if present
spu_data_reduction_ratio:
  description: >-
      The data reduction ratio for user data stored on drives. A value of C(2) can be interpreted
      as C(2:1). This value is rounded to two digits after the decimal point.
  type: float
  returned: if present
spu_raw_bytes:
  description: >-
      Total raw capacity of a services processing unit (SPU). This capacity excludes any metadata
      that the system uses on the physical drives (~ 1MB).
  type: float
  returned: if present
spu_usable_bytes:
  description: >-
      Total usable capacity available for user data. It excludes capacity from erasure coding and
      system overheads.
  type: float
  returned: if present
volume_host_written_bytes:
  description: >-
     Total capacity written to the volume by hosts.
  type: float
  returned: if present
volume_size_bytes:
  description: Total size of the volume.
  type: float
  returned: if present
npod_consumed_bytes:
  description: >-
      Total capacity stored on drives that is user data after compression, deduplication,
      and encryption. This is the aggregate user data capacity in a nPod.
  type: float
  returned: if present
npod_data_reduction_ratio:
  description: >-
      The data reduction ratio for user data stored on drives. A value of C(2) can be interpreted
      as C(2:1). This value is rounded to two digits after the decimal point.
  type: float
  returned: if present
npod_raw_bytes:
  description: >-
      Total raw capacity of all services processing units (SPUs) in a nPod. This capacity excludes
      any metadata that the system uses on the physical drives (~ 1MB).
  type: float
  returned: if present
npod_usable_bytes:
  description: >-
      Total usable capacity available for user data. It excludes capacity from erasure coding and
      system overheads.
  type: float
  returned: if present
"""

# pylint: disable=wrong-import-position,no-name-in-module,import-error
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    validate_sdk,
)

# safe import of the Nebulon Python SDK
try:
    from nebpyclient import (
        NebPyClient,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None

# SPU and nPod queries
RAW_QUERY = 'sum(spu_raw_bytes{%s})'
DRR_QUERY = 'sum(spu_written_nozero_bytes{%s})/sum(spu_consumed_bytes{%s})'
USABLE_QUERY = 'sum(spu_usable_bytes{%s})'
CONSUMED_QUERY = 'sum(spu_consumed_bytes{%s})'

# Volume queries
SIZE_QUERY = 'sum(spu_disk_total{%s,ownership="owner"})'
WRITTEN_QUERY = 'sum(spu_disk_written{%s,ownership="owner"})'


def _run_promql_query(client, query):
    # type: (NebPyClient, str) -> float
    """Run a PromQL query against Nebulon ON"""

    payload = f"query={query}"
    cookie_value = client.session.cookies.get("session-data")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(payload)),
        "Cookie": f"session-data={cookie_value}"
    }
    response = client.session.post(
        url="https://ucapi.nebcloud.nebulon.com/api/v1/query",
        data=payload,
        headers=headers,
    )
    data = response.json()
    return _get_value_from_promql(data)


def _get_value_from_promql(data):
    # type: (dict) -> float
    """Get the metrics value from a PromQL response"""
    try:
        if data['status'] == 'success':
            value = data['data']['result'][0]['value']
            value_float = float(value[1])
            return round(value_float, 2)
        else:
            return -1.0

    # pylint: disable=broad-except
    except Exception:
        return -1.0


def get_spu_capacity(client, spu_serial):
    # type: (NebPyClient, str) -> dict
    """Get capacity information for a SPU"""

    filter_string = f'spu_serial="{spu_serial}"'

    # setup queries
    spu_raw_query = RAW_QUERY % filter_string
    spu_drr_query = DRR_QUERY % (filter_string, filter_string)
    spu_usable_query = USABLE_QUERY % filter_string
    spu_consumed_query = CONSUMED_QUERY % filter_string

    result = {
        'spu_raw_bytes': _run_promql_query(client, spu_raw_query),
        'spu_data_reduction_ratio': _run_promql_query(client, spu_drr_query),
        'spu_usable_bytes': _run_promql_query(client, spu_usable_query),
        'spu_consumed_bytes': _run_promql_query(client, spu_consumed_query),
    }
    return result


def get_volume_capacity(client, volume_uuid):
    # type: (NebPyClient, str) -> dict
    """Get capacity information for a volume"""

    filter_string = f'id="{volume_uuid}"'

    # setup queries
    volume_size_query = SIZE_QUERY % filter_string
    volume_host_written_query = WRITTEN_QUERY % filter_string

    result = {
        'volume_size_bytes': _run_promql_query(client, volume_size_query),
        'volume_host_written_bytes': _run_promql_query(client, volume_host_written_query),
    }
    return result


def get_npod_capacity(client, npod_uuid):
    # type: (NebPyClient, str) -> dict
    """Get capacity information for a nPod"""

    filter_string = f'pod="{npod_uuid}"'

    # setup queries
    spu_raw_query = RAW_QUERY % filter_string
    spu_drr_query = DRR_QUERY % (filter_string, filter_string)
    spu_usable_query = USABLE_QUERY % filter_string
    spu_consumed_query = CONSUMED_QUERY % filter_string

    result = {
        'npod_raw_bytes': _run_promql_query(client, spu_raw_query),
        'npod_data_reduction_ratio': _run_promql_query(client, spu_drr_query),
        'npod_usable_bytes': _run_promql_query(client, spu_usable_query),
        'npod_consumed_bytes': _run_promql_query(client, spu_consumed_query),
    }
    return result


def main():
    """Main entry point"""

    # set up the Ansible module arguments
    module_args = dict(
        spu_serial=dict(
            required=False,
            type='str',
            default=None,
        ),
        volume_uuid=dict(
            required=False,
            type='str',
            default=None,
        ),
        npod_uuid=dict(
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
            ('spu_serial', 'volume_uuid', 'npod_uuid')
        ],
        required_one_of=[
            ('spu_serial', 'volume_uuid', 'npod_uuid')
        ],
    )

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    # initialize the result
    result = dict(
        changed=False,
    )

    try:
        # login and connect to nebulon ON client
        client = get_client(module)

        # read module parameters
        spu_serial = module.params['spu_serial']
        volume_uuid = module.params['volume_uuid']
        npod_uuid = module.params['npod_uuid']

        # get the metrics as per the module parameters
        if spu_serial is not None:
            spu_capacity_info = get_spu_capacity(client, spu_serial)
            result.update(spu_capacity_info)
            module.exit_json(**result)

        if volume_uuid is not None:
            volume_capacity_info = get_volume_capacity(client, volume_uuid)
            result.update(volume_capacity_info)
            module.exit_json(**result)

        if npod_uuid is not None:
            npod_capacity_info = get_npod_capacity(client, npod_uuid)
            result.update(npod_capacity_info)
            module.exit_json(**result)

        module.exit_json(**result)

    # pylint: disable=broad-except
    except Exception as err:
        module.fail_json(msg=str(err), **result)


if __name__ == '__main__':
    main()
