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
import re
import ipaddress
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

try:
    from omdrivers.EqualLogic.lifecycle.EqualLogicConfig import EqualLogicConfig
    from omdrivers.EqualLogic.lifecycle.EqualLogicConfig import EqualLogicPSNMPCmds
    from omdrivers.EqualLogic.lifecycle.EqualLogicConfig import ConfigFileTypeEnum
    Pyconfig_mgr = True
except ImportError:
    Pyconfig_mgr = False

class NoConfig:
    def __init__(self, obj):
        logger.debug("not implemented")

if not Pyconfig_mgr:
    EqualLogicConfig = NoConfig
if not Pyconfig_mgr and PyPSNMP:
    EqualLogicPSNMPCmds = {}

EqualLogicCompEnum = EnumWrapper('EqualLogicCompEnum', {
    "System" : "System",
    "Member" : "Member",
    "Volume" : "Volume",
    "PhysicalDisk" : "PhysicalDisk",
    "StoragePool" : "StoragePool",
    "InetAddr" : "InetAddr",
}).enum_type

if PyPSNMP:
    EqualLogicPSNMPViews = {
     EqualLogicCompEnum.System : { 
         'SysObjectID' : ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
         'GroupName' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.1.1.19"),
         'GroupIP' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.1.1.20"),
         'GroupIPv6' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.1.1.54"),
         'MemberCount' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.2.1.13"),
         'VolumeCount' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.2.1.12"), 
         'RAIDPolicy' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.15.1.3.1.968588590"),
         'SysName' : ObjectIdentity("1.3.6.1.2.1.1.5")
     },
     EqualLogicCompEnum.Member : { 
         'Name' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.1.1.9"),
         'ControllerMajorVersion' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.1.1.21"),
         'ControllerMinorVersion' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.1.1.22"),
         'ControllerMaintenanceVersion' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.1.1.23"),
         'ProductFamily' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.11.1.9"),
         'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.11.1.8"),
         'Model' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.11.1.1"),
         'ChassisType' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.11.1.7"),
         'DiskCount' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.11.1.4"),
         'RaidStatus' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.13.1.1"),
         'Capacity' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.10.1.1"),
         'UsedStorage' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.10.1.2"),
         'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.5.1.1"),
         'RAIDPolicy' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.15.1.3"),
         'GroupName' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.1.1.19"),
         'GroupIP' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.1.1.20"),
         'GroupIPv6' : ObjectIdentity("1.3.6.1.4.1.12740.1.1.1.1.54"),
         'EqlDriveGroupStoragePoolIndex' : ObjectIdentity("1.3.6.1.4.1.12740.2.1.15.1.2"),
     },

     EqualLogicCompEnum.Volume : { 
       'Name' : ObjectIdentity("1.3.6.1.4.1.12740.5.1.7.1.1.4"), 
       'TotalSize' : ObjectIdentity("1.3.6.1.4.1.12740.5.1.7.1.1.8"), 
       'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.12740.5.1.7.7.1.8"), 
       'StoragePoolIndex' : ObjectIdentity("1.3.6.1.4.1.12740.5.1.7.1.1.22"),
     },
     EqualLogicCompEnum.PhysicalDisk : { 
       'Status' : ObjectIdentity("1.3.6.1.4.1.12740.3.1.1.1.8"), 
       'Slot' : ObjectIdentity("1.3.6.1.4.1.12740.3.1.1.1.11"), 
       'Model' : ObjectIdentity("1.3.6.1.4.1.12740.3.1.1.1.3"), 
       'SerialNumber' : ObjectIdentity("1.3.6.1.4.1.12740.3.1.1.1.5"),
       'FirmwareVersion' : ObjectIdentity("1.3.6.1.4.1.12740.3.1.1.1.4"),
       'TotalSize' : ObjectIdentity("1.3.6.1.4.1.12740.3.1.1.1.6"),
     },
     EqualLogicCompEnum.StoragePool : {
       'StorageName' : ObjectIdentity("1.3.6.1.4.1.12740.16.1.1.1.3"),
       'MemberCount' : ObjectIdentity("1.3.6.1.4.1.12740.16.1.2.1.8"),
       'VolumeCount' : ObjectIdentity("1.3.6.1.4.1.12740.16.1.2.1.16"),
     },
     EqualLogicCompEnum.InetAddr : {
       'EntityName' : ObjectIdentity("1.3.6.1.4.1.12740.9.5.1.3")
     }
    }

    EqualLogicSNMPViews_FieldSpec = {
        EqualLogicCompEnum.System: {
            "RAIDPolicy" : {
                'Lookup'  :  'True',
                'Values' : {
                    "0" : "Unconfigured",
                    "1" : "RAID 50",
                    "2" : "RAID 10",
                    "3" : "RAID 5",
                    "4" : "RAID 50-nospares",
                    "5" : "RAID 10-nospares",
                    "6" : "RAID 5-nospares",
                    "7" : "RAID 6",
                    "8" : "RAID 6-nospares",
                    "9" : "RAID 6-accelerated",
                    "10" : "Hvs-storage",
                }
            },
            "GroupIPv6" : {
                'IPv6edit' : 'True'
                }
        },
        EqualLogicCompEnum.Member : {
            "Capacity" : { 'Type' : 'Bytes', 'InUnits' : "MB" },
            "UsedStorage" : {'Type' : 'Bytes', 'InUnits' : "MB"},
            "RAIDPolicy" : {
                'Lookup'  :  'True',
                'Values' : {
                    "0" : "Unconfigured",
                    "1" : "RAID 50",
                    "2" : "RAID 10",
                    "3" : "RAID 5",
                    "4" : "RAID 50-nospares",
                    "5" : "RAID 10-nospares",
                    "6" : "RAID 5-nospares",
                    "7" : "RAID 6",
                    "8" : "RAID 6-nospares",
                    "9" : "RAID 6-accelerated",
                    "10" : "Hvs-storage",
                }
            },
            "GroupIPv6" : {
                'IPv6edit' : 'True'
                }
        },
        EqualLogicCompEnum.Volume : {
            "TotalSize" : { 'Type' : 'Bytes', 'InUnits' : "MB", 'OutUnits' : "GB"},
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "online",
                    "2" : "offline",
                    "3" : "offline (snap reserve met)",
                    "4" : "offline (member down)",
                    "5" : "offline (lost blocks)",
                    "6" : "offline (thin max grow met)",
                    "7" : "offline (nospace auto grow)",
                    "8" : "offline (missing pages)",
                    "9" : "unavailable due to SyncRep",
                    "10" : "available (no new connections)",
                    "11" : "unavailable due to internal error"
                }
            }
        },
        EqualLogicCompEnum.PhysicalDisk : {
            "TotalSize" : { 'Type' : 'Bytes', 'InUnits' : "MB" },
        }
    }
    EqualLogicPSNMPClassifier = {
        EqualLogicCompEnum.System : {
            'SysObjectID' : 'SNMPv2-SMI::enterprises\\.12740\\.17\\.1'
        }
    }
