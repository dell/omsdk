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

try:
    from omdrivers.F10.lifecycle.F10Config import F10Config
    from omdrivers.F10.lifecycle.F10Config import F10PSNMPCmds
    from omdrivers.F10.lifecycle.F10Config import ConfigFileTypeEnum
    Pyconfig_mgr = True
except ImportError:
    Pyconfig_mgr = False

class NoConfig:
    def __init__(self, obj):
        logger.debug("not implemented")

if not Pyconfig_mgr:
    F10Config = NoConfig
if not Pyconfig_mgr and PyPSNMP:
    F10PSNMPCmds = {}

F10CompEnum = EnumWrapper('F10CompEnum', {
    "System" : "System",
    "FanTray" : "FanTray",
    "PEBinding" : "PEBinding",
    "Card" : "Card",
    "Chassis" : "Chassis",
    "PowerSupply" : "PowerSupply",
    "Flash" : "Flash",
    "SwModule" : "SwModule",
    "SysIf" : "SysIf",
    "StackPort" : "StackPort",
    "SysCores" : "SysCores",
    "StackUnit" : "StackUnit",
    "CpuUtil" : "CpuUtil",
    "PE" : "PE",
    "Processor" : "Processor",
    "Port" : "Port",
    "Fan" : "Fan",
    "PowerSupplyTray" : "PowerSupplyTray",
}).enum_type

F10MiscEnum = EnumWrapper("F10MiscEnum", {
    "EntityPortMap" : "EntityPortMap"
    }).enum_type

F10ComponentTree = {
    F10CompEnum.System : [
        F10CompEnum.Fan,
        F10CompEnum.PowerSupply,
        "Interfaces"
    ],
    "Interfaces": [
        "UserPorts"
    ],
    "UserPorts": [
                F10CompEnum.Port
    ]
}

