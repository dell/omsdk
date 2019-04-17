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
import sys
import logging
from enum import Enum
from omsdk.sdkcenum import EnumWrapper, TypeHelper, PY2Enum

if PY2Enum:
    from enum import EnumValue

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class AutoNumber(Enum):
    def __new__(cls):
        value = 1 << len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Filter(object):
    def check(self, scopeType):
        not_implemented

    def allowedtype(self, scopeType):
        not_implemented

    def add(self, scopeType):
        if self.check(scopeType):
            self.mix = self.mix | TypeHelper.resolve(scopeType)
        else:
            raise AttributeError("Filter can only take Flag in argument")

    def __init__(self, *args):
        self.mix = 0
        for scopeType in args:
            self.add(scopeType)

    def isset(self, scopeType):
        n = TypeHelper.resolve(scopeType)
        return ((self.mix & n) == n)

    def unset(self, scopeType):
        n = TypeHelper.resolve(scopeType)
        self.mix = (~(self.mix & n) & self.mix)

    def _all(self, enumtype):
        if self.allowedtype(enumtype):
            for i in enumtype:
                self.add(i)
        else:
            logger.debug(str(enumtype) + " is not allowed for " + str(self))
        return self

    def test(self, enumtype):
        if self.allowedtype(enumtype):
            for i in enumtype:
                logger.debug("  " + str(i) + "=" + str(self.isset(i)))
        else:
            logger.debug(str(enumtype) + " is not allowed for " + str(self))


MonitorScopeMap = {
    "Key": 1 << 0,
    "Metrics": 1 << 1,
    "ConfigState": 1 << 2,
    # Inventory includes all
    "BasicInventory": 1 << 3,
    "OtherInventory": 1 << 4,
    "Inventory": 1 << 3 | 1 << 4,

    "MainHealth": 1 << 10,  # Main component health
    "OtherHealth": 1 << 11,  # other health component
    # Health includes all health
    "Health": 1 << 10 | 1 << 11,
}
MonitorScope = EnumWrapper("MS", MonitorScopeMap).enum_type


class MonitorScopeFilter(Filter):
    def __init__(self, *args):
        if PY2:
            super(MonitorScopeFilter, self).__init__(*args)
        else:
            super().__init__(*args)
        self.monitorScopedefaultMap = {
            MonitorScope.Key: "Not Available",
            MonitorScope.Metrics: None,
            MonitorScope.ConfigState: "Not Available",
            MonitorScope.BasicInventory: "Not Available",
            MonitorScope.OtherInventory: "Not Available",
            MonitorScope.Inventory: "Not Available",
            MonitorScope.MainHealth: None,  # Main component health
            MonitorScope.OtherHealth: None,  # other health component
            MonitorScope.Health: None
        }

    def allowedtype(self, scopeType):
        return type(scopeType) == type(MonitorScope)

    def check(self, scopeEnum):
        return TypeHelper.belongs_to(MonitorScope, scopeEnum)

    def all(self):
        return self._all(MonitorScope)

    def getdefaultMap(self, mscope):
        if mscope in self.monitorScopedefaultMap:
            return self.monitorScopedefaultMap[mscope]
        else:
            return None

    def setdefaultMap(self, mscope, ndefval):
        self.monitorScopedefaultMap[mscope] = ndefval


def CreateMonitorScopeFilter(argument=""):
    if argument == "":
        argument = "Health+Inventory+Metrics+ConfigState"
    monitorfilter = MonitorScopeFilter()
    for i in argument.split("+"):
        for j in MonitorScope:
            if TypeHelper.get_name(j, MonitorScopeMap) == i:
                monitorfilter.add(j)
    return monitorfilter


MonitorScopeFilter_All = MonitorScopeFilter().all()


class ComponentScope:
    def __init__(self, *args):
        self.comps = {}
        for comp in args:
            try:
                if PY2Enum and isinstance(comp, EnumValue):
                    self.comps[comp.key] = True
                    continue
            except:
                pass

            if isinstance(comp, Enum):
                self.comps[comp.value] = True
            else:
                self.comps[comp] = True

    def isMatch(self, comp):
        return (comp in self.comps)

    def printx(self):
        for i in self.comps:
            print(i)


class RegExpFilter:
    def __init__(self, *args):
        self.rexp = []
        for rexp in args:
            self.rexp.append(re.compile(rexp))

    def isMatch(self, obj):
        for rexp in self.rexp:
            if rexp.match(obj):
                return True
        return False


class DeviceGroupFilter(RegExpFilter):
    pass


class DeviceFilter(RegExpFilter):
    pass
