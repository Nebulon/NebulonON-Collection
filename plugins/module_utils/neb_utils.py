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
    'get_volume'
]


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
