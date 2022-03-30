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

from ansible.module_utils.basic import AnsibleModule
import nebpyclient
import sys
from nebpyclient import NebPyClient

__all__ = [
    "get_login_arguments",
    "get_client"
]

REQUIRED_NEB_SDK_VERSION = "1.0.15"
REQ_PYTHON_VERSION_MAJOR = 3
REQ_PYTHON_VERSION_MINOR = 6


def get_login_arguments():
    # type: () -> dict
    """Get the parameters required to login to Nebulon ON"""
    return dict(
        neb_username=dict(required=True),
        neb_password=dict(required=True, no_log=True),
    )


def is_python_compatible(module, major_version, minor_version):
    # type: (AnsibleModule, int, int) -> None
    """Checks if the installed Python version is compatible with the requirement"""
    if major_version <= REQ_PYTHON_VERSION_MAJOR and minor_version < REQ_PYTHON_VERSION_MINOR:
        version_string = f"{major_version}.{minor_version}"
        module.fail_json(msg=f"The Nebulon Ansible Collection requires Python "
                         f"{REQ_PYTHON_VERSION_MAJOR}.{REQ_PYTHON_VERSION_MINOR} or "
                         f"higher, Your current version is {version_string}. Please install supported version.")


def get_client(module):
    # type: (AnsibleModule) -> NebPyClient
    """Setup nebulon ON connection"""

    # read credentials from module parameters
    neb_username = module.params['neb_username']
    neb_password = module.params['neb_password']

    # fail the module gracefully when the required credentials are not there
    if neb_username is None or neb_password is None:
        module.fail_json(msg="username and password must be provided")

    # setup ansible identity for the audit log
    client_name = 'ansible'
    client_version = module.ansible_version

    # check for Python compatibility
    is_python_compatible(module, sys.version_info.major, sys.version_info.minor)

    # check for Nebulon SDK compatibility
    installed_sdk_version = nebpyclient.__version__.strip()
    if REQUIRED_NEB_SDK_VERSION != installed_sdk_version:
        module.fail_json(msg="The Nebulon Ansible Collection depends on the Python library nebpyclient version " +
                             REQUIRED_NEB_SDK_VERSION + ". Your current version is " + installed_sdk_version +
                             ". Please install the supported version with 'python3 -m pip install nebpyclient=" +
                             REQUIRED_NEB_SDK_VERSION + "'")

    try:

        # try signing in to nebulon ON, will raise an Exception on failure
        client = NebPyClient(
            username=neb_username,
            password=neb_password,
            client_name=client_name,
            client_version=client_version,
            verbose=False
        )

        # login succeeded, return the client
        return client

    except Exception as err:
        # return the error message from nebulon ON
        module.fail_json(msg=str(err))
