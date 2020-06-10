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
import os
import sys

from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.sdkdevice import iDeviceTopologyInfo
from omsdk.sdkproto import PWSMAN,PREDFISH, PSNMP, ProtocolEnum, ProtocolOptionsFactory
from omdrivers.enums.iDRAC.iDRACEnums import *
from omsdk.idracmsgdb import eemiregistry
from omsdk.sdkcenum import TypeHelper
from omsdk.http.sdkredfishbase import RedfishOptions
from omsdk.http.sdkwsmanbase import WsManOptions

logger = logging.getLogger(__name__)


class NoConfig:
    def __init__(self, arg1):
        logger.debug("iDRAC:Not implemented")


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False

try:
    from omdrivers.lifecycle.iDRAC.iDRACJobs import iDRACJobs
    from omdrivers.lifecycle.iDRAC.iDRACConfig import iDRACConfig
    from omdrivers.lifecycle.iDRAC.iDRACConfig import iDRACRedfishCmds
    from omdrivers.lifecycle.iDRAC.iDRACConfig import iDRACWsManCmds
    from omdrivers.lifecycle.iDRAC.iDRACLogs import iDRACLogs
    from omdrivers.lifecycle.iDRAC.iDRACUpdate import iDRACUpdate
    from omdrivers.lifecycle.iDRAC.iDRACLicense import iDRACLicense
    from omdrivers.lifecycle.iDRAC.iDRACSecurity import iDRACSecurity
    from omdrivers.lifecycle.iDRAC.iDRACStreaming import iDRACStreaming
    from omdrivers.lifecycle.iDRAC.iDRACCredsMgmt import iDRACCredsMgmt
except ImportError as ex:
    logger.debug(str(ex))
    iDRACJobs = NoConfig
    iDRACConfig = NoConfig
    iDRACLogs = NoConfig
    iDRACUpdate = NoConfig
    iDRACRedfishCmds = {}
    iDRACWsManCmds = {}

iDRACCompEnum = EnumWrapper("iDRACCompEnum", {
    "System" : "System",
    "Memory" : "Memory",
    "CPU" : "CPU",
    "iDRAC" : "iDRAC",
    "FC" : "FC",
    "NIC" : "NIC",
    "HostNIC" : "HostNIC",
    "PCIDevice" : "PCIDevice",
    "Fan" : "Fan",
    "PowerSupply" : "PowerSupply",
    "Enclosure" : "Enclosure",
    "EnclosureEMM" : "EnclosureEMM",
    "EnclosurePSU" : "EnclosurePSU",
    "EnclosureSensor" : "EnclosureSensor",
    "EnclosureFanSensor" : "EnclosureFanSensor",
    "EnclosureTempSensor" : "EnclosureTempSensor",
    "VFlash"  : "VFlash",
    "Video" : "Video",
    "ControllerBattery" : "ControllerBattery" ,
    "Controller" : "Controller",
    "ControllerSensor" : "ControllerSensor",
    "VirtualDisk" : "VirtualDisk",
    "PhysicalDisk" : "PhysicalDisk",
    "PCIeSSDExtender" : "PCIeSSDExtender",
    "PCIeSSDBackPlane" : "PCIeSSDBackPlane",
    "PCIeSSDDisk" : "PCIeSSDDisk",
    "Sensors_Amperage" : "Sensors_Amperage",
    "Sensors_Temperature" : "Sensors_Temperature",
    "Sensors_Voltage" : "Sensors_Voltage",
    "Sensors_Intrusion" : "Sensors_Intrusion",
    "Sensors_Battery" : "Sensors_Battery",
    "Sensors_Fan" : "Sensors_Fan",
    "LogicalSystem" : "LogicalSystem",
    "License" : "License",
    "iDRACNIC" : "iDRACNIC",
    "BIOS" : "BIOS",
    "SystemMetrics" : "SystemMetrics",
    "SystemBoardMetrics" : "SystemBoardMetrics",
    "PresenceAndStatusSensor" : "PresenceAndStatusSensor"
    }).enum_type

iDRACSensorEnum = EnumWrapper("iDRACSensorEnum", {
    "ServerSensor" : "ServerSensor",
    "NumericSensor" : "NumericSensor",
    "PSNumericSensor" : "PSNumericSensor",
    }).enum_type

iDRACMiscEnum = EnumWrapper("iDRACMiscEnum", {
    "SystemString" : "SystemString",
    "NICString" : "NICString",
    "NICEnumeration" : "NICEnumeration",
    "iDRACString" : "iDRACString",
    "iDRACEnumeration" : "iDRACEnumeration",
    "NICStatistics" : "NICStatistics",
    "NICCapabilities" : "NICCapabilities",
    "SwitchConnection" : "SwitchConnection",
    "FCStatistics" : "FCStatistics",
    "HostNICView" : "HostNICView",
    "RAIDEnumeration" : "RAIDEnumeration",
    "LCString" : "LCString",
    "ChassisRF" : "ChassisRF",
    "DellAttributes" : "DellAttributes"
    }).enum_type

iDRACMetricsEnum = EnumWrapper("iDRACMetricsEnum", {
    "AggregationMetric" : "AggregationMetric",
    "BaseMetricValue" : "BaseMetricValue",
    }).enum_type


#iDRACFirmEnum.SelLog : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SELLogEntry",

iDRACComponentTree = {
    iDRACCompEnum.System : [ 
        iDRACCompEnum.Memory, 
        iDRACCompEnum.CPU, 
        iDRACCompEnum.iDRAC,
        iDRACCompEnum.FC,
        iDRACCompEnum.NIC,
        iDRACCompEnum.PCIDevice,
        iDRACCompEnum.Fan,
        iDRACCompEnum.PowerSupply,
        iDRACCompEnum.VFlash,
        iDRACCompEnum.Video,
        iDRACCompEnum.License,
        iDRACCompEnum.HostNIC,
        iDRACCompEnum.BIOS,
        "Sensors",
        "Storage"
    ],
    iDRACCompEnum.iDRAC : [
        iDRACCompEnum.iDRACNIC,
    ],
    "Storage" : [
        iDRACCompEnum.Controller,
        iDRACCompEnum.PCIeSSDExtender
    ],
    "Sensors" : [
        iDRACCompEnum.Sensors_Amperage,
        iDRACCompEnum.Sensors_Temperature,
        iDRACCompEnum.Sensors_Voltage,
        iDRACCompEnum.Sensors_Intrusion,
        iDRACCompEnum.Sensors_Battery,
        iDRACCompEnum.Sensors_Fan,
        iDRACCompEnum.PresenceAndStatusSensor
    ],
    iDRACCompEnum.Controller : [
        iDRACCompEnum.Enclosure, # Enclosure.RAID.Modular.3-1
        iDRACCompEnum.VirtualDisk, #VirtualDisk.RAID.Modular.3-1
        iDRACCompEnum.PhysicalDisk, #DirectDisk.RAID
        iDRACCompEnum.ControllerSensor
    ],
    iDRACCompEnum.VirtualDisk : [
        iDRACCompEnum.PhysicalDisk
    ],
    iDRACCompEnum.ControllerSensor : [
        iDRACCompEnum.ControllerBattery,
    ],
    iDRACCompEnum.Enclosure : [
        iDRACCompEnum.EnclosureEMM,
        iDRACCompEnum.EnclosurePSU,
        iDRACCompEnum.PhysicalDisk,
        iDRACCompEnum.EnclosureSensor,
        # iDRACCompEnum.PCIeSSDExtender
    ],
    iDRACCompEnum.PCIeSSDExtender : [
        # iDRACCompEnum.PCIeSSDBackPlane,
        iDRACCompEnum.PCIeSSDDisk
    ],
    iDRACCompEnum.PCIeSSDBackPlane : [
        iDRACCompEnum.PCIeSSDDisk
    ],
    iDRACCompEnum.EnclosureSensor : [
        iDRACCompEnum.EnclosureFanSensor,
        iDRACCompEnum.EnclosureTempSensor
    ]
}

iDRACSWCompMapping = {
    'BIOS' : 'BIOS.*',
    'CMC' : 'CMC.*',
    'CPLD' : 'CPLD.*',
    'LC' : '.*LC.Embedded.*',
    'PhysicalDisk' : 'Disk.*',
    'DriverPack' : 'DriverPack.*',
    'Enclosure' : 'Enclosure.*',
    'NIC' : 'NIC.*',
    'OSCollector' : 'OSCollector.*',
    'RAID' : 'RAID.*',
    'iDRAC' : 'iDRAC.*',
    'Chassis' : '.*Chassis.*'
}

# http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICStatistics
iDRACWsManViews = {
    iDRACCompEnum.System: "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_SystemView",
    iDRACCompEnum.Memory : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_MemoryView",
    iDRACCompEnum.CPU : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_CPUView",
    iDRACCompEnum.Fan : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_FanView",
    iDRACCompEnum.iDRAC : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardView",
    iDRACCompEnum.iDRACNIC : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardView",
    iDRACCompEnum.FC : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_FCView",
    iDRACCompEnum.NIC : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICView",
    iDRACCompEnum.HostNIC : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_HostNetworkInterfaceView",
    iDRACCompEnum.PowerSupply : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PowerSupplyView",
    iDRACCompEnum.VFlash : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_VFlashView",
    iDRACCompEnum.Video : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_VideoView",
    iDRACCompEnum.PhysicalDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PhysicalDiskView",
    iDRACCompEnum.PCIeSSDExtender : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PCIeSSDExtenderView",
    iDRACCompEnum.PCIeSSDBackPlane : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PCIeSSDBackPlaneView",
    iDRACCompEnum.PCIeSSDDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PCIeSSDView",
    iDRACCompEnum.ControllerBattery : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerBatteryView",
    iDRACCompEnum.Controller : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerView",
    iDRACCompEnum.ControllerSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerView",
    iDRACCompEnum.EnclosureEMM : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureEMMView",
    iDRACCompEnum.EnclosurePSU : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosurePSUView",
    iDRACCompEnum.Enclosure : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureView",
    iDRACCompEnum.EnclosureSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureView",
    iDRACCompEnum.PCIDevice : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PCIDeviceView",
    iDRACCompEnum.VirtualDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_VirtualDiskView",
    iDRACSensorEnum.ServerSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_Sensor",
    iDRACSensorEnum.NumericSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NumericSensor",
    iDRACSensorEnum.PSNumericSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PSNumericSensor",
    iDRACFirmEnum.Firmware : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_SoftwareIdentity",
    iDRACJobsEnum.Jobs : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob",
    iDRACOSDJobsEnum.OSDJobs : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDConcreteJob",
    # iDRACMiscEnum.SystemString : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_SystemString",
    iDRACMiscEnum.SystemString : ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_SystemString", "select FQDD,InstanceID,AttributeName,CurrentValue from DCIM_SystemString WHERE AttributeName = 'OSName' or AttributeName = 'OSVersion'"],
    # iDRACMiscEnum.NICString : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICString",
    iDRACMiscEnum.NICString: ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICString", "select FQDD,InstanceID,AttributeName,CurrentValue from DCIM_NICString WHERE AttributeName = 'VirtWWN' or AttributeName = 'VirtWWPN' or AttributeName = 'WWN' or AttributeName = 'WWPN' or AttributeName = 'VirtMacAddr'"],
    iDRACMiscEnum.NICEnumeration : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICEnumeration",
    # iDRACMiscEnum.iDRACString : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardString",
    iDRACMiscEnum.iDRACString : ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardString", "select FQDD,InstanceID,AttributeName,CurrentValue from DCIM_iDRACCardString WHERE InstanceID = 'iDRAC.Embedded.1#IPv4.1#Address' or  InstanceID = 'iDRAC.Embedded.1#Info.1#Product' or  InstanceID = 'iDRAC.Embedded.1#CurrentNIC.1#MACAddress' or  InstanceID = 'iDRAC.Embedded.1#CurrentIPv6.1#Address1' or  InstanceID = 'iDRAC.Embedded.1#GroupManager.1#GroupName' or  InstanceID = 'iDRAC.Embedded.1#NIC.1#SwitchConnection' or  InstanceID = 'iDRAC.Embedded.1#NIC.1#SwitchPortConnection' or AttributeName = 'Destination'"],
    # iDRACMiscEnum.iDRACEnumeration : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardEnumeration",
    iDRACMiscEnum.iDRACEnumeration : ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardEnumeration", "select FQDD,InstanceID,AttributeName,CurrentValue from DCIM_iDRACCardEnumeration WHERE InstanceID='iDRAC.Embedded.1#GroupManager.1#Status' or InstanceID='iDRAC.Embedded.1#NIC.1#Duplex' or InstanceID='iDRAC.Embedded.1#NIC.1#Speed' or InstanceID='iDRAC.Embedded.1#NIC.1#Enable' or InstanceID='iDRAC.Embedded.1#Lockdown.1#SystemLockdown' or AttributeName = 'State'"],
    iDRACMiscEnum.NICStatistics : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICStatistics",
    iDRACMiscEnum.NICCapabilities : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICCapabilities",
    iDRACMiscEnum.SwitchConnection : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_SwitchConnectionView",
    iDRACMiscEnum.FCStatistics : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_FCStatistics",
    iDRACMiscEnum.HostNICView : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_HostNetworkInterfaceView",
    iDRACCompEnum.License : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_License",
    iDRACLicenseEnum.LicensableDevice : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicensableDevice",
    iDRACLogsEnum.SELLog : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SELLogEntry",
    iDRACCompEnum.BIOS : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_SoftwareIdentity",
    iDRACCompEnum.EnclosureFanSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureFanSensor",
    iDRACMiscEnum.RAIDEnumeration : ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDEnumeration","select FQDD,InstanceID,AttributeName,CurrentValue from DCIM_RAIDEnumeration WHERE AttributeName = 'RAIDNegotiatedSpeed'"],
    iDRACCompEnum.EnclosureTempSensor : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureTemperatureSensor",
    iDRACMetricsEnum.BaseMetricValue : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BaseMetricValue",
    iDRACMetricsEnum.AggregationMetric : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_AggregationMetricValue",
    iDRACCompEnum.PresenceAndStatusSensor : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_PresenceAndStatusSensor",
    iDRACMiscEnum.LCString : ["http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LCString","select InstanceID,AttributeName,CurrentValue from DCIM_LCString WHERE AttributeName = 'VirtualAddressManagementApplication'"]
}