if PyPSNMP:
    F10PSNMPViews = {
     F10CompEnum.System : { 
         'SysObjectID' : ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
         'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.4"),
         'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.1"),
         'Model' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.7"),
         'Description' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.2"),
         'FirmwareVersion' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.4"),
         'Location' : ObjectIdentity("1.3.6.1.2.1.1.6"),
         'NetwUMACAddress' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.16"),
         'NetwUStatus':  ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.8"),
         'NetwUSerialNo':  ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.11"),
         'NetwUPartNo':  ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.17"),
         'PPID' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.7"),
         'ExpressServiceCode' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.9"),
         #M - Series switch is failing hence commented this out
         #'ManagementIP' :  ObjectIdentity("1.3.6.1.2.1.4.20.1.1"),
         'Hostname' : ObjectIdentity("1.3.6.1.2.1.1.5"),
         'SwitchUptime': ObjectIdentity("1.3.6.1.2.1.1.3"),
         #This is crashing throwing error as Device not fiund
         #'HWVersion': ObjectIdentity("1.3.6.1.2.1.47.1.1.1.1.8"),
     },
     F10CompEnum.Port : {
       'Description' : ObjectIdentity('IF-MIB', 'ifDescr'),
       'Type' : ObjectIdentity('IF-MIB', 'ifType'),
       'Address' : ObjectIdentity('IF-MIB', 'ifPhysAddress'),
       'ifIndex' : ObjectIdentity('IF-MIB', 'ifIndex'),
       'Status' : ObjectIdentity('1.3.6.1.2.1.2.2.1.7'),
       'ifInOctets' : ObjectIdentity('1.3.6.1.2.1.2.2.1.10'),
       'ifOutOctets' : ObjectIdentity('1.3.6.1.2.1.2.2.1.16'),
       'ifInDiscards' : ObjectIdentity('1.3.6.1.2.1.2.2.1.13'),
       'ifOutDiscards' : ObjectIdentity('1.3.6.1.2.1.2.2.1.19'),
       'ifInErrors' : ObjectIdentity('1.3.6.1.2.1.2.2.1.14'),
       'ifOutErrors' : ObjectIdentity('1.3.6.1.2.1.2.2.1.20'),
       'ifInUnknownProtos' : ObjectIdentity('1.3.6.1.2.1.2.2.1.15'),
       'ifSpeed' : ObjectIdentity('1.3.6.1.2.1.2.2.1.5'),
       'SysIfName' : ObjectIdentity('1.3.6.1.4.1.6027.3.26.1.4.10.1.2'),
     },
     F10MiscEnum.EntityPortMap : {
       'ifIndex' : ObjectIdentity('ENTITY-MIB', 'entAliasMappingIdentifier'),
       'Class' : ObjectIdentity('ENTITY-MIB', 'entPhysicalClass'),
     },
     F10CompEnum.FanTray : {
       'FanDeviceIndex' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.3"),
       'PiecePartID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.5"), 
       'Type' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.1"),
       'ExpressServiceCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.8"),
       'PPIDRevision' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.6"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.7"), 
       'OperStatus' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.4"),
       # 'Speed' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.4"),
     },
     F10CompEnum.Fan: {
       'Index': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.1"),
       'Description': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.2"),
       'OperStatus': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.3"),
       'Speed': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.4"),
     },
     F10CompEnum.PEBinding : {
       'PEBindPEIndex' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.1.1.2"),
       'PEBindCascadePortIfIndex' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.1.1.1"),
     },
     F10CompEnum.Card : {
       'PartNum' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.9"), 
       'NumOfPorts' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.17"), 
       'Type' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.2"), 
       'MfgDate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.8"), 
       'Status' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.5"), 
       'ProductRev' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.10"), 
       'VendorId' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.7"), 
       'CountryCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.12"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.1"), 
       'Description' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.3"), 
       'PPIDRevision' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.14"), 
       'ChassisIndex' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.4"), 
       'PiecePartID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.13"), 
       'ProductOrder' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.11"), 
       'ExpServiceCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.16"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.15"), 
       'Temp' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.4.1.6"), 
     },
     F10CompEnum.Chassis : {
       'MfgDate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.8"), 
       'ExpServiceCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.12"), 
       'NumSlots' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.13"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.11"), 
       'PPIDRev' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.10"), 
       'CountryCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.9"), 
       'PartNum' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.5"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.1"), 
       'NumPowerSupplies' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.16"), 
       'NumLineCardSlots' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.14"), 
       'NumFanTrays' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.15"), 
       'Type' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.2"), 
       'ProductRev' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.6"), 
       'VendorId' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.7"), 
       'MacAddr' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.3"), 
       'SerialNumber' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.2.3.1.4"), 
       'WebURL' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.6"),
     },
     F10CompEnum.PowerSupply : {
       'Index' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.1"),
       'OperStatus' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.3"),
       'Description': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.2"),
       'Source': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.4"),
       'envMonSupplyCurrentPower': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.5"),
       'envMonSupplyAveragePower': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.6"),
       'envMonSupplyAvgStartTime': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.7"),
     },
     F10CompEnum.PowerSupplyTray: {
       'ServiceTag': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.8"),
       'OperStatus': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.4"),
       'PowerDeviceType': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.1"),
       'PiecePartID': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.6"),
       'ExpressServiceCode': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.9"),
       'Type': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.5"),
       'PowerDeviceIndex': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.3"),
       'Usage': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.10"),
       'PPIDRevision': ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.6.1.7"),
     },
     F10CompEnum.Flash : {
       'PartitionFree' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.8.1.5"),
       'PartitionNumber' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.8.1.1"),
       'PartitionSize' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.8.1.3"),
       'PartitionMountPoint' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.8.1.6"),
       'PartitionUsed' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.8.1.4"),
       'PartitionName' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.8.1.2"),
     },
     F10CompEnum.SwModule : {
       'BootSelectorImgVersion' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.4"), 
       'NextRebootImage' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.5"), 
       'BootFlashImgVersion' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.3"), 
       'CurrentBootImage' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.6"), 
       'RuntimeImgDate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.2"), 
       'RuntimeImgVersion' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.1"), 
       'InPartitionAImgVers' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.7"), 
       'InPartitionBImgVers' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.5.1.8"), 
     },
     F10CompEnum.SysIf : {
       'Type' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.1"), 
       'XfpRecvPower' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.5"), 
       'OperStatus' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.4"), 
       'AdminStatus' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.3"), 
       'XfpTxPower' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.7"), 
       'XfpRecvTemp' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.6"), 
       'Name' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.10.1.2"), 
     },
     F10CompEnum.StackPort : {
       'ConfiguredMode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.2"), 
       'RunningMode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.3"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.1"), 
       'LinkSpeed' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.5"), 
       'RxTotalErrors' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.8"), 
       'TxDataRate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.9"), 
       'RxErrorRate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.7"), 
       'TxTotalErrors' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.11"), 
       'RxDataRate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.6"), 
       'TxErrorRate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.10"), 
       'LinkStatus' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.5.1.4"), 
     },
     F10CompEnum.SysCores : {
       'StackUnitNumber' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.9.1.4"), 
       'FileName' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.9.1.2"), 
       'Instance' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.9.1.1"), 
       'TimeCreated' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.9.1.3"), 
       'Process' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.9.1.5"), 
     },
     F10CompEnum.StackUnit : {
       'ProductOrder' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.19"), 
       'VendorId' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.14"), 
       'MgmtStatus' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.4"), 
       'MacAddress' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.16"), 
       'MfgDate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.15"), 
       'Status' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.8"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.2"), 
       'Number' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.1"), 
       'CountryCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.20"), 
       'PPIDRevision' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.22"), 
       'AdmMgmtPreference' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.6"), 
       'Description' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.9"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.23"), 
       'NumPluggableModules' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.28"), 
       'ModelId' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.7"), 
       'PartNum' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.17"), 
       'NumOfPorts' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.25"), 
       'HwMgmtPreference' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.5"), 
       'NumFanTrays' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.26"), 
       'UpTime' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.12"), 
       'CodeVersion' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.10"), 
       'ProductRev' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.18"), 
       'IOMMode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.29"), 
       'PiecePartID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.21"), 
       'ExpServiceCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.24"), 
       'Temp' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.13"), 
       'NumPowerSupplies' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.27"), 
       'BladeSlotId' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.30"), 
       'SerialNumber' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.11"), 
     },
     F10CompEnum.CpuUtil : {
       'CpuFlashUsage' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.4.1.7"),
       'MemUsage' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.4.1.6"), 
       '5Min' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.4.1.5"), 
       '5Sec' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.4.1.1"), 
       '1Min' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.4.1.4"), 
     },
     F10CompEnum.PE : {
       'VendorId' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.8"), 
       'Description' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.5"), 
       'PEID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.2"), 
       'PiecePartID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.14"), 
       'CountryCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.13"), 
       'UnitID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.3"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.16"), 
       'PartNum' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.10"), 
       'ExpServiceCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.17"), 
       'NumPowerSupplies' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.20"), 
       'MfgDate' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.9"), 
       'NumPluggableModules' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.21"), 
       'Temp' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.7"), 
       'Status' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.6"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.1"), 
       'PPIDRevision' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.15"), 
       'ProductRev' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.11"), 
       'NumFanTrays' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.19"), 
       'Type' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.4"), 
       'NumOfPorts' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.18"), 
       'ProductOrder' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.2.1.12"), 
     },
     F10CompEnum.Processor : {
       'DeviceType' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.1"), 
       'Module' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.4"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.3"),
       'UpTime' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.5"), 
       'AvailableMemSize' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.6"), 
     },
    }
    F10SNMPViews_FieldSpec = {
        F10CompEnum.System : {
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical"
                }
            },
            "Model" : {
                'Lookup'  :  'True',
                'Values' : {
			"1" : "e1200", 
			"2" : "e600", 
			"3" : "e300", 
			"4" : "e150", 
			"5" : "e610", 
			"6" : "c150", 
			"7" : "c300", 
			"8" : "e1200i", 
			"9" : "s2410cp", 
			"10" : "s2410p", 
			"11" : "s50", 
			"12" : "s50e", 
			"13" : "s50v", 
			"14" : "s50nac", 
			"15" : "s50ndc", 
			"16" : "s25pdc", 
			"17" : "s25pac", 
			"18" : "s25v", 
			"19" : "s25n", 
			"20" : "s60", 
			"21" : "s55", 
			"22" : "s4810", 
			"23" : "s6410", 
			"24" : "z9000", 
			"25" : "m-MXL", 
			"26" : "m-IOA", 
			"27" : "s4820", 
			"28" : "s6000", 
			"29" : "s5000", 
			"30" : "s-FN410S-IOA", 
			"31" : "s-FN410T-IOA", 
			"32" : "s-FN2210S-IOA", 
			"33" : "z9500", 
			"34" : "c9010", 
			"35" : "c1048p", 
			"36" : "s4048on", 
			"37" : "s4810on", 
			"38" : "s6000on", 
			"39" : "s3048on", 
			"40" : "z9100", 
			"41" : "s6100", 
			"42" : "s3148p", 
			"43" : "s3124p", 
			"44" : "s3124f", 
			"45" : "s3124", 
			"46" : "s3148", 
			"47" : "s4048ton", 
			"48" : "s6010", 
			"49" : "n2048p", 
			"50" : "n2024p", 
			"51" : "n2024", 
			"52" : "n2048", 
			"53" : "n3048p", 
			"54" : "n3024p", 
			"55" : "n3024f", 
			"56" : "n3024", 
			"57" : "n3048"
                }
            },
            "NetwUMACAddress" : {
                'Macedit' : 'True'
                },
            "NetwUStatus": {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Ok",
                    "2" : "Unsupported",
                    "3" : "Code Mismatch",
                    "4" : "Config Mismatch",
                    "5" : "Unit Down",
                    "6" : "Not Present"
                }
            }
        },
        F10CompEnum.PowerSupply : {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Healthy",
                    "2" : "Warning",
                    "3" : "Critical",
                    "4" : "Unknown",
                    "5" : "Absent",
                    "6" : "Critical"
                }
            },
            "Source" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "AC",
                    "3" : "DC",
                    "4" : "External PowerSupply",
                    "5" : "Internal Redundant",
                }
            }
        },
        F10CompEnum.FanTray : {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1": "Up",
                    "2": "Down",
                    "3": "Absent",
                    "4": "Unknown"
                }
            },
            "Type" : {
                'Lookup'  :  'True',
                'Values' : {
			"1" : "Chassis", 
			"2" : "Stack", 
			"3" : "RPM", 
			"4" : "Supervisor", 
			"5" : "Linecard", 
			"6" : "Port-extender" 
                }
            }
        },
        F10CompEnum.Port : {
            "Status" : {
                'Lookup'  :  'True',
                'Values' : {
                    "up" : "Up",
                    "down" : "Down",
                    "testing" : "Testing"
                }
            }
        },
        F10CompEnum.PowerSupplyTray : {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "0" : "Unknown",
                    "1" : "Up",
                    "2" : "Down",
                    "3" : "Absent"
                }
            },
            "Type" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "AC",
                    "3" : "DC"
                }
            }
        },
        F10CompEnum.Fan: {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Healthy",
                    "2" : "Warning",
                    "3" : "Critical",
                    "4" : "Unknown",
                    "5" : "Absent",
                    "6" : "Critical"
                }
            }
        },
        F10CompEnum.Processor : {
            "AvailableMemSize" : { 'Type' : 'Bytes' , 'InUnits' : 'MB', 'OutUnits' : 'GB' },
            "Module" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "ControlProcessor",
                    "2" : "RoutingProcessor1",
                    "3" : "RoutingProcessor2",
                    "4" : "LinecardProcessor",
                    "5" : "RpmProcessor",
                    "6" : "RoutingProcessor"
                }
            }
        },
        F10CompEnum.Flash : {
            "PartitionSize" : { 'Type' : 'Bytes' , 'InUnits' : 'KB', 'OutUnits' : 'GB' },
            "PartitionFree" : { 'Type' : 'Bytes' , 'InUnits' : 'KB', 'OutUnits' : 'GB' },
            "PartitionUsed" : { 'Type' : 'Bytes' , 'InUnits' : 'KB', 'OutUnits' : 'GB' },
        },
        F10CompEnum.SysIf: {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Healthy",
                    "2" : "Warning",
                    "3" : "Critical",
                    "4" : "Unknown",
                    "5" : "Absent",
                    "6" : "Critical"
                }
            },
            "AdminStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Up",
                    "2": "Down"
                }
            },
            "Type": {
                'Lookup': 'True',
                'Values': {
                    "1": "Port Serial",
                    "2": "Port Fast Ether",
                    "3": "Port Gig Ether",
                    "4": "Port 10 Gig Ether",
                    "5": "Port 40 Gig Ether",
                    "6": "Port Fibre Channel",
                    "7": "Port Aux",
                    "8": "Port 25 Gig Ether",
                    "9": "Port 50 Gig Ether",
                    "10": "Port 100 Gig Ether",
                    "11": "Port PEGig Ether",
                    "99": "Port Unknown"
                }
            }
        },
        F10CompEnum.StackUnit: {
            "Status": {
                'Lookup': 'True',
                'Values': {
                    "1" : "Ok",
                    "2" : "Unsupported",
                    "3" : "Code Mismatch",
                    "4" : "Config Mismatch",
                    "5" : "Unit Down",
                    "6" : "Not Present"
                }
            },
            "ModelId": {
                'Lookup': 'True',
                'Values': {
                    "1" : "e1200",
                    "2" : "e600",
                    "3" : "e300",
                    "4" : "e150",
                    "5" : "e610",
                    "6" : "c150",
                    "7" : "c300",
                    "8" : "e1200i",
                    "9" : "s2410cp",
                    "10" : "s2410p",
                    "11" : "s50",
                    "12" : "s50e",
                    "13" : "s50v",
                    "14" : "s50nac",
                    "15" : "s50ndc",
                    "16" : "s25pdc",
                    "17" : "s25pac",
                    "18" : "s25v",
                    "19" : "s25n",
                    "20" : "s60",
                    "21" : "s55",
                    "22" : "s4810",
                    "23" : "s6410",
                    "24" : "z9000",
                    "25" : "m-MXL",
                    "26" : "m-IOA",
                    "27" : "s4820",
                    "28" : "s6000",
                    "29" : "s5000",
                    "30" : "s-FN410S-IOA",
                    "31" : "s-FN410T-IOA",
                    "32" : "s-FN2210S-IOA",
                    "33" : "z9500",
                    "34" : "c9010",
                    "35" : "c1048p",
                    "36" : "s4048on",
                    "37" : "s4810on",
                    "38" : "s6000on",
                    "39" : "s3048on",
                    "40" : "z9100",
                    "41" : "s6100",
                    "42" : "s3148p",
                    "43" : "s3124p",
                    "44" : "s3124f",
                    "45" : "s3124",
                    "46" : "s3148",
                    "47" : "s4048ton",
                    "48" : "s6010",
                    "49" : "n2048p",
                    "50" : "n2024p",
                    "51" : "n2024",
                    "52" : "n2048",
                    "53" : "n3048p",
                    "54" : "n3024p",
                    "55" : "n3024f",
                    "56" : "n3024",
                    "57" : "n3048"
                }
            },
            "MgmtStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Management Unit",
                    "2": "Standby Unit",
                    "3": "Stack Unit",
                    "4": "Unassigned"
                }
            },
            "HwMgmtPreference": {
                'Lookup': 'True',
                'Values': {
                    "0": "Disabled",
                    "1": "Unassigned",
                    "2": "Assigned"
                }
            },
            "MacAddress": {
                'Macedit': 'True'
            },
            "Temp": {'UnitScale': '0', 'UnitAppend' : 'Degree Celsius'}
        }
    }

    F10PSNMPClassifier = {
        F10CompEnum.System : {
            'SysObjectID' : 'SNMPv2-SMI::enterprises\\.6027' 
        }
    }
