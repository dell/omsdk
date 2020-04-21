#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Copyright © 2019 Dell Inc. or its subsidiaries. All rights reserved.
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
# Authors: Sachin Apagundi
#
from enum import Enum
from omsdk.sdkdevice import iDeviceDiscovery, iDeviceRegistry, iDeviceDriver
from omsdk.sdkcenum import EnumWrapper
from omsdk.sdkproto import PSNMP, ProtocolEnum
import sys
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    from pysnmp.proto import rfc1902
    from pysnmp import debug
    PyPSNMP = True
except ImportError:
    PyPSNMP = False

class NoConfig:
    def __init__(self, obj):
        logger.debug("not implemented")


F10NGCompEnum = EnumWrapper('F10NGCompEnum', {
    "System": "System",
    "FanTray": "FanTray",
    "PowerSupply": "PowerSupply",
    "Port": "Port",
    "Fan": "Fan",
}).enum_type

if PyPSNMP:
    F10NGPSNMPViews = {
        F10NGCompEnum.System : {
            'SysObjectID' : ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
            'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.3.1.7"),
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1.4"),
            'Model' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1.2"),
            'Description' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1.3"),
            'Location' : ObjectIdentity("1.3.6.1.2.1.1.6"),
            'NetwUMACAddress' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.3.1.3"),
            'NetwUPartNo':  ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1.6"),
            'PPID' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1.7"),
            'ExpressServiceCode' : ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.1.4.1.10"),
            'Hostname' : ObjectIdentity("1.3.6.1.2.1.1.5"),
            'SwitchUptime': ObjectIdentity("1.3.6.1.2.1.1.3"),
        },
        F10NGCompEnum.Port: {
            'Description': ObjectIdentity('IF-MIB', 'ifDescr'),
            'Type': ObjectIdentity('IF-MIB', 'ifType'),
            'Address': ObjectIdentity('IF-MIB', 'ifPhysAddress'),
            'ifIndex': ObjectIdentity('IF-MIB', 'ifIndex'),
            'Status': ObjectIdentity('1.3.6.1.2.1.2.2.1.7'),
            'ifInOctets': ObjectIdentity('1.3.6.1.2.1.2.2.1.10'),
            'ifOutOctets': ObjectIdentity('1.3.6.1.2.1.2.2.1.16'),
            'ifInDiscards': ObjectIdentity('1.3.6.1.2.1.2.2.1.13'),
            'ifOutDiscards': ObjectIdentity('1.3.6.1.2.1.2.2.1.19'),
            'ifInErrors': ObjectIdentity('1.3.6.1.2.1.2.2.1.14'),
            'ifOutErrors': ObjectIdentity('1.3.6.1.2.1.2.2.1.20'),
            'ifInUnknownProtos': ObjectIdentity('1.3.6.1.2.1.2.2.1.15'),
            'ifSpeed': ObjectIdentity('1.3.6.1.2.1.2.2.1.5'),
        },
        F10NGCompEnum.FanTray: {
            'Index': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.2.1.3"),
            'Type': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.2.1.2"),
            'PiecePartID': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.2.1.5"),
            'ExpressServiceCode': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.2.1.7"),
            'ServiceTag': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.2.1.5"),
            'OperStatus': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.2.1.4"),
        },
        F10NGCompEnum.Fan: {
            'Index': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.3.1.3"),
            'OperStatus': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.3.1.7"),
        },
        F10NGCompEnum.PowerSupply: {
            'Index': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.1.1.3"),
            'OperStatus': ObjectIdentity("1.3.6.1.4.1.674.11000.5000.100.4.1.2.1.1.4"),
        },
    }
    F10NGSNMPViews_FieldSpec = {
        F10NGCompEnum.System : {
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Healthy",
                    "2" : "Critical",
                    "3" : "Critical",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Warning"
                }
            },
            "Model" : {
                'Lookup'  :  'True',
                'Values' : {
                    "0" : "notPresent",
                    "1" : "s6000on",
                    "2" : "s4048on",
                    "3" : "s4048Ton",
                    "4" : "s3048on",
                    "5" : "s6010on",
                    "6" : "s4148Fon",
                    "7" : "s4128Fon",
                    "8" : "s4148Ton",
                    "9" : "s4128Ton",
                    "10" : "s4148FEon",
                    "11" : "s4148Uon",
                    "12" : "s4200on",
                    "13" : "mx5108Non",
                    "14" : "mx9116Non",
                    "15" : "s5148Fon",
                    "16" : "z9100on",
                    "17" : "s4248FBon",
                    "18" : "s4248FBLon",
                    "19" : "s4112Fon",
                    "20" : "s4112Ton",
                    "21" : "z9264Fon",
                    "22" : "z9232Fon",
                    "23" : "s5212Fon",
                    "24" : "s5224Fon",
                    "25" : "s5232Fon",
                    "26" : "s5248Fon",
                    "27" : "s5296Fon",
                    "28" : "z9332Fon",
                    "29" : "n3248TEon",
                    "9999" : "unknown",
                }
            },
            "NetwUMACAddress" : {
                'Macedit' : 'True'
                },
        },
        F10NGCompEnum.Port: {
            "Status": {
                'Lookup': 'True',
                'Values': {
                    "up": "Up",
                    "down": "Down",
                    "testing": "Testing"
                }
            }
        },
        F10NGCompEnum.FanTray: {
            "OperStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Up",
                    "2": "Down",
                    "3": "Testing",
                    "4": "Unknown",
                    "5": "Down",
                    "6": "Absent",
                    "7": "Down",
                    "8": "Down",
                }
            },
            "Type": {
                'Lookup': 'True',
                'Values': {
                    "1": "Chassis",
                    "2": "Stack",
                    "3": "RPM",
                    "4": "Supervisor",
                    "5": "Linecard",
                }
            }
        },
        F10NGCompEnum.Fan: {
            "OperStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Healthy",
                    "2": "Critical",
                    "3": "Testing",
                    "4": "Unknown",
                    "5": "Warning",
                    "6": "Absent",
                    "7": "Warning",
                    "8": "Critical",
                }
            }
        },
        F10NGCompEnum.PowerSupply: {
            "OperStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Healthy",
                    "2": "Critical",
                    "3": "Testing",
                    "4": "Unknown",
                    "5": "Warning",
                    "6": "Absent",
                    "7": "Warning",
                    "8": "Critical",
                }
            }
        },
    }

    F10NGPSNMPClassifier = {
        F10NGCompEnum.System : {
            'SysObjectID': 'SNMPv2-SMI::enterprises\\.674\\.11000'
        }
    }
