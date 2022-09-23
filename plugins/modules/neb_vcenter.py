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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: neb_vcenter
short_description: Configure Nebulon vCenter integration
description:
  - This module configures the Nebulon vCenter integration for a nPod that is
    used for collecting application statistics and optimal workload placement
    for virtual machines.
author:
  - Tobias Flitsch (@tflitsch) <tobias@nebulon.com>
options:
  npod_name:
    description: The name of the nPod for which to enable the integration
    type: str
    required: true
  vcenter_username:
    description: The vCenter username to use for the integration
    type: str
    required: false
  vcenter_password:
    description: The vCenter password to use for the provided username
    type: str
    required: false
  vcenter_network_identity:
    description: The IP address or hostname for the vCenter instance
    type: str
    required: false
  vcenter_ssl_port:
    description: The vCenter network port to use for HTTPS
    type: int
    required: false
    default: 443
  enable_affinity_rules:
    description: Enable the vCenter affinity rules to optimize VM placement
    required: false
    type: bool
    default: false
  insecure:
    description: Trust the self-signed certificates of the vCenter instance
    required: false
    type: bool
    default: false
  state:
    description: Enable or disable the vCenter integration
    required: false
    type: str
    choices:
      - present
      - absent
    default: present
notes:
  - When enabling the vCenter integration, all of C(vcenter_username),
    C(vcenter_password), C(vcenter_network_identity) are required. When disabling
    the integration, these fields are optional.
  - Since the Nebulon cloud does not know the user provided passwords, it can
    not determine if it is already set, rendering this module not idempotent.
    In effect, this means that if the state is C(present) it will always update
    the vCenter integration with the provided password.
extends_documentation_fragment:
  - nebulon.nebulon_on.login_util_options
"""

EXAMPLES = r"""
- name: Enable the vCenter integration with all options enabled
  nebulon.nebulon_on.neb_vcenter:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_name: my_vcenter_npod
    vcenter_username: administrator@vsphere.local
    vcenter_password: S3cureP@ssword!
    vcenter_network_identity: myvcenter.nebulon.com
    vcenter_ssl_port: 443
    enable_affinity_rules: true
    state: present

- name: Disable vCenter integration
  nebulon.nebulon_on.neb_vcenter:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_name: my_vcenter_npod
    state: absent

- name: Enable the vCenter integration without affinity rules
  nebulon.nebulon_on.neb_vcenter:
    neb_username: nebulon_on_user
    neb_password: nebulon_on_password
    npod_name: my_vcenter_npod
    vcenter_username: administrator@vsphere.local
    vcenter_password: S3cureP@ssword!
    vcenter_network_identity: mycenter.nebulon.com
    state: present
"""

RETURN = r"""
vcenter_username:
  description: The configured vCenter username
  returned: if present
  type: str
vcenter_network_identity:
  description: The configured IP address or hostname for the vCenter instance
  returned: if present
  type: str
vcenter_ssl_port:
  description: The configured vCenter network port to use
  returned: if present
  type: int
enable_affinity_rules:
  description: If the vCenter affinity rules are enabled
  returned: if present
  type: bool
state:
  description: The current state for the vCenter integration for the nPod
  returned: always
  type: str
