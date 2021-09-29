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


from ansible.module_utils.basic import AnsibleModule
from nebpyclient import NebPyClient


__all__ = [
    "get_login_arguments",
    "get_client"
]


def get_login_arguments():
    # type: () -> dict
    """Get the parameters required to login to Nebulon ON"""
    return dict(
        neb_username=dict(required=True),
        neb_password=dict(required=True, no_log=True),
    )


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