else:
    F10NGPSNMPViews = {}
    F10NGPSNMPClassifier = {}

F10NGClassifier = [F10NGCompEnum.System]

F10NGSubsystemHealthSpec = {
    F10NGCompEnum.System : { "Component" : F10NGCompEnum.System, "Field" : 'PrimaryStatus' },
}

class F10NG(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(F10NG, self).__init__(iDeviceRegistry("F10NG", srcdir, F10NGCompEnum))
        else:
            super().__init__(iDeviceRegistry("F10NG", srcdir, F10NGCompEnum))
        if PyPSNMP:
            self.protofactory.add(PSNMP(
                views = F10NGPSNMPViews,
                classifier = F10NGPSNMPClassifier,
                view_fieldspec = F10NGSNMPViews_FieldSpec))
        self.protofactory.addClassifier(F10NGClassifier)
        self.protofactory.addSubsystemSpec(F10NGSubsystemHealthSpec)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return F10NGEntity(self.ref, protofactory, ipaddr, creds)

class F10NGEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(F10NGEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)

    def _isin(self, parentClsName, parent, childClsName, child):
        if 'MyPos' in parent:
            return parent['MyPos'] == child['ContainedIn']
        else:
            return self._get_obj_index(parentClsName, parent) in \
                   self._get_obj_index(childClsName, child)

    def _should_i_include(self, component, entry):
        if component in ["Fan", "FanTray", "PowerSupply", "Port"]:
            if entry.get("OperStatus") == 'Absent' or entry.get("Status") == 'Testing':
                return False
        if component in ["System"]:
            if 'Model' in entry:
                entry["SwitchType"] = entry.get('Model')[:1].upper() + "Series"
            if ':' in self.ipaddr:
                entry['SwitchIPv6'] = self.ipaddr
            else:
                entry['SwitchIPv4'] = self.ipaddr
        if component in ["FanTray"]:
            entry["FanDeviceIndex"] = entry.get("_SNMPIndex")
        return True

    def _should_i_modify_component(self, finalretjson, component):
        pass
