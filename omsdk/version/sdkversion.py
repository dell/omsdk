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
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY2UC = (sys.version_info < (3, 0, 0))

OMSDKVersion = (0, 9, 1002)

APIVersions = {
    'ConfigFactory': (1, 0, 0),
    'DeviceDriver': (1, 0, 0),
    'ConsoleDriver': (0, 1, 0),
    'SNMPListener': (0, 0, 1)
}

OverrideCompatibleEnumPyVersion = None


class Compatibility:
    def __init__(self):
        self.compat_enum_version = None

    def set_compat_enum_version(self, version):
        self.compat_enum_version = version


class CompatibilityFactory:
    compat = Compatibility()

    @staticmethod
    def get_compat():
        return CompatibilityFactory.compat


cc = CompatibilityFactory()

if PY3:
    _EnumStyle = 'V3'
else:
    _EnumStyle = 'NotPresent'
    try:
        import enum

        if hasattr(enum, 'version'):
            _EnumStyle = 'V3'
        elif hasattr(enum, '__version__'):
            _EnumStyle = 'V2'
    except ImportError:
        pass
if _EnumStyle == 'V3':
    OverrideCompatibleEnumPyVersion = sys.version_info
else:
    OverrideCompatibleEnumPyVersion = (3, 0, 0)
