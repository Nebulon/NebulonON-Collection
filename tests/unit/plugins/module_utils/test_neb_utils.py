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

# pylint: disable=import-error,no-name-in-module
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    validate_sdk,
)
# pylint: enable=import-error,no-name-in-module


class MockModule(dict):
    failed = False

    def exit_json(self, **kwargs):
        self.failed = False

    def fail_json(self, **kwargs):
        self.failed = True


class TestLibraryCheck(unittest.TestCase):
    """Test class to validate nebpyclient library version checks"""

    def test_version_simple_match(self):
        """A simple test to match versions exactly"""
        version = '1.0.0'
        supported_versions = [
            '1.0.0'
        ]
        mock_module = MockModule()
        validate_sdk(
            module=mock_module,
            version=version,
            ok_versions=supported_versions
        )
        self.assertFalse(mock_module.failed)

    def test_version_simple_list(self):
        """A simple test to check version in a list"""
        version = '1.0.1'
        supported_versions = [
            '1.0.0',
            '1.0.1',
            '1.0.2',
        ]
        mock_module = MockModule()
        validate_sdk(
            module=mock_module,
            version=version,
            ok_versions=supported_versions
        )
        self.assertFalse(mock_module.failed)

    def test_version_range(self):
        """A test to check version in a range"""
        version = '1.0.0'
        supported_versions = [
            '1.0.[0-10]'
        ]
        mock_module = MockModule()
        validate_sdk(
            module=mock_module,
            version=version,
            ok_versions=supported_versions
        )
        self.assertFalse(mock_module.failed)

    def test_version_wildcard(self):
        """A test to check for a wildcard pattern"""
        version = '1.0.0'
        supported_versions = [
            '1.0.*'
        ]
        mock_module = MockModule()
        validate_sdk(
            module=mock_module,
            version=version,
            ok_versions=supported_versions
        )
        self.assertFalse(mock_module.failed)

    def test_version_incompatible(self):
        """A test to check for incompatibility"""
        version = '3.0.0'
        supported_versions = [
            '1.*.*'
        ]
        mock_module = MockModule()
        validate_sdk(
            module=mock_module,
            version=version,
            ok_versions=supported_versions
        )
        self.assertTrue(mock_module.failed)

    def test_invalid_version_pattern(self):
        """A test to check that an error is raised for invalid versions"""

        version = '3..0'
        supported_versions = [
            '1.*.*'
        ]
        mock_module = MockModule()
        try:
            validate_sdk(
                module=mock_module,
                version=version,
                ok_versions=supported_versions
            )
            self.fail(msg="Value Error not raised with invalid version")

        except ValueError:
            pass

    def test_invalid_version_ok_pattern(self):
        """A test to check that an error is raised for invalid versions"""

        version = '1.0.0'
        supported_versions = [
            '1.10.',
        ]
        mock_module = MockModule()
        try:
            validate_sdk(
                module=mock_module,
                version=version,
                ok_versions=supported_versions
            )
            self.fail(msg="Value Error not raised with invalid version")

        except ValueError:
            pass