else:
    EqualLogicPSNMPViews = {}
    EqualLogicPSNMPClassifier = {}

EqualLogicComponentTree = {
    "Full" : [ 
        EqualLogicCompEnum.System,
        EqualLogicCompEnum.Member,
        EqualLogicCompEnum.Volume,
        EqualLogicCompEnum.PhysicalDisk,
        EqualLogicCompEnum.StoragePool,
        EqualLogicCompEnum.InetAddr,
    ]
}

EqualLogic_more_details_spec = {
    "System":{
        "_components_enum": [
          EqualLogicCompEnum.System,
          EqualLogicCompEnum.Member,
          EqualLogicCompEnum.InetAddr,
          EqualLogicCompEnum.StoragePool
        ]
    },
    "Member": {
        "_components_enum": [
            EqualLogicCompEnum.System,
            EqualLogicCompEnum.Member,
            EqualLogicCompEnum.InetAddr,
            EqualLogicCompEnum.StoragePool
        ]
    },
    "PhysicalDisk": {
        "_components_enum": [
            EqualLogicCompEnum.System,
            EqualLogicCompEnum.Member,
            EqualLogicCompEnum.InetAddr,
            EqualLogicCompEnum.StoragePool,
            EqualLogicCompEnum.PhysicalDisk
        ]
    },
    "Volume": {
        "_components_enum": [
            EqualLogicCompEnum.StoragePool
        ]
    }
}

EqualLogicClassifier = [ EqualLogicCompEnum.System ]

