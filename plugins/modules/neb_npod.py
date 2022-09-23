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
module: neb_npod
short_description: To create or delete a nPod
description:
  - This module allows creating or deleting a nPod
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  name:
    description: Name of the nPod
    type: str
    required: true
  npod_group_uuid:
    description: The unique identifier of the nPod group this nPod will be added to
    type: str
    required: false
  spus:
    description: List of SPU configuration information that will be used in the new nPod
    type: list
    required: false
    elements: dict
    suboptions:
      spu_serial:
        description: Specifies the SPU serial number
        type: str
        required: false
      ip_info_config:
        description: Allows configuring the SPUs network interfaces
        type: list
        required: false
        elements: dict
        suboptions:
          dhcp:
            description: Specifies if DHCP should be used for the data network
            type: bool
            required: false
          bond_mode:
            description: Link aggregation mode for the data interfaces
            type: str
            choices:
              - BondModeNone
              - BondMode8023ad
              - BondModeBalanceALB
            required: false
            default: BondMode8023ad
          interfaces:
            description: List of interfaces to include in the configuration
            type: list
            elements: str
            required: false
          address:
            description: IPv4 or IPv6 address if static IP address is used
            type: str
            required: false
          netmask_bits:
            description: Netmask in bits if static IP address is used
            type: int
            required: false
          gateway:
            description: Gateway IP address if static IP address is used
            type: str
            required: false
          half_duplex:
            description: Specifies if the network interface shall use half duplex
            type: bool
            required: false
            default: false
          speed_mb:
            description: Allows overwriting interface speed
            type: int
            required: false
          locked_speed:
            description: Allows locking interface speed
            type: bool
            required: false
          mtu:
            description: Allows specifying MTU
            type: int
            required: false
          bond_transmit_hash_policy:
            description: Allows specifying the transmit hashing policy
            type: str
            choices:
              - TransmitHashPolicyLayer2
              - TransmitHashPolicyLayer34
              - TransmitHashPolicyLayer23
            required: false
            default: TransmitHashPolicyLayer34
          bond_mii_monitor_ms:
            description: >-
              Allows alerting the default media independent interface monitoring
              interval
            type: int
            required: false
          bond_lacp_transmit_rate:
            description: Allows altering the default LACP transmit rate
            type: str
            choices:
              - LACPTransmitRateSlow
              - LACPTransmitRateFast
            required: false
            default: LACPTransmitRateFast
  npod_template_uuid:
    description: The unique identifier of the nPod template
    type: str
    required: false
  note:
    description: An optional note for the new nPod
    type: str
    required: false
  timezone:
    description: The timezone to be configured for all SPUs in the nPod
    type: str
    required: false
  ignore_warnings:
    description: To proceed even if nebulon ON reports warnings
    type: bool
    required: false
    default: false
  state:
    description: Defines the intended state for the nPod volume
    type: str
    choices:
      - present
      - absent
    required: true
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Create new nPod
  nebulon.nebulon_on.neb_npod:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: my_pod
    npod_group_uuid: 4bc34bf2-3c09-49bd-85de-a03aaeb3d17f
    spus:
      - spu_serial: 0123B1A5586FD38CEE
        ip_info_config:
          - dhcp: false
            bond_mode: BondModeNone
            interfaces:
              - enP8p1s0f0np0
            address: 192.168.1.100
            netmask_bits: 0
            gateway: 192.168.1.1
            half_duplex: false
            speed_mb: 100
            locked_speed: false
            mtu: 1500
            bond_transmit_hash_policy: TransmitHashPolicyLayer2
            bond_mii_monitor_ms: 100
            bond_lacp_transmit_rate: LACPTransmitRateSlow
    npod_template_uuid: e90cba40-805a-4bcc-8c4b-99dcf87377d3
    note: npod-note
    timezone: US/Pacific
    ignore_warnings: true
    state: present

- name: Delete existing nPod
  nebulon.nebulon_on.neb_npod:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    name: my_npod
    state: absent
"""

RETURN = r"""
npod:
  description: The detailed information of a nPod
  returned: always
  type: dict
  contains:
    uuid:
      description: The unique identifier of the nPod
      type: str
      returned: always
    name:
      description: The name for the nPod
      type: str
      returned: always
    npod_group_uuid:
      description: The unique identifier of the nPod group this nPod belongs to
      type: str
      returned: always
    note:
      description: An optional note for the nPod
      type: str
      returned: always
    volume_uuids:
      description: List of volume identifiers defined in this nPod
      type: list
      elements: str
      returned: always
    volume_count:
      description: Number of volumes defined in this nPod
      type: int
      returned: always
    host_uuids:
      description: List of host identifiers part of this nPod
      type: list
      elements: str
      returned: always
    host_count:
      description: Number of hosts part of this nPod
      type: int
      returned: always
    spu_serials:
      description: List of serial numbers part of this nPod
      type: list
      elements: str
      returned: always
    spu_count:
      description: Number of spus part of this nPod
      type: int
      returned: always
    snapshot_uuids:
      description: List of snapshot identifiers defined in this nPod
      type: list
      elements: str
      returned: always
    update_history:
      description: List of updates performed on this nPod
      type: list
      elements: dict
      returned: always
      contains:
        update_id:
          description: The identifier of the update
          type: str
        packageName:
          description: The name of the package that is installed
          type: str
        start:
          description: Date and time when the update started
          type: str
        finish:
          description: Date and time when the update complete
          type: str
        success:
          description: Indicates if the update completed successfully
          type: bool
    npod_template_uuid:
      description: Unique identifier for the nPod template used during nPod creation
      type: str
      returned: always
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
        NPod,
        NPodFilter,
        StringFilter,
        NPodSpuInput,
        IPInfoConfigInput,
        CreateNPodInput,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None


