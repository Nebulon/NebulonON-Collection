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

from enum import Enum

__all__ = [
    "to_dict",
]


def to_dict(src):
    # type: (any) -> dict
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