class EqualLogic(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(EqualLogic, self).__init__(iDeviceRegistry("EqualLogic", srcdir, EqualLogicCompEnum))
        else:
            super().__init__(iDeviceRegistry("EqualLogic", srcdir, EqualLogicCompEnum))
        if PyPSNMP:
            self.protofactory.add(PSNMP(
                views = EqualLogicPSNMPViews,
                classifier = EqualLogicPSNMPClassifier,
                view_fieldspec = EqualLogicSNMPViews_FieldSpec,
                cmds = EqualLogicPSNMPCmds))
        self.protofactory.addCTree(EqualLogicComponentTree)
        self.protofactory.addClassifier(EqualLogicClassifier)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return EqualLogicEntity(self.ref, protofactory, ipaddr, creds)

class EqualLogicEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(EqualLogicEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)

        if Pyconfig_mgr:
            self.config_mgr = EqualLogicConfig(self)
        self.supports_entity_mib = False
        self.more_details_spec = EqualLogic_more_details_spec      

    def _isin(self, parentClsName, parent, childClsName, child):
        if 'MyPos' in parent:
            return parent['MyPos'] == child['ContainedIn']
        else:
            return self._get_obj_index(parentClsName, parent) in \
                   self._get_obj_index(childClsName, child)

    def _should_i_include(self, component, entry):
        if component in ["Volume"]:
            if entry["Name"] == 'vss-control' or entry["Name"] == 'pe-control-vol' or entry["Name"] == 'xpr-control-vol': 
                return False
            if 'StoragePool' in self.entityjson:
                storagepoolarr = self.entityjson['StoragePool']
                if 'StoragePoolIndex' in entry:
                    for p in storagepoolarr:
                        if str(p['_SNMPIndex']).endswith((str(entry['StoragePoolIndex']))):
                            entry['AssociatedPool'] = p['StorageName']
        if component in ["PhysicalDisk", "Member"]:
            if self.entityjson["System"][0]["DeviceType"] != "EqualLogic Member":
                return False
            elif entry["_SNMPIndex"].find(self.entityjson["System"][0]["_SNMPIndex"]) != 0:
                return False
        if component == "System":
            if 'GroupIP' in entry:
                entry['GroupURL'] = "http://"+entry['GroupIP']
            if ':' in self.ipaddr:
                if 'GroupIPv6' in entry:
                    entry['GroupURL'] = "http://"+"["+entry['GroupIPv6']+"]"
                    entry['GroupIP'] = entry['GroupIPv6'] 
        if component == "Member":
            if ':' in self.ipaddr:
                if 'GroupIPv6' in entry:
                    entry['GroupIP'] = entry['GroupIPv6']
            if 'StoragePool' in self.entityjson:
                storagepoolarr = self.entityjson['StoragePool']
                if 'EqlDriveGroupStoragePoolIndex' in entry:
                    for p in storagepoolarr:
                        if str(entry['EqlDriveGroupStoragePoolIndex']) == str(p['_SNMPIndex'])[-1]:
                            entry['StoragePool'] = p['StorageName']
        return True

    def _call_it(self,keyComp):
        self.memid = "" 
        sys_dict = self.entityjson[keyComp][0]
        for item in self.entityjson:
            if type(self.entityjson[item]) is list:
                for temp in self.entityjson[item]:
                    if temp['_SNMPIndex'].find('.' + self.ipaddr) > 0:
                        #code is IPv4 specific 
                        templist = temp['_SNMPIndex'].split(".1.4." + self.ipaddr)
                        self.memid = templist[0]
                        #get the exact member index
                        #self._get_index(self.memid)
                        #it help you to filter member specific values  
                    if ':' in self.ipaddr:
                        #code is IPv6 specific
                        if (sys.version_info > (3, 0)):
                            u = self.ipaddr
                        else:
                            u = unicode(self.ipaddr, "utf-8")
                        addr = ipaddress.ip_address(u)
                        v = addr.exploded.replace(":", "")
                        x = [int(v[i:i+2], 16) for i in range(0, len(v), 2)]
                        z = ".".join(str(l) for l in x)
                        if temp['_SNMPIndex'].find('.' + z) > 0:
                            templist = temp['_SNMPIndex'].split(".2.16." + z)
                            self.memid = templist[0]
        if ':' in self.ipaddr:
            if (sys.version_info > (3, 0)):
                u = self.ipaddr
            else:
                u = unicode(self.ipaddr, "utf-8")
            addr = ipaddress.ip_address(u)
            ipaddr = str(addr.exploded)
            if (ipaddr == sys_dict.get('GroupIPv6')):
                sys_dict.update({"DeviceType" : "EqualLogic Group"})
            elif keyComp == 'System':
                sys_dict.update({'_SNMPIndex': self.memid})
                sys_dict.update({"DeviceType": "EqualLogic Member"})
        elif (self.ipaddr == sys_dict.get('GroupIP')):
            sys_dict.update({"DeviceType" : "EqualLogic Group"})
        elif keyComp == 'System':
            sys_dict.update({'_SNMPIndex':self.memid})
            sys_dict.update({"DeviceType" : "EqualLogic Member"})
        if self.entityjson.get('Member', None):
            for item in self.entityjson.get('Member', None):
                item.update({"GroupName" : self.entityjson[keyComp][0].get('GroupName', None)})

    def _get_index(self,memid):
        print ("memid:", memid)
        temp1,temp2 = memid.split("1.")
        return temp2
