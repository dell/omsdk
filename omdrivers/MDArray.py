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
from enum import Enum
from omsdk.sdkdevice import iDeviceDiscovery, iDeviceRegistry, iDeviceDriver
from omsdk.sdkcenum import EnumWrapper
from omsdk.sdkfile import FileOnShare, Share
from omsdk.sdkcreds import UserCredentials
from omsdk.sdkproto import PSNMP
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    from pysnmp.proto import rfc1902
    from pysnmp import debug

    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False

MDArrayCompEnum = EnumWrapper('MDArrayCompEnum', {
    "System": "System",
}).enum_type

if PySnmpPresent:
    MDArraySNMPViews = {
        MDArrayCompEnum.System: {
            'SysObjectID': ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
            'Name': ObjectIdentity('1.3.6.1.4.1.674.10893.2.31.500.1.1'),
            'WWID': ObjectIdentity('1.3.6.1.4.1.674.10893.2.31.500.1.2'),
            'ServiceTag': ObjectIdentity('1.3.6.1.4.1.674.10893.2.31.500.1.3'),
            'ProductID': ObjectIdentity('1.3.6.1.4.1.674.10893.2.31.500.1.5'),
            'Status': ObjectIdentity('1.3.6.1.4.1.674.10893.2.31.500.1.7'),
            'SysName': ObjectIdentity('1.3.6.1.2.1.1.5')
        }
    }
    MDArraySNMPClassifier = {
        MDArrayCompEnum.System: {
            'SysObjectID': 'SNMPv2-SMI::enterprises\\.674\\.10893\\.2\\.31|1\\.3\\.6\\.1\\.4\\.1\\.674\\.10893\\.2\\.31'
        }
    }

    MDArrayComponentTree = {
        "Full": [
            MDArrayCompEnum.System
        ]
    }
else:
    MDArraySNMPViews = {}
    MDArrayComponentTree = {}
    MDArraySNMPClassifier = {}


class MDArray(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(MDArray, self).__init__(iDeviceRegistry("MDArray", srcdir, MDArrayCompEnum))
        else:
            super().__init__(iDeviceRegistry("MDArray", srcdir, MDArrayCompEnum))
        if PySnmpPresent:
            self.protofactory.add(PSNMP(
                views=MDArraySNMPViews,
                classifier=MDArraySNMPClassifier,
                useSNMPGetFlag=True
            ))
        self.protofactory.addCTree(MDArrayComponentTree)
        self.protofactory.addClassifier([MDArrayCompEnum.System])

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return iDeviceDriver(self.ref, protofactory, ipaddr, creds)
