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
from omsdk.sdkcenum import EnumWrapper
import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)

BackplaneTypeTypes = EnumWrapper("BackplaneTypeTypes", {
    "Not_Shared": "Not Shared",
    "Shared": "Shared",
}).enum_type

CachecadeTypes = EnumWrapper("CachecadeTypes", {
    "Cachecade_Virtual_Disk": "Cachecade Virtual Disk",
    "Not_a_Cachecade_Virtual_Disk": "Not a Cachecade Virtual Disk",
}).enum_type

CurrentControllerModeTypes = EnumWrapper("CurrentControllerModeTypes", {
    "HBA": "HBA",
    "RAID": "RAID",
}).enum_type

DiskCachePolicyTypes = EnumWrapper("DiskCachePolicyTypes", {
    "Default": "Default",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EncryptionModeTypes = EnumWrapper("EncryptionModeTypes", {
    "Dell_Key_Management": "Dell Key Management",
    "Local_Key_Management": "Local Key Management",
    "T_None": "None",
}).enum_type

LockStatusTypes = EnumWrapper("LockStatusTypes", {
    "Locked": "Locked",
    "Unlocked": "Unlocked",
}).enum_type

PCIeSSDSecureEraseTypes = EnumWrapper("PCIeSSDSecureEraseTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

RAIDControllerBootModeTypes = EnumWrapper("RAIDControllerBootModeTypes", {
    "Continue_Boot_On_Error": "Continue Boot On Error",
    "Headless_Mode_Continue_On_Error": "Headless Mode Continue On Error",
    "Headless_Safe_Mode": "Headless Safe Mode",
    "User_Mode": "User Mode",
}).enum_type

RAIDEnclosureCurrentCfgModeTypes = EnumWrapper("RAIDEnclosureCurrentCfgModeTypes", {
    "Split_Mode": "Split Mode",
    "Unified_Mode": "Unified Mode",
}).enum_type

RAIDEnclosureRequestedCfgModeTypes = EnumWrapper("RAIDEnclosureRequestedCfgModeTypes", {
    "Split_Mode": "Split Mode",
    "T_None": "None",
    "Unified_Mode": "Unified Mode",
}).enum_type

RAIDEnhancedAutoImportForeignConfigTypes = EnumWrapper("RAIDEnhancedAutoImportForeignConfigTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RAIDHotSpareStatusTypes = EnumWrapper("RAIDHotSpareStatusTypes", {
    "Dedicated": "Dedicated",
    "Global": "Global",
    "No": "No",
}).enum_type

RAIDMaxCapableSpeedTypes = EnumWrapper("RAIDMaxCapableSpeedTypes", {
    "T_12_GBS": "12_GBS",
    "T_1_5_GBS": "1_5_GBS",
    "T_3_GBS": "3_GBS",
    "T_6_GBS": "6_GBS",
}).enum_type

RAIDNegotiatedSpeedTypes = EnumWrapper("RAIDNegotiatedSpeedTypes", {
    "T_12_GBS": "12_GBS",
    "T_1_5_GBS": "1_5_GBS",
    "T_3_GBS": "3_GBS",
    "T_6_GBS": "6_GBS",
    "T_None": "None",
}).enum_type

RAIDPDStateTypes = EnumWrapper("RAIDPDStateTypes", {
    "Blocked": "Blocked",
    "Failed": "Failed",
    "Foreign": "Foreign",
    "Missing": "Missing",
    "Non_RAID": "Non-RAID",
    "Online": "Online",
    "Ready": "Ready",
    "Unknown": "Unknown",
}).enum_type

RAIDSupportedRAIDLevelsTypes = EnumWrapper("RAIDSupportedRAIDLevelsTypes", {
    "RAID_0": "RAID-0",
    "RAID_1": "RAID-1",
    "RAID_10": "RAID-10",
    "RAID_5": "RAID-5",
    "RAID_50": "RAID-50",
    "RAID_60": "RAID-60",
}).enum_type

RAIDTypesTypes = EnumWrapper("RAIDTypesTypes", {
    "RAID_0": "RAID 0",
    "RAID_1": "RAID 1",
    "RAID_10": "RAID 10",
    "RAID_5": "RAID 5",
    "RAID_50": "RAID 50",
    "RAID_6": "RAID 6",
    "RAID_60": "RAID 60",
    "Volume": "Volume",
}).enum_type

RAIDactionTypes = EnumWrapper("RAIDactionTypes", {
    "Create": "Create",
    "CreateAuto": "CreateAuto",
    "Delete": "Delete",
    "Update": "Update",
}).enum_type

RAIDbatteryLearnModeTypes = EnumWrapper("RAIDbatteryLearnModeTypes", {
    "Automatic": "Automatic",
    "Disabled": "Disabled",
    "T_None": "None",
    "Warn_only": "Warn only",
}).enum_type

RAIDccModeTypes = EnumWrapper("RAIDccModeTypes", {
    "Normal": "Normal",
    "StopOnError": "StopOnError",
}).enum_type

RAIDcopybackModeTypes = EnumWrapper("RAIDcopybackModeTypes", {
    "Off": "Off",
    "On": "On",
    "On_with_SMART": "On with SMART",
}).enum_type

RAIDdedicatedSpareTypes = EnumWrapper("RAIDdedicatedSpareTypes", {
    "autoselect": "autoselect",
}).enum_type

RAIDdefaultReadPolicyTypes = EnumWrapper("RAIDdefaultReadPolicyTypes", {
    "Adaptive": "Adaptive",
    "AdaptiveReadAhead": "AdaptiveReadAhead",
    "NoReadAhead": "NoReadAhead",
    "ReadAhead": "ReadAhead",
}).enum_type

RAIDdefaultWritePolicyTypes = EnumWrapper("RAIDdefaultWritePolicyTypes", {
    "WriteBack": "WriteBack",
    "WriteBackForce": "WriteBackForce",
    "WriteThrough": "WriteThrough",
}).enum_type

RAIDforeignConfigTypes = EnumWrapper("RAIDforeignConfigTypes", {
    "Clear": "Clear",
    "Ignore": "Ignore",
    "Import": "Import",
}).enum_type

RAIDinitOperationTypes = EnumWrapper("RAIDinitOperationTypes", {
    "Fast": "Fast",
    "T_None": "None",
}).enum_type

RAIDloadBalancedModeTypes = EnumWrapper("RAIDloadBalancedModeTypes", {
    "Automatic": "Automatic",
    "Disabled": "Disabled",
}).enum_type

RAIDprModeTypes = EnumWrapper("RAIDprModeTypes", {
    "Automatic": "Automatic",
    "Disabled": "Disabled",
    "Manual": "Manual",
}).enum_type

RAIDrekeyTypes = EnumWrapper("RAIDrekeyTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

RAIDremovecontrollerKeyTypes = EnumWrapper("RAIDremovecontrollerKeyTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

RAIDresetConfigTypes = EnumWrapper("RAIDresetConfigTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

RAIDsupportedDiskProtTypes = EnumWrapper("RAIDsupportedDiskProtTypes", {
    "SAS": "SAS",
    "SATA": "SATA",
}).enum_type

StripeSizeTypes = EnumWrapper("StripeSizeTypes", {
    "Default": "Default",
    "T_128KB": "131072",
    "T_16KB": "16384",
    "T_1KB": "1024",
    "T_1MB": "1048576",
    "T_256KB": "262144",
    "T_2KB": "2048",
    "T_2MB": "2097152",
    "T_32KB": "32768",
    "T_4KB": "4096",
    "T_4MB": "4194304",
    "T_512": "512",
    "T_512KB": "524288",
    "T_64KB": "65536",
    "T_8KB": "8192",
    "T_8MB": "8388608",
}).enum_type

T10PIStatusTypes = EnumWrapper("T10PIStatusTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type