iDRACWsManViews_FieldSpec = {
    iDRACCompEnum.Memory : {
        "Size" : { 'Type' : 'Bytes', 'InUnits' : "MB" },
        "CurrentOperatingSpeed" : { 'Type' : 'ClockSpeed', 'InUnits' : "MHz", 'OutUnits' : 'MHz' },
        "Speed" : { 'Type' : 'ClockSpeed', 'InUnits' : "MHz" },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        }
    },
    iDRACCompEnum.Fan : {
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "RedundancyStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "DMTF Reserved",
                "2": "Fully Redundant",
                "3": "Degraded Redundancy",
                "4": "Redundancy Lost",
                "5": "Overall Failure",
                "6": "Not Applicable"
            }
        }
    },
    iDRACCompEnum.FC : {
        "LinkStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Down",
                "1" : "Up",
                "2" : "Unknown",
            }
        }
    },
    iDRACCompEnum.Controller : {
        "CacheSizeInMB" : { 'Rename' : 'CacheSize', 'Type' : 'Bytes', 'InUnits' : 'MB', 'OutUnits' : 'MB' },
        "SecurityStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Encryption Not Capable",
                "1" : "Encryption Capable",
                "2" : "Security Key Assigned"
            }
        },
        "EncryptionMode" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "None",
                "1" : "Local Key Management",
                "2" : "Dell Key Management",
                "3" : "Pending Dell Key Management"
            }
        },
        "EncryptionCapability" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "None",
                "1" : "Local Key Management Capable",
                "2" : "Dell Key Management Capable",
                "3" : "Local Key Management and Dell Key Management Capable"
            }
        },
        "SlicedVDCapability" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Sliced Virtual Disk creation not supported",
                "1" : "Sliced Virtual Disk creation supported"
            }
        },
        "CachecadeCapability" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Cachecade Virtual Disk not supported",
                "1" : "Cachecade Virtual Disk supported"
            }
        },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        },
        "RollupStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
            }
        }
    },
    iDRACCompEnum.CPU : {
        "CPUFamily" : {
            'Lookup'  :  'True',
            'Values' : {
                "1" : "Other",
                "2" : "Unknown",
                "3" : "8086",
                "4" : "80286",
                "5" : "80386",
                "6" : "80486",
                "7" : "8087",
                "8" : "80287",
                "9" : "80387",
                "A" : "80487",
                "B" : "Pentium(R)brand",
                "C" : "Pentium(R)Pro",
                "D" : "pentium(R) II",
                "E" : "Pentium(R) Processor with MMX(TM) technology",
                "F" : "Celeron(TM)",
                "10" : "Pentium(R) II Xeon(TM)",
                "11" : "Pentium(R) III",
                "12" : "M1 Family",
                "13" : "M2 Family",
                "14" : "Intel(R) Celeron(R) M processor",
                "15" : "Intel(R) Pentium(R) 4 HT processor",
                "18" : "K5 Family",
                "19" : "K6 Family" ,
                "1A" : "K6-2",
                "1B" : "K6-3",
                "1C" : "AMD Athlon(TM) Processor Family",
                "1D" : "AMD(R) Duron(TM) Processor",
                "1E" : "AMD29000 Family",
                "1F" : "K6-2+",
                "20" : "Power PC Family",
                "21" : "Power PC 601",
                "22" : "Power PC 603",
                "23" : "Power PC 603+",
                "24" : "Power PC 604",
                "25" : "Power PC 620",
                "26" : "Power PC X704",
                "27" : "Power PC 750",
                "28" : "Intel(R) Core(TM) Duo processor",
                "29" : "Intel(R) Core(TM) Duo mobile processor",
                "2A" : "Intel(R) Core(TM) Solo mobile processor",
                "2B" : "Intel(R) Atom(TM) processor",
                "30" : "Alpha Family",
                "31" : "Alpha 21064",
                "32" : "Alpha 21066",
                "33" : "Alpha 21164",
                "34" : "Alpha 21164PC",
                "35" : "Alpha 21164a",
                "36" : "Alpha 21264",
                "37" : "Alpha 21364",
                "38" : "AMD Turion(TM) II Ultra Dual-Core Mobile M Processor Family",
                "39" : "AMD Turion(TM) II Dual-Core Mobile M Processor Family",
                "3A" : "AMD Athlon(TM) II Dual-Core Mobile M Processor Family",
                "3B" : "AMD Opteron(TM) 6100 Series Processor",
                "3C" : "AMD Opteron(TM) 4100 Series Processor",
                "3D" : "AMD Opteron(TM) 6200 Series Processor",
                "3E" : "AMD Opteron(TM) 4200 Series Processor",
                "40" : "MIPS Family",
                "41" : "MIPS R4000",
                "42" : "MIPS R4200",
                "43" : "MIPS R4400",
                "44" : "MIPS R4600",
                "45" : "MIPS R10000",
                "46" : "AMD C-Series Processor",
                "47" : "AMD E-Series Processor",
                "48" : "AMD S-Series Processor",
                "49" : "AMD G-Series Processor",
                "50" : "SPARC Family",
                "51" : "SuperSPARC",
                "52" : "microSPARC II",
                "53" : "microSPARC IIep",
                "54" : "UltraSPARC",
                "55" : "UltraSPARC II",
                "56" : "UltraSPARC IIi",
                "57" : "UltraSPARC III",
                "58" : "UltraSPARC IIIi",
                "60" : "68040",
                "61" : "68xxx Family",
                "62" : "68000",
                "63" : "68010",
                "64" : "68020",
                "65" : "68030",
                "70" : "Hobbit Family",
                "78" : "Crusoe(TM) TM5000 Family",
                "79" : "Crusoe(TM) TM3000 Family",
                "7A" : "Efficeon(TM) TM8000 Family",
                "80" : "Weitek",
                "82" : "Itanium(TM) Processor",
                "83" : "AMD Athlon(TM) 64 Processor Family",
                "84" : "AMD Opteron(TM) Processor Family",
                "85" : "AMD Sempron(TM) Processor Family",
                "86" : "AMD Turion(TM) 64 Mobile Technology",
                "87" : "Dual-Core AMD Opteron(TM) Processor Family",
                "88" : "AMD Athlon(TM) 64 X2 Dual-Core Processor Family",
                "89" : "AMD Turion(TM) 64 X2 Mobile Technology",
                "8A" : "Quad-Core AMD Opteron(TM) Processor Family",
                "8B" : "Third Generation AMD Opteron(TM) Processor Family",
                "8C" : "AMD Phenom(TM) FX Quad-Core Processor Family",
                "8D" : "AMD Phenom(TM) X4 Quad-Core Processor Family",
                "8E" : "AMD Phenom(TM) X2 Dual-Core Processor Family",
                "8F" : "AMD Athlon(TM) X2 Dual-Core Processor Family",
                "90" : "PA-RISC Family",
                "91" : "PA-RISC 8500",
                "92" : "PA-RISC 8000",
                "93" : "PA-RISC 7300LC",
                "94" : "PA-RISC 7200",
                "95" : "PA-RISC 7100LC",
                "96" : "PA-RISC 7100",
                "A0" : "V30 Family",
                "A1" : "Quad-Core Intel(R) Xeon(R) processor 3200 Series",
                "A2" : "Dual-Core Intel(R) Xeon(R) processor 3000 Series",
                "A3" : "Quad-Core Intel(R) Xeon(R) processor 5300 Series",
                "A4" : "Dual-Core Intel(R) Xeon(R) processor 5100 Series",
                "A5" : "Dual-Core Intel(R) Xeon(R) processor 5000 Series",
                "A6" : "Dual-Core Intel(R) Xeon(R) processor LV",
                "A7" : "Dual-Core Intel(R) Xeon(R) processor ULV",
                "A8" : "Dual-Core Intel(R) Xeon(R) processor 7100 Series",
                "A9" : "Quad-Core Intel(R) Xeon(R) processor 5400 Series",
                "AA" : "Quad-Core Intel(R) Xeon(R) processor",
                "AB" : "Dual-Core Intel(R) Xeon(R) processor 5200 Series",
                "AC" : "Dual-Core Intel(R) Xeon(R) processor 7200 Series",
                "AD" : "Quad-Core Intel(R) Xeon(R) processor 7300 Series",
                "AE" : "Quad-Core Intel(R) Xeon(R) processor 7400 Series",
                "AF" : "Multi-Core Intel(R) Xeon(R) processor 7400 Series",
                "B0" : "Pentium(R) III Xeon(TM)",
                "B1" : "Pentium(R) III Processor with Intel(R) SpeedStep(TM) Technology",
                "B2" : "Pentium(R) 4",
                "B3" : "Intel(R) Xeon(TM)",
                "B4" : "AS400 Family",
                "B5" : "Intel(R) Xeon(TM) Processor MP",
                "B6" : "AMD Athlon(TM) XP Family",
                "B7" : "AMD Athlon(TM) MP Family",
                "B8" : "Intel(R) Itanium(R) 2",
                "B9" : "Intel(R) Pentium(R) M Processor",
                "BA" : "Intel(R) Celeron(R) D Processor",
                "BB" : "Intel(R) Pentium(R) D Processor",
                "BC" : "Intel(R) Pentium(R) Processor Extreme Edition",
                "BD" : "Intel(R) Core(TM) Solo Processor",
                "BE" : "K7",
                "BF" : "Intel(R) Core(TM) 2 Duo Processor",
                "C0" : "Intel(R) Core(TM) 2 Solo Processor",
                "C1" : "Intel(R) Core(TM) 2 Extreme Processor",
                "C2" : "Intel(R) Core(TM) 2 Quad Processor",
                "C3" : "Intel(R) Core(TM) 2 Extreme mobile Processor",
                "C4" : "Intel(R) Core(TM) 2 Duo mobile Processor",
                "C5" : "Intel(R) Core(TM) 2 solo mobile Processor",
                "C6" : "Intel(R) Core(TM) i7 processor",
                "C7" : "Dual-Core Intel(R) Celeron(R) Processor",
                "C8" : "S/390 and zSeries Family",
                "C9" : "ESA/390 G4",
                "CA" : "ESA/390 G5",
                "CB" : "ESA/390 G6",
                "CC" : "z/Architecture base",
                "CD" : "Intel(R) Core(TM) i5 processor",
                "CE" : "Intel(R) Core(TM) i3 processor",
                "D2" : "VIA C7(TM)-M Processor Family",
                "D3" : "VIA C7(TM)-D Processor Family",
                "D4" : "VIA C7(TM) Processor Family",
                "D5" : "VIA Eden(TM) Processor Family",
                "D6" : "Multi-Core Intel(R) Xeon(R) processor",
                "D7" : "Dual-Core Intel(R) Xeon(R) processor 3xxx Series",
                "D8" : "Quad-Core Intel(R) Xeon(R) processor 3xxx Series",
                "D9" : "VIA Nano(TM) Processor Family",
                "DA" : "Dual-Core Intel(R) Xeon(R) processor 5xxx Series",
                "DB" : "Quad-Core Intel(R) Xeon(R) processor 5xxx Series",
                "DD" : "Dual-Core Intel(R) Xeon(R) processor 7xxx Series",
                "DE" : "Quad-Core Intel(R) Xeon(R) processor 7xxx Series",
                "DF" : "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
                "E0" : "Multi-Core Intel(R) Xeon(R) processor 3400 Series",
                "E6" : "Embedded AMD Opteron(TM) Quad-Core Processor Family",
                "E7" : "AMD Phenom(TM) Triple-Core Processor Family",
                "E8" : "AMD Turion(TM) Ultra Dual-Core Mobile Processor Family",
                "E9" : "AMD Turion(TM) Dual-Core Mobile Processor Family",
                "EA" : "AMD Athlon(TM) Dual-Core Processor Family",
                "EB" : "AMD Sempron(TM) SI Processor Family",
                "EC" : "AMD Phenom(TM) II Processor Family",
                "ED" : "AMD Athlon(TM) II Processor Family",
                "EE" : "Six-Core AMD Opteron(TM) Processor Family",
                "EF" : "AMD Sempron(TM) M Processor Family",
                "FA" : "i860",
                "FB" : "i960",
                "FE" : "Reserved (SMBIOS Extension)",
                "FF" : "Reserved (Un-initialized Flash Content - Lo)",
                "104" : "SH-3",
                "105" : "SH-4",
                "118" : "ARM",
                "119" : "StrongARM",
                "12C" : "6x86",
                "12D" : "MediaGX",
                "12E" : "MII",
                "140" : "WinChip",
                "15E" : "DSP",
                "1F4" : "Video Processor",
                "FFFE" : "Reserved (For Future Special Purpose Assignment)",
                "FFFF" : "Reserved (Un-initialized Flash Content - Hi)",
                "E5" : "AMD AMD Sempron(TM) II Processor",
                "66" : "AMD Athlon(TM) X4 Quad-Core Processor Family",
                "3F" : "AMD FX(TM) Series Processor",
                "4F" : "AMD FirePro(TM) Series Processor",
                "E4" : "AMD Opteron(TM) 3000 Series Processor",
                "4E" : "AMD Opteron(TM) 3300 Series Processor",
                "4C" : "AMD Opteron(TM) 4300 Series Processor",
                "4D" : "AMD Opteron(TM) 6300 Series Processor",
                "69" : "AMD Opteron(TM) A-Series Processor",
                "67" : "AMD Opteron(TM) X1000 Series Processor",
                "68" : "AMD Opteron(TM) X2000 Series APU",
                "6A" : "AMD Opteron(TM) X3000 Series APU",
                "4B" : "AMD R-Series Processor",
                "4A" : "AMD Z-Series Processor",
                "6B" : "AMD Zen Processor Family",
                "2C" : "Intel(R) Core(TM) M processor",
                "2D" : "Intel(R) Core(TM) m3 processor",
                "2E" : "Intel(R) Core(TM) m5 processor",
                "2F" : "Intel(R) Core(TM) m7 processor"
            }
        },
        "HyperThreadingCapable" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },            
        "VirtualizationTechnologyCapable": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },
        "TurboModeCapable": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },
        "HyperThreadingEnabled": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },
        "TurboModeEnabled": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },
        "VirtualizationTechnologyEnabled": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },
        "ExecuteDisabledEnabled": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes",
                "2" : "Not Applicable"
            }
        },
        "ExecuteDisabledCapable": {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "No", 
                "1" : "Yes" 
            }
        },
        "MaxClockSpeed" : { 'Type' : 'ClockSpeed', 'InUnits' : "MHz" },
        "CurrentClockSpeed" : { 'Type' : 'ClockSpeed', 'InUnits' : "MHz", 'OutUnits' : 'GHz' },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        }
    },
    iDRACMiscEnum.NICStatistics : {
        "LinkStatus" : { 
            'Lookup'  :  'True',
            'Values' : {
                '0' : "Unknown",
                '1' : "Up",      
                '3' : "Down"
            }
        }
    },
    iDRACCompEnum.PhysicalDisk : {
        "SizeInBytes" : { 'Rename' : 'Size', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'GB' },
        "UsedSizeInBytes" : { 'Rename' : 'UsedSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'GB' },
        "FreeSizeInBytes" : { 'Rename' : 'FreeSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'GB' },
        "BlockSizeInBytes":  { 'Rename' : 'BlockSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'B' },
        "RemainingRatedWriteEndurance":  {
            'Lookup' : 'True',
            'Values' : {
                '255' : "Not Available"
            }
        },
        "MediaType" : {
            'Lookup'  :  'True',
            'Values' : {
                '0' : "HDD",
                '1' : "SSD"
            }
        },
        "BusProtocol" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "SCSI",
                "2" : "PATA",
                "3" : "FIBRE",
                "4" : "USB",
                "5" : "SATA",
                "6" : "SAS",
                "7" : "PCIe",
                "8" : "NVME"
            }
        },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        },
        "RaidStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Ready",
                "2" : "Online",
                "3" : "Foreign",
                "4" : "Offline",
                "5" : "Blocked",
                "6" : "Failed",
                "7" : "Degraded",
                "8" : "Non-RAID",
                "9" : "Missing"
            }
        },
        "PredictiveFailureState" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Healthy",
                "1" : "Warning"
            }
        },
        "FailurePredicted": {
            'Rename' : 'PredictiveFailureState',
            'Lookup'  :  'True',
            'Values' : {
                "YES" : "Warning",
                "NO" : "Healthy"
            }
        },
        "MaxCapableSpeed" : {
            'Lookup': 'True',
            'Values': {
                "0":"Unknown", "1": "1.5 Gbps", "2": "3 Gbps", "3": "6 Gbps","4": "12 Gbps"
            }
        },
        "T10PICapability": {
            'Lookup': 'True',
            'Values': {
                "0": "T10 PI not supported", "1": "T10 PI supported"
            }
        },
    },
    iDRACCompEnum.PCIeSSDDisk : {
        "SizeInBytes" : { 'Rename' : 'Size', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'GB' },
        "UsedSizeInBytes" : { 'Rename' : 'UsedSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'GB' },
        "FreeSizeInBytes" : { 'Rename' : 'FreeSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'GB' },
        "BlockSizeInBytes":  { 'Rename' : 'BlockSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'B' },
        "RemainingRatedWriteEndurance":  {
            'Lookup' : 'True',
            'Values' : {
                '255' : "Unknown"
            }
        },
        "MediaType" : {
            'Lookup'  :  'True',
            'Values' : {
                '0' : "HDD",
                '1' : "SSD"
            }
        },
        "BusProtocol" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "SCSI",
                "2" : "PATA",
                "3" : "FIBRE",
                "4" : "USB",
                "5" : "SATA",
                "6" : "SAS",
                "7" : "PCIe",
                "8" : "NVME"
            }
        },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        },
        "RaidStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Ready",
                "2" : "Online",
                "3" : "Foreign",
                "4" : "Offline",
                "5" : "Blocked",
                "6" : "Failed",
                "7" : "Degraded",
                "8" : "Non-RAID",
                "9" : "Missing"
            }
        },
        "FailurePredicted": {
            'Rename' : 'PredictiveFailureState',
            'Lookup'  :  'True',
            'Values' : {
                "YES" : "Warning",
                "NO" : "Healthy"
            }
        },
        "DriveFormFactor" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "1.8 inch",
                "2" : "2.5 inch",
                "3" : "3.5 inch",
                "4" : "2.5 inch Add-in card"
            }
        }
    },
    iDRACCompEnum.PCIeSSDExtender : {
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        }
    },
    iDRACCompEnum.PCIeSSDBackPlane : {
        "RollupStatus" : {'Rename' : 'PrimaryStatus',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical",
                "0x8000" : "Unknown",
                "0xFFFF" : "Unknown"
            }
        }
    },
    iDRACCompEnum.System: {
        "SysMemMaxCapacitySize" : { 'Type' : 'Bytes' , 'InUnits' : 'MB', 'OutUnits' : 'TB' },
        "SysMemTotalSize" : { 'Type' : 'Bytes' , 'InUnits' : 'MB', 'OutUnits' : 'GB' },
        "CurrentRollupStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                '0'       :  'Unknown',
                '1'       :  'Healthy',
                '2'       :  'Warning',
                '3'       :  'Critical'
            }
        },
        "FanRollupStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "RollupStatus" : {
            'Rename': 'PrimaryStatus',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "PowerCapEnabledState": {
            'Lookup': 'True',
            'Values': {
                "2": "Enabled",
                "3": "Disabled"
            }
        },
        "PowerState": {
            'Lookup': 'True',
            'Values': {
                "2": "On",
                "8": "Off - Soft"
            }
        }
    },
    iDRACCompEnum.VirtualDisk : {
        "SizeInBytes" : { 'Rename' : 'Size', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'Metrics' : 'GB'},
        "BlockSizeInBytes":  { 'Rename' : 'BlockSize', 'Type' : 'Bytes' , 'InUnits' : 'B', 'Metrics' : 'B' },
        "RAIDTypes" : {
            'Lookup'  :  'True',
            'Values' : {
                '1'       :  'No RAID',
                '2'       :  'RAID 0',
                '4'       :  'RAID 1',
                '64'      :  'RAID 5',
                '128'     :  'RAID 6',
                '2048'    :  'RAID 10',
                '8192'    :  'RAID 50',
                '16384'   :  'RAID 60'
            }
        },
        "RAIDStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Ready",
                "2" : "Online",
                "3" : "Foreign",
                "4" : "Offline",
                "5" : "Blocked",
                "6" : "Failed",
                "7" : "Degraded"
            }
        },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "StripeSize" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Default",
                "1" :        "512",
                "2" :       "1024",
                "4" :       "2048",
                "8" :       "4096",
                "16" :      "8192",
                "32" :     "16384",
                "64" :     "32768",
                "128" :    "65536",
                "256" :   "131072",
                "512" :   "262144",
                "1024" :  "524288",
                "2048" : "1048576",
                "4096" : "2097152",
                "8192" : "4194304",
                "16384" :"8388608",
                "32768" : "16777216"
            }
        },
        "EnabledState" : { 'Rename' : 'State',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Other",
                "2" : "Enabled",
                "3" : "Disabled",
                "4" : "Shutting Down",
                "5" : "Not Applicable",
                "6" : "Enabled but Offline",
                "7" : "In Test",
                "8" : "Deferred",
                "9" : "Quiesce",
                "10" : "Starting"
            }
        }
    },
    iDRACCompEnum.VFlash : {
        "Capacity" : { 'Type' : 'Bytes', 'InUnits' : 'MB' },
        "AvailableSize" : { 'Type' : 'Bytes', 'InUnits' : 'MB' },
        "HealthStatus" : { 'Rename' : 'PrimaryStatus',
            'Lookup'  :  'True',
            'Values' : {
                "OK" : "Healthy",
                "Error" : "Critical",
                "Critical" : "Critical"
            }
        }
    },
    iDRACSensorEnum.ServerSensor : {
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "ElementName":  { 'Rename' : 'Location'},
        "EnabledState" : { 'Rename' : 'State',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Other",
                "2" : "Enabled",
                "3" : "Disabled",
                "4" : "Shutting Down",
                "5" : "Not Applicable",
                "6" : "Enabled but Offline",
                "7" : "In Test",
                "8" : "Deferred",
                "9" : "Quiesce",
                "10" : "Starting"
            }

        }
    },
    iDRACSensorEnum.NumericSensor : {
        "CurrentReading" :  {'UnitModify': 'UnitModifier', 
                             'UnitName' : 'BaseUnits',
                             'BaseUnits' : {
                                '6' : None, #'Amps',
                                '7' : None, #'Watts',
                                '2' : None, #'Degrees C',
                                '5' : None, #'Volts',
                                '19' : None, #'RPM',
                                '65' : None, #'Percentage'
                            }
                        },
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "ElementName":  { 'Rename' : 'Location'},
        "EnabledState" : { 'Rename' : 'State',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Other",
                "2" : "Enabled",
                "3" : "Disabled",
                "4" : "Shutting Down",
                "5" : "Not Applicable",
                "6" : "Enabled but Offline",
                "7" : "In Test",
                "8" : "Deferred",
                "9" : "Quiesce",
                "10" : "Starting"
            }
        }
    },
    iDRACSensorEnum.PSNumericSensor : {
        "CurrentReading" :  {'UnitModify': 'UnitModifier', 
                             'UnitName' : 'BaseUnits',
                             'BaseUnits' : {
                                '6' : None, #'Amps',
                                '7' : None, #'Watts',
                                '2' : None, # 'Degrees C',
                                '5' : None, # 'Volts',
                                '19' : None, # 'RPM',
                                '65' : None, #'Percentage'
                            }
                        },
        "ElementName":  { 'Rename' : 'Location'},
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }

        },
        "EnabledState" : { 'Rename' : 'State',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Other",
                "2" : "Enabled",
                "3" : "Disabled",
                "4" : "Shutting Down",
                "5" : "Not Applicable",
                "6" : "Enabled but Offline",
                "7" : "In Test",
                "8" : "Deferred",
                "9" : "Quiesce",
                "10" : "Starting"
            }

        }   
    },
    iDRACMiscEnum.iDRACEnumeration : {
        "InstanceID" : {
            'Lookup'  :  'True',
            'Values' : {
                "iDRAC.Embedded.1#GroupManager.1#Status" : 'GroupStatus',
                "iDRAC.Embedded.1#NIC.1#Duplex" : 'NICDuplex',
                "iDRAC.Embedded.1#NIC.1#Speed": 'NICSpeed',
                "iDRAC.Embedded.1#Lockdown.1#SystemLockdown" : 'SystemLockDown',
                "iDRAC.Embedded.1#NIC.1#Enable" : 'NICEnabled'
            }
        }
    },
    iDRACMiscEnum.iDRACString : {
        "InstanceID" : {
            'Lookup'  :  'True',
            'Values' : {
                "iDRAC.Embedded.1#IPv4.1#Address" : 'IPv4Address',
                "iDRAC.Embedded.1#Info.1#Product" : 'ProductInfo',
                "iDRAC.Embedded.1#CurrentNIC.1#MACAddress" : 'MACAddress',
                "iDRAC.Embedded.1#CurrentIPv6.1#Address1" : 'IPv6Address',
                "iDRAC.Embedded.1#GroupManager.1#GroupName" : 'GroupName',
                "iDRAC.Embedded.1#NIC.1#SwitchConnection" : 'SwitchConnection',
                "iDRAC.Embedded.1#NIC.1#SwitchPortConnection" : 'SwitchPortConnection'
            }
        }
    },
    iDRACCompEnum.PowerSupply : {
        "TotalOutputPower" : {'UnitScale': '0', 'UnitAppend' : 'W'},
        "Range1MaxInputPower" : {'UnitScale': '0', 'UnitAppend' : 'W'},
        "PrimaryStatus" : {
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        },
        "RedundancyStatus" : { 'Rename' : 'Redundancy',
            'Lookup'  :  'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "DMTF Reserved",
                "2" : "Fully Redundant",
                "3" : "Degraded Redundancy",
                "4" : "Redundancy Lost",
                "5" : "Overall Failure"
            }
        }
    },
    iDRACMetricsEnum.BaseMetricValue : {
        "InstanceID" : {
            'Lookup'  :  'True',
            'Values' : {
        "DCIM:System:Point:Energy:Cont" : 'EnergyConsumption',
        "DCIM:System:Point:PowerHdrm:Cont" : 'PowerConsumption',
        "DCIM:System:Point:InletTempWarnPerc:Cont" : 'InletTempWarnPerc',
        "DCIM:System:Point:InletTempCriticalPerc:Cont" : 'InletTempCriticalPerc'
            }
        }
    },
    iDRACMetricsEnum.AggregationMetric: {
        "InstanceID" : {
            'Lookup'  :  'True',
            'Values' : {
                "DCIM:SystemBoard:Min:CPUUsage:1H" : 'CPUUsageMin1H',
                "DCIM:SystemBoard:Min:CPUUsage:1D" : 'CPUUsageMin1D',                  
                "DCIM:SystemBoard:Min:CPUUsage:1W" : 'CPUUsageMin1W',                 
                "DCIM:SystemBoard:Max:CPUUsage:1H" : 'CPUUsageMax1H',                 
                "DCIM:SystemBoard:Max:CPUUsage:1D" : 'CPUUsageMax1D',                 
                "DCIM:SystemBoard:Max:CPUUsage:1W" : 'CPUUsageMax1W',                
                "DCIM:SystemBoard:Avg:CPUUsage:1H" : 'CPUUsageAvg1H',              
                "DCIM:SystemBoard:Avg:CPUUsage:1D" : 'CPUUsageAvg1D',                 
                "DCIM:SystemBoard:Avg:CPUUsage:1W" : 'CPUUsageAvg1W',
                "DCIM:SystemBoard:Min:MemoryUsage:1H" : 'MemoryUsageMin1H',               
                "DCIM:SystemBoard:Min:MemoryUsage:1D" : 'MemoryUsageMin1D',               
                "DCIM:SystemBoard:Min:MemoryUsage:1W" : 'MemoryUsageMin1W',              
                "DCIM:SystemBoard:Max:MemoryUsage:1H" : 'MemoryUsageMax1H',             
                "DCIM:SystemBoard:Max:MemoryUsage:1D" : 'MemoryUsageMax1D',               
                "DCIM:SystemBoard:Max:MemoryUsage:1W" : 'MemoryUsageMax1W',             
                "DCIM:SystemBoard:Avg:MemoryUsage:1H" : 'MemoryUsageAvg1H',               
                "DCIM:SystemBoard:Avg:MemoryUsage:1D" : 'MemoryUsageAvg1D',               
                "DCIM:SystemBoard:Avg:MemoryUsage:1W" : 'MemoryUsageAvg1W',             
                "DCIM:SystemBoard:Min:IOUsage:1H" : 'IOUsageMin1H',                   
                "DCIM:SystemBoard:Min:IOUsage:1D" : 'IOUsageMin1D',
                "DCIM:SystemBoard:Min:IOUsage:1W" : 'IOUsageMin1W',                   
                "DCIM:SystemBoard:Max:IOUsage:1H" : 'IOUsageMax1H',                   
                "DCIM:SystemBoard:Max:IOUsage:1D" : 'IOUsageMax1D',                   
                "DCIM:SystemBoard:Max:IOUsage:1W" : 'IOUsageMax1W',                   
                "DCIM:SystemBoard:Avg:IOUsage:1H" : 'IOUsageAvg1H',                   
                "DCIM:SystemBoard:Avg:IOUsage:1D" : 'IOUsageAvg1D',                  
                "DCIM:SystemBoard:Avg:IOUsage:1W" : 'IOUsageAvg1W',                   
                "DCIM:SystemBoard:Min:SYSUsage:1H" : 'SYSUsageMin1H',                  
                "DCIM:SystemBoard:Min:SYSUsage:1D" : 'SYSUsageMin1D',                  
                "DCIM:SystemBoard:Min:SYSUsage:1W" : 'SYSUsageMin1W',                  
                "DCIM:SystemBoard:Max:SYSUsage:1H" : 'SYSUsageMax1H',                  
                "DCIM:SystemBoard:Max:SYSUsage:1D" : 'SYSUsageMax1D',                  
                "DCIM:SystemBoard:Max:SYSUsage:1W" : 'SYSUsageMax1W',                  
                "DCIM:SystemBoard:Avg:SYSUsage:1H" : 'SYSUsageAvg1H',                  
                "DCIM:SystemBoard:Avg:SYSUsage:1D" : 'SYSUsageAvg1D',                 
                "DCIM:SystemBoard:Avg:SYSUsage:1W" : 'SYSUsageAvg1W',                  
                "DCIM:System:Max:Current:Cont" : 'PeakAmperage',
                "DCIM:System:Max:Power:Cont" : 'PeakPower',
                "DCIM:System:Max:PowerHdrm:Cont" : 'PeakHeadroom',
                "DCIM:SystemBoard:Peak:CPUUsage" : 'SYSPeakCPUUsage',
                "DCIM:SystemBoard:Peak:IOUsage" : 'SYSPeakIOUsage',
                "DCIM:SystemBoard:Peak:MemoryUsage" : 'SYSPeakMemoryUsage',
                "DCIM:SystemBoard:Peak:SYSUsage" : 'SYSPeakSYSUsage'
            }
        }
    },
    iDRACCompEnum.License : {
        "LicenseInstallDate" : {'DateTime' : None},
        "LicenseSoldDate" : {'DateTime' : None},
        "LicensePrimaryStatus": {
            'Rename' : 'PrimaryStatus',
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "Healthy",
                "2": "Warning",
                "3": "Critical"
            }
        },
        "LicenseType": {
            'Lookup': 'True',
            'Values': {
                "1": "Perpetual",
                "2": "Leased",
                "3": "Evaluation",
                "4": "Site"
            }
        }
    },
    iDRACCompEnum.EnclosureFanSensor: {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "Healthy",
                "2": "Warning",
                "3": "Critical"
            }
        }
    },
    iDRACCompEnum.EnclosureTempSensor: {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "Healthy",
                "2": "Warning",
                "3": "Critical"
            }
        }
    },
    iDRACCompEnum.HostNIC: {
        "Status": {
            'Rename': 'PrimaryStatus',
            'Lookup': 'True',
            'Values': {
                "0": "Healthy",
                "1": "Critical",
                "2": "Warning",
                "3": "Warning",
                "4": "Warning",
                "5": "Warning",
                "6": "Critical"
            }
        }
    },
    iDRACCompEnum.PresenceAndStatusSensor: {
        "CurrentState":{
            'Rename': 'PrimaryStatus',
            'Lookup': 'True',
            'Values': {
                "OK": "Healthy",
                "Critical": "Critical"
            }
        }
    },
    iDRACMiscEnum.NICCapabilities: {
        "FCoEBootSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "PXEBootSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "iSCSIBootSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "WOLSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "FlexAddressingSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "VFSRIOVSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "iSCSIOffloadSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "FCoEOffloadSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "NicPartitioningSupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "TCPChimneySupport": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        },
        "DCBExchangeProtocol": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Supported",
                "3": "Not Supported"
            }
        }
    },
    iDRACCompEnum.NIC: {
        "FCoEOffloadMode": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Enabled",
                "3": "Disabled"
            }
        },
        "iScsiOffloadMode": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Enabled",
                "3": "Disabled"
            }
        },
        "AutoNegotiation": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Enabled",
                "3": "Disabled"
            }
        }
    },
    iDRACCompEnum.ControllerBattery: {
        "RAIDState": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown",
                "1" : "Ready",
                "6" : "Failed",
                "7" : "Degraded",
                "9" : "Missing",
                "10" : "Charging",
                "12" : "Below Threshold"
            }
        },
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "Healthy",
                "2": "Warning",
                "3": "Critical"
            }
        }
    },
    iDRACCompEnum.Enclosure: {
        "PrimaryStatus": {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Warning",
                "1" : "Healthy",
                "2" : "Warning",
                "3" : "Critical"
            }
        }
    }
}