"""

# pylint: disable=wrong-import-position,import-error,no-name-in-module
import traceback
import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.login_utils import (
    get_client,
    get_login_arguments,
)
from ansible_collections.nebulon.nebulon_on.plugins.module_utils.neb_utils import (
    validate_sdk,
)

try:
    from nebpyclient import (
        NebPyClient,
        NPod,
        NPodFilter,
        StringFilter,
        VsphereCredentials,
        VsphereCredentialsFilter,
        UpsertVsphereCredentialsInput,
        UUIDFilter,
        __version__,
    )

except ImportError:
    NEBULON_SDK_VERSION = None
    NEBULON_IMPORT_ERROR = traceback.format_exc()

else:
    NEBULON_SDK_VERSION = __version__.strip()
    NEBULON_IMPORT_ERROR = None
# pylint: enable=import-error,no-name-in-module,line-too-long

# maximum time we wait for the SPU to report its new status to the cloud
NEBULON_UPDATE_TIMEOUT_SEC = 3 * 60


def get_npod(client, npod_name):
    # type: (NebPyClient, str) -> NPod
    """Get the nPod that matches the specified name"""
    # search for the nPod by the provided name
    npod_list = client.get_npods(
        npod_filter=NPodFilter(
            name=StringFilter(
                equals=npod_name
            )
        )
    )
    # found exactly one nPod that matches the name
    if npod_list.filtered_count == 1:
        return npod_list.items[0]

    # this should only be reached when the nPod does not exist at all. More
    # than 1 nPods can not be found as the nPod names are unique within one
    # customer organization.
    raise Exception(f"nPod with name '{npod_name}' could not be identified.")


def get_vcenter_integration(client, npod_uuid):
    # type: (NebPyClient, str) -> VsphereCredentials | None
    """Get the vCenter integration for a nPod"""
    vsphere_credentials = client.get_vsphere_credentials(
        credential_filter=VsphereCredentialsFilter(
            npod_uuid=UUIDFilter(
                equals=npod_uuid,
            )
        )
    )
    # found exactly one configuration that matches the provided UUID
    if vsphere_credentials.filtered_count == 1:
        return vsphere_credentials.items[0]

    # this should only be reached when the nPod does not have a vCenter
    # configuration. The calling function needs to check for None.
    return None


def delete_vcenter_integration(client, npod_uuid):
    # type: (NebPyClient, str) -> None
    """Delete the vCenter integration for an nPod"""
    client.delete_vsphere_credentials(
        npod_uuid=npod_uuid
    )

    # validate that it is really gone by querying the cloud if it still
    # has the vCenter integration information.
    nap_time = NEBULON_UPDATE_TIMEOUT_SEC

    while nap_time > 0:
        vcenter_integration = get_vcenter_integration(
            client=client,
            npod_uuid=npod_uuid,
        )

        # if the deletion was successful, the vcenter_integration variable
        # should be None, otherwise it wasn't fully deleted
        if vcenter_integration is None:
            return

        # try again after 5 seconds
        nap_time = nap_time - 5
        time.sleep(5)

    raise Exception("Disabling vCenter integration timed out")


def get_vcenter_url(vcenter_network_identity, vcenter_ssl_port):
    # type: (str, int) -> str
    """Generates the vCenter URL from user parameters"""

    # compile a reasonable URL that doesn't show the default HTTPS port
    if vcenter_ssl_port == 443:
        return f"https://{vcenter_network_identity}"

    return f"https://{vcenter_network_identity}:{vcenter_ssl_port}"


def update_vcenter_integration(
        client,
        npod_uuid,
        vcenter_username,
        vcenter_password,
        vcenter_network_identity,
        vcenter_ssl_port=443,
        enable_affinity_rules=False,
        insecure=False):
    # type: (NebPyClient, str, str, str, str, int, bool) -> VsphereCredentials
    """Configure the vCenter integration for an nPod"""

    # compile the vCenter URL
    url = get_vcenter_url(
        vcenter_network_identity=vcenter_network_identity,
        vcenter_ssl_port=vcenter_ssl_port,
    )

    credentials_input = UpsertVsphereCredentialsInput(
        username=vcenter_username,
        password=vcenter_password,
        url=url,
        insecure=insecure,
        enable_vmhost_affinity=enable_affinity_rules,
    )

    client.set_vsphere_credentials(
        npod_uuid=npod_uuid,
        credentials_input=credentials_input,
    )

    # validate that it is really there
    nap_time = NEBULON_UPDATE_TIMEOUT_SEC

    while nap_time > 0:
        vcenter_integration = get_vcenter_integration(
            client=client,
            npod_uuid=npod_uuid,
        )

        if vcenter_integration is not None:
            # TODO: Test that the changes were made
            return vcenter_integration

        # try again after 5 seconds
        nap_time = nap_time - 5
        time.sleep(5)

    raise Exception("Enabling vCenter integration timed out")


def main():
    """Main entry point"""

    # setup the Ansible module arguments
    module_args = dict(
        npod_name=dict(
            required=True,
            type='str',
        ),
        vcenter_username=dict(
            required=False,
            type='str',
        ),
        vcenter_password=dict(
            required=False,
            type='str',
            no_log=True,
        ),
        vcenter_network_identity=dict(
            required=False,
            type='str',
        ),
        vcenter_ssl_port=dict(
            required=False,
            type='int',
            default=443,
        ),
        enable_affinity_rules=dict(
            required=False,
            type='bool',
            default=False,
        ),
        insecure=dict(
            required=False,
            type='bool',
            default=False,
        ),
        state=dict(
            required=False,
            choices=['present', 'absent'],
            default='present',
        ),
    )
    # append the standard login arguments to the module
    module_args.update(get_login_arguments())

    # set up the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            (
                'state',
                'present', [
                    'vcenter_username',
                    'vcenter_password',
                    'vcenter_network_identity',
                ],
                True
            ),
        ]
    )

    # check for Nebulon SDK compatibility
    validate_sdk(
        module=module,
        version=NEBULON_SDK_VERSION,
        import_error=NEBULON_IMPORT_ERROR,
    )

    # read the module parameters
    npod_name = module.params['npod_name']
    vcenter_username = module.params['vcenter_username']
    vcenter_password = module.params['vcenter_password']
    vcenter_network_identity = module.params['vcenter_network_identity']
    vcenter_ssl_port = module.params['vcenter_ssl_port']
    enable_affinity_rules = module.params['enable_affinity_rules']
    insecure = module.params['insecure']
    desired_state = module.params['state']

    # initialize the result.
    result = dict(
        changed=False,
    )

    # login and connect the nebulon ON client
    client = get_client(module)

    try:
        # try to find the nPod with the name the user provided. This will
        # throw an exception if the nPod is not found
        npod = get_npod(client, npod_name)

        # check the current state of the system in regard to vCenter integration.
        vcenter_integration = get_vcenter_integration(
            client=client,
            npod_uuid=npod.uuid,
        )

        if desired_state == 'absent':
            # integration should not be enabled

            if vcenter_integration is None:
                # the desired state is already set, so we can exit here. This is
                # also the case when the module is called with check_mode
                result['changed'] = False
                result['state'] = 'absent'
                module.exit_json(**result)

            # handle check_mode
            if module.check_mode:
                result['changed'] = True
                result['state'] = 'absent'
                result['msg'] = "Would remove the vCenter integration"
                module.exit_json(**result)

            # disable the vCenter integration. If it fails, this will raise an
            # exception, so we don't have to check for anything here
            delete_vcenter_integration(
                client=client,
                npod_uuid=npod.uuid,
            )

            result['changed'] = True
            result['state'] = 'absent'
            module.exit_json(**result)

        # we need to change the state every time the user wants to enable the
        # integration since we can not compare the passwords
        if module.check_mode:
            result['changed'] = True
            result['state'] = 'present'
            result['vcenter_username'] = vcenter_username
            result['vcenter_network_identity'] = vcenter_network_identity
            result['vcenter_ssl_port'] = vcenter_ssl_port
            result['insecure'] = insecure
            result['enable_affinity_rules'] = enable_affinity_rules
            module.exit_json(**result)

        # update the vCenter integration. This will raise an Exception if it
        # didn't work, so there is no need to check anything.
        vcenter_integration = update_vcenter_integration(
            client=client,
            npod_uuid=npod.uuid,
            vcenter_username=vcenter_username,
            vcenter_password=vcenter_password,
            vcenter_network_identity=vcenter_network_identity,
            vcenter_ssl_port=vcenter_ssl_port,
            enable_affinity_rules=enable_affinity_rules,
            insecure=insecure,
        )

        result['changed'] = True
        result['state'] = 'present'
        result['vcenter_username'] = vcenter_integration.username
        result['vcenter_network_identity'] = vcenter_network_identity
        result['vcenter_ssl_port'] = vcenter_ssl_port
        result['insecure'] = insecure
        result['enable_affinity_rules'] = vcenter_integration.enable_vmhost_affinity
        module.exit_json(**result)

    # pylint: disable=broad-except
    except Exception as err:
        module.fail_json(msg=str(err), **result)


if __name__ == '__main__':
    main()