else:
    F10PSNMPViews = {}
    F10PSNMPClassifier = {}

F10Classifier = [ F10CompEnum.System ]

F10SubsystemHealthSpec = {
    F10CompEnum.System : { "Component" : F10CompEnum.System, "Field" : 'PrimaryStatus' },
}

F10_more_details_spec = {
    "Port": {
        "_components_enum": [
            F10CompEnum.Port,
            F10MiscEnum.EntityPortMap
        ]
    },
    "System": {
        "_components_enum": [
            F10CompEnum.System,
            F10CompEnum.Fan,
            F10CompEnum.PowerSupply,
        ]
    }
}

def check_classifier(myListoFDict, cls=None):
    # Full OID to be expanded and added to list
    # sobj_list = ['SNMPv2-SMI::enterprises.6027.1.3.20', 'SNMPv2-SMI::enterprises.6027.1.3.23']
    sys_obj_str = 'SNMPv2-SMI::enterprises.6027.1.3.'
    if isinstance(myListoFDict, list):
        for sys in myListoFDict:
            if sys_obj_str in sys.get('SysObjectID', "NA"):
                return (True, sys)
    elif isinstance(myListoFDict, dict):
        return (True, myListoFDict)
    return (False, myListoFDict)

classify_cond = {
    F10CompEnum.System :
    {
        ProtocolEnum.SNMP : check_classifier
    }
}