iDRACClassifier = [ iDRACCompEnum.System ]

iDRACRedfishViews = {
    iDRACCompEnum.System: ["Systems","Members"],
    iDRACCompEnum.NIC : ["Systems","Members","EthernetInterfaces","Members"],
    iDRACCompEnum.CPU : ["Systems","Members","Processors","Members"],
    iDRACCompEnum.Sensors_Fan : ["Systems","Members","Links","CooledBy"],
    iDRACCompEnum.PowerSupply : ["Systems","Members","Links","PoweredBy"],
    iDRACCompEnum.Sensors_Voltage : ["Chassis","Members","Power","Voltages"],
    iDRACCompEnum.Sensors_Temperature : ["Chassis","Members","Thermal","Temperatures"],
    iDRACCompEnum.Controller : ["Systems","Members","SimpleStorage","Members"],
    iDRACCompEnum.iDRAC : ["Managers", "Members"],
    iDRACMiscEnum.ChassisRF : ["Chassis","Members"],
    iDRACMiscEnum.DellAttributes : ["Managers", "Members", "Links", "Oem", "Dell", "DellAttributes"]
}

iDRACRedfishViews_FieldSpec = {
    iDRACCompEnum.System : {
        "MemorySummary" : {'Create' : {
                                        'SysMemTotalSize' : {'_Attribute' : 'TotalSystemMemoryGiB'},
                                        'SysMemPrimaryStatus' :{ '_Attribute' : {'Status':'Health'}}
                                      }
                          },
        "ProcessorSummary" : {'Create' : {
                                            'CPURollupStatus' : {'_Attribute' : {'Status':'Health'}}
                                         }
                             },
        "Status" : {'Create' : { 'PrimaryStatus' : {'_Attribute' : 'Health'}}},
        "SKU" : { 'Rename' : 'ServiceTag'},
        "BiosVersion" : { 'Rename' : 'BIOSVersionString'},
        "PartNumber" : { 'Rename' : 'BoardPartNumber'},
        "SerialNumber" : { 'Rename' : 'BoardSerialNumber'}
    },
    iDRACCompEnum.NIC : {
        "Id" : { 'Rename' : 'FQDD'},
        "SpeedMbps" : {'Rename' : 'LinkSpeed', 'UnitScale': '0', 'UnitAppend' : 'Mbps'},
        # "Name" : {'Rename' : 'ProductName'},
        "AutoNeg" : {'Rename' : 'AutoNegotiation',
                     'Lookup': 'True',
                     'Values': {
                        False : "Unknown",
                        True : "Enabled"
                        }
                     },
        "MACAddress" : {'Rename' : 'CurrentMACAddress'},
        "Status" : {'Create' : {
                                'NICStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping' : { 'OK' : 'Healthy',
                                                                  'Critical' : 'Critical',
                                                                  'Warning' : 'Warning'
                                                        }
                                                   },
                                'LinkStatus' : {'_Attribute' : 'State',
                                                '_Mapping' : {'Enabled' : 'Up',
                                                              'Disabled' : 'Down',
                                                              'StandbyOffline': 'Down',
                                                              'StandbySpare' : 'Down',
                                                              'InTest' : 'Down',
                                                              'Starting' : 'Down',
                                                              'Absent' : 'Down',
                                                              'UnavailableOffline' : 'Down',
                                                              'Deferring' : 'Down',
                                                              'Quiesced' : 'Down',
                                                              'Updating' : 'Down'}
                                               }
                               }
                   },
        "Description" : {'Rename' : 'DeviceDescription'},
        "FullDuplex": {'Rename': 'LinkDuplex',
                       'Lookup': 'True',
                       'Values': {
                            False: 'Unknown',
                            True: 'Full Duplex'
                            }
                        }
    },
    iDRACCompEnum.CPU : {
        "Id" : { 'Rename' : 'FQDD'},
        "ProcessorId" : {'Create' : {
                                     'VendorId' : {'_Attribute' : 'VendorID'},
                                     'CPUFamily': {'_Attribute' : 'EffectiveFamily'}
                                    }
                         },
        "Status" : {'Create' : {'PrimaryStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping': {'OK': 'Healthy',
                                                       'Critical': 'Critical',
                                                       'Warning': 'Warning'
                                                       }
                                                   },
                                }
                    },
        "TotalCores" : { 'Rename' : 'NumberOfProcessorCores'},
        "TotalThreads" : { 'Rename' : 'NumberOfEnabledThreads'},
        "MaxSpeedMHz" : {'Rename' : 'MaxClockSpeed',
                         'Type': 'ClockSpeed', 'InUnits': "MHz", 'OutUnits': 'GHz'},
        "Name" : {'Rename' : 'DeviceDescription'},
        # https://www.dmtf.org/sites/default/files/standards/documents/DSP0134_3.2.0.pdf 
        "CPUFamily": {
            'Lookup': 'True',
            'Values': {
                "1": "Other",
                "2": "Unknown",
                "3": "8086",
                "4": "80286",
                "5": "Intel386 processor",
                "6": "Intel486 processor",
                "7": "8087",
                "8": "80287",
                "9": "80387",
                "10": "80487",
                "11": "Intel Pentium processor",
                "12": "Pentium Pro processor",
                "13": "Pentium II processor",
                "14": "Pentium processor with MMX technology",
                "15": "Intel Celeron processor",
                "16": "Pentium II Xeon processor",
                "17": "Pentium III processor",
                "18": "M1 Family",
                "19": "M2 Family",
                "20": "Intel Celeron M processor",
                "21": "Intel Pentium 4 HT processor",
                "24": "AMD Duron Processor Family [1]",
                "25": "K5 Family [1]",
                "26": "K6 Family [1]",
                "27": "K6-2 [1]",
                "28": "K6-3 [1]",
                "29": "AMD Athlon Processor Family [1]",
                "30": "AMD29000 Family",
                "31": "K6-2+",
                "32": "Power PC Family",
                "33": "Power PC 601",
                "34": "Power PC 603",
                "35": "Power PC 603+",
                "36": "Power PC 604",
                "37": "Power PC 620",
                "38": "Power PC x704",
                "39": "Power PC 750",
                "40": "Intel Core Duo processor",
                "41": "Intel Core Duo mobile processor",
                "42": "Intel Core Solo mobile processor",
                "43": "Intel Atom processor",
                "44": "Intel Core M processor",
                "45": "Intel(R) Core(TM) m3 processor",
                "46": "Intel(R) Core(TM) m5 processor",
                "47": "Intel(R) Core(TM) m7 processor",
                "48": "Alpha Family [2]",
                "49": "Alpha 21064",
                "50": "Alpha 21066",
                "51": "Alpha 21164",
                "52": "Alpha 21164PC",
                "53": "Alpha 21164a",
                "54": "Alpha 21264",
                "55": "Alpha 21364",
                "56": "AMD Turion II Ultra Dual-Core Mobile M Processor Family",
                "57": "AMD Turion II Dual-Core Mobile M Processor Family",
                "58": "AMD Athlon II Dual-Core M Processor Family",
                "59": "AMD Opteron 6100 Series Processor",
                "60": "AMD Opteron 4100 Series Processor",
                "61": "AMD Opteron 6200 Series Processor",
                "62": "AMD Opteron 4200 Series Processor",
                "63": "AMD FX Series Processor",
                "64": "MIPS Family",
                "65": "MIPS R4000",
                "66": "MIPS R4200",
                "67": "MIPS R4400",
                "68": "MIPS R4600",
                "69": "MIPS R10000",
                "70": "AMD C-Series Processor",
                "71": "AMD E-Series Processor",
                "72": "AMD A-Series Processor",
                "73": "AMD G-Series Processor",
                "74": "AMD Z-Series Processor",
                "75": "AMD R-Series Processor",
                "76": "AMD Opteron 4300 Series Processor",
                "77": "AMD Opteron 6300 Series Processor",
                "78": "AMD Opteron 3300 Series Processor",
                "79": "AMD FirePro Series Processor",
                "80": "SPARC Family",
                "81": "SuperSPARC",
                "82": "microSPARC II",
                "83": "microSPARC IIep",
                "84": "UltraSPARC",
                "85": "UltraSPARC II",
                "86": "UltraSPARC Iii",
                "87": "UltraSPARC III",
                "88": "UltraSPARC IIIi",
                "96": "68040 Family",
                "97": "68xxx",
                "98": "68000",
                "99": "68010",
                "100": "68020",
                "101": "68030",
                "102": "AMD Athlon(TM) X4 Quad-Core Processor Family",
                "103": "AMD Opteron(TM) X1000 Series Processor",
                "104": "AMD Opteron(TM) X2000 Series APU",
                "105": "AMD Opteron(TM) A-Series Processor",
                "106": "AMD Opteron(TM) X3000 Series APU",
                "107": "AMD Zen Processor Family",
                "112": "Hobbit Family",
                "120": "Crusoe TM5000 Family",
                "121": "Crusoe TM3000 Family",
                "122": "Efficeon TM8000 Family",
                "128": "Weitek",
                "129": "Available for assignment",
                "130": "Itanium processor",
                "131": "AMD Athlon 64 Processor Family",
                "132": "AMD Opteron Processor Family",
                "133": "AMD Sempron Processor Family",
                "134": "AMD Turion 64 Mobile Technology",
                "135": "Dual-Core AMD Opteron Processor F",
                "136": "AMD Athlon 64 X2 Dual-Core Processor Family",
                "137": "AMD Turion 64 X2 Mobile Technology",
                "138": "Quad-Core AMD Opteron Processor Family",
                "139": "Third-Generation AMD Opteron Processor Family",
                "140": "AMD Phenom FX Quad-Core Processor Family",
                "141": "AMD Phenom X4 Quad-Core Processor Family",
                "142": "AMD Phenom X2 Dual-Core Processor Family",
                "143": "AMD Athlon X2 Dual-Core Processor Family",
                "144": "PA-RISC Family",
                "145": "PA-RISC 8500",
                "146": "PA-RISC 8000",
                "147": "PA-RISC 7300LC",
                "148": "PA-RISC 7200",
                "149": "PA-RISC 7100LC",
                "150": "PA-RISC 7100",
                "160": "V30 Family",
                "161": "Quad-Core Intel Xeon processor 3200 Series",
                "162": "Dual-Core Intel Xeon processor 3000 Series",
                "163": "Quad-Core Intel Xeon processor 5300 Series",
                "164": "Dual-Core Intel Xeon processor 5100 Series",
                "165": "Dual-Core Intel Xeon processor 5000 Series",
                "166": "Dual-Core Intel Xeon processor LV",
                "167": "Dual-Core Intel Xeon processor ULV",
                "168": "Dual-Core Intel Xeon processor 7100 Series",
                "169": "Quad-Core Intel Xeon processor 5400 Series",
                "170": "Quad-Core Intel Xeon processor",
                "171": "Dual-Core Intel Xeon processor 5200 Series",
                "172": "Dual-Core Intel Xeon processor 7200 Series",
                "173": "Quad-Core Intel Xeon processor 7300 Series",
                "174": "Quad-Core Intel Xeon processor 7400 Series",
                "175": "Multi-Core Intel Xeon processor 7400 Series",
                "176": "Pentium III Xeon processor",
                "177": "Pentium III Processor with Intel SpeedStep Technology",
                "178": "Pentium 4 Processor",
                "179": "Intel Xeon processor",
                "180": "AS400 Family",
                "181": "Intel Xeon processor MP",
                "182": "AMD Athlon XP Processor Family",
                "183": "AMD Athlon MP Processor Family",
                "184": "Intel Itanium 2 processor",
                "185": "Intel Pentium M processor",
                "186": "Intel Celeron D processor",
                "187": "Intel Pentium D processor",
                "188": "Intel Pentium Processor Extreme Edition",
                "189": "Intel Core Solo Processor",
                "190": "Reserved [3]",
                "191": "Intel Core 2 Duo Processor",
                "192": "Intel Core 2 Solo processor",
                "193": "Intel Core 2 Extreme processor",
                "194": "Intel Core 2 Quad processor",
                "195": "Intel Core 2 Extreme mobile processor",
                "196": "Intel Core 2 Duo mobile processor",
                "197": "Intel Core 2 Solo mobile processor",
                "198": "Intel Core i7 processor",
                "199": "Dual-Core Intel Celeron processor",
                "200": "IBM390 Family",
                "201": "G4",
                "202": "G5",
                "203": "ESA/390 G6",
                "204": "z/Architecture base",
                "205": "Intel Core i5 processor",
                "206": "Intel Core i3 processor",
                "207": "Intel Core i9 processor",
                "210": "VIA C7-M Processor Family",
                "211": "VIA C7-D Processor Family",
                "212": "VIA C7 Processor Family",
                "213": "VIA Eden Processor Family",
                "214": "Multi-Core Intel Xeon processor",
                "215": "Dual-Core Intel Xeon processor 3xxx Series",
                "216": "Quad-Core Intel Xeon processor 3xxx Series",
                "217": "VIA Nano Processor Family",
                "218": "Dual-Core Intel Xeon processor 5xxx Series",
                "219": "Quad-Core Intel Xeon processor 5xxx Series",
                "220": "Available for assignment",
                "221": "Dual-Core Intel Xeon processor 7xxx Series",
                "222": "Quad-Core Intel Xeon processor 7xxx Series",
                "223": "Multi-Core Intel Xeon processor 7xxx Series",
                "224": "Multi-Core Intel Xeon processor 3400 Series",
                "228": "AMD Opteron 3000 Series Processor",
                "229": "AMD Sempron II Processor",
                "230": "Embedded AMD Opteron Quad-Core Processor Family",
                "231": "AMD Phenom Triple-Core Processor Family",
                "232": "AMD Turion Ultra Dual-Core Mobile Processor Family",
                "233": "AMD Turion Dual-Core Mobile Processor Family",
                "234": "AMD Athlon Dual-Core Processor Family",
                "235": "AMD Sempron SI Processor Family",
                "236": "AMD Phenom II Processor Family",
                "237": "AMD Athlon II Processor Family",
                "238": "Six-Core AMD Opteron Processor Family",
                "239": "AMD Sempron M Processor Family",
                "250": "i860",
                "251": "i960",
                "254": "Indicator to obtain the processor family from the Processor Family 2 field",
                "255": "Reserved",
                "256": "ARMv7",
                "257": "ARMv8",
                "260": "SH-3",
                "261": "SH-4",
                "280": "ARM",
                "281": "StrongARM",
                "300": "6x86",
                "301": "MediaGX",
                "302": "MII",
                "320": "WinChip",
                "350": "DSP",
                "500": "Video Processor"
            }
        }
    },
    iDRACCompEnum.Sensors_Fan : {
        "MemberID": {'Rename': 'DeviceID'},
        "MemberId": {'Rename': 'DeviceID'},
        "Name" : { 'Rename' : 'Location'},
        "Status" : {'Create' : {'PrimaryStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping': {'OK': 'Healthy',
                                                       'Critical': 'Critical',
                                                       'Warning': 'Warning'
                                                       }
                                                   },
                                'State' : {'_Attribute' : 'State'}}
                   },
        "Reading" : { 'Rename' : 'CurrentReading'}
    },
    iDRACCompEnum.Sensors_Voltage : {
        "MemberID" : { 'Rename' : 'DeviceID'},
        "MemberId" : { 'Rename' : 'DeviceID'},
        "Name" : { 'Rename' : 'Location'},
        "Status" : {'Create' : {'PrimaryStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping': {'OK': 'Healthy',
                                                       'Critical': 'Critical',
                                                       'Warning': 'Warning'
                                                       }
                                                   },
                                'State' : {'_Attribute' : 'State'}}
                    },
        "ReadingVolts" : { 'Rename' : 'Reading(V)'}
    },
    iDRACCompEnum.Sensors_Temperature : {
        "MemberID" : { 'Rename' : 'DeviceID'},
        "MemberId" : { 'Rename' : 'DeviceID'},
        "Name" : { 'Rename' : 'Location'},
        "Status" : {'Create' : {'PrimaryStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping': {'OK': 'Healthy',
                                                       'Critical': 'Critical',
                                                       'Warning': 'Warning'
                                                       }
                                                   },
                                'State' : {'_Attribute' : 'State'}}
                    },
        "ReadingCelsius" : { 'Rename' : 'CurrentReading(Degree Celsius)'}
    },
    iDRACCompEnum.PowerSupply : {
        "MemberID" : { 'Rename' : 'FQDD'},
        "LastPowerOutputWatts" : {'Rename' : 'TotalOutputPower'},
        "LineInputVoltage" : { 'Rename' : 'InputVoltage'},
        "Status" : {'Create' : {'PrimaryStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping': {'OK': 'Healthy',
                                                       'Critical': 'Critical',
                                                       'Warning': 'Warning'
                                                       }
                                                   },
                                }
                    },
        "Redundancy" : { 'Rename' : 'RedfishRedundancy'},#This is to not show redundancy
        "PowerSupplyType": {'Rename': 'Type'}
    },
    iDRACCompEnum.Controller : {
        "Id" : { 'Rename' : 'FQDD'},
        "Name" : {'Rename' : 'ProductName'},
        "Status" : {'Create' : {'PrimaryStatus' : {'_Attribute' : 'Health',
                                                   '_Mapping': {'OK': 'Healthy',
                                                       'Critical': 'Critical',
                                                       'Warning': 'Warning'
                                                       }
                                                   },
                                'RollupStatus': {'_Attribute': 'HealthRollup',
                                                '_Mapping': {'OK': 'Healthy',
                                                             'Critical': 'Critical',
                                                             'Warning': 'Warning'
                                                             }
                                                },
                              }
                   }
    },
    iDRACMiscEnum.DellAttributes : {
        "Attributes" : {'Create' : {'GroupName' : {'_Attribute' : 'GroupManager.1.GroupName'},
                                    'GroupStatus' : {'_Attribute' : 'GroupManager.1.Status'},
                                    'OSName' : {'_Attribute' : 'ServerOS.1.OSName'},
                                    'OSVersion' : {'_Attribute' : 'ServerOS.1.OSVersion'},
                                    'SystemLockDown' : {'_Attribute' : 'Lockdown.1.SystemLockdown'},
                                    'LifecycleControllerVersion' : {'_Attribute' : 'Info.1.Version'},
                                    'IPv4Address' : {'_Attribute' : 'CurrentIPv4.1.Address'},
                                    'ProductInfo' : {'_Attribute' : 'Info.1.Product'},
                                    'MACAddress' : {'_Attribute' : 'CurrentNIC.1.MACAddress'},
                                    'NICDuplex' : {'_Attribute' : 'NIC.1.Duplex'},
                                    'NICSpeed' : {'_Attribute' : 'NIC.1.Speed'},
                                    'DNSDomainName' : {'_Attribute' : 'NIC.1.DNSDomainName'},
                                    'DNSRacName' : {'_Attribute' : 'NIC.1.DNSRacName'},
                                    'IPv6Address' : {'_Attribute' : 'IPv6.1.Address1'},
                                    'PermanentMACAddress': {'_Attribute' : 'NIC.1.MACAddress'},
                                    'VirtualAddressManagementApplication' : {'_Attribute' : 'LCAttributes.1.VirtualAddressManagementApplication'},
                                    'ChassisServiceTag' : {'_Attribute' : 'ChassisInfo.1.ChassisServiceTag'}}
                        }
    },
    iDRACMiscEnum.ChassisRF : {
        "Location" : {'Create' : {'ChassisLocation' : {'_Attribute' : 'Info'}}},
        'SKU' : {'Rename' : 'ChassisServiceTag'},
        'Model' : {'Rename' : 'ChassisModel'},
        'Name' : {'Rename' : 'ChassisName'},
        'PhysicalSecurity' : {'Create' : {'IntrusionRollupStatus' : {'_Attribute' :'IntrusionSensor'}}}
    }
    # iDRACCompEnum.iDRAC : {
    #     "Links" : {'Create' : {'DellHealth' : {'Oem':{'Dell' : '@odata.type'}}}
    #               }
    # }
}

