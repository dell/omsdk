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


CompellentCompEnum = EnumWrapper('CompellentCompEnum', {
    "System" : "System",
    "Controller" : "Controller",
    "Enclosure" : "Enclosure",
    "Disk" : "Disk",
    "Volume" : "Volume",
    "EnclosurePSU" : "EnclosurePSU",
    "UPS" : "UPS",
    "PowerSupply" : "PowerSupply",
    "EnclosureFan" : "EnclosureFan",
    "EnclosureIOM" : "EnclosureIOM",
    "ControllerFan" : "ControllerFan",
    "StorageCenter" : "StorageCenter",
    "PhysicalDisk" : "PhysicalDisk",
}).enum_type

if PySnmpPresent:
    CompellentSNMPViews = {
     CompellentCompEnum.System : {
        'SysObjectID': ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
        #'SysObjectID': ObjectIdentity('1.3.6.1.4.1.8072.3.2.8'),
        'ProductID' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.1'),
        'Description' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.2'),
        'Vendor' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.3'),
        'Version' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.4'),
        'ServiceTag' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.5'),
        'PrimaryStatus' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.6'),
        'ManagementIP': ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.8"),
        'URLString' : ObjectIdentity('1.3.6.1.4.1.674.11000.2000.500.1.2.8'),
        'SerialNumber': ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.9"),
        'Name': ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.4"),
        'IPv6MgmtIP' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.11"),
        'SysName' : ObjectIdentity("1.3.6.1.2.1.1.5")
     },
     CompellentCompEnum.StorageCenter : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.1"),
       'IPv6MgmtIPPrefix' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.12"), 
       'Location' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.6"), 
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.3"), 
       'ManagementIP' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.8"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.2"),
       'Name' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.4"), 
       'IPv6MgmtIP' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.11"), 
       'SerialNumber' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.9"), 
       'Contact' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.29.1.5"), 
     },
     CompellentCompEnum.Controller : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.1"),
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.2"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.3"), 
       'Name' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.4"), 
       'Model' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.7"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.8"), 
       'AssetTag' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.9"), 
       'Leader' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.12"), 
       'IPAddress' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.5"),
       'IPv6Eth0IPPrefix' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.11"), 
       'IPv6Address' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.10"),
       'ForceTrap' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.13.1.6"), 
     },
     CompellentCompEnum.Disk : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.1"),
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.2"),
       'DiskStatusMsg' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.6"),
       'Position' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.4"), 
       'Size' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.9"), 
       'Enclosure' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.11"), 
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.3"), 
       'Healthy' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.5"), 
       'IoPortType' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.14.1.10"), 
     },
     CompellentCompEnum.Enclosure : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.1"),
       'EnclosureNumber' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.2"),
       'EnclosureAssetTag' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.10"),
       'EnclosureType' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.6"),
       'EnclosureStatus' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.3"),
       'EnclosureName' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.4"),
       'EnclosureModel' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.7"),
       'EnclosureServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.15.1.9"),
     },
     CompellentCompEnum.EnclosureFan : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.20.1.1"),
       'Location' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.20.1.4"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.20.1.2"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.20.1.3"), 
     },
     CompellentCompEnum.EnclosurePSU : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.21.1.1"),
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.21.1.2"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.21.1.3"), 
       'Position' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.21.1.4"), 
     },
     CompellentCompEnum.EnclosureIOM : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.22.1.1"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.22.1.3"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.22.1.2"),
       'Position' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.22.1.4"), 
     },
     CompellentCompEnum.ControllerFan : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.16.1.1"),
       'Name' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.16.1.4"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.16.1.2"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.16.1.3"), 
     },
     CompellentCompEnum.Volume : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.26.1.1"),
       'Name' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.26.1.4"), 
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.26.1.3"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.26.1.2"),
     },
     CompellentCompEnum.UPS : {
       'ID' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.30.1.1"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.30.1.3"), 
       'Name' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.30.1.4"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.30.1.2"),
       'BatteryLife' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.30.1.5"), 
     },
     CompellentCompEnum.PowerSupply : {
       'ID': ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.17.1.1"),
       'Name' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.17.1.4"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.17.1.2"),
       'Status' : ObjectIdentity("1.3.6.1.4.1.674.11000.2000.500.1.2.17.1.3")
     }
    }
    CompellentSNMPClassifier = {
        CompellentCompEnum.System: {
            'SysObjectID' : 'SNMPv2-SMI::enterprises\\.8072\\.3\\.2\\.8|1\\.3\\.6\\.1\\.4\\.1\\.8072\\.3\\.2\\.8'
            # 'SysObjectID': ObjectIdentity('1.3.6.1.4.1.8072.3.2.8'),
        }
    }

    CompellentComponentTree = {
        "Full" : [ 
            CompellentCompEnum.System
        ]
    }
