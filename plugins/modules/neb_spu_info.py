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
module: neb_spu_info
short_description: returns details for a Nebulon ON SPUs
description:
  - This module returns details for a Nebulon ON Services Processing Unit(SPU).
author:
  - Nebulon Team (@nebulon) <info@nebulon.com>
options:
  spu_serials:
    description: The serial numbers of the SPUs
    type: list
    elements: str
    required: true
  not_in_npod:
    description: Determines if returns SPUs that are allocated to a nPod
    type: bool
    required: false
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Get SPU info
  nebulon.nebulon_on.neb_spu_info:
    neb_user_name: nebulon_on_user
    neb_password: nebulon_on_password
    spu_serials:
      - 012355D3F69FF16FEE
    not_in_npod: false
"""

RETURN = r"""
spus:
  description: Information about requested SPUs.
  returned: always
  type: list
  elements: dict
  contains:
    npod_uuid:
      description: The services processing unit's nPod identifier
      returned: always
      type: str
    host_uuid:
      description: The unique identifier of the host the SPU is installed in
      returned: always
      type: str
    serial:
      description: The unique serial number of the SPU
      returned: always
      type: str
    version:
      description: The version of nebOS that is running on the SPU
      returned: always
      type: str
    spu_type:
      description: The type of SPU
      returned: always
      type: str
    hw_revision:
      description: The hardware revision of the SPU
      returned: always
      type: str
    control_interface:
      description: Network information for the control interface
      returned: always
      type: dict
      contains:
        dhcp:
          description: Indicates if DHCP is used for IP addressing
          returned: always
          type: bool
        addresses:
          description: List of IPv4 or IPv6 addresses in CIDR format
          returned: always
          type: list
          elements: str
        gateway:
          description: The gateway IP address specified for the interface
          returned: always
          type: str
        bond_mode:
          description: The link aggregation mode for the interface
          returned: always
          type: str
        bond_transmit_hash_policy:
          description: The active transmit hash policy for the link aggregation
          returned: always
          type: str
        bond_mii_monitor_milli_seconds:
          description: The active MII monitoring interval in ms for the link aggregation
          returned: always
          type: int
        bond_lacp_transmit_rate:
          description: The active LACP transmit rate for the link aggregation
          returned: always
          type: str
        interface_names:
          description: The names of the physical interfaces for the logical interface
          returned: always
          type: list
          elements: str
        interface_mac:
          description: The physical address of the interface
          returned: always
          type: str
        half_duplex:
          description: Indicates if the interface operates in half-duplex
          returned: always
          type: bool
        speed:
          description: Indicates the network interface speed
          returned: always
          type: int
        locked_speed:
          description: Indicates if the network interface speed is locked
          returned: always
          type: bool
        mtu:
          description: maximum transfer unit
          returned: always
          type: int
        switch_name:
          description: The name of the switch this interface connects to
          returned: always
          type: str
        switch_port:
          description: The port identifier of the switch this interface connects to
          returned: always
          type: str
    data_interfaces:
      description: Network information for the data interfaces
      returned: always
      type: list
      elements: dict
      contains:
        dhcp:
          description: Indicates if DHCP is used for IP addressing
          returned: always
          type: bool
        addresses:
          description: List of IPv4 or IPv6 addresses in CIDR format
          returned: always
          type: list
          elements: str
        gateway:
          description: The gateway IP address specified for the interface
          returned: always
          type: str
        bond_mode:
          description: The link aggregation mode for the interface
          returned: always
          type: str
        bond_transmit_hash_policy:
          description: The active transmit hash policy for the link aggregation
          returned: always
          type: str
        bond_mii_monitor_milli_seconds:
          description: The active MII monitoring interval in ms for the link aggregation
          returned: always
          type: int
        bond_lacp_transmit_rate:
          description: The active LACP transmit rate for the link aggregation
          returned: always
          type: str
        interface_names:
          description: The names of the physical interfaces for the logical interface
          returned: always
          type: list
          elements: str
        interface_mac:
          description: The physical address of the interface
          returned: always
          type: str
        half_duplex:
          description: Indicates if the interface operates in half-duplex
          returned: always
          type: bool
        speed:
          description: Indicates the network interface speed
          returned: always
          type: int
        locked_speed:
          description: Indicates if the network interface speed is locked
          returned: always
          type: bool
        mtu:
          description: maximum transfer unit
          returned: always
          type: int
        switch_name:
          description: The name of the switch this interface connects to
          returned: always
          type: str
        switch_port:
          description: The port identifier of the switch this interface connects to
          returned: always
          type: str
    lun_uuids:
      description: List of unique identifiers of LUNs provisioned on the SPU
      returned: always
      type: str
    lun_count:
      description: Number of provisioned LUNs on the SPU
      returned: always
      type: int
    physical_drive_wwns:
      description: List of WWNs for all physical drives attached to the SPU
      returned: always
      type: list
      elements: str
    physical_drive_count:
      description: Number of physical drives attached to the SPU
      returned: always
      type: int
    npod_member_can_talk_count:
      description: Number of SPUs that can successfully communicate with each other
      returned: always
      type: int
    uptime_seconds:
      description: Uptime of the services processing unit in seconds
      returned: always
      type: int
    update_history:
      description: List of historical updates that were applied to the SPU
      returned: always
      type: list
      elements: dict
      contains:
        update_id:
          description: The identifier of the update
          returned: always
          type: str
        package_name:
          description: The name of the package that is installed
          returned: always
          type: str
        start:
          description: Date and time when the update started
          returned: always
          type: str
        finish:
          description: Date and time when the update completed
          returned: always
          type: str
        success:
          description: Indicates if the update completed successfully
          returned: always
          type: bool
    last_reported:
      description: Date and time when the SPU last reported state to Nebulon ON
      returned: always
      type: str
    reset_reason_int:
      description: A int representation of the reason why a SPU was reset
      returned: always
      type: int
    reset_reason_string:
      description: A string representation of the reason why a SPU was reset
      returned: always
      type: str
    ntp_servers:
      description: List of configured NTP servers
      returned: always
      type: list
      elements: dict
      contains:
        server_hostname:
          description: The DNS hostname of the NTP server
          returned: always
          type: str
        pool:
          description: Indicates if the specified NTP server hostname is a NTP pool
          returned: always
          type: bool
        prefer:
          description: Indicates if the specified NTP server is the preferred NTP server
          returned: always
          type: bool
    ntp_status:
      description: Status message for NTP
      returned: always
      type: str
    time_zone:
      description: The configured time zone
      returned: always
      type: str
    uefi_version:
      description: Version for UEFI
      returned: always
      type: str
    wiping:
      description: Indicates if the SPU is doing a secure wipe
      returned: always
      type: str
"""

from ansible_collections.nebulon.nebulon_on.plugins.module_utils.class_utils import to_dict
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import get_client, get_login_arguments
from ansible.module_utils.basic import AnsibleModule
from nebpyclient import SpuFilter, StringFilter, PageInput


def get_spu_info_list(module, client):
    # type: (AnsibleModule, NebPyClient) -> list[dict]
    """Retrieves a list of SPUs"""
    spu_info_list = []
    page_number = 1
    while True:
        spu_list = client.get_spus(
            page=PageInput(page=page_number),
            spu_filter=SpuFilter(
                serial=StringFilter(
                    in_list=module.params['spu_serials']
                ),
                and_filter=SpuFilter(
                    not_in_npod=module.params['not_in_npod'],
                )
            )
        )
        for i in range(len(spu_list.items)):
            spu_info_list.append(to_dict(spu_list.items[i]))
        if not spu_list.more:
            break
        page_number += 1

    return spu_info_list


def main():
    module_args = dict(
        spu_serials=dict(required=True, type='list', elements='str'),
        not_in_npod=dict(required=False, type='bool', default=None)
    )
    module_args.update(get_login_arguments())

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        spus=[]
    )

    client = get_client(module)

    result['spus'] = get_spu_info_list(module, client)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