def chk_classifier(myListoFDict, cls=None):
    valid = False
    flist = []
    for sys in myListoFDict:
        id = sys.get('Id', 'None')
        if 'System.Embedded' in id:
            flist.append(sys)
    if flist:
        valid = True
    return (valid, flist)

classify_cond = {
    iDRACCompEnum.System :
    {
        ProtocolEnum.REDFISH : chk_classifier
    }
}

if PySnmpPresent:
    iDRACSNMPViews = {
        iDRACCompEnum.System : {
            'SysObjectID' : ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
            "ServiceTag" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.1.3.1'),
            "NodeID" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.1.3.18'),
            "Model" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.1.3.12'),
            "SystemGeneration" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.1.1.7'),
            "ChassisServiceTag" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.1.2.1'),
            "PrimaryStatus" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.2.1'),
            'ChassisModel' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.6"), 
            'StateSettings' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.3"), 
            'Manufacturer' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.8"), 
            'ChassisName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.7"), 
            'parentIndexReference' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.5"), 
            'StateCapabilities' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.2"), 
            'Status' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.4"), 
            'HostName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.15"), 
            "OSVersion" :  ObjectIdentity('1.3.6.1.4.1.674.10892.5.1.3.14'),
            'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.11"), 
            'SystemRevisionName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.48"), 
            'SystemRevisionNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.47"), 
            'ExpressServiceCodeName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.49"), 
            'AssetTag' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.10.1.10"), 
            'SysMemPrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.27"), 
            "CPURollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.50"),
            "FanRollupStatus" : ObjectIdentity(".1.3.6.1.4.1.674.10892.5.4.200.10.1.21"),
            "PSRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.9"),
            "StorageRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.2.3"),
            "VoltRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.12"),
            "TempRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.24"),
            "CurrentRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.15"),
            "BatteryRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.52"),
            "SDCardRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.56"),
            "IDSDMRollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.58"),
            "ChassisIntrusion" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.30"),
            "ChassisStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.4"),
            "CoolingUnit" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.44"),
            "PowerUnit" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.200.10.1.42"),
            "LifecycleControllerVersion" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.1.1.8"),
            "OSName" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.1.3.6"),
            "iDRACURL" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.1.1.6"),
            # "RollupStatus" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.2.1"),
            "DeviceType" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.1.1.2"),
			"SysName" : ObjectIdentity("1.3.6.1.2.1.1.5")
        },
        iDRACCompEnum.CPU : {
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.2"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.5"), 
            'Type' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.7"), 
            'Manufacturer' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.8"), 
            'CPUFamily' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.10"), 
            'MaxClockSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.11"), 
            'CurrentClockSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.12"), 
            'ExternalClockSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.13"), 
            'Voltage' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.14"), 
            'Version' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.16"), 
            "NumberOfProcessorCores" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.17"), 
            "NumberOfEnabledCores" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.18"),
            "NumberOfEnabledThreads" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.19"),
            "Characteristics" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.20"), 
            "ExtendedCapabilities" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.21"),
            "ExtendedEnabled" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.22"), 
            'Model' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.23"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.26"), 
            'processorDeviceStateSettings' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.30.1.4"),
        },
        iDRACCompEnum.Memory : {
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.26"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.5"), 
            'MemoryType' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.7"), 
            'LocationName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.8"), 
            'BankLabel' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.10"), 
            'Size' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.14"), 
            'CurrentOperatingSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.15"), 
            'Manufacturer' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.21"), 
            'PartNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.22"), 
            'SerialNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.23"), 
            'StateCapabilities' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.3"), 
            'memoryDeviceStateSettings' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.4"),
            # 'Rank' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.50.1.2"),
            # The OID above corresponds to Index and Rank not in iDRAC MIB
        },
        iDRACCompEnum.NIC : {
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.2"), 
            'NICStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.3"),
            'LinkStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.4"), 
            'ProductName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.6"), 
            'Vendor' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.7"), 
            'CurrentMACAddress' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.15"), 
            'PermanentMACAddress' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.16"), 
            'PCIBusNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.17"), 
            'PCIDeviceNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.18"), 
            'PCIFunctionNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.19"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.30"), 

            "TOECapabilityFlags" :  ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.23"), 
            "iSCSICapabilityFlags" :  ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.27"), 
            "iSCSIEnabled" : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.90.1.28"), 
        },
        iDRACCompEnum.PCIDevice : {
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.80.1.2"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.80.1.5"), 
            'DataBusWidth' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.80.1.7"), 
            'Manufacturer' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.80.1.8"), 
            'Description' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.80.1.9"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.1100.80.1.12"), 
        },
        iDRACCompEnum.Sensors_Fan : {
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.2"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.5"), 
            'coolingUnitIndexReference' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.15"), 
            'CurrentReading' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.6"), 
            'Type' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.7"),
            'State' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.4"),
            'Location' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.8"), 
            'SubType' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.16"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.700.12.1.19"), 
        },
        iDRACCompEnum.PowerSupply : {
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.2"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.5"), 
            "TotalOutputPower" :  ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.6"), 
            'Type' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.7"), 
            'Location' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.8"), 
            'InputVoltage' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.9"), 
            'Range1MaxInputPower' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.14"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.15"), 
            'IndexReference' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.10"), 
            'powerSupplyStateCapabilitiesUnique' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.3"),
            'PowerSupplySensorState' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.600.12.1.11"),
        },
        iDRACCompEnum.Enclosure : {
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.1"), 
            'ProductName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.2"), 
            'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.8"), 
            'AssetTag' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.9"), 
            'State' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.4"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.24"), 
            'Version' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.26"), 
            'SASAddress' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.30"), 
            'DriveCount' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.31"), 
            'TotalSlots' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.32"), 
            'FanCount' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.40"), 
            'PSUCount' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.41"), 
            'EMMCount' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.42"), 
            'TempProbeCount' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.43"), 
            'Position' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.45"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.47"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.48"), 
            'RollUpStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.3.1.23"), 
        },
        iDRACCompEnum.EnclosureEMM : {
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.15"), 
            'Name' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.2"), 
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.1"), 
            'State' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.4"), 
            'PartNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.6"), 
            'FWVersion' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.8"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.16"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.13.1.11"), 
        },
        "EnclosureFan" : {
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.1"), 
            'Name' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.2"), 
            'State' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.4"), 
            'CurrentSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.11"), 
            'PartNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.7"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.15"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.20"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.7.1.21"), 
        },
        iDRACCompEnum.EnclosurePSU : {
            'Name' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.2"), 
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.1"), 
            'State' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.4"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.15"), 
            'PartNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.7"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.9"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.9.1.16"), 
        },
        iDRACCompEnum.ControllerBattery : {
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.15.1.1"), 
            'State' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.15.1.4"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.15.1.6"), 
            'PredictedCapacity' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.15.1.10"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.15.1.20"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.15.1.21"), 
        },
        iDRACCompEnum.Controller : {
            'ProductName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.2"), 
            'ControllerFirmwareVersion' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.8"), 
            'CacheSize' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.9"), 
            'RollupStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.37"),
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.38"), 
            'DriverVersion' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.41"), 
            'PCISlot' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.42"), 
            'HotspareStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.59"), 
            'CopyBackMode' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.71"), 
            'SecurityStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.72"), 
            'EncryptionCapability' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.74"), 
            'LoadBalancingMode' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.75"), 
            'MaxSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.76"), 
            'SASAddress' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.77"), 
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.1"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.78"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.79"),
            'T10PICapability': ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.80"),
            'SupportRAID10UnevenSpans': ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.81"),
            'SupportEnhancedAutoForeignImport': ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.82"),
            'SupportControllerBootMode': ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.1.1.83"),
        },
        iDRACCompEnum.VirtualDisk : {
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.1"), 
            'Name' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.2"), 
            'RAIDStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.4"),
            'Size' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.6"), 
            'WriteCachePolicy' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.10"), 
            'ReadCachePolicy' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.11"), 
            'RAIDTypes' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.13"),
            'StripeSize' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.14"), 
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.20"), 
            'Secured' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.24"), 
            'IsCacheCade' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.25"), 
            'DiskCachePolicy' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.26"), 
            'MediaType' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.33"), 
            'RemainingRedundancy' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.34"), 
            'OperationalState' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.30"), 
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.35"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.140.1.1.36"), 
        },
        iDRACCompEnum.PhysicalDisk : {
            'Number' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.1"), 
            'Name' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.2"), 
            'RaidStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.4"),
            'Model' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.6"), 
            'SerialNumber' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.7"), 
            'Revision' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.8"), 
            'Size' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.11"), 
            'UsedSize' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.17"),
            'FreeSize' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.19"),
            'BusProtocol' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.21"),
            'HotSpareStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.22"),
            'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.24"), 
            'PPID' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.27"), 
            'SASAddress' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.28"), 
            'RAIDNegotiatedSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.29"),
            'PredictiveFailureState' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.31"),
            'MaxCapableSpeed' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.30"),
            'MediaType' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.35"), 
            'PowerState' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.42"), 
            'DriveFormFactor' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.53"), 
            'Manufacturer' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.3"), 
            'ManufacturingDay' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.32"), 
            'ManufacturingWeek' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.33"), 
            'ManufacturingYear' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.34"), 
            'OperationalState' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.50"), 
            'SecurityState' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.52"),
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.54"), 
            'DeviceDescription' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.55"),
            'T10PICapability': ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.57"),
            'BlockSize': ObjectIdentity("1.3.6.1.4.1.674.10892.5.5.1.20.130.4.1.58"),
        },
        "FRU" : {
            'FQDD' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.12"), 
            'ChassisIndex' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.1"), 
            'SerialNumberName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.7"), 
            'RevisionName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.9"), 
            'InformationStatus' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.3"), 
            'ManufacturerName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.6"), 
            'PartNumberName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.8"), 
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.2000.10.1.2"), 
        },
      #  "systemBattery" : {
        #    "ChassisIndex" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBatteryChassisIndex'),
        #    "Index" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBatteryIndex'),
        #    "Status" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBatteryStatus'),
        #    "Reading" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBatteryReading'),
        #    "LocationName" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBatteryLocationName'),
      #  },
        "firmware" : {
            'Status' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.5"), 
            'VersionName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.11"), 
            'StateSettings' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.4"), 
            'Type' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.7"), 
            'Size' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.6"), 
            'chassisIndex' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.1"), 
            'TypeName' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.8"), 
            'StateCapabilities' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.3"), 
            'Index' : ObjectIdentity("1.3.6.1.4.1.674.10892.5.4.300.60.1.2"), 
        },
        "SystemBIOS" : {
            "chassisIndex" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBIOSchassisIndex'),
            "Index" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBIOSIndex'),
        #    "Status" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBIOSStatus'),
        #    "ReleaseDateName" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBIOSReleaseDateName'),
            "VersionName" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBIOSVersionName'),
            "ManufacturerName" : ObjectIdentity('IDRAC-MIB-SMIv2', 'systemBIOSManufacturerName'),
        },
        iDRACCompEnum.Sensors_Amperage : {
            "Location" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.30.1.8'),
            "PrimaryStatus" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.30.1.5'),
            "State" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.30.1.4'),
            "ProbeReading" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.30.1.6'),
            "ProbeType" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.30.1.7'),
            "CurrentReading" : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.30.1.16'),
        },
        iDRACCompEnum.Sensors_Battery : {
            "State"           : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.50.1.4'),
            "PrimaryStatus"   : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.50.1.5'),
            "CurrentReading"         : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.50.1.6'),
            "Location"        : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.50.1.7'),
        },
        iDRACCompEnum.Sensors_Intrusion : {
            "State"           : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.300.70.1.4'),
            "Type"            : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.300.70.1.7'),
            "PrimaryStatus"   : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.300.70.1.5'),
            "CurrentReading"         : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.300.70.1.6'),
            "Location"        : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.300.70.1.8'),
        },
        iDRACCompEnum.Sensors_Voltage: {
            "VoltageProbeIndex": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.2'),
            "State": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.4'),
            "PrimaryStatus": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.5'),
            "Reading(V)": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.6'),
            "VoltageProbeType": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.7'),
            "Location": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.8'),
            "CurrentReading": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.600.20.1.16'),
        },
        iDRACCompEnum.Sensors_Temperature : {
            "State"           : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.700.20.1.4'),
            "CurrentReading"         : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.700.20.1.16'),
            "PrimaryStatus"   : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.700.20.1.5'),
            "CurrentReading(Degree Celsius)"      : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.700.20.1.6'),
            "Location"        : ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.700.20.1.8'),
            "SensorType": ObjectIdentity('1.3.6.1.4.1.674.10892.5.4.700.20.1.7.1'),
        },
    }
    iDRACSNMPViews_FieldSpec = {
        iDRACCompEnum.Memory : {
            "Size" : { 'Type' : 'Bytes', 'InUnits' : "KB" },
            "CurrentOperatingSpeed" : { 'Type' : 'ClockSpeed', 'InUnits' : "MHz", 'OutUnits' : 'MHz' },
            "memoryDeviceStateSettings" : {
                'Lookup' :  'True',
                'Values' : {
                    "1"  : "Unknown",
                    "2"  : "Enabled",
                    "4"  : "Not Ready",
                    "6"  : "Enabled Not Ready"
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
        },
        iDRACCompEnum.Controller : {
            "CacheSize" : { 'Type' : 'Bytes', 'InUnits' : 'MB', 'OutUnits' : 'MB' },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "RollupStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "Unknown",
                    "3": "Healthy",
                    "4": "Warning",
                    "5": "Critical",
                    "6": "Critical"
                }
            },
            "T10PICapability": {
                'Lookup': 'True',
                'Values': {
                    "1": "Other", "2": "Capable", "3": "Not Capable"
                }
            },
            "EncryptionCapability": {
                'Lookup': 'True',
                'Values': {
                    "1": "Other",
                    "2": "None",
                    "3": "LKM"
                }
            },
            "SecurityStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "None",
                    "3": "LKM"
                }
            },
            "SupportEnhancedAutoForeignImport": {
                'Lookup': 'True',
                'Values': {
                    "1": "Other",
                    "2": "Not Supported",
                    "3": "Disabled",
                    "4": "Enabled"
                }
            },
            "SupportControllerBootMode": {
                'Lookup': 'True',
                'Values': {
                    "0": "Not Supported",
                    "1": "Supported"
                }
            },
            "SupportRAID10UnevenSpans": {
                'Lookup': 'True',
                'Values': {
                    "0": "Uneven span for RAID10 not supported",
                    "1": "Uneven span for RAID10 supported"
                }
            }
        },

        iDRACCompEnum.Enclosure: {
            "State": {
                'Lookup' : 'True',
                'Values' : {
                    "1": "Unknown",
                    "2": "Ready",
                    "3": "Failed",
                    "4": "Missing",
                    "5": "Degraded"
                }
            },
            "PrimaryStatus": {
                'Lookup' : 'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            }
        },

        iDRACCompEnum.Sensors_Fan: {
            "State" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Enabled",
                    "4" : "Not Ready",
                    "6" : "Enabled Not Ready"
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical",
                    "7" : "Warning",
                    "8" : "Critical",
                    "9" : "Critical",
                    "10" : "Critical"
                }
            },
            "Type" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "coolingDeviceTypeIsOther", 
                    "2" : "coolingDeviceTypeIsUnknown", 
                    "3" : "coolingDeviceTypeIsAFan", 
                    "4" : "coolingDeviceTypeIsABlower", 
                    "5" : "coolingDeviceTypeIsAChipFan", 
                    "6" : "coolingDeviceTypeIsACabinetFan", 
                    "7" : "coolingDeviceTypeIsAPowerSupplyFan", 
                    "8" : "coolingDeviceTypeIsAHeatPipe", 
                    "9" : "coolingDeviceTypeIsRefrigeration", 
                    "10" : "coolingDeviceTypeIsActiveCooling", 
                    "11" : "coolingDeviceTypeIsPassiveCooling"
                }
            },
            "SubType" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "coolingDeviceSubTypeIsOther",
                    "2" : "coolingDeviceSubTypeIsUnknown", 
                    "3" : "coolingDeviceSubTypeIsAFanThatReadsInRPM", 
                    "4" : "coolingDeviceSubTypeIsAFanReadsONorOFF", 
                    "5" : "coolingDeviceSubTypeIsAPowerSupplyFanThatReadsinRPM", 
                    "6" : "coolingDeviceSubTypeIsAPowerSupplyFanThatReadsONorOFF", 
                    "16" : "coolingDeviceSubTypeIsDiscrete"
                }
            },
        },
        iDRACCompEnum.CPU : {
            "processorDeviceStateSettings" : {
                'Lookup' :  'True',
                'Values' : {
                    "1"  : "Unknown",
                    "2"  : "Enabled",
                    "4"  : "Not Ready",
                    "6"  : "Enabled Not Ready"
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "CPUFamily" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1"                           :  "Other",
                    "2"                         :  "Unknown",
                    "3"                            :  "8086",
                    "4"                           :  "80286",
                    "5"                        :  "Intel386 processor",
                    "6"                        :  "Intel486 processor",
                    "7"                            :  "8087",
                    "8"                           :  "80287",
                    "9"                           :  "80387",
                    "10"                          :  "80487",
                    "11"                        :  "Pentium processor Family",
                    "12"                     :  "Pentium Pro processor",
                    "13"                      :  "Pentium II processor",
                    "14"                     :  "Pentium processor with MMX technology",
                    "15"                        :  "Celeron processor",
                    "16"                  :  "Pentium II Xeon processor",
                    "17"                     :  "Pentium III processor",
                    "18"                 :  "Pentium III Xeon processor",
                    "19"            :  "Pentium III Processor with Intel SpeedStep Technology",
                    "20"                        :  "Itanium processor",
                    "21"                      :  "Intel Xeon",
                    "22"                       :  "Pentium 4 Processor",
                    "23"                    :  "Intel Xeon processor MP",
                    "24"                  :  "Intel Itanium 2 processor",
                    "25"                             :  "K5 Family",
                    "26"                             :  "K6 Family",
                    "27"                        :  "K6-2",
                    "28"                        :  "K6-3",
                    "29"                      :  "AMD Athlon Processor Family",
                    "30"                        :  "AMD2900 Family",
                    "31"                    :  "K6-2+",
                    "32"                        :  "Power PC Family",
                    "33"                     :  "Power PC 601",
                    "34"                     :  "Power PC 603",
                    "35"                 :  "Power PC 603+",
                    "36"                     :  "Power PC 604",
                    "37"                     :  "Power PC 620",
                    "38"                    :  "Power PC x704",
                    "39"                     :  "Power PC 750",
                    "40"                   :  "Intel(R) Core(TM) Duo processor",
                    "41"             :  "Intel(R) Core(TM) Duo mobile processor",
                    "42"            :  "Intel(R) Core(TM) Solo mobile processor",
                    "43"                      :  "Intel(R) Atom(TM) processor",
                    "48"                          :  "Alpha Family",
                    "49"                     :  "Alpha 21064",
                    "50"                     :  "Alpha 21066",
                    "51"                     :  "Alpha 21164",
                    "52"                   :  "Alpha 21164PC",
                    "53"                    :  "Alpha 21164a",
                    "54"                     :  "Alpha 21264",
                    "55"                     :  "Alpha 21364",
                    "56"    :  "AMD Turion(TM) II Ultra Dual-Core Mobile M Processor Family",
                    "57"         :  "AMD Turion(TM) II Dual-Core Mobile M Processor Family",
                    "58"         :  "AMD Athlon(TM) II Dual-Core Mobile M Processor Family",
                    "59"                 :  "AMD Opteron(TM) 6100 Series Processor",
                    "60"                 :  "AMD Opteron(TM) 4100 Series Processor",
                    "61"                 :  "AMD Opteron(TM) 6200 Series Processor",
                    "62"                 :  "AMD Opteron(TM) 4200 Series Processor",
                    "64"                           :  "MIPS Family",
                    "65"                      :  "MIPS R4000",
                    "66"                      :  "MIPS R4200",
                    "67"                      :  "MIPS R4400",
                    "68"                      :  "MIPS R4600",
                    "69"                     :  "MIPS R10000",
                    "80"                          :  "SPARC Family",
                    "81"                     :  "SuperSPARC",
                    "82"                   :  "microSPARC II",
                    "83"                 :  "microSPARC IIep",
                    "84"                     :  "UltraSPARC",
                    "85"                   :  "UltraSPARC II",
                    "86"                  :  "UltraSPARC IIi",
                    "87"                  :  "UltraSPARC III",
                    "88"                 :  "UltraSPARC IIIi",
                    "96"                          :  "68040 Family",
                    "97"                          :  "68xxx",
                    "98"                          :  "68000",
                    "99"                          :  "68010",
                    "100"                         :  "68020",
                    "101"                         :  "68030",
                    "112"                        :  "Hobbit Family",
                    "120"                  :  "Crusoe TM5000 Family",
                    "121"                  :  "Crusoe TM3000 Family",
                    "122"                :  "Efficeon TM8000 Family",
                    "128"                        :  "Weitek",
                    "130"                 :  "Intel(R) Celeron(R) M processor",
                    "131"                   :  "AMD Athlon 64 Processor Family",
                    "132"                    :  "AMD Opteron Processor Family",
                    "133"                    :  "AMD Sempron Processor Family",
                    "134"             :  "AMD Turion 64 Mobile Technology",
                    "135"            :  "Dual-Core AMD Opteron(TM) Processor Family",
                    "136"         :  "AMD Athlon 64 X2 Dual-Core Processor Family",
                    "137"           :  "AMD Turion(TM) 64 X2 Mobile Technology",
                    "138"            :  "Quad-Core AMD Opteron(TM) Processor Family",
                    "139"     :  "Third-Generation AMD Opteron(TM) Processor Family",
                    "140"           :  "AMD Phenom(TM) FX Quad-Core Processor Family",
                    "141"           :  "AMD Phenom(TM) X4 Quad-Core Processor Family",
                    "142"           :  "AMD Phenom(TM) X2 Dual-Core Processor Family",
                    "143"           :  "AMD Athlon(TM) X2 Dual-Core Processor Family",
                    "144"                        :  "PA-RISC Family",
                    "145"                    :  "PA-RISC 8500",
                    "146"                    :  "PA-RISC 8000",
                    "147"                  :  "PA-RISC 7300LC",
                    "148"                    :  "PA-RISC 7200",
                    "149"                  :  "PA-RISC 7100LC",
                    "150"                    :  "PA-RISC 7100",
                    "160"                           :  "V30 Family",
                    "161"         :  "Quad-Core Intel(R) Xeon(R) processor 3200 Series",
                    "162"         :  "Dual-Core Intel(R) Xeon(R) processor 3000 Series",
                    "163"         :  "Quad-Core Intel(R) Xeon(R) processor 5300 Series",
                    "164"         :  "Dual-Core Intel(R) Xeon(R) processor 5100 Series",
                    "165"         :  "Dual-Core Intel(R) Xeon(R) processor 5000 Series",
                    "166"           :  "Dual-Core Intel(R) Xeon(R) processor LV",
                    "167"          :  "Dual-Core Intel(R) Xeon(R) processor ULV",
                    "168"         :  "Dual-Core Intel(R) Xeon(R) processor 7100 Series",
                    "169"         :  "Quad-Core Intel(R) Xeon(R) processor 5400 Series",
                    "170"             :  "Quad-Core Intel(R) Xeon(R) processor",
                    "171"         :  "Dual-Core Intel(R) Xeon(R) processor 5200 Series",
                    "172"         :  "Dual-Core Intel(R) Xeon(R) processor 7200 Series",
                    "173"         :  "Quad-Core Intel(R) Xeon(R) processor 7300 Series",
                    "174"         :  "Quad-Core Intel(R) Xeon(R) processor 7400 Series",
                    "175"        :  "Multi-Core Intel(R) Xeon(R) processor 7400 Series",
                    "176"                            :  "M1 Family",
                    "177"                            :  "M2 Family",
                    "179"               :  "Intel(R) Pentium(R) 4 HT processor",
                    "180"                         :  "AS400 Family",
                    "182"                   :  "AMD Athlon XP Processor Family",
                    "183"                   :  "AMD Athlon MP Processor Family",
                    "184"                      :  "AMD Duron Processor Family",
                    "185"                 :  "Intel Pentium M processor",
                    "186"                 :  "Intel Celeron D processor",
                    "187"                 :  "Intel Pentium D processor",
                    "188"           :  "Intel Pentium Processor Extreme Edition",
                    "189"                 :  "Intel(R) Core(TM) Solo processor",
                    "190"                    :  "Intel(R) Core(TM)2 processor",
                    "191"                 :  "Intel(R) Core(TM)2 Duo processor",
                    "192"                :  "Intel(R) Core(TM)2 Solo processor",
                    "193"             :  "Intel(R) Core(TM)2 Extreme processor",
                    "194"                :  "Intel(R) Core(TM)2 Quad processor",
                    "195"       :  "Intel(R) Core(TM)2 Extreme mobile processor",
                    "196"           :  "Intel(R) Core(TM)2 Duo mobile processor",
                    "197"          :  "Intel(R) Core(TM)2 Solo mobile processor",
                    "198"                   :  "Intel(R) Core(TM) i7 processor",
                    "199"          :  "Dual-Core Intel(R) Celeron(R) Processor",
                    "200"                        :  "IBM390 Family",
                    "201"                            :  "G4",
                    "202"                            :  "G5",
                    "203"                      :  "ESA/390 G6",
                    "204"                  :  "z/Architectur base",
                    "205"                   :  "Intel(R) Core(TM) i5 processor",
                    "206"                   :  "Intel(R) Core(TM) i3 processor",
                    "210"                        :  "VIA C7(TM)-M Processor Family",
                    "211"                        :  "VIA C7(TM)-D Processor Family",
                    "212"                         :  "VIA C7(TM) Processor Family",
                    "213"                       :  "VIA Eden(TM) Processor Family",
                    "214"            :  "Multi-Core Intel(R) Xeon(R) processor",
                    "215"         :  "Dual-Core Intel(R) Xeon(R) processor 3xxx Series",
                    "216"         :  "Quad-Core Intel(R) Xeon(R) processor 3xxx Series",
                    "217"                       :  "VIA Nano(TM) Processor Family",
                    "218"         :  "Dual-Core Intel(R) Xeon(R) processor 5xxx Series",
                    "219"         :  "Quad-Core Intel(R) Xeon(R)  processor 5xxx Series",
                    "221"         :  "Dual-Core Intel(R) Xeon(R) processor 7xxx Series",
                    "222"         :  "Quad-Core Intel(R) Xeon(R) processor 7xxx Series",
                    "223"        :  "Multi-Core Intel(R) Xeon(R) processor 7xxx Series",
                    "224"        :  "Multi-Core Intel(R) Xeon(R) processor 3400 Series ",
                    "230"    :  "Embedded AMD Opteron(TM) Quad-Core Processor Family",
                    "231"           :  "AMD Phenom(TM) Triple-Core Processor Family",
                    "232"  :  "AMD Turion(TM) Ultra Dual-Core Mobile Processor Family",
                    "233"       :  "AMD Turion(TM) Dual-Core Mobile Processor Family",
                    "234"             :  "AMD Athlon(TM) Dual-Core Processor Family",
                    "235"                  :  "AMD Sempron(TM) SI Processor Family",
                    "236"                   :  "AMD Phenom(TM) II Processor Family",
                    "237"                   :  "AMD Athlon(TM) II Processor Family",
                    "238"             :  "Six-Core AMD Opteron(TM) Processor Family",
                    "239"                   :  "AMD Sempron(TM) M Processor Family",
                    "250"                          :  "i860",
                    "251"                          :  "i960"
                }
            },
            "MaxClockSpeed": {'Type': 'ClockSpeed', 'InUnits': "MHz", 'OutUnits': "GHz"},
            "Voltage": {'UnitScale': '-3'}
        },
        iDRACCompEnum.NIC : {
            "LinkStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Up",      
                    "2" : "Down",
                    "3" : "Down", 
                    "4" : "Down", 
                    "10" : "Down",
                    "11" : "Down",
                    "12" : "Down",
                    "13" : "Down",
                }
	    },
            "NICStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
	     },
	    "CurrentMACAddress" : { 
		'Macedit' : 'True'
		},
            "PermanentMACAddress" : {
                'Macedit' : 'True'
                }
        },
        iDRACCompEnum.VirtualDisk : {
            "Size" : { 'Type' : 'Bytes', 'InUnits' : 'MB' },
            "RAIDStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    '1'       :  'Unknown',
                    '2'       :  'Online',
                    '3'       :  'Failed',
                    '4'       :  'Degraded'
                }
            },
            "RAIDTypes" : {
                'Lookup'  :  'True',
                'Values' : {
                    '1'       :  'Other',
                    '2'       :  'RAID 0',
                    '3'       :  'RAID 1',
                    '4'       :  'RAID 5',
                    '5'       :  'RAID 6',
                    '6'       :  'RAID 10',
                    '7'       :  'RAID 50',
                    '8'       :  'RAID 60',
                    '9'       :  'Concatenated RAID 1',
                    '10'      :  'Concatenated RAID 5'
                }
            },
            "ReadCachePolicy" : {
                'Lookup'  :  'True',
                'Values' : {
                    '1'       :  'No Read Ahead',
                    '2'       :  'Read Ahead',
                    '3'       :  'Adaptive Read Ahead',
                }
            },
            "DiskCachePolicy" : {
                'Lookup'  :  'True',
                'Values' : {
                    '1'       :  'Enabled',
                    '2'       :  'Disabled',
                    '3'       :  'Default',
                }
            },
            "WriteCachePolicy" : {
                'Lookup'  :  'True',
                'Values' : {
                    '1'       :  'Write Through',
                    '2'       :  'Write Back',
                    '3'       :  'Write Back Force',
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "StripeSize" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Other",
                    "2" : "default",
                    "3" : "512",
                    "4" : "1024",
                    "5" : "2048",
                    "6" : "4096",
                    "7" : "8192",
                    "8" : "16384",
                    "9" : "32768",
                    "10" : "65536",
                    "11" : "131072",
                    "12" : "262144",
                    "13" : "524288",
                    "14" : "1048576",
                    "15" : "2097152",
                    "16" : "4194304",
                    "17" : "8388608",
                    "18" : "16777216",
                }
            }
        },
        iDRACCompEnum.PhysicalDisk : {
            "Size" : { 'Type' : 'Bytes' , 'InUnits' : 'MB' },
            "UsedSize" : { 'Type' : 'Bytes' , 'InUnits' : 'MB' , 'Metrics' : 'GB'},
            "FreeSize" : { 'Type' : 'Bytes' , 'InUnits' : 'MB', 'Metrics' : 'GB' },
            "BlockSize": {'Type': 'Bytes', 'InUnits': 'B', 'OutUnits': 'B'},
            "RaidStatus" : {
                'Lookup' :  'True',
                'Values' : {
                    "1"  : "Unknown",
                    "2"  : "Ready",
                    "3"  : "Online",
                    "4"  : "Foreign",
                    "5"  : "Offline",
                    "6"  : "Blocked",
                    "7"  : "Failed",
                    "8"  : "Nonraid",
                    "9"  : "Removed",
                    "10" : "Readonly"
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical",
                    "7" : "Warning",
                    "8" : "Critical",
                    "9" : "Critical",
                    "10" : "Critical",
                }
            },
            "MediaType" : {
                'Lookup' :  'True',
                'Values' : {
                    "1" : "unknown",
                    "2" : "HDD",
                    "3" : "SSD"
                }
            },
            "ManufacturingDay": {
                'Lookup': 'True',
                'Values': {
                    "1": "Sunday",
                    "2": "Monday",
                    "3": "Tuesday",
                    "4": "Wednesday",
                    "5": "Thursday",
                    "6": "Friday",
                    "7": "Saturday"
                }
            },
            "MaxCapableSpeed": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "1.5 Gbps",
                    "3": "3.0 Gbps",
                    "4": "6.0 Gbps",
                    "5": "12.0 Gbps",
                    "6": "5 GT/s",
                    "7": "8 GT/s"
                }
            },
            "T10PICapability": {
                'Lookup': 'True',
                'Values': {
                    "1": "Other", "2": "Capable", "3": "Not Capable"
                }
            },
            "RAIDNegotiatedSpeed": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "1.5 Gbps",
                    "3": "3.0 Gbps",
                    "4": "6.0 Gbps",
                    "5": "12.0 Gbps",
                    "6": "5 GT/s",
                    "7": "8 GT/s"
                }
            },
            "SecurityState": {
                'Lookup': 'True',
                'Values': {
                    "1": "Supported",
                    "2": "Not Supported",
                    "3": "Secured",
                    "4": "Locked",
                    "5": "Foreign"
                }
            },
            "HotSpareStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Not A Spare",
                    "2": "Dedicated Hot Spare",
                    "3": "Global Hot Spare"
                }
            },
            "PredictiveFailureState": {
                'Lookup': 'True',
                'Values': {
                    "0": "Smart Alert Absent",
                    "1": "Smart Alert Present"
                }
            },
            "BusProtocol": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "SCSI",
                    "3": "SAS",
                    "4": "SATA",
                    "5": "Fibre Channel",
                    "6": "PCIe"
                }
            },
            "DriveFormFactor": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "1.8 inch",
                    "3": "2.5 inch",
                    "4": "3.5 inch"
                }
            }
        },
        iDRACCompEnum.System : {
            "SystemGeneration" : {
                'Lookup' :  'True',
                'Values' : {
                    "1"  : "other",
                    "2"  : "unknown",
                    "16" : "12G Monolithic",
                    "17" : "12G Modular",
                    "21" : "12G DCS",
                    "32" : "13G Monolithic",
                    "33" : "13G Modular",
                    "34" : "13G DCS",
                    "48" : "14G Monolithic",
                    "49" : "14G Modular",
                    "50" : "14G DCS"
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "RollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "PSRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "CPURollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "SysMemPrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "FanRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "BatteryRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "SDCardRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "ChassisIntrusion" : { 'Rename' : 'IntrusionRollupStatus', 
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "CoolingUnit" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "PowerUnit" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "ChassisStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "StorageRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "VoltRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "CurrentRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "TempRollupStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            }
        },
        iDRACCompEnum.PowerSupply : {
            'TotalOutputPower' :  {'UnitScale': '-1', 'UnitAppend' : 'W'},
            'Range1MaxInputPower' :  {'UnitScale': '-1', 'UnitAppend' : 'W'},
            "powerSupplyStateCapabilitiesUnique" : {
                'Lookup'  :  'True',
                'Values' : {
                    "0" : "No Power Supply State",
                    "1" : "unknown",
                    "2" : "onlineCapable",
                    "4" : "notReadyCapable",
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "PowerSupplySensorState" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "presenceDetected",
                    "2" : "psFailureDetected",
                    "4" : "predictiveFailure",
                    "8" : "psACLost",
                    "16" : "acLostOrOutOfRange",
                    "32" : "acOutOfRangeButPresent",
                    "64" : "configurationError"
                }
            }
        },
        iDRACCompEnum.Sensors_Battery : {
            "CurrentReading" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "predictiveFailure",
                    "2" : "failed",
                    "4" : "presenceDetected",
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "State" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Enabled",
                    "4" : "Not Ready",
                    "6" : "Enabled Not Ready"
                }
            }
        },
        iDRACCompEnum.Sensors_Intrusion: {
            "CurrentReading" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "chassisNotBreached",
                    "2" : "chassisBreached",
                    "3" : "chassisBreachedPrior",
                    "4" : "chassisBreachSensorFailure",
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical"
                }
            },
            "Type" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "chassisBreachDetectionWhenPowerON",
                    "2" : "chassisBreachDetectionWhenPowerOFF",
                }
            },
            "State" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Enabled",
                    "4" : "Not Ready",
                    "6" : "Enabled Not Ready"
                }
            }
        },
        iDRACCompEnum.Sensors_Amperage : {
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical",
                    "7" : "Warning",
                    "8" : "Critical",
                    "9" : "Critical",
                    "10" : "Critical"
                }
            },
            "ProbeType": {
                'Lookup': 'True',
                'Values': {
                    "1": "amperageProbeTypeIsOther",
                    "2": "amperageProbeTypeIsUnknown",
                    "3": "amperageProbeTypeIs1Point5Volt",
                    "4": "amperageProbeTypeIs3Point3volt",
                    "5": "amperageProbeTypeIs5Volt",
                    "6": "amperageProbeTypeIsMinus5Volt",
                    "7": "amperageProbeTypeIs12Volt",
                    "8": "amperageProbeTypeIsMinus12Volt",
                    "9": "amperageProbeTypeIsIO",
                    "10": "amperageProbeTypeIsCore",
                    "11": "amperageProbeTypeIsFLEA",
                    "12": "amperageProbeTypeIsBattery",
                    "13": "amperageProbeTypeIsTerminator",
                    "14": "amperageProbeTypeIs2Point5Volt",
                    "15": "amperageProbeTypeIsGTL",
                    "16": "amperageProbeTypeIsDiscrete",
                    "23": "amperageProbeTypeIsPowerSupplyAmps",
                    "24": "amperageProbeTypeIsPowerSupplyWatts",
                    "25": "amperageProbeTypeIsSystemAmps",
                    "26": "amperageProbeTypeIsSystemWatts"
                }
            },
            "State" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Enabled",
                    "4" : "Not Ready",
                    "6" : "Enabled Not Ready"
                }
            },
            "CurrentReading": {
                'Lookup': 'True',
                'Values': {
                    "1": "Good",
                    "2": "Bad"
                }
            }
        },
        iDRACCompEnum.Sensors_Temperature : {
            'Reading(Degree Celsius)' :  {'UnitScale': '-1', 'UnitAppend' : 'Degree Celsius'},
            'CurrentReading(Degree Celsius)': {'UnitScale': '-1'},
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical",
                    "7" : "Warning",
                    "8" : "Critical",
                    "9" : "Critical",
                    "10" : "Critical"
                }
            },
            "State" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Enabled",
                    "4" : "Not Ready",
                    "6" : "Enabled Not Ready"
                }
            },
            "SensorType": {
                'Lookup': 'True',
                'Values': {
                    "1": "Other",
                    "2": "Unknown",
                    "3": "Ambient ESM",
                    "16": "Discrete"
                }
            }
        },
        iDRACCompEnum.Sensors_Voltage : {
            'Reading(V)' :  {'UnitScale': '-3', 'UnitAppend' : 'V'},
            "CurrentReading" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "voltageIsGood",
                    "2" : "voltageIsBad",
                }
            },
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Unknown",
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical",
                    "6" : "Critical",
                    "7" : "Warning",
                    "8" : "Critical",
                    "9" : "Critical",
                    "10" : "Critical"
                }
            },
            "State" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "Enabled",
                    "4" : "Not Ready",
                    "6" : "Enabled Not Ready"
                }
            },
            "VoltageProbeType": {
                'Lookup': 'True',
                'Values': {
                    "1": "voltageProbeTypeIsOther",
                    "2": "voltageProbeTypeIsUnknown",
                    "3": "voltageProbeTypeIs1Point5Volt",
                    "4": "voltageProbeTypeIs3Point3Volt",
                    "5": "voltageProbeTypeIs5Volt",
                    "6": "voltageProbeTypeIsMinus5Volt",
                    "7": "voltageProbeTypeIs12Volt",
                    "8": "voltageProbeTypeIsMinus12Volt",
                    "9": "voltageProbeTypeIsIO",
                    "10": "voltageProbeTypeIsCore",
                    "11": "voltageProbeTypeIsFLEA",
                    "12": "voltageProbeTypeIsBattery",
                    "13": "voltageProbeTypeIsTerminator",
                    "14": "voltageProbeTypeIs2Point5Volt",
                    "15": "voltageProbeTypeIsGTL",
                    "16": "voltageProbeTypeIsDiscrete",
                    "17": "voltageProbeTypeIsGenericDiscrete",
                    "18": "voltageProbeTypeIsPSVoltage",
                    "19": "voltageProbeTypeIsMemoryStatus"
                }
            }
        },
        iDRACCompEnum.ControllerBattery: {
            "PrimaryStatus": {
                'Lookup': 'True',
                'Values': {
                    "1": "Unknown",
                    "2": "Unknown",
                    "3": "Healthy",
                    "4": "Warning",
                    "5": "Critical",
                    "6": "Critical"
                }
            }
        }
    }

    iDRACSNMPClassifier = {
        iDRACCompEnum.System : {
            'SysObjectID' : 'SNMPv2-SMI::enterprises\\.674\\.10892\\.5|IDRAC-MIB-SMIv2::outOfBandGroup'
        }
    }