else:
    CompellentSNMPViews = {}
    CompellentComponentTree = {}
    CompellentSNMPClassifier = {}

CompellentComponentTree = {
    CompellentCompEnum.System : [
        CompellentCompEnum.System,
        CompellentCompEnum.StorageCenter,
        CompellentCompEnum.Controller,
        CompellentCompEnum.Enclosure,
        CompellentCompEnum.Volume,
        CompellentCompEnum.UPS,
        CompellentCompEnum.PowerSupply
    ],
    CompellentCompEnum.Enclosure : [
        CompellentCompEnum.PhysicalDisk,
        CompellentCompEnum.EnclosurePSU,
        CompellentCompEnum.EnclosureFan,
        CompellentCompEnum.EnclosureIOM
    ],
    CompellentCompEnum.Controller : [
        CompellentCompEnum.ControllerFan
    ]
}

Compellent_more_details_spec = {
    "System":{
        "_components_enum": [
            CompellentCompEnum.System,
            CompellentCompEnum.Controller,
            CompellentCompEnum.StorageCenter
        ]
    }
}

class Compellent(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(Compellent, self).__init__(iDeviceRegistry("Compellent", srcdir, CompellentCompEnum))
        else:
            super().__init__(iDeviceRegistry("Compellent", srcdir, CompellentCompEnum))
        if PySnmpPresent:
            self.protofactory.add(PSNMP(
                views = CompellentSNMPViews,
                classifier=CompellentSNMPClassifier
            ))
        self.protofactory.addCTree(CompellentComponentTree)
        self.protofactory.addClassifier([CompellentCompEnum.System])

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return CompellentEntity(self.ref, protofactory, ipaddr, creds)

class CompellentEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(CompellentEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)

        self.supports_entity_mib = False
        self.more_details_spec = Compellent_more_details_spec

    def _should_i_include(self, component, entry):
        if component == "System":
            if ':' in self.ipaddr:
                if 'IPv6MgmtIP' in entry:
                    entry["ManagementIP"] = self.entityjson["System"][0].get("IPv6MgmtIP","Not Available") 

        if component == "Controller":
            if ':' in self.ipaddr:
                mgmtIP = self.entityjson['System'][0].get("IPv6MgmtIP", "Not Available")
            else:
                mgmtIP = self.entityjson['System'][0].get("ManagementIP", "Not Available")
            if self.ipaddr == mgmtIP:
                return True

            if ':' in self.ipaddr:
                if entry.get("IPv6Address", "Not Available") != self.ipaddr:
                    return False 
            elif entry.get("IPAddress", "Not Available") != self.ipaddr:
                return False

            entry["URLString"] = self.entityjson["System"][0].get("URLString", "Not Available")

        return True

    def _call_it(self, keyComp):
        # pass
        if(keyComp == "System"):
            # self._add_ctrl_details(keyComp)
            systemList = self.entityjson['System']
            for sysDict in systemList:
                if 'Controller' in self.entityjson:
                    ctrlList = self.entityjson['Controller']
                    for ctrlDict in ctrlList:
                        if ctrlDict['Leader'] == '1':
                            sysDict.update({'PrimaryController{0}'.format(k): v for k, v in ctrlDict.items()})
                        elif ctrlDict['Leader'] == '2':
                            sysDict.update({'SecondaryController{0}'.format(k): v for k, v in ctrlDict.items()})
                sysDict['isManagementIP'] = 'False'
                sysDict['isControllerIP'] = 'True'
                if sysDict['ManagementIP'] == self.ipaddr:
                    sysDict['isManagementIP'] = 'True'
                    sysDict['isControllerIP'] = 'False'