class F10(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(F10, self).__init__(iDeviceRegistry("F10", srcdir, F10CompEnum))
        else:
            super().__init__(iDeviceRegistry("F10", srcdir, F10CompEnum))
        if PyPSNMP:
            self.protofactory.add(PSNMP(
                views = F10PSNMPViews,
                classifier = F10PSNMPClassifier,
                classifier_cond= classify_cond,
                view_fieldspec = F10SNMPViews_FieldSpec,
                cmds = F10PSNMPCmds))
        self.protofactory.addCTree(F10ComponentTree)
        self.protofactory.addClassifier(F10Classifier)
        self.protofactory.addSubsystemSpec(F10SubsystemHealthSpec)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return F10Entity(self.ref, protofactory, ipaddr, creds)

class F10Entity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(F10Entity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.more_details_spec = F10_more_details_spec
        if Pyconfig_mgr:
            self.config_mgr = F10Config(self)
        self.supports_entity_mib = False

    def _isin(self, parentClsName, parent, childClsName, child):
        if 'MyPos' in parent:
            return parent['MyPos'] == child['ContainedIn']
        else:
            return self._get_obj_index(parentClsName, parent) in \
                   self._get_obj_index(childClsName, child)
    def _should_i_include(self, component, entry):
        comp_list = ["Flash", "SwModule", "SysCores", "Chassis", "CpuUtil", "FanTray", \
                     "PowerSupplyTray", "Processor", "PEBinding", "StackPort"]
        if component in comp_list:
            if entry.get("Name", "NA") == component+"_Name_null":
                entry['Name'] = component
        if component in ["Fan", "FanTray", "PowerSupplyTray", "PowerSupply"]:
            if entry.get("OperStatus") == 'Absent':
                return False
        if component in ["Port"]:
            if entry.get("Status") == 'Testing':
                return False
            if 'ifIndex' in entry:
                if entry.get("ifIndex") == component + '_ifIndex_null':
                    return False
            # This is implimented to ignore virtual port instances
            if not 'SysIfName' in entry:
                    return False
        if component in ["System"]:
            name = entry.get("Hostname", "Not Available")
            entry["Hostname"] = name.strip('\"\'')
            if 'SwitchUptime' in entry:
                x = entry.get("SwitchUptime", "Seconds").split()
                if "Seconds" not in x :
                    s = float(entry.get("SwitchUptime", 0)) / 100.0
                    m, s = divmod(s, 60)
                    h, m = divmod(m, 60)
                    l = [('Hours', int(h)), ('Minutes', int(m)), ('Seconds', int(s))]
                    entry["SwitchUptime"] = ' '.join('{} {}'.format(value, name)
                                        for name, value in l
                                        if value)
            if 'Model' in entry:
                entry["SwitchType"] = entry.get('Model')[:1].upper()+"Series"
            if ':' in self.ipaddr:
                entry['SwitchIPv6'] = self.ipaddr
            else:
                entry['SwitchIPv4'] = self.ipaddr

        if component in ["Processor", "StackUnit"]:
            if 'UpTime' in entry:
                x = entry.get("UpTime", "Seconds").split()
                if "Seconds" not in x :
                    s = float(entry.get("UpTime", 0)) / 100.0
                    m, s = divmod(s, 60)
                    h, m = divmod(m, 60)
                    l = [('Hours', int(h)), ('Minutes', int(m)), ('Seconds', int(s))]
                    entry["UpTime"] = ' '.join('{} {}'.format(value, name)
                                        for name, value in l
                                        if value)
        if component in ["EntityPortMap"]:
            if 'ifIndex' in entry:
                if entry.get("ifIndex") == component + '_ifIndex_null':
                        return False
                temp = entry.get("ifIndex", "NA").split(".")[-1]
                entry["ifIndex"] =  temp
        return True

    def _should_i_modify_component(self, finalretjson, component):
        if component == 'Port':
            if "Port" and "EntityPortMap" in finalretjson:
                 Portlist = finalretjson.get('Port')
                 entportlist = finalretjson.get('EntityPortMap')
                 tempEntPortDict = {}
                 for ep in entportlist:
                     if "ifIndex" in ep:
                        tempEntPortDict[ep['ifIndex']] = ep
                 for dnp in Portlist:
                     if "ifIndex" in dnp:
                         dnp['Class'] = tempEntPortDict.get(dnp.get('ifIndex', "NA"),{}).get('Class', 'Not Available')
        if component == 'EntityPortMap':
            del finalretjson[component]

    @property
    def ContainmentTree(self):
        """
        Adding Fan and PowerSupply to Scalable CompTree
        :return: JSON
        """
        device_json = self.get_json_device()
        ctree = self._build_ctree(self.protofactory.ctree, device_json)
        mf10model = self.entityjson.get('System',[None])[0].get('Model', "")
        if 'm-MXL' in mf10model or 'm-IOA' in mf10model:
            return ctree
        fn = {"Fan":[]}
        ps = {"PowerSupply":[]}
        if not "Fan" in ctree.get("System"):
            ctree["System"].update(fn)
        if not "PowerSupply" in ctree.get("System"):
            ctree.get("System", "NA").update(ps)
        return ctree

    def get_basic_entityjson(self):
        plist = []
        for comp in self.protofactory.classifier:
            plist.append(comp)
        entj = self.get_partial_entityjson(*plist)
        if entj:
            compList = ["Fan", "PowerSupply"]
            for comp in compList:
                tmp = {}
                compiList = entj.pop(comp, [])
                if compiList:
                    finalStat = 'Healthy'
                    for iComp in compiList:
                        iStat = iComp.get('OperStatus','Unknown')
                        if iStat == 'Critical':
                            finalStat = iStat
                            break
                        elif iStat == 'Warning':
                            finalStat = iStat
                        elif iStat == 'Unknown' and finalStat != 'Warning':
                            finalStat = iStat
                    tmp.update({"Key": comp})
                    tmp.update({"PrimaryStatus": finalStat})
                    entj.get("Subsystem", []).append(tmp)

    def get_entityjson(self):
        plist = []
        for comp in self.ComponentEnum:
            plist.append(comp)
        entj = self.get_partial_entityjson(*plist)
        if entj:
            compList = ["Fan", "PowerSupply"]
            for comp in compList:
                tmp = {}
                compiList = entj.get(comp, [])
                if compiList:
                    finalStat = 'Healthy'
                    for iComp in compiList:
                        iStat = iComp.get('OperStatus','Unknown')
                        if iStat == 'Critical':
                            finalStat = iStat
                            break
                        elif iStat == 'Warning':
                            finalStat = iStat
                        elif iStat == 'Unknown' and finalStat != 'Warning':
                            finalStat = iStat
                    tmp.update({"Key": comp})
                    tmp.update({"PrimaryStatus": finalStat})
                    entj.get("Subsystem", "NA").append(tmp)