# Agnostic of protocols
iDRACSubsystemHealthSpec = {
    iDRACCompEnum.System : { "Component" : iDRACCompEnum.System, "Field": 'PrimaryStatus' },
    iDRACCompEnum.Memory : { "Component" : iDRACCompEnum.System, "Field" : 'SysMemPrimaryStatus' },
    iDRACCompEnum.CPU : { "Component" : iDRACCompEnum.System, "Field": 'CPURollupStatus' },
    'Sensors_Fan' : { "Component" : iDRACCompEnum.System, "Field": 'FanRollupStatus' },
    # iDRACCompEnum.iDRAC : { "Component" : iDRACCompEnum.System, "Field": 'RollupStatus' },
    iDRACCompEnum.PowerSupply : { "Component" : iDRACCompEnum.System, "Field": 'PSRollupStatus' },
    'Storage' : { "Component" : iDRACCompEnum.System, "Field": 'StorageRollupStatus' },
    'License' : { "Component" : iDRACCompEnum.System, "Field": 'LicensingRollupStatus' },
    'Sensors_Voltage' : { "Component" : iDRACCompEnum.System, "Field": 'VoltRollupStatus' },
    'Sensors_Temperature' : { "Component" : iDRACCompEnum.System, "Field": 'TempRollupStatus' },
    'Sensors_Battery' : { "Component" : iDRACCompEnum.System, "Field": 'BatteryRollupStatus' },
    'VFlash' : { "Component" : iDRACCompEnum.System, "Field": 'SDCardRollupStatus' },
    'Sensors_Intrusion' : { "Component" : iDRACCompEnum.System, "Field": 'IntrusionRollupStatus' },
    'Sensors_Amperage' : { "Component" : iDRACCompEnum.System, "Field": 'CurrentRollupStatus' },
    'Chassis' : { "Component" : iDRACCompEnum.System, "Field": 'ChassisStatus' },
    'Cooling_Unit' : { "Component" : iDRACCompEnum.System, "Field": 'CoolingUnit' },
    'Power_Unit' : { "Component" : iDRACCompEnum.System, "Field": 'PowerUnit' },
}

