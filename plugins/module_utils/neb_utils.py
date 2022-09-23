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

import platform
import sys
import re
from enum import Enum
from ansible.module_utils.basic import (
    missing_required_lib,
)

# safe import of the Nebulon Python SDK
try:
    from nebpyclient import (
        NebPyClient,
        NPod,
        NPodFilter,
        UUIDFilter,
        Volume,
        VolumeFilter,
    )

except ImportError:
    pass


__all__ = [
    'get_npod',
    'get_volume',
    'validate_sdk',
    'to_dict',
]

RE_VERSION = "^([0-9]+)[.]([0-9]+)[.]([0-9]+)$"
RE_VERSION_OK = "^[*]|(([*]|[0-9]+|[[0-9]+-[0-9]+])([.]([*]|[0-9]+|[[0-9]+-[0-9]+])){1,2})$"


COMPATIBLE_SDK_VERSIONS = [
    "2.0.8",
]


def validate_sdk(module, version=None, import_error=None, ok_versions=None):
    # type (AnsibleModule, str, str, List[str]) -> None
    """Checks if a loaded nebulon SDK is compatible with a module"""

    # if the version is not provided, that means that the SDK
    # could not be loaded
    if version is None:
        module.fail_json(
            msg=missing_required_lib("nebpyclient"),
            error_details=str(import_error),
            error_class=type(import_error).__name__,
        )

    # make sure that we have a clean version string
    clean_version = version.strip()

    # if there is no explicit list of compatible versions
    # we use the standard supported versions
    if ok_versions is None and not _is_sdk_compatible(clean_version, COMPATIBLE_SDK_VERSIONS):
        module.fail_json(
            msg=incompatible_nebulon_sdk(clean_version, COMPATIBLE_SDK_VERSIONS),
            error_details=f"Compatible versions are {COMPATIBLE_SDK_VERSIONS}",
        )

    # if there is an explicit list of compatible versions
    # check against that list
    if ok_versions is not None and not _is_sdk_compatible(clean_version, ok_versions):
        module.fail_json(
            msg=incompatible_nebulon_sdk(clean_version, ok_versions),
            error_details=f"Compatible versions are {ok_versions}",
        )


def incompatible_nebulon_sdk(version, ok_versions):
    # type: (str, List[str]) -> str

    hostname = platform.node()
    executable = sys.executable
    ok_versions_str = ", ".join(ok_versions)
    return (
        f"Installed nebpyclient version ({version}) on {hostname}'s Python {executable} "
        "is incompatible with this module. The module requires one of the following "
        f"versions of the nebpyclient library installed: {ok_versions_str}. "
        "Please install one of the supported versions. If the required version "
        "is installed, but Ansible is using the wrong Python interpreter, "
        "please consult the documentation on ansible_python_interpreter"
    )


def _is_sdk_compatible(version, ok_versions):
    # type: (str, List[str]) -> bool

    # make sure that version has the right format
    version_check = re.compile(RE_VERSION)
    version_match = version_check.match(version)

    if version_match is None:
        raise ValueError(f'Provided version "{version}" is not valid')

    # regular expression for checking a pattern for defining a compatible
    # version
    ok_version_check = re.compile(RE_VERSION_OK)

    # supported_versions is a list of patterns that describe the supported
    # versions of the required Nebulon library. For example: 1.0.* matches with
    # all of 1.0.1, 1.0.2, ... 1.0.10. Whereas 1.0.[1-2] only matches with
    # 1.0.1 and 1.0.2.
    for supported_version in ok_versions:
        # check if the pattern is ok
        ok_version_match = ok_version_check.match(supported_version)
        if ok_version_match is None:
            raise ValueError(f'provided version pattern "{supported_version}" is not valid')

        # we need to modify the passed string as the '.' is supposed to be a
        # real '.' and not a wildcard character in a regular expression. We're
        # doing this only to make the passed parameter more legible, because
        # this will be shown to the user as part of an error message.
        regex_string = supported_version.replace('.', '[.]')

        # same thing for the '*', which is supposed to be a wildcard character
        # for any number (or possibly character if we eventually allow
        # something like '1.0.1a').
        regex_string = regex_string.replace('*', '([^.]+)')

        # now match the regular expression with the provided version string
        match_result = re.match(regex_string, version)

        if match_result:
            return True

    return False


def to_dict(src):
    # type: (any) -> dict | any
    """Returns an object as a dict"""

    result = {}
    if not hasattr(src, '__dict__'):
        return src

    fields = src.__dict__
    type_name = type(src).__name__

    for key in fields:

        # cleanup the key
        clean_key = key.replace(f'_{type_name}__', '')

        # convert Enums
        if isinstance(fields[key], Enum):
            result[clean_key] = fields[key].value
            continue

        # convert arrays / lists
        if isinstance(fields[key], list):
            result[clean_key] = [to_dict(i) for i in fields[key]]
            continue

        result[clean_key] = to_dict(fields[key])

    return result


def get_npod(client, npod_uuid):
    # type: (NebPyClient, str) -> NPod
    """Gets the definition for a nPod"""

    # search for the volume that matches the provided UUID
    npod_list = client.get_npods(
        npod_filter=NPodFilter(
            uuid=UUIDFilter(
                equals=npod_uuid
            )
        )
    )

    # raise an Exception if the volume is not uniquely identified.
    if npod_list.filtered_count != 1:
        raise Exception(f"nPod with UUID '{npod_uuid}' not identified")

    return npod_list.items[0]


def get_volume(client, volume_uuid):
    # type: (NebPyClient, str) -> Volume
    """Gets the definition for a volume"""

    # search for the volume that matches the provided UUID
    volume_list = client.get_volumes(
        volume_filter=VolumeFilter(
            uuid=UUIDFilter(
                equals=volume_uuid
            )
        )
    )

    # raise an Exception if the volume is not uniquely identified.
    if volume_list.filtered_count != 1:
        raise Exception(f"Volume with UUID '{volume_uuid}' not identified")

    return volume_list.items[0]
