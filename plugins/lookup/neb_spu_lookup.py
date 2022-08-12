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


from __future__ import absolute_import, division, print_function
from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

__metaclass__ = type

DOCUMENTATION = """
    name: neb_spu_lookup
    author:
        - Tobias Flitsch <tobias@nebulon.com>
    version_added: "1.2.2"
    short_description: Get SPU configuration from inventory for neb_npod module
    description:
        - This lookup gets SPU configuration information from your inventory
          and converts it to a structure that can be passed to the neb_npod
          module when creating a new nPod
        - It will first lookup in host variables and then for any other
          variables that are provided to the play
    options:
        _terms:
            description:
                - The name of the host group used for extracting variables
            required: True
        bond_mode:
            description: Lookup key for the bond_mode parameter
            type: str
            default: bond_mode
            required: False
        bond_lacp_transmit_rate:
            description: Lookup key for the bond_lacp_transmit_rate parameter
            type: str
            default: bond_lacp_transmit_rate
            required: False
        bond_transmit_hash_policy:
            description: Lookup key for the bond_transmit_hash_policy parameter
            type: str
            default: bond_transmit_hash_policy
            required: False
        dhcp:
            description: Lookup key for the dhcp parameter
            type: str
            default: dhcp
            required: False
        mtu:
            description: Lookup key for the mtu parameter
            type: str
            default: mtu
            required: False
        netmask_bits:
            description: Lookup key for the netmask_bits parameter
            type: str
            default: netmask_bits
            required: False
        spu_address:
            description: Lookup key for the address parameter
            type: str
            default: spu_address
            required: False
        spu_serial:
            description: Lookup key for the spu_serial parameter
            type: str
            default: spu_serial
            required: False
"""

EXAMPLES = """
- name: Basic usage
  ansible.builtin.debug:
    msg: "{{lookup('nebulon.nebulon_on.neb_spu_lookup', 'servers')}}"

- name: Custom lookup keys - mtu is looked with the 'my_mtu' key
  ansible.builtin.debug:
    msg: "{{lookup('nebulon.nebulon_on.neb_spu_lookup', 'all', mtu='my_mtu')}}"
"""

RETURN = """
_list:
    description:
        - Values for the spu parameter of the neb_npod module
    type: list
"""

display = Display()


def _try_lookup_key(key, primary=None, fallback=None):
    # type: (str, dict, dict) -> any
    """Lookup a value in a primary and fallback dictionary"""
    try:
        if primary is not None and key in primary:
            return primary[key]
        if fallback is not None and key in fallback:
            return fallback[key]
        return None

    # pylint: disable=broad-except
    except Exception:
        return None


LOOKUP_KEYS = [
    "bond_lacp_transmit_rate",
    "bond_mode",
    "bond_transmit_hash_policy",
    "dhcp",
    "mtu",
    "netmask_bits",
    "spu_address",
    "spu_serial",
]


def lookup_key_values(**kwargs):
    """Compile the lookup keys dictionary from plugin arguments"""
    lookup_keys = {}
    for key in LOOKUP_KEYS:
        lookup_keys[key] = key if key not in kwargs else kwargs[key]
        display.vvv(f"Lookup key for '{key}' is: '{lookup_keys[key]}'")

    return lookup_keys


class LookupModule(LookupBase):
    """SPU configuration information lookup module"""
    def run(self, terms, variables=None, **kwargs):

        # not sure if this is required, but let's make sure that we can
        # access the needed variables
        if variables is None:
            raise AnsibleError("Could not load variables")

        # make sure that there is one group name provided and that it exists
        if len(terms) == 0:
            raise AnsibleError("Host group not provided")

        for term in terms:
            if term not in variables["groups"]:
                raise AnsibleError(f"Host group {term} not found in inventory")

        # define the lookup keys
        lookup_keys = lookup_key_values(**kwargs)

        ret = []
        for group, hosts in variables["groups"].items():
            if group not in terms:
                continue

            display.vvv(f"Processing group {group}...")

            for host in hosts:
                if host not in variables["hostvars"].keys():
                    raise AnsibleError(f"Host {host} not found in hostvars")

                display.vvv(f"Processing host {host}...")
                host_vars = variables["hostvars"][host]

                # read the configuration properties for the host
                host_config = {}
                for key, lookup_key in lookup_keys.items():
                    host_config[key] = _try_lookup_key(
                        lookup_key, host_vars, variables["vars"]
                    )
                    display.vvv(f"Value for {lookup_key}: {host_config[key]}")

                # convert properties for a suitable input format
                # for the neb_npod module
                entry = {}
                entry["spu_serial"] = host_config["spu_serial"]
                entry["ip_info_config"] = []

                # depending on the bonding mode, we need to format the
                # structure of networking differently. First, handle non-bonded
                # interfaces.
                if_list = ["enP8p1s0f0np0", "enP8p1s0f1np1"]

                if host_config["bond_mode"] == "BondModeNone":
                    if_index = 0
                    for address in host_config["spu_address"].split(","):
                        ip_info_config = {}
                        ip_info_config["interfaces"] = [if_list[if_index]]
                        ip_info_config["address"] = address

                        optional_keys = [
                            "bond_mode",
                            "bond_lacp_transmit_rate",
                            "bond_transmit_hash_policy",
                            "dhcp",
                            "mtu",
                            "netmask_bits",
                        ]

                        for key in optional_keys:
                            if host_config[key] is not None:
                                ip_info_config[key] = host_config[key]

                        entry["ip_info_config"].append(ip_info_config)
                        if_index += 1

                else:
                    ip_info_config = {}
                    ip_info_config["interfaces"] = if_list
                    ip_info_config["address"] = host_config["spu_address"]

                    optional_keys = [
                        "bond_mode",
                        "bond_lacp_transmit_rate",
                        "bond_transmit_hash_policy",
                        "dhcp",
                        "mtu",
                        "netmask_bits",
                    ]

                    for key in optional_keys:
                        if host_config[key] is not None:
                            ip_info_config[key] = host_config[key]

                    entry["ip_info_config"].append(ip_info_config)

                ret.append(entry)

        return ret