iDRACUnionCompSpec = {
   "Sensors":{
        "_components": [
            "ServerSensor",
            "NumericSensor",
            "PSNumericSensor"
        ],
        "_components_enum": [
            iDRACSensorEnum.ServerSensor,
            iDRACSensorEnum.NumericSensor,
            iDRACSensorEnum.PSNumericSensor
        ],
        "_remove_duplicates" : True,
        "_pivot" : "SensorType",
        "SensorType" : {
            "1": "Battery",
            "2" : "Temperature",
            "3" : "Voltage",
            "5" : "Fan",
            "13" : "Amperage",
            "16" : "Intrusion"
        }
    }
}

iDRACDynamicValUnion = {
    "System":{
        "_complexkeys": {
            "SystemString" : ["FQDD", "AttributeName", "CurrentValue"],
            "LCString" :[None, "AttributeName", "CurrentValue" ],
            "iDRACEnumeration" :[None, "InstanceID", "CurrentValue"]
        },
        "_components_enum": [
          iDRACMiscEnum.SystemString,
          iDRACMiscEnum.LCString,
          iDRACMiscEnum.iDRACEnumeration
        ],
        "_createFlag" : False
    },
    "NIC":{
        "_complexkeys": {
            "NICString" :["FQDD", "AttributeName", "CurrentValue"],
        },
        "_components_enum": [
          iDRACMiscEnum.NICString,
        ]
    },
    "iDRAC":{
        "_complexkeys": {
            "iDRACEnumeration" :["FQDD", "InstanceID", "CurrentValue"],
            "iDRACString" :["FQDD", "InstanceID", "CurrentValue"]
        },
        "_components_enum": [
          iDRACMiscEnum.iDRACEnumeration,
          iDRACMiscEnum.iDRACString
        ]
    },
    "iDRACNIC":{
        "_complexkeys": {
            "iDRACEnumeration" :["FQDD", "InstanceID", "CurrentValue"],
            "iDRACString" :["FQDD", "InstanceID", "CurrentValue"]
        },
        "_components_enum": [
          iDRACMiscEnum.iDRACEnumeration,
          iDRACMiscEnum.iDRACString
        ],
        "_createFlag" : False
    },
    "PhysicalDisk":{
        "_complexkeys": {
            "RAIDEnumeration" :["FQDD", "AttributeName", "CurrentValue"],
        },
        "_components_enum": [
          iDRACMiscEnum.RAIDEnumeration
        ],
        "_createFlag" : False
    },
    "SystemMetrics":{
        "_complexkeys": {
            "BaseMetricValue" :[None, "InstanceID", "MetricValue" ]
        },
        "_components_enum": [
          iDRACMetricsEnum.BaseMetricValue
        ],
        "_createFlag" : True
    },
    "SystemBoardMetrics":{
        "_complexkeys": {
            "AggregationMetric" :[None, "InstanceID", "MetricValue" ]
        },
        "_components_enum": [
          iDRACMetricsEnum.AggregationMetric
        ],
        "_createFlag" : True 
    }    
}

