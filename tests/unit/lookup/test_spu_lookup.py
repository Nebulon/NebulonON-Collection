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

__metaclass__ = type

import unittest
from ansible.errors import AnsibleError

# pylint: disable=no-name-in-module,import-error
from ansible_collections.nebulon.nebulon_on.plugins.lookup.neb_spu_lookup import (
    LookupModule,
    LOOKUP_KEYS,
    lookup_key_values,
)
# pylint: enable=no-name-in-module,import-error


#
# MOCK SECTION
#
# The following setup is used for testing the lookup module by compiling
# a data structure that would natively be done by Ansible and passed into
# the lookup plugin.

# mock data for a configuration without bonding
mock_server_nobond = dict(
    bond_mode="BondModeNone",
    dhcp=False,
    mtu=1500,
    netmask_bits=22,
    spu_address="10.100.10.11,10.100.10.12",
    spu_serial="SPUSERIALSPUSERIAL",
)

# mock data for a configuration with LACP bonding
mock_server_lacp = dict(
    bond_lacp_transmit_rate="LACPTransmitRateFast",
    bond_mode="BondMode8023ad",
    bond_transmit_hash_policy="TransmitHashPolicyLayer34",
    dhcp=False,
    mtu=1500,
    netmask_bits=22,
    spu_address="10.100.10.11",
    spu_serial="SPUSERIALSPUSERIAL",
)

mock_vars = dict(groups={}, hostvars={}, vars={})
mock_vars["groups"]["lacp"] = []
mock_vars["groups"]["nobond"] = []

for host in ["host1", "host2", "host3"]:
    mock_vars["groups"]["lacp"].append(host)
    mock_vars["hostvars"][host] = mock_server_lacp

for host in ["host4", "host5", "host6"]:
    mock_vars["groups"]["nobond"].append(host)
    mock_vars["hostvars"][host] = mock_server_nobond


class TestLookupKeyValues(unittest.TestCase):
    """Test class for validating key lookups"""

    def test_lookup_mapping_without_parameter(self):
        """Test lookup without any key customization"""
        result = lookup_key_values()

        for key, value in result.items():
            self.assertEqual(key, value)

    def test_lookup_mapping_with_parameters(self):
        """Test lookup with key customization"""
        new_keys = {}
        for key in LOOKUP_KEYS:
            new_keys[key] = f"{key}_modified"

        result = lookup_key_values(**new_keys)

        for key, lookup_key in result.items():
            self.assertEqual(lookup_key, f"{key}_modified")


class TestSPULookupModule(unittest.TestCase):
    """Test class for testing inventory lookups"""

    def setUp(self) -> None:
        self.module = LookupModule()

    def test_host_group_not_provided(self):
        """Test for an error when there is no host group"""
        try:
            self.module.run(terms=[], variables=mock_vars)
            self.fail("Lookup didn't fail when host group was not provided.")

        except AnsibleError:
            pass

    def test_invalid_host_group(self):
        """Test for an error when an invalid host group is provided"""
        try:
            self.module.run(
                terms=["invalid_host_group"], variables=mock_vars,
            )
            self.fail("Lookup didn't fail when invalid host group provided")

        except AnsibleError:
            pass

    def test_create_nobond_configuration_from_hostvars(self):
        """Test lookup of configuration without a bonded configuration"""

        result = self.module.run(terms=["nobond"], variables=mock_vars,)

        self.assertEqual(len(mock_vars["groups"]["nobond"]), len(result))

        for config in result:
            self.assertEqual(mock_server_nobond["spu_serial"], config["spu_serial"])
            self.assertEqual(2, len(config["ip_info_config"]))

            # two separate IP configurations
            for inf in range(0, 1):

                net = config["ip_info_config"][inf]
                self.assertEqual("enP8p1s0f0np0", net["interfaces"][0])
                self.assertEqual("BondModeNone", net["bond_mode"])
                self.assertEqual(
                    mock_server_nobond["spu_address"].split(",", maxsplit=1)[inf],
                    net["address"],
                )
                self.assertEqual(
                    mock_server_nobond["dhcp"], net["dhcp"],
                )
                self.assertEqual(
                    mock_server_nobond["mtu"], net["mtu"],
                )
                self.assertEqual(
                    mock_server_nobond["netmask_bits"], net["netmask_bits"],
                )

    def test_create_lacp_configuration_from_hostvars(self):
        """Test lookup of configuration with a LACP bonded configuration"""

        result = self.module.run(terms=["lacp"], variables=mock_vars,)

        self.assertEqual(len(mock_vars["groups"]["lacp"]), len(result))

        for config in result:
            self.assertEqual(mock_server_nobond["spu_serial"], config["spu_serial"])
            self.assertEqual(1, len(config["ip_info_config"]))

            # two separate IP configurations
            inf = 0

            net = config["ip_info_config"][inf]
            self.assertEqual("enP8p1s0f0np0", net["interfaces"][0])
            self.assertEqual("BondMode8023ad", net["bond_mode"])
            self.assertEqual(
                mock_server_nobond["spu_address"].split(",", maxsplit=1)[inf],
                net["address"],
            )
            self.assertEqual(
                mock_server_nobond["dhcp"], net["dhcp"],
            )
            self.assertEqual(
                mock_server_nobond["mtu"], net["mtu"],
            )
            self.assertEqual(
                mock_server_nobond["netmask_bits"], net["netmask_bits"],
            )
