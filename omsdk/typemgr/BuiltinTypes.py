#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Copyright © 2018 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its subsidiaries.
# Other trademarks may be trademarks of their respective owners.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Vaideeswaran Ganesan
#
import re
from omsdk.typemgr.FieldType import FieldType
from omsdk.typemgr.ClassType import ClassType
from omsdk.sdkcenum import EnumWrapper, TypeHelper
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

AddressTypes = EnumWrapper("ADT", {
    'IPv4Address': 1,
    'IPv6Address': 2,
    'IPAddress': 3,
    'MACAddress': 4,
    'WWPNAddress': 5,
}).enum_type

if PY2:
    MaxInteger = sys.maxint
    MinInteger = -sys.maxint
else:
    MaxInteger = 2 ** 63 - 1
    MinInteger = -2 ** 63


class CompositeFieldType(FieldType):
    def __init__(self, *parts):
        if PY2:
            super(CompositeFieldType, self).__init__(None, tuple, 'Attribute', None, None, True)
        else:
            super().__init__(None, tuple, 'Attribute', None, None, True)
        self.__dict__['_value'] = parts
        self._composite = True

    def clone(self, parent=None):
        return type(self)(*self.__dict__['_value'])

    def get_value(self):
        return [i for i in self._value if i and i not in ['']]

    def set_value(self, value):
        raise AttributeError('cannot modify composite field')


class RootClassType(ClassType):
    def __init__(self, fname, alias, parent=None):
        if PY2:
            super(RootClassType, self).__init__(fname, alias, parent)
        else:
            super().__init__(fname, alias, parent)


class CloneableFieldType(FieldType):
    def clone(self, parent=None, commit=False):
        if isinstance(self, EnumTypeField):
            return type(self)(self._value, entype=self._type, alias=self._alias,
                              parent=parent, volatile=self._volatile,
                              modifyAllowed=self._modifyAllowed,
                              deleteAllowed=self._deleteAllowed,
                              rebootRequired=self._rebootRequired,
                              default_on_delete=self._default_on_delete,
                              loading_from_scp=not commit)
        elif isinstance(self, IntRangeField):
            return type(self)(self._value, self._min, self._max,
                              entype=self._type, alias=self._alias,
                              parent=parent, volatile=self._volatile,
                              modifyAllowed=self._modifyAllowed,
                              deleteAllowed=self._deleteAllowed,
                              rebootRequired=self._rebootRequired,
                              default_on_delete=self._default_on_delete,
                              loading_from_scp=not commit)
        else:
            return type(self)(self._value, alias=self._alias,
                              parent=parent, volatile=self._volatile,
                              modifyAllowed=self._modifyAllowed,
                              deleteAllowed=self._deleteAllowed,
                              rebootRequired=self._rebootRequired,
                              default_on_delete=self._default_on_delete,
                              loading_from_scp=not commit)


class PortField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(PortField, self).__init__(init_value, int, 'Attribute', alias, parent,
                                            volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)
        else:
            super().__init__(init_value, int, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def my_accept_value(self, value):
        if value is None or value == '':
            return True
        if not isinstance(value, int) or value <= 0:
            raise ValueError(str(value) + " should be an integer > 0")
        return True

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class IntField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(IntField, self).__init__(init_value, int, 'Attribute', alias, parent,
                                           volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)
        else:
            super().__init__(init_value, int, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class IntRangeField(CloneableFieldType):
    def __init__(self, init_value, min_value, max_value, alias=None,
                 parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        self._min = min_value
        if self._min is None: self._min = MinInteger
        self._max = max_value
        if self._max is None: self._max = MaxInteger

        if PY2:
            super(IntRangeField, self).__init__(init_value, int, 'Attribute', alias, parent,
                                                volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                default_on_delete)
        else:
            super().__init__(init_value, int, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def my_accept_value(self, value):
        if not self._min and not self._max:
            # not initialized yet!!!
            return True
        if value is None or value == '':
            return True
        if not isinstance(value, int) or \
                value < self._min or value > self._max:
            raise ValueError(str(value) + " should be in range[" +
                             str(self._min) + ", " + str(self._max) + " ]")
        return True

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class BooleanField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(BooleanField, self).__init__(init_value, bool, 'Attribute', alias, parent,
                                               volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                               default_on_delete)
        else:
            super().__init__(init_value, bool, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class StringField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(StringField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                              volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class ListField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(ListField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                            volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)
        self.__dict__['_list'] = True

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class EnumTypeField(CloneableFieldType):
    def __init__(self, init_value, entype, alias=None, parent=None,
                 volatile=False, modifyAllowed=True, deleteAllowed=True,
                 rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(EnumTypeField, self).__init__(init_value, entype, 'Attribute', alias, parent,
                                                volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                default_on_delete)
        else:
            super().__init__(init_value, entype, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def __str__(self):
        return TypeHelper.resolve(self._value)

    def __repr__(self):
        return TypeHelper.resolve(self._value)


class AddressHelpers(object):
    @staticmethod
    def _check_address(value, address_type):
        match_regex = []
        if address_type in [AddressTypes.IPv4Address, AddressTypes.IPAddress]:
            match_regex.append('^\d+([.]\d+){3}$')
        elif address_type in [AddressTypes.IPv6Address, AddressTypes.IPAddress]:
            match_regex.append('^[A-Fa-f0-9:]+$')
        elif address_type in [AddressTypes.MACAddress]:
            match_regex.append('^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$')
        elif address_type in [AddressTypes.WWPNAddress]:
            match_regex.append('^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){7}$')

        if value is None or value == '':
            return True

        if not isinstance(value, str):
            return False

        for pattern in match_regex:
            if not re.match(pattern, value):
                return False

        if address_type in [AddressTypes.IPv4Address, AddressTypes.IPAddress] \
                and ':' not in value:
            for n in value.split('.'):
                if int(n) > 255:
                    return False
        return True


class IPv4AddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(IPv4AddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                                   volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                   default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.IPv4Address)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class IPv6AddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(IPv6AddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                                   volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                   default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.IPv6Address)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class IPAddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(IPAddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                                 volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                 default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    # Accepts both IPv4 and IPv6
    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.IPAddress)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class MacAddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(MacAddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                                  volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                  default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.MACAddress)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)


class WWPNAddressField(CloneableFieldType):
    def __init__(self, init_value, alias=None, parent=None, volatile=False,
                 modifyAllowed=True, deleteAllowed=True, rebootRequired=False,
                 default_on_delete=''):
        if PY2:
            super(WWPNAddressField, self).__init__(init_value, str, 'Attribute', alias, parent,
                                                   volatile, modifyAllowed, deleteAllowed, rebootRequired,
                                                   default_on_delete)
        else:
            super().__init__(init_value, str, 'Attribute', alias, parent,
                             volatile, modifyAllowed, deleteAllowed, rebootRequired, default_on_delete)

    def my_accept_value(self, value):
        return AddressHelpers._check_address(value, AddressTypes.WWPNAddress)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self._value)
