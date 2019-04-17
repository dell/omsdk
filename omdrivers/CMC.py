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

from enum import Enum
from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.sdkdevice import iDeviceTopologyInfo
from omsdk.sdkproto import PWSMAN
from omsdk.sdkcenum import EnumWrapper, TypeHelper

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


# MessageID, Message
CMCCompEnum = EnumWrapper("CMCCompEnum", {
    "System" : "System",
    "ComputeModule" : "ComputeModule",
    "StorageModule" : "StorageModule",
    "IOModule" : "IOModule",
    "Fan" : "Fan",
    "CMC" : "CMC",
    "PowerSupply" : "PowerSupply",
    "Controller" : "Controller",
    "Enclosure" : "Enclosure",
    "EnclosureEMM" : "EnclosureEMM",
    "EnclosurePSU" : "EnclosurePSU",
    "PCIDevice" : "PCIDevice",
    "ControllerBattery" : "ControllerBattery" ,
    "VirtualDisk" : "VirtualDisk",
    "PhysicalDisk" : "PhysicalDisk",
    "KVM" : "KVM",
    "BladeSlot" : "BladeSlot",
    "License" : "License",
    "Slots_Summary" : "Slots_Summary"
    }).enum_type

CMCMiscEnum = EnumWrapper("CMCMiscEnum", {
    "PassThroughModule" : "PassThroughModule",
    "PSPackage" : "PSPackage",
    "PSSlot" : "PSSlot",
    "PCISlot" : "PCISlot",
    "FanPackage" : "FanPackage",
    "FanSlot" : "FanSlot",
    "SystemChassis": "SystemChassis"
    }).enum_type

CMCLogsEnum = EnumWrapper("CMCLogEnum", {
    "Logs" : "Logs",
    }).enum_type

CMCJobsEnum = EnumWrapper("CMCJobEnum", {
    "Jobs" : "Jobs",
    }).enum_type

CMCFirmEnum = EnumWrapper("CMCFirmEnum", {
    "Firmware" : "Firmware",
    }).enum_type

CMCComponentTree = {
    CMCCompEnum.System : [
        CMCCompEnum.IOModule,
        CMCCompEnum.Fan,
        CMCCompEnum.CMC,
        CMCCompEnum.PowerSupply,
        CMCCompEnum.PCIDevice,
        CMCCompEnum.ComputeModule,
        CMCCompEnum.StorageModule,
        CMCCompEnum.Slots_Summary,
        "Storage"
    ],
    "Storage" : [
        CMCCompEnum.Controller
    ],
    CMCCompEnum.Controller : [
        CMCCompEnum.Enclosure,
        CMCCompEnum.ControllerBattery,
        CMCCompEnum.VirtualDisk,
        CMCCompEnum.PhysicalDisk
    ],
    CMCCompEnum.VirtualDisk : [
        CMCCompEnum.PhysicalDisk
    ],
    CMCCompEnum.Enclosure : [
        CMCCompEnum.EnclosureEMM,
        CMCCompEnum.EnclosurePSU,
        CMCCompEnum.PhysicalDisk
    ]
}

CMCWsManViews = {
    CMCCompEnum.System: "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ModularChassisView",
    CMCMiscEnum.SystemChassis: "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dell/Dell_Chassis",
    CMCCompEnum.ComputeModule : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BladeServerView",
    CMCCompEnum.StorageModule : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_StorageSledView",
    CMCCompEnum.Fan : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_Fan",
    CMCMiscEnum.FanPackage : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_FanPackage",
    CMCMiscEnum.FanSlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_FanSlot",
    CMCCompEnum.PCIDevice : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_ChassisPCIDeviceView",
    CMCMiscEnum.PCISlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_ChassisPCISlot",
    CMCCompEnum.CMC : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_ChMgrPackage",
    CMCCompEnum.IOModule : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_IOMPackage",
    CMCMiscEnum.PassThroughModule : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PassThroughModule",
    CMCCompEnum.PowerSupply : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PowerSupply",
    CMCMiscEnum.PSPackage : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PSPackage",
    CMCMiscEnum.PSSlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PSSlot",
    CMCFirmEnum.Firmware : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SoftwareIdentity",
    CMCJobsEnum.Jobs : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob",
    CMCLogsEnum.Logs : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_HWLogEntry",
    CMCCompEnum.Controller : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerView",
    CMCCompEnum.EnclosureEMM : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureEMMView",
    CMCCompEnum.EnclosurePSU : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosurePSUView",
    CMCCompEnum.Enclosure : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureView",
    CMCCompEnum.ControllerBattery : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerBatteryView",
    CMCCompEnum.VirtualDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_VirtualDiskView",
    CMCCompEnum.PhysicalDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PhysicalDiskView",
    CMCCompEnum.KVM : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_KVM",
    CMCCompEnum.BladeSlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_BladeSlot",
    CMCCompEnum.License : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_License"
}

