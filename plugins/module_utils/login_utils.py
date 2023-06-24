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

import sys
import os
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    validate_sdk,
)

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

__all__ = [
    "get_login_arguments",
    "get_client"
]

COMPATIBLE_SDK_VERSIONS = [
    "2.0.8",
    "2.0.10",
]
REQ_PYTHON_VERSION_MAJOR = 3
REQ_PYTHON_VERSION_MINOR = 6

# Need to statically provide the collection version here as the standard files
# where this information can be collected from won't be sent to the remote
# machine.
COLLECTION_VERSION = '1.4.1'


def get_login_arguments():
    # type: () -> dict
    """Get the parameters required to log in to Nebulon ON"""
    return dict(
        neb_username=dict(required=True, type='str'),
        neb_password=dict(required=True, type='str', no_log=True),
    )


def is_python_compatible(module, major_version, minor_version):
    # type: (AnsibleModule, int, int) -> None
    """Checks if the installed Python version is compatible with the requirement"""
    if major_version <= REQ_PYTHON_VERSION_MAJOR and minor_version < REQ_PYTHON_VERSION_MINOR:

        err_msg = "The Nebulon Ansible Collection requires Python version"
        err_msg += f" {REQ_PYTHON_VERSION_MAJOR}.{REQ_PYTHON_VERSION_MINOR} or higher."
        err_msg += f" Your current version is {major_version}.{minor_version}."
        module.fail_json(msg=err_msg)


def get_client(module):
    # type: (AnsibleModule) -> NebPyClient
    """Setup nebulon ON connection"""

    # read credentials from module parameters
    neb_username = module.params['neb_username']
    neb_password = module.params['neb_password']

    # fail the module gracefully when the required credentials are not there
    if neb_username is None or neb_password is None:
        module.fail_json(msg="username and password must be provided")

    # setup ansible identity for the audit log. The resulting entry will be:
    # <client>/<ansible version>,<collection version>
    client_name = 'ansible'
    client_version = f'{module.ansible_version},{COLLECTION_VERSION}'

    # check for Python compatibility
    is_python_compatible(module, sys.version_info.major, sys.version_info.minor)

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
        ok_versions=COMPATIBLE_SDK_VERSIONS,
    )

    try:

        # try signing in to nebulon ON, will raise an Exception on failure
        client = NebPyClient(
            username=neb_username,
            password=neb_password,
            client_name=client_name,
            client_version=client_version,
            verbose=False,
        )

        # login succeeded, return the client
        return client

    # pylint: disable=broad-except
    except Exception as err:
        # return the error message from nebulon ON
        module.fail_json(
            msg="Login failed",
            error_details=str(err),
            error_class=type(err).__name__,
        )
