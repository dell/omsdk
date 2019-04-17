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
from omsdk.version.sdkversion import OverrideCompatibleEnumPyVersion

from enum import Enum, EnumMeta
import sys

if OverrideCompatibleEnumPyVersion:
    PY2Enum = (sys.version_info < OverrideCompatibleEnumPyVersion)
    PY3Enum = (sys.version_info >= OverrideCompatibleEnumPyVersion)

if PY2Enum:
    from enum import EnumValue

# 
#  If you create a enumeration as:
#      TestOptions_Map = { 'VAL_1' : 'Value 1', 'VAL_2' : 'Value 2' }
#      TestOptionsEnum = EnumWrapper("Test",  TestOptions_Map).enum_type
#
#  TypeHelper.resolve('VAL_1') ==> 'Value 1'
#  TypeHelper.resolve(TestOptionsEnum.VAL_1) ==> 'Value 1'
#
#  TypeHelper.belongs_to(TestOptionsEnum, TestOptionsEnum.VAL_1) ==> True
#  TypeHelper.belongs_to(TestOptionsEnum, OtherEnum.VAL_1) ==> False
#  TypeHelper.belongs_to(TestOptionsEnum, 'VAL_1') ==> False
#
#  TypeHelper.get_name('Value 1', TestOptions_Map) ==> 'VAL_1'
#  TypeHelper.get_name('Value N', TestOptions_Map) ==> None
#
#  TypeHelper.convert_to_enum('Value 1', TestOptions) => TestOptionsEnum.VAL_1
#  TypeHelper.convert_to_enum('Value 2', TestOptions) => TestOptionsEnum.VAL_2
#  TypeHelper.convert_to_enum('Value N', TestOptions) => None
#


class TypeHelper:
    @staticmethod
    def belongs_to(entype, value):
        if PY2Enum:
            if (type(entype) is Enum):
                return (isinstance(value,
                                   EnumValue) and value.enumtype == entype)
            elif entype == type(value):
                return True
            else:
                return False
        else:
            return entype.__name__ == type(value).__name__
            # if not isinstance(value, argtype) and \
            #   argtype.__name__ != type(value).__name__:

    @staticmethod
    def resolve(enval):
        if PY2Enum and isinstance(enval, EnumValue):
            return (enval.key)
        elif PY3Enum and isinstance(enval, Enum):
            return (enval.value)
        else:
            return enval

    @staticmethod
    def get_name(enval, mymap):
        if PY2Enum or not isinstance(enval, Enum):
            for i in mymap:
                if mymap[i] == TypeHelper.resolve(enval):
                    return i
        elif PY3Enum and isinstance(enval, Enum):
            return (enval.name)
        else:
            return enval

    @staticmethod
    def get_enumname(enval):
        if PY2Enum and TypeHelper.is_enum(enval):
            mymap = enval.enumtype.__dict__
            enval_value = TypeHelper.resolve(enval)
            for i in mymap:
                if hasattr(mymap[i], '_key') and mymap[i]._key == enval_value:
                    return i
        elif PY3Enum and isinstance(enval, Enum):
            return (enval.name)
        else:
            return enval

    @staticmethod
    def convert_to_enum(enval, entype, defval=None):
        for i in entype:
            if enval == TypeHelper.resolve(i):
                return i
        return defval

    @staticmethod
    def is_enum(entype):
        if PY3Enum and (isinstance(entype, EnumMeta) or isinstance(entype, Enum)):
            return True
        elif PY2Enum and isinstance(entype, EnumValue):
            return True
        return False


class EnumWrapper(object):
    enum_entries = {}
    enum_name = None

    def __init__(self, name, entries):
        EnumWrapper.enum_entries[name] = entries
        if PY2Enum:
            EnumWrapper.enum_name = name
            ent = EnumWrapper.enum_entries[name].keys()
            self.enum_type = Enum(*ent, value_type=EnumWrapper.mapvalue)
        else:
            self.enum_type = Enum(name, EnumWrapper.enum_entries[name])

    @staticmethod
    def mapvalue(self, i, value):
        if PY2Enum:
            return EnumValue(self, i, EnumWrapper.enum_entries[EnumWrapper.enum_name][value])
        else:
            pass

    @staticmethod
    def resolve(enval):
        if PY2Enum:
            return (enval.key)
        else:
            return (enval.value)