iDRACMergeJoinCompSpec = {
   "NIC" : {
        "_components" : [
            ["NIC", "FQDD", "NICStatistics", "FQDD"],
            ["NIC", "FQDD", "NICCapabilities", "FQDD"],
            ["NIC", "FQDD", "SwitchConnection", "FQDD"],
            ["NIC", "FQDD", "HostNICView", "DeviceFQDD"]
        ],
        "_components_enum": [
            iDRACCompEnum.NIC,
            iDRACMiscEnum.NICStatistics,
            iDRACMiscEnum.NICCapabilities,
            iDRACMiscEnum.SwitchConnection,
            iDRACMiscEnum.HostNICView
        ],
        "_overwrite" : False
   },
   "FC" : {
        "_components" : [
            ["FC", "FQDD", "FCStatistics", "FQDD"]
        ],
        "_components_enum": [
            iDRACCompEnum.FC,
            iDRACMiscEnum.FCStatistics
        ],
        "_overwrite" : False
   }
}

iDRAC_more_details_spec = {
    "System":{
        "_components_enum": [
            iDRACCompEnum.System,
            iDRACMiscEnum.ChassisRF,
            iDRACMiscEnum.DellAttributes,
            iDRACCompEnum.iDRAC,
            iDRACMiscEnum.iDRACString
        ]
    },
    "iDRAC":{
        "_components_enum": [
            iDRACCompEnum.iDRAC,
            iDRACMiscEnum.DellAttributes
        ]
    }
}