def get_ip_info_list(ip_info_config_list):
    # type: (list) -> list[IPInfoConfigInput]
    """Retrives list of IPInfoConfigInput to be used to configure the SPUs network interfaces"""
    ip_info_list = []
    for ip_info in ip_info_config_list:
        ip_info_list.append(
            IPInfoConfigInput(
                dhcp=ip_info['dhcp'],
                bond_mode=ip_info['bond_mode'],
                interfaces=ip_info['interfaces'],
                address=ip_info['address'],
                netmask_bits=ip_info['netmask_bits'],
                gateway=ip_info['gateway'],
                half_duplex=ip_info['half_duplex'],
                speed_mb=ip_info['speed_mb'],
                locked_speed=ip_info['locked_speed'],
                mtu=ip_info['mtu'],
                bond_transmit_hash_policy=ip_info['bond_transmit_hash_policy'],
                bond_mii_monitor_ms=ip_info['bond_mii_monitor_ms'],
                bond_lacp_transmit_rate=ip_info['bond_lacp_transmit_rate']
            )
        )
    return ip_info_list


def get_spu_list(module):
    # type: (AnsibleModule) -> list[NPodSpuInput]
    """Retrive list of SPU configuration information that will be used in the new nPod."""
    spu_list = []
    for spu in module.params['spus']:
        spu_list.append(
            NPodSpuInput(
                spu_serial=spu['spu_serial'],
                spu_data_ips=get_ip_info_list(spu['ip_info_config'])
            )
        )
    return spu_list


def get_npod(module, client, npod_name):
    # type: (AnsibleModule, NebPyClient, str) -> NPod
    """Get the nPod that matches the specified name"""
    npod_list = client.get_npods(
        npod_filter=NPodFilter(
            name=StringFilter(
                equals=npod_name
            )
        )
    )
    if npod_list.filtered_count > 1:
        module.fail_json(
            msg=f"Found more than one nPod with name: {npod_name}")
    elif npod_list.filtered_count == 1:
        return npod_list.items[0]


def delete_npod(module, client, npod_uuid):
    # type: (AnsibleModule, NebPyClient, str) -> dict
    """Allows deletion of a nPod"""
    result = dict(
        changed=False
    )
    try:
        client.delete_npod(npod_uuid)
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    return result


def create_npod(module, client):
    # type: (AnsibleModule, NebPyClient) -> dict
    """Allows creating a new nPod"""
    result = dict(
        changed=False,
        npod=None,
    )
    try:
        new_npod = client.create_npod(
            create_npod_input=CreateNPodInput(
                name=module.params['name'],
                npod_group_uuid=module.params['npod_group_uuid'],
                spus=get_spu_list(module),
                npod_template_uuid=module.params['npod_template_uuid'],
                note=module.params['note'],
                timezone=module.params['timezone']
            ),
            ignore_warnings=module.params['ignore_warnings']
        )
    except Exception as err:
        module.fail_json(msg=str(err))

    result['changed'] = True
    result['npod'] = to_dict(new_npod)
    return result


def main():
    module_args = dict(
        name=dict(required=True, type='str'),
        npod_group_uuid=dict(required=False, type='str'),
        spus=dict(required=False, type='list', elements='dict', options=dict(
            spu_serial=dict(required=False, type='str'),
            ip_info_config=dict(required=False, type='list', elements='dict', options=dict(
                dhcp=dict(required=False, type='bool'),
                bond_mode=dict(required=False, choices=[
                               'BondModeNone', 'BondMode8023ad', 'BondModeBalanceALB'], default='BondMode8023ad'),
                interfaces=dict(required=False, type='list', elements='str'),
                address=dict(required=False, type='str'),
                netmask_bits=dict(required=False, type='int', default=0),
                gateway=dict(required=False, type='str'),
                half_duplex=dict(required=False, type='bool', default=False),
                speed_mb=dict(required=False, type='int'),
                locked_speed=dict(required=False, type='bool'),
                mtu=dict(required=False, type='int'),
                bond_transmit_hash_policy=dict(required=False, choices=['TransmitHashPolicyLayer2',
                                                                        'TransmitHashPolicyLayer34',
                                                                        'TransmitHashPolicyLayer23'], default='TransmitHashPolicyLayer34'),
                bond_mii_monitor_ms=dict(required=False, type='int'),
                bond_lacp_transmit_rate=dict(required=False, choices=[
                                             'LACPTransmitRateSlow', 'LACPTransmitRateFast'], default='LACPTransmitRateFast'),
            ))
        )),
        npod_template_uuid=dict(required=False, type='str'),
        note=dict(required=False, type='str'),
        timezone=dict(required=False, type='str', default=None),
        ignore_warnings=dict(required=False, type='bool', default=False),
        state=dict(required=True, choices=['present', 'absent']),
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

    npod = get_npod(module, client, module.params['name'])

    if module.params['state'] == 'absent':
        if npod is not None:
            result = delete_npod(module, client, npod.uuid)
    elif module.params['state'] == 'present':
        if npod is None:
            result = create_npod(module, client)
        else:
            result['npod'] = to_dict(npod)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