CMCWsManCmds = { }
CMCWsManCompMap = { }

CMCUnionCompSpec = {
   "Slots_Summary":{
        "_components": [
            "ComputeModule",
            "StorageModule"
        ],
        "_components_enum": [
            CMCCompEnum.ComputeModule,
            CMCCompEnum.StorageModule
        ],
        "_remove_duplicates" : False
   }
}

CMC_more_details_spec = {
    "System": {
        "_components_enum": [
            CMCCompEnum.System,
            CMCCompEnum.ComputeModule,
            CMCCompEnum.StorageModule
        ]
    }
}

CMCMergeJoinCompSpec = {
   "Fan" : {
        "_components" : [
            ["Fan", "ClassId", "FanSlot", "ClassId"],
            ["Fan", "ClassId", "FanPackage", "ClassId"]
        ],
        "_components_enum": [
            CMCCompEnum.Fan,
            CMCMiscEnum.FanPackage,
            CMCMiscEnum.FanSlot
        ],
        "_overwrite" : False
   },
   "PowerSupply" : {
        "_components" : [
            ["PowerSupply", "ClassId", "PSPackage", "ClassId"],
            ["PowerSupply", "ClassId", "PSSlot", "ClassId"]
        ],
        "_components_enum": [
            CMCCompEnum.PowerSupply,
            CMCMiscEnum.PSPackage,
            CMCMiscEnum.PSSlot
        ],
        "_overwrite" : False
   },
   "IOModule" : {
        "_components" : [
            ["IOModule", "ClassId", "PassThroughModule", "ClassId"]
        ],
        "_components_enum": [
            CMCCompEnum.IOModule,
            CMCMiscEnum.PassThroughModule
        ],
        "_overwrite" : True
   },
   "PCIDevice" : {
        "_components" : [
            ["PCIDevice", "SlotFQDD", "PCISlot", "FQDD"]
        ],
        "_components_enum": [
            CMCCompEnum.PCIDevice,
            CMCMiscEnum.PCISlot
        ],
        "_overwrite" : False
   },
   "System": {
        "_components": [
            ["System", "PhysicalLocationChassisName", "SystemChassis", "Name"]
        ],
        "_components_enum": [
            CMCCompEnum.System,
            CMCMiscEnum.SystemChassis
        ],
        "_overwrite": False
   }
}
CMCWsManViews_FieldSpec = {
    CMCMiscEnum.SystemChassis: {
        "ElementName": {"Rename": "ProductShortName"}
    },
    CMCCompEnum.PowerSupply : {
        "HealthState":  {
            'Rename' : 'PrimaryStatus',
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "5" : "Healthy",
                "10" : "Warning", "15" : "Warning",
                "20": "Critical", "25" : "Critical", "30" : "Critical"
            }
        },
        "TotalOutputPower": {'UnitScale': '-3', 'UnitAppend': 'Watts'},
    },
    CMCCompEnum.Fan : {
        "HealthState":  {
            'Rename' : 'PrimaryStatus',
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "5" : "Healthy",
                "10" : "Warning", "15" : "Warning",
                "20": "Critical", "25" : "Critical", "30" : "Critical"
            }
        }
    },
    CMCMiscEnum.FanSlot : {
        "Number": {'Rename' : 'SlotNumber'}
    },
    CMCCompEnum.KVM : {
        "HealthState":  {
            'Rename': 'PrimaryStatus',
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "5" : "Healthy",
                "10" : "Warning", "15" : "Warning",
                "20": "Critical", "25" : "Critical", "30" : "Critical"
            }
        },
        "RequestedState": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "2": "Enabled",
                "3": "Disabled",
                "4": "Shut Down",
                "5": "No Change",
                "6": "Offline",
                "7": "Test",
                "8" : "Deferred",
                "9": "Quiesce",
                "10": "Reboot",
                "11": "Reset",
                "12": "Not Applicable "
            }
        },
        "EnabledState": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "Other",
                "2": "Enabled",
                "3": "Disabled",
                "4": "Shutting Down",
                "5": "Not Applicable",
                "6": "Enabled but Offline",
                "7": "In Test",
                "8": "Deferred",
                "9": "Quiesce",
                "10": "Starting"
            }
        },
        "OperationalStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown",
                "1": "Other",
                "2": "OK",
                "3": "Degraded",
                "4": "Stressed",
                "5": "Predictive Failure",
                "6": "Error",
                "7": "Non-Recoverable Error",
                "8": "Starting",
                "9": "Stopping",
                "10": "Stopped",
                "11": "In Service",
                "12": "No Contact",
                "13": "Lost Communication",
                "14": "Aborted",
                "15": "Dormant",
                "16": "Supporting Entity in Error",
                "17": "Completed",
                "18": "Power Mode",
                "19": "Relocating"
            }
        }
    },
    CMCMiscEnum.PSPackage : {
        "Tag":  { 'Rename' : 'PSPackage_Tag' }
    },
    CMCMiscEnum.PSSlot : {
        "Tag":  { 'Rename' : 'PSSlot_Tag' },
        "Number" : {'Rename' : 'Slot'}
    },
    CMCCompEnum.PhysicalDisk : {
        "SizeInBytes" : { 'Rename' : 'Capacity', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "FreeSizeInBytes" : { 'Rename' : 'FreeSpace', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "UsedSizeInBytes" : { 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "MediaType":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Hard Disk Drive",
                "1" : "Solid State Drive"
            }
        },
        "BusProtocol":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "1" : "SCSI", "2" : "PATA", "3" : "FIBRE", "4" : "USB", "5" : "SATA", "6" : "SAS"
            }
        },
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical", "0x8000" :"Warning", "0xFFFF" : "Warning"
            }
        },
        "SecurityState" : {
            'Lookup': 'True',
            'Values': {
                "0" : "Not Capable", "1" : "Secured", "2" : "Locked", "3" : "Foreign", "4" : "Encryption Capable", "5" : "Unknown"
            }
        },
        "PredictiveFailureState" : {
            'Lookup': 'True',
            'Values': {
                "0" : "Healthy", "1" : "Warning"
            }
        },
        "DriveFormFactor": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown", "1": "1.8 inch", "2": "2.5 inch", "3": "3.5 inch", "4": "2.5 inch Add-in card"
            }
        },
        "HotSpareStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "No", "1": "Dedicated", "2": "Global"
            }
        },
        "MaxCapableSpeed" : {
            'Lookup': 'True',
            'Values': {
                "0":"Unknown", "1": "1.5 Gbps", "2": "3 Gbps", "3": "6 Gbps","4": "12 Gbps"
            }
        }
    },
    CMCCompEnum.VirtualDisk : {
        "SizeInBytes" : { 'Rename' : 'Capacity', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "RAIDTypes":  {
            'Lookup' : 'True',
            'Values' : {
                "1" : "No RAID",
                "2" : "RAID0",
                "4" : "RAID1",
                "64" : "RAID5",
                "128" : "RAID6",
                "2048" : "RAID10",
                "8192" : "RAID50",
                "16384" : "RAID60"
            }
        },
        "MediaType":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Magnetic Drive",
                "2" : "Solid State Drive"
            }
        },
        "BusProtocol":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "1" : "SCSI", "2" : "PATA", "3" : "FIBRE", "4" : "USB", "5" : "SATA", "6" : "SAS"
            }
        },
        "StripeSize":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Default", "1" : "512B", "2" : "1KB", "4" : "2KB", "8" : "4KB", "16" : "8KB",
                "32" : "16KB", "64" : "32KB", "128" : "64KB", "256" : "128KB", "512" : "256KB",
                "1024" : "512KB", "2048" : "1MB", "4096" : "2MB", "8192" : "4MB", "16384" : "8MB", "32768" : "16MB"
            }
        },
        "ReadCachePolicy":  {
            'Lookup' : 'True',
            'Values' : {
                 "0" : "Unknown", "16" : "No Read Ahead", "32" : "Read Ahead", "64" : "Adaptive Read Ahead"
            }
        },
        "WriteCachePolicy":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "1" : "Write Through", "2" : "Write Back", "4" : "Write Back Force"
            }
        },
        "DiskCachePolicy":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "256" : "Default", "512" : "Enabled", "1024" : "Disabled"
            }
        },
        "LockStatus":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unlocked", "1" : "Locked"
            }
        },
        "Cachecade":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Not a Cachecade Virtual Disk", "1" : "Cachecade Virtual Disk"
            }
        }
    },
    CMCCompEnum.License : {
        "LicenseType":  {
            'Lookup' : 'True',
            'Values' : {
                "1" : "Perpetual", "2" : "Leased", "3" : "Evaluation", "4" : "Site"
            }
        },
        "LicensePrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0": "Unknown", "1": "Healthy", "2": "Warning", "3": "Critical"
            }
        }
    },
    CMCCompEnum.PCIDevice : {
        "PowerStateStatus":  {
            'Lookup' : 'True',
            'Values' : {
                "2" : "On", "3" : "Off"
            }
        },
        "DataBusWidth":  {
            'Lookup' : 'True',
            'Values' : {
                "0001" : "Other", 
                "0002" : "Unknown",
                "0003" : "8 bit",
                "0004" : "16 bit",
                "0005" : "32 bit",
                "0006" : "64 bit",
                "0007" : "128 bit",
                "0008" : "1x or x1",
                "0009" : "2x or x2",
                "000A" : "4x or x4",
                "000B" : "8x or x8",
                "000C" : "12x or x12",
                "000D" : "16x or x16",
                "000E" : "32x or x32"
            }
        }
    },
    CMCCompEnum.Controller : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical", "0x8000" :"Warning", "0xFFFF" : "Warning"
            }
        },
        "PatrolReadState" : {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Stopped", "2" : "Running"
            }
        },
        "SecurityStatus" : {
            'Lookup': 'True',
            'Values': {
                #MOF-Diff
                "0" : "Unknown", "1" : "Encryption Capable", "2" : "Security Key Assigned"
            }
        },
        'SlicedVDCapability' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "Sliced Virtual Disk creation not supported", "1" : "Sliced Virtual Disk creation supported"
            }
        },
        'CachecadeCapability' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "Cachecade Virtual Disk not supported", "1" : "Cachecade Virtual Disk supported"
            }
        },
        'EncryptionMode' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "None", "1" : "Local Key Management",
                    "2" : "Dell Key Management", "3" : "Pending Dell Key Management"
            }
        },
        'EncryptionCapability' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "None", "1" : "Local Key Management Capable",
                    "2" : "Dell Key Management Capable", "3" : "Pending Dell Key Management Capable"
            }
        },
        'DeviceCardSlotLength' : {
            'Lookup': 'True',
            'Values' : {
                    "3" : "Short", "4" : "Long"
            }
        },
        "CacheSizeInMB": {'Type': 'Bytes', 'InUnits': 'MB', 'OutUnits': 'MB'},
    },
    CMCCompEnum.Enclosure : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical", "0x8000" :"Warning", "0xFFFF" : "Warning"
            }
        },
        "WiredOrder" :  { 'Rename' : 'BayID' }
    },
    CMCMiscEnum.PassThroughModule :{
        "LinkTechnologies": {
            'Lookup': 'True',
            'Values': {
                "0" :   "Unknown",
                "1" : "Other",
                "2" :  "Ethernet",
                "3" :  "IB",
                "4" :  "FC",
                "5" :  "FDDI",
                "6" :  "ATM",
                "7" :  "Token Ring",
                "8" :  "Frame Relay",
                "9" :  "Infrared",
                "10" :  "BlueTooth",
                "11" :  "Wireless LAN"
            }
        }
    },
    CMCCompEnum.IOModule : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical"
            }
        }
    },
    CMCCompEnum.ComputeModule: {
        "PowerState": {
            'Lookup': 'True',
            'Values': {
                "1": "Other", "2": "Power On", "6": "Power Off"
            }
        }
    },
    CMCCompEnum.StorageModule: {
        "PowerState": {
            'Lookup': 'True',
            'Values': {
                "1": "Other", "2": "Power On", "6": "Power Off"
            }
        }
    },
    CMCCompEnum.System : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical"
            }
        },
        "PowerState": {
            'Lookup': 'True',
            'Values': {
                "1": "Other",
                "2": "Power On",
                "6": "Power Off - Hard"
            }
        }
    }
}