class iDRAC(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(iDRAC, self).__init__(iDeviceRegistry("iDRAC", srcdir, iDRACCompEnum))
        else:
            super().__init__(iDeviceRegistry("iDRAC", srcdir, iDRACCompEnum))
        self.srcdir = srcdir
        self.protofactory.add(PWSMAN(
            selectors = {"__cimnamespace" : "root/dcim" },
            views = iDRACWsManViews,
            view_fieldspec = iDRACWsManViews_FieldSpec,
            compmap = iDRACSWCompMapping,
            cmds = iDRACWsManCmds
        ))
        self.protofactory.add(PREDFISH(
            views=iDRACRedfishViews,
            cmds=iDRACRedfishCmds,
            view_fieldspec=iDRACRedfishViews_FieldSpec,
            classifier_cond=classify_cond
        ))
        if PySnmpPresent:
            self.protofactory.add(PSNMP(
                views = iDRACSNMPViews,
                classifier = iDRACSNMPClassifier,
                view_fieldspec = iDRACSNMPViews_FieldSpec
            ))
        self.protofactory.addCTree(iDRACComponentTree)
        self.protofactory.addSubsystemSpec(iDRACSubsystemHealthSpec)
        self.protofactory.addClassifier(iDRACClassifier)
        self.prefDiscOrder = 1

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return iDRACEntity(self.ref, protofactory, ipaddr, creds, self.srcdir, 'iDRAC')

    def my_aliases(self):
        return ['Server']


class iDRACEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds, srcdir, name):
        if PY2:
            super(iDRACEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.config_dir = os.path.join(srcdir, name, "Config")
        self.ePowerStateEnum = PowerStateEnum
        self.job_mgr = iDRACJobs(self)
        self.use_redfish = False
        self.config_mgr = iDRACConfig(self)
        self.log_mgr = iDRACLogs(self)
        self.update_mgr = iDRACUpdate(self)
        self.license_mgr = iDRACLicense(self)
        self.security_mgr = iDRACSecurity(self)
        self.streaming_mgr = iDRACStreaming(self)
        self.user_mgr = iDRACCredsMgmt(self)
        self.comp_union_spec = iDRACUnionCompSpec
        self.comp_misc_join_spec = iDRACDynamicValUnion
        self.comp_merge_join_spec = iDRACMergeJoinCompSpec
        self.more_details_spec = iDRAC_more_details_spec
        self.device_type = 'Server'
        self.eemi_registry = eemiregistry

    def my_reset(self):
        if hasattr(self, 'update_mgr'):
            self.update_mgr.reset()
        #self.config_mgr.reset()
        #self.log_mgr.reset()

    def my_fix_obj_index(self, clsName, key, js):
        retval = None
        if clsName == "System":
            if 'ServiceTag' not in js or js['ServiceTag'] is None:
                js['ServiceTag'] = self.ipaddr
            retval = js['ServiceTag']
        else:
            idlist = ['Id','DeviceID', 'MemberID', 'MemberId', '@odata.id']
            retval = clsName + "_null"
            for id in idlist:
                if id in js:
                    retval = js[id]
                    return retval
        return retval

    def _isin(self, parentClsName, parent, childClsName, child):
        if TypeHelper.resolve(parentClsName) == "Controller" and \
           TypeHelper.resolve(childClsName) == "PhysicalDisk" and \
           ("Disk.Direct" not in self._get_obj_index(childClsName, child)):
           return False
        if TypeHelper.resolve(parentClsName) == "VirtualDisk" and \
           TypeHelper.resolve(childClsName) == "PhysicalDisk":
            if 'PhysicalDiskIDs' in parent:
                parentdiskListStr = parent['PhysicalDiskIDs'].strip("[]")
                if (self._get_obj_index(childClsName, child) in parentdiskListStr):
                    return True
            else:
                return False
        return self._get_obj_index(parentClsName, parent) in \
               self._get_obj_index(childClsName, child)

    def _get_MemoryType(self, idx):
        ty = self._get_field_device("Memory", "type", idx)
        return self.ref.Translate("Memory", "type", ty)

    @property
    def ServiceTag(self):
        return self._get_field_device(self.ComponentEnum.System, "ServiceTag")

    @property
    def SystemID(self):
        return self._get_field_device(self.ComponentEnum.System, "SystemID")

    @property
    def SystemIDInHex(self):
        sid = self._get_field_device(self.ComponentEnum.System, "SystemID")
        # following line is kludge for reflection api
        if sid == None or sid == '<not_found>': sid = '0'
        return (('0000' + str(hex(int(sid)))[2:])[-4:])

    @property
    def Model(self):
        return self._get_field_device(self.ComponentEnum.System, "Model")

    @property
    def ServerGeneration(self):
        return self._get_field_device(self.ComponentEnum.System, "SystemGeneration")

    @property
    def CMCIPAddress(self):
        val = self._get_field_device(self.ComponentEnum.System, "CMCIP")
        if val is None or val in ['<not_found>', "Not Available", '']:
            return None
        return val

    @property
    def IsRackStyleManaged(self):
        # return true if rack services, pounce platform
        if not "Modular" in self.get_server_generation():
            return True

        # check if psu is enumerable from idrac. if yes, it is rsm mode
        self.get_partial_entityjson(self.ComponentEnum.PowerSupply)
        psfq= self._get_field_device(self.ComponentEnum.PowerSupply, "FQDD", 0)
        if psfq is None or psfq in ['<not_found>', "Not Available", '']:
            return False
        return True

    @property
    def AssetTag(self):
        return self._get_field_device(self.ComponentEnum.System, "AssetTag")

    @property
    def IDRACURL(self):
        self.get_partial_entityjson(self.ComponentEnum.iDRAC)
        return self._get_field_device(self.ComponentEnum.iDRAC, "URLString")

    @property
    def IDRACFirmwareVersion(self):
        self.get_partial_entityjson(self.ComponentEnum.iDRAC)
        return self._get_field_device(self.ComponentEnum.iDRAC, "LifecycleControllerVersion")

    @property
    def PowerCap(self):
        return self._get_field_device(self.ComponentEnum.System, "PowerCap")

    @property
    def PowerState(self):
        pstate = self._get_field_device(self.ComponentEnum.System, "PowerState")
        return TypeHelper.convert_to_enum(int(pstate), PowerStateEnum)

    @property
    def IDRACDNSName(self):
        self.get_partial_entityjson(self.ComponentEnum.iDRAC)
        return self._get_field_device(self.ComponentEnum.iDRAC, "DnsDRACName")

    def _should_i_include(self, component, entry):
        #if component in ["PhysicalDisk"]:
        #    if entry["RollupStatus"] == 0 or entry["PrimaryStatus"] == 0: 
        #        return False
        if component == 'System':
            if self.cfactory.work_protocols[0].name == "WSMAN":
                port = 443
                if isinstance(self.pOptions, ProtocolOptionsFactory):
                    pOptions = self.pOptions.get(ProtocolEnum.REDFISH)
                    if pOptions:
                        port = pOptions.port
                elif isinstance(self.pOptions, WsManOptions):
                    port = self.pOptions.port
                if ':' in self.ipaddr:
                    entry['iDRACURL'] = "https://["+str(self.ipaddr) +"]:"+str(port)
                else:
                    entry['iDRACURL'] = "https://" + str(self.ipaddr) + ":" +str(port)
            if 'ChassisRF' in self.entityjson:
                ChaSysDict = self.entityjson['ChassisRF'][0]
                ChassisDict = None
                if len(self.entityjson['ChassisRF']) > 1:
                    for chinst in self.entityjson['ChassisRF']:
                        if 'Chassis/System.' in chinst['@odata.id']:
                            ChaSysDict = chinst
                        if 'Chassis/Chassis.' in chinst['@odata.id']:
                            ChassisDict = chinst
                chassisAttr = ['ChassisServiceTag', 'ChassisLocation', 'ChassisName', 'IntrusionRollupStatus']
                for attr in chassisAttr:
                    # if attr in ChasysDict and ChasysDict[attr]:
                    entry.update({attr: ChaSysDict.get(attr, 'Not Available')})
                chassisAttr = ['ChassisServiceTag', 'ChassisModel', 'ChassisName']
                if ChassisDict:
                    for attr in chassisAttr:
                        # if attr in ChassisDict and ChassisDict[attr]:
                        entry.update({attr : ChassisDict.get(attr, 'Not Available')})

                # del self.entityjson['ChassisRF']
                if self.cfactory.work_protocols[0].name == "REDFISH":
                    # For RedFish SysMemTotalSize's value is converted to GiB to GB
                    if isinstance(entry.get("SysMemTotalSize", 0), float):
                        entry['SysMemTotalSize'] = str(1.074 * entry.get("SysMemTotalSize", 0)) + ' GB'
                    else:
                        entry['SysMemTotalSize'] = "Not Available"
            if 'DellAttributes' in self.entityjson:
                dellAttrList = self.entityjson['DellAttributes']
                needAttr = ['ChassisServiceTag', 'OSName' ,'OSVersion','SystemLockDown','LifecycleControllerVersion','VirtualAddressManagementApplication']
                for dAttr in dellAttrList:
                    for attr in needAttr:
                        if attr in dAttr and dAttr[attr]:
                            entry.update({attr: dAttr[attr]})
        if component == 'iDRAC':
            if 'DellAttributes' in self.entityjson:
                dellAttrList = self.entityjson['DellAttributes']
                needAttr = ['GroupName','GroupStatus','SystemLockDown','IPv4Address','ProductInfo','MACAddress',
'NICDuplex', 'NICSpeed' ,'DNSDomainName','DNSRacName','IPv6Address', 'PermanentMACAddress']
                for dAttr in dellAttrList:
                    for attr in needAttr:
                        if dAttr.get(attr,None):
                            entry.update({attr: dAttr[attr]})
            if self.cfactory.work_protocols[0].name == "REDFISH":
                port = 443
                if isinstance(self.pOptions, ProtocolOptionsFactory):
                    pOptions = self.pOptions.get(ProtocolEnum.REDFISH)
                    if pOptions:
                        port = pOptions.port
                elif isinstance(self.pOptions, RedfishOptions):
                    port = self.pOptions.port
                if ':' in self.ipaddr:
                    entry['URLString'] = "https://["+str(self.ipaddr) +"]:"+str(port)
                else:
                    entry['URLString'] = "https://" + str(self.ipaddr) + ":" +str(port)
                if 'System' in self.entityjson:
                    self.entityjson["System"][0]["iDRACURL"] = entry['URLString']

        if component == 'iDRACNIC':
            if 'NICEnabled' in entry:
                h_map = {"Enabled" : "Healthy", "Disabled" : "Critical", "Unknown" : "Unknown"}
                entry['PrimaryStatus'] = h_map.get(entry.get('NICEnabled', "Unknown"),"Unknown")
        if component in ["Sensors_Battery"]:
           if "OtherSensorTypeDescription" in entry:
                if not entry["OtherSensorTypeDescription"] == 'Battery':
                    return False
        if component == "NIC":
            supportedBootProtocol = ""
            sbpDict = {"FCoEBootSupport" : "FCOE,",
                        "PXEBootSupport" : "PXE,",
                        "iSCSIBootSupport" : "iSCSI,"}  
            for bootproto in sbpDict:
                if(bootproto in entry) and (entry[bootproto] == "2"):
                    supportedBootProtocol=supportedBootProtocol+sbpDict[bootproto]
            if(supportedBootProtocol != ""):
                entry["SupportedBootProtocol"] = supportedBootProtocol.rstrip(',')
                
            nicCapabilities = ""
            ncpDict = {"WOLSupport" : "WOL,",
                        "FlexAddressingSupport" : "FlexAddressing,",
                        "VFSRIOVSupport" : "SR-IOV,",
                        "iSCSIOffloadSupport" : "iSCSI Offload,",
                        "FCoEOffloadSupport" : "FCoE Offload,",
                        "NicPartitioningSupport" : "Partitioning,",
                        "TCPChimneySupport" : "TOE,",
                        "DCBExchangeProtocol" : "DCB,"}  
            for ncp in ncpDict:
                if(ncp in entry) and (entry[ncp] == "2"):
                    nicCapabilities=nicCapabilities+ncpDict[ncp]
            if(nicCapabilities != ""):
                entry["NICCapabilities"] = nicCapabilities.rstrip(',')
            if 'PrimaryStatus' not in entry:
                entry['PrimaryStatus'] = {'Up':'Healthy','Down':'Critical', 'Unknown':'Unknown'}.get(entry.get('LinkStatus','Unknown'))
        if component == "BIOS":
            # SCOM Requirement to get 1 instance
            if not (entry["ComponentType"] == 'BIOS') or not ("INSTALLED#" in entry["InstanceID"]):
                return False
            else:
                if 'System' in self.entityjson:
                    entry['SMBIOSPresent'] = 'True'
                    entry['BIOSReleaseDate'] = self.entityjson['System'][0]['BIOSReleaseDate']
        if component == "HostNIC":
            if not entry["DeviceFQDD"] or entry["DeviceFQDD"] == "Not Available":
                return False
        if component == 'Sensors_Fan':
            cl = ['Key','Location']
            for x in cl:
                if x in entry:
                    s = entry[x]
                    if '|' in s:
                        entry[x] = s.split('|')[-1]
            cl = None
        if component == "VFlash":
            if 'PrimaryStatus' in entry:
                if entry["PrimaryStatus"] == "Not Available":
                    entry["PrimaryStatus"] = "Unknown"
        if component == 'SystemBoardMetrics':
            try:
                entry['PeakAmperage'] = float(entry.get('PeakAmperage',0))/10
            except ValueError:
                logger.info(self.ipaddr+" Warning: Converting PeakAmperage not a number "+entry.get('PeakAmperage', 'Not Present'))
                entry['PeakAmperage'] = "0"
        if component == "PresenceAndStatusSensor":
            if entry.get('ElementName') != "Chassis Controller":
                return False
        if 'Sensors_' in component:
            entry['Key'] = entry.get('Location', entry.get('Key', component))
            if (entry.get('SensorType', "Not Available")):
                entry["SensorType"] = component.split('_')[-1]
        if component == 'CPU':
            if self.cfactory.work_protocols[0].name == "SNMP":
                try:
                    ExtCapabilities = int(entry.get('ExtendedCapabilities', None))
                    if int(ExtCapabilities):
                        if (ExtCapabilities >> 0) & 1:
                            entry['VirtualizationTechnologyCapable'] = "Supported"
                        else:
                            entry['VirtualizationTechnologyCapable'] = "Not Supported"
                        if (ExtCapabilities >> 2) & 1:
                            entry['ExecuteDisabledCapable'] = "Supported"
                        else:
                            entry['ExecuteDisabledCapable'] = "Not Supported"
                        if (ExtCapabilities >> 3) & 1:
                            entry['HyperThreadingCapable'] = "Supported"
                        else:
                            entry['HyperThreadingCapable'] = "Not Supported"
                        if (ExtCapabilities >> 4) & 1:
                            entry['TurboModeCapable'] = "Supported"
                        else:
                            entry['TurboModeCapable'] = "Not Supported"
                except ValueError:
                    logger.info(
                        self.ipaddr + " Warning: extended capabilities of the processor device Not Available"
                    )
                try:
                    ExtEnabled = int(entry.get('ExtendedEnabled', None))
                    if int(ExtCapabilities):
                        if (ExtEnabled >> 0) & 1:
                            entry['VirtualizationTechnologyEnabled'] = "Enabled"
                        else:
                            entry['VirtualizationTechnologyEnabled'] = "Disabled"
                        if (ExtEnabled >> 2) & 1:
                            entry['ExecuteDisabledEnabled'] = "Enabled"
                        else:
                            entry['ExecuteDisabledEnabled'] = "Disabled"
                        if (ExtEnabled >> 3) & 1:
                            entry['HyperThreadingEnabled'] = "Enabled"
                        else:
                            entry['HyperThreadingEnabled'] = "Disabled"
                        if (ExtEnabled >> 4) & 1:
                            entry['TurboModeEnabled'] = "Enabled"
                        else:
                            entry['TurboModeEnabled'] = "Disabled"
                except ValueError:
                    logger.info(
                        self.ipaddr + " Warning: extended settings of the processor device Not Available"
                    )

        return True

    def _should_i_modify_component(self, finalretjson, component):
        if 'Sensors_' in component:
            pkeys = ["Key"]
            filtered = {tuple((k, d[k]) for k in sorted(d) if k in pkeys): d for d in finalretjson[component]}
            finalretjson[component] = list(filtered.values())
        if component == 'ChassisRF' or component == 'DellAttributes':
            del finalretjson[component]
        # if component == 'Subsystem':
        #     component = finalretjson.keys()
        #     subsystem = finalretjson["Subsystem"]
        #     finalretjson["Subsystem"] = list(filter(lambda eachdict: eachdict['Key'] in component, subsystem))
        """
        Reading(V) attribute value is displayed for different instance than actual. 
        In OMSDK value is shown for first instance where as actually its for 32nd instance.
        
        CurrentReading attribute value is displayed for different instance than actual. 
        For 36th instance OMSDK shows value as "Not Available", but actual value on device is "VoltageIsGood
        """
        if 'Sensors_Voltage' in component:
            if self.cfactory.work_protocols[0].name == "SNMP":
                """
                Sorting is done as instances are not in order in Linux 
                """
                sensors_voltage = sorted(finalretjson.get('Sensors_Voltage', []), key=lambda k: int(k.get('VoltageProbeIndex', 99999)))
                cr = []
                rv = []
                for val in sensors_voltage:
                        cr.append(val.get('CurrentReading', 'Not Available'))
                        rv.append(val.get('Reading(V)', 'Not Available'))
                i = 0
                j = 0
                for item in sensors_voltage:
                    if str(item.get('VoltageProbeType', 'Not Available')) != "voltageProbeTypeIsDiscrete" \
                            and str(item.get('State', 'Not Available')) == "Enabled":
                        item['Reading(V)'] = rv[i]
                        i += 1
                    if str(item.get('VoltageProbeType', 'Not Available')) == "voltageProbeTypeIsDiscrete":
                        item['Reading(V)'] = "Not Available"
                        item['CurrentReading'] = cr[j]
                        j += 1
                    if str(item.get('VoltageProbeType', 'Not Available')) != "voltageProbeTypeIsDiscrete":
                        item['CurrentReading'] = "Not Available"

    def _get_topology_info(self):
        return iDRACTopologyInfo(self.get_json_device())

    def _get_topology_influencers(self):
        return { 'System' : [
                        'ServiceTag',
                        'SystemGeneration',
                        'Model',
                        'GroupManager'
                ] }

    @property
    def ContainmentTree(self):
        """
        Removing PowerSupply, Sensors_Fan and Sensor_intrusion Groups
        :return: JSON
        """
        device_json = self.get_json_device()
        ctree = self._build_ctree(self.protofactory.ctree, device_json)
        syslist = self.entityjson.get('System', [{}])
        sysdict = syslist[0]
        blademodel = sysdict.get('Model', 'Not Available')
        #logger.info(self.ipaddr+" BLAde Model "+blademodel)

        if blademodel:
            systree = ctree.get('System', {})
            sensdict = systree.get('Sensors', {})
            if 'poweredge m' in str(blademodel).lower():
                systree.pop('PowerSupply', None)
                sensdict.pop('Sensors_Fan', None)
                sensdict.pop('Sensors_Intrusion', None)
            if ('poweredge fc' in str(blademodel).lower()) or ('poweredge fm' in str(blademodel).lower()):
                sensdict.pop('Sensors_Intrusion', None)
        return ctree

class iDRACTopologyInfo(iDeviceTopologyInfo):
    def __init__(self, json):
        if PY2:
            super(iDeviceTopologyInfo, self).__init__('Server', json)
        else:
            super().__init__('Server', json)

    def my_static_groups(self, tbuild):
        tbuild.add_group('Dell', static=True)
        tbuild.add_group('Dell Servers', 'Dell', static=True)
        tbuild.add_group('Dell Rack Workstations', 'Dell', static=True)
        tbuild.add_group('Dell Modular Servers', 'Dell Servers', static=True)
        tbuild.add_group('Dell Monolithic Servers', 'Dell Servers', static=True)
        tbuild.add_group('Dell Sled Servers', 'Dell Servers', static=True)
        tbuild.add_group('Dell FM Servers', 'Dell Sled Servers', static=True)
        tbuild.add_group('Dell Unmanaged Servers', 'Dell Servers', static=True)
        tbuild.add_group('Dell iDRAC GMs', 'Dell', static=True)

    def my_groups(self, tbuild):

        if 'ServiceTag' not in self.system:
            return False

        serviceTag = self.system['ServiceTag']
        grpname = 'Dell Unmanaged Servers'
        if 'SystemGeneration' in self.system:
            if 'Modular' in self.system['SystemGeneration']:
                grpname = 'Dell Modular Servers'
            elif 'Monolithic' or 'DCS' in self.system['SystemGeneration']:
                grpname = 'Dell Monolithic Servers'

        if 'Model' in self.system:
            if 'FM' in self.system['Model']:
                fmgrp = 'FMServer-' + serviceTag
                tbuild.add_group(fmgrp, 'Dell FM Servers')
                self._add_myself(tbuild, fmgrp)
                grpname = fmgrp
            if 'FC' in self.system['Model']:
                grpname = 'Dell Sled Servers'

        self._add_myself(tbuild, grpname)

        # if 'GroupManager' in self.system and self.system['GroupManager']:
        #     fmgrp = 'iGM-' + self.system['GroupManager']
        #     tbuild.add_group(fmgrp, 'Dell iDRAC GMs')
        #     self._add_myself(tbuild, fmgrp)

        return True

    def my_assoc(self, tbuild):
        if 'ServiceTag' not in self.system:
            return False

        serviceTag = self.system['ServiceTag']

        if 'ChassisServiceTag' not in self.system:
            # Rack Server or Rack Station or Tower system
            return True

        chassisSvcTag = self.system['ChassisServiceTag']

        if chassisSvcTag is None or chassisSvcTag == serviceTag:
            return True

        ### Commented out this section as slot
        ### returned by iDRAC is different from CMC-Slot FQDD
        #slot = 'undef'
        #if 'BaseBoardChassisSlot' in self.system:
        #    slot = self.system['BaseBoardChassisSlot']
        #
        #self._add_assoc(tbuild, ['CMC', chassisSvcTag],
        #                        ['ComputeModule', slot],
        #                        [self.mytype, self.system['Key']])

        return True