CMCSubsystemHealthSpec = {
    CMCCompEnum.CMC : { "Component" : CMCCompEnum.System, "Field" : 'PrimaryStatus' },
    CMCCompEnum.IOModule : { "Component" : CMCCompEnum.System, "Field" : 'IOMRollupStatus' },
    CMCCompEnum.ComputeModule : { "Component" : CMCCompEnum.System, "Field" : 'BladeRollupStatus' },
    'Storage' : { "Component" : CMCCompEnum.System, "Field" : 'ChassisStorageRollupStatus' },
    CMCCompEnum.PowerSupply : { "Component" : CMCCompEnum.System, "Field" : 'PSRollupStatus' },
    CMCCompEnum.KVM : { "Component" : CMCCompEnum.System, "Field" : 'KVMRollupStatus' },
    CMCCompEnum.Fan : { "Component" : CMCCompEnum.System, "Field" : 'FanRollupStatus' },
    CMCCompEnum.StorageModule : { "Component" : CMCCompEnum.System, "Field" : 'StorageSledRollupStatus' }
    #ChassisTempRollupStatus
}

class CMC(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(CMC, self).__init__(iDeviceRegistry("CMC", srcdir, CMCCompEnum))
        else:
            super().__init__(iDeviceRegistry("CMC", srcdir, CMCCompEnum))
        self.protofactory.add(PWSMAN(
            selectors = {"__cimnamespace" : "root/dell/cmc" },
            views = CMCWsManViews,
            view_fieldspec = CMCWsManViews_FieldSpec,
            cmds = CMCWsManCmds,
            compmap = CMCWsManCompMap
        ))
        self.protofactory.addClassifier([CMCCompEnum.System])
        self.protofactory.addCTree(CMCComponentTree)
        self.protofactory.addSubsystemSpec(CMCSubsystemHealthSpec)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return CMCEntity(self.ref, protofactory, ipaddr, creds)

class CMCEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(CMCEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.comp_merge_join_spec = CMCMergeJoinCompSpec
        self.comp_union_spec = CMCUnionCompSpec
        self.more_details_spec = CMC_more_details_spec

    def my_fix_obj_index(self, clsName, key, js):
        retval = None
        if clsName == "System":
            if 'ServiceTag' not in js or js['ServiceTag'] is None:
                js['ServiceTag'] = self.ipaddr
            retval = js['ServiceTag']
        if retval is None:
            retval = self.ipaddr + "cmc_null"
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
                diskids = parentdiskListStr.split(',')
                for d in diskids:
                    fd = d.strip().strip("'")
                    # print("FD is ",fd, " VD ",self._get_obj_index(childClsName,child))
                    if (self._get_obj_index(childClsName,child) in fd):
                        # print("Add to CTREE SUCCESS")
                        return True
            else:
                return False
        return self._get_obj_index(parentClsName, parent) in \
               self._get_obj_index(childClsName, child)

    def get_idrac_ips(self):
        self.get_partial_entityjson(self.ComponentEnum.ComputeModule)
        return self._get_field_device_for_all(self.ComponentEnum.ComputeModule, "IPv4Address")

    def _get_topology_info(self):
        self.get_partial_entityjson(self.ComponentEnum.ComputeModule)
        return CMCTopologyInfo(self.get_json_device())

    def _get_topology_influencers(self):
        return { 'System' : [ 'Model' ],
                 'ComputeModule' : [ 'ServiceTag' ] }

    def _should_i_include(self, component, entry):
        if component == "ComputeModule":
            # print("IN SHOULD I Include")
            if (not entry.get('SubSlot') or (entry.get('SubSlot') == "NA")):
                entry['FormFactor'] = 'Half length Blade'
            else:
                entry['FormFactor'] = 'Quarter length Blade'
            if (entry.get('MasterSlotNumber') != entry.get('SlotNumber')) and (entry.get('SubSlot') == 'NA' or entry.get('SubSlot') == None):
                entry['ExtensionSlot'] = entry.get('SlotNumber')
                entry['FormFactor'] = 'Full length Blade'
            if entry.get('Model'):
                if 'FM' in entry.get('Model'):
                    entry['FormFactor'] = 'Half length Blade'

        if component == "Slots_Summary":
            if not 'StorageMode' in entry:
                if (not entry.get('SubSlot')) or (entry.get('SubSlot') == "NA"):
                    entry['FormFactor'] = 'Half length Blade'
                else:
                    entry['FormFactor'] = 'Quarter length Blade'
                if (entry.get('MasterSlotNumber') != entry.get('SlotNumber')) and (entry.get('SubSlot') == 'NA' or entry.get('SubSlot') == None):
                    entry['ExtensionSlot'] = entry.get('SlotNumber')
                    entry['FormFactor'] = 'Full length Blade'

        if component == "StorageModule":
            if "StorageModule" in self.entityjson:
                storageslot = self.entityjson["StorageModule"]
                for slot in storageslot:
                    slot['MasterSlotNumber'] = int(slot['FQDD'][-2:])
                    slot['FormFactor'] = 'Half length Blade'
                    slot['SlotName'] = 'SLOT-'+str(slot['FQDD'][-2:])

        if component == "CMC":
            attrlist = ['PrimaryStatus', 'MgmtControllerFirmwareVersion', 'Model']
            sysdict = self.entityjson.get('System',[None])[0]
            cmcdict = self.entityjson.get('CMC',[None])[0]
            if sysdict and cmcdict:
                for attr in attrlist:
                    cmcdict[attr] = sysdict.get(attr, 'Not Available')

        if component == "System":
            default, aisle, rack, rackslot = "NA", entry.get("PhysicalLocationAisle", "NA"), \
                                             entry.get("PhysicalLocationRack", "NA"), \
                                             entry.get("PhysicalLocationRackSlot", "NA")
            if  aisle == None:
                aisle = default
            if rack == None:
                rack = default
            if rackslot == None:
                rackslot = default
            entry["Location"] = "AISLE:{}, RACK:{}, Slot on Rack:{}".format(
                aisle, rack, rackslot )
        compsList = ["PowerSupply", "Fan", "KVM"]
        if component in compsList :
            if "PrimaryStatus" in entry:
                entry["HealthState"] = entry.get("PrimaryStatus", "Not Available")
        return True

    def _should_i_modify_component(self, finalretjson, component):
        if component == 'ComputeModule':
            if "ComputeModule" in finalretjson:
                bladeslot = finalretjson['ComputeModule']
                st_dict = {}
                slt_ndict = {}
                for slot in bladeslot:
                    slot_srvtag = slot.get('MasterSlotNumber')
                    slt_ndict.setdefault(slot_srvtag, []).append(slot.get('SlotNumber'))
                    if slot_srvtag in st_dict:
                        st_dict[slot_srvtag] = st_dict[slot_srvtag] + 1
                    else:
                        st_dict[slot_srvtag] = 1
                for slot in bladeslot:
                    if (st_dict[slot.get('MasterSlotNumber')] == 2) and (slot.get('SubSlot') == 'NA'):
                        slot['FormFactor'] = 'Full length Blade'
                        if slot.get('MasterSlotNumber') != slot.get('SlotNumber'):
                            slot['ExtensionSlot'] = True
                        slot['SlotNumber'] = "/".join(sorted(slt_ndict[slot.get('MasterSlotNumber')],key=int))
                    if 'FormFactor' in slot:
                        if 'Quarter' in slot['FormFactor']:
                            if slot.get('SubSlot') not in slot.get('SlotNumber'):
                                slot['SlotNumber'] = slot.get('SlotNumber') + slot.get('SubSlot')

                newbladeList = []
                tmpDupList = []
                #TODO: Replacing 4 FM servers with Single - Will affect Nagios
                fmSlotNumSet = {}
                cmcmodel = self.entityjson['System'][0]["Model"]
                slotArch = 1
                if 'FX2' in cmcmodel:
                    slotArch = 2
                for slot in bladeslot:
                    if 'FM' in slot.get('Model', 'Not Available'):
                        fmSlotNumSet[slot.get('MasterSlotNumber')] = slot
                    else:
                        if slot.get('ExtensionSlot',False) != True:
                            if 'Full' in slot.get('FormFactor',"Not Available"):
                                extslot = slot.get('SlotNumber').split('/')
                                slot['ExtensionSlot'] = extslot[-1]
                                if abs(int(slot.get('MasterSlotNumber')) - int(slot['ExtensionSlot'])) == slotArch:
                                    slot['FormFactor'] = "Half length Double width"
                            newbladeList.append(slot)
                            tmpDupList.append(slot)
                #To remove FM servers who dont show Model - based on MasterSlotNumber
                for slot in tmpDupList:
                    if slot.get('MasterSlotNumber') in fmSlotNumSet:
                        newbladeList.remove(slot)

                del finalretjson["ComputeModule"]
                finalretjson['ComputeModule'] = newbladeList + list(fmSlotNumSet.values())

                storagelist = []
                for m in finalretjson['ComputeModule']:
                    if m.get('Model',"") == "PS-M4110":
                        storagelist.append(m)
                if storagelist:
                    storagemod = finalretjson.get('StorageModule', None)
                    if not storagemod:
                        storagemod = []
                    storagemod = storagemod + storagelist
                    finalretjson['StorageModule'] = storagemod
                    for x in storagelist:
                        finalretjson['ComputeModule'].remove(x)

        if component == "Slots_Summary":
            if "Slots_Summary" in finalretjson:
                bladeslot = self.entityjson["Slots_Summary"]
                st_dict = {}
                slt_ndict = {}
                for slot in bladeslot:
                    if not "StorageMode" in slot:
                        slt_ndict.setdefault(slot.get('MasterSlotNumber'), []).append(slot.get('SlotNumber'))
                        if slot.get('MasterSlotNumber') in st_dict:
                            st_dict[slot.get('MasterSlotNumber')] = st_dict[slot.get('MasterSlotNumber')] + 1
                        else:
                            st_dict[slot.get('MasterSlotNumber')] = 1
                for slot in bladeslot:
                    if not "StorageMode" in slot:
                        if (st_dict[slot.get('MasterSlotNumber')] == 2) and ((slot.get('SubSlot') == 'NA') or (slot.get('SubSlot') == None)):
                            slot['FormFactor'] = 'Full length Blade'
                        if 'FormFactor' in slot:
                            if 'Quarter' in slot['FormFactor']:
                                slot['SlotNumber'] = slot.get('MasterSlotNumber') + slot.get('SubSlot')

                cmcmodel = self.entityjson['System'][0]["Model"]
                freeslots = set()
                occupiedSlots = set()
                extensionSlots = set()
                if 'FX2' in cmcmodel:
                    slotArch = 1
                    freeslots = set(range(1, 5))
                if 'VRTX' in cmcmodel:
                    slotArch = 2
                    freeslots = set(range(1, 5))
                if 'M1000e' in cmcmodel:
                    slotArch = 8
                    freeslots = set(range(1, 17))

                bladeslot = self.entityjson["Slots_Summary"]
                for slot in bladeslot:
                    if 'StorageMode' in slot:  # this is a Sled
                        sledslot = int(slot['FQDD'][-2:])
                        freeslots.discard(sledslot)
                        occupiedSlots.add(sledslot)
                    else:  # this is a blade
                        if 'FormFactor' in slot:
                            if 'Full' in slot['FormFactor']:
                                if 'ExtensionSlot' in slot:
                                    freeslots.discard(int(slot['ExtensionSlot']))
                                    extensionSlots.add(int(slot['ExtensionSlot']))
                                else:
                                    freeslots.discard(int(slot['MasterSlotNumber']))
                                    occupiedSlots.add(int(slot['MasterSlotNumber']))
                            if 'Half' in slot['FormFactor']:
                                freeslots.discard(int(slot['MasterSlotNumber']))
                                occupiedSlots.add(int(slot['MasterSlotNumber']))

                quarterSlotdict = {'a': 'b', 'b': 'a', 'c': 'd', 'd': 'c'}
                extSlotIndicator = {'a': False, 'b': False, 'c': True, 'd': True}
                for slot in bladeslot:
                    if 'FormFactor' in slot:
                        if 'Quarter' in slot['FormFactor']:
                            slotModifier = 0
                            if (extSlotIndicator[slot['SubSlot']] and (slot['Model'] and 'FM' not in slot['Model'])):
                                slotModifier = slotArch
                            extSlot = int(slot['MasterSlotNumber']) + slotModifier
                            if extSlot in freeslots:
                                freeslots.discard(extSlot)
                            qSlot = slot['MasterSlotNumber'] + slot['SubSlot']
                            if qSlot in freeslots:
                                freeslots.discard(qSlot)
                            occupiedSlots.add(qSlot)
                            otherslot = slot['MasterSlotNumber'] + quarterSlotdict[slot['SubSlot']]
                            if otherslot not in occupiedSlots:
                                freeslots.add(otherslot)

                slot_summary = {}
                slot_summary['Key'] = 'SlotSummary'
                slot_summary['InstanceID'] = 'SlotSummary'
                if freeslots:
                    slot_summary['FreeSlots'] = ",".join(str(x) for x in freeslots)
                else:
                    slot_summary['FreeSlots'] = "Chassis is fully occupied"
                if occupiedSlots:
                    slot_summary['OccupiedSlots'] = ",".join(str(x) for x in occupiedSlots)
                else:
                    slot_summary['OccupiedSlots'] = "Chassis is empty"
                if extensionSlots:
                    slot_summary['ExtensionSlots'] = ",".join(str(x) for x in extensionSlots)
                else:
                    if occupiedSlots:
                        slot_summary['ExtensionSlots'] = "Chassis does not have any Full length blades"
                    else:
                        slot_summary['ExtensionSlots'] = "Chassis is empty"
                del finalretjson["Slots_Summary"]
                finalretjson['Slots_Summary'] = []
                finalretjson['Slots_Summary'].append(slot_summary)

    @property
    def ContainmentTree(self):
        """
        Removing storage component from M1000e and FX2 model chassis
        :return: JSON
        """
        device_json = self.get_json_device()
        ctree = self._build_ctree(self.protofactory.ctree, device_json)
        cmcmodel = self.entityjson['System'][0]["Model"]
        if 'M1000e' in cmcmodel or 'FX2' in cmcmodel:
            if "Storage" in ctree:
                del ctree["Storage"]
            if "Storage" in ctree["System"]:
                del ctree["System"]["Storage"]
        return ctree


class CMCTopologyInfo(iDeviceTopologyInfo):
    def __init__(self, json):
        if PY2:
            super(iDeviceTopologyInfo, self).__init__('CMC', json)
        else:
            super().__init__('CMC', json)

    def my_static_groups(self, tbuild):
        tbuild.add_group('Dell', static=True)
        tbuild.add_group('Dell Chassis', 'Dell', static=True)

    def my_groups(self, tbuild):
        if 'Model' in self.system:
            fmgrp = "Dell "+self.system['Model']
            tbuild.add_group(fmgrp, 'Dell Chassis')
            self._add_myself(tbuild, fmgrp)

    def my_assoc(self, tbuild):
        if 'ComputeModule' not in self.json:
            return
        self._remove_assoc(tbuild, [self.mytype, self.system['Key']])
        for slot in self.json['ComputeModule']:
            self._add_assoc(tbuild,
                            [self.mytype, self.system['Key']],
                            ['ComputeModule', slot['Key']],
                            ['Server', slot['ServiceTag']])
