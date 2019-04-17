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

AcPwrRcvryDelayTypes = EnumWrapper("AcPwrRcvryDelayTypes", {
    "Immediate": "Immediate",
    "Random": "Random",
    "User": "User",
}).enum_type

AcPwrRcvryTypes = EnumWrapper("AcPwrRcvryTypes", {
    "Last": "Last",
    "Off": "Off",
    "On": "On",
}).enum_type

AcPwrRcvryUserDelayTypes = EnumWrapper("AcPwrRcvryUserDelayTypes", {
    "N_A": "N/A",
}).enum_type

AddrBasMirTypes = EnumWrapper("AddrBasMirTypes", {
    "AllMem": "AllMem",
    "HalfMem": "HalfMem",
    "T_64GB": "64GB",
}).enum_type

AesNiTypes = EnumWrapper("AesNiTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AssetTagTypes = EnumWrapper("AssetTagTypes", {
    "N_A": "N/A",
}).enum_type

AttemptFastBootColdTypes = EnumWrapper("AttemptFastBootColdTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AttemptFastBootTypes = EnumWrapper("AttemptFastBootTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BiosUpdateControlTypes = EnumWrapper("BiosUpdateControlTypes", {
    "Limited": "Limited",
    "Locked": "Locked",
    "Unlocked": "Unlocked",
}).enum_type

BootModeTypes = EnumWrapper("BootModeTypes", {
    "Bios": "Bios",
    "Uefi": "Uefi",
}).enum_type

BootSeqRetryTypes = EnumWrapper("BootSeqRetryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BrowserDebugModeTypes = EnumWrapper("BrowserDebugModeTypes", {
    "BrowserDebugModeDefault": "BrowserDebugModeDefault",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BrowserModeTypes = EnumWrapper("BrowserModeTypes", {
    "BrowserModeDefault_BrowserModeGraphic": "BrowserModeDefault:BrowserModeGraphic",
    "BrowserModeText": "BrowserModeText",
}).enum_type

BugCheckingTypes = EnumWrapper("BugCheckingTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CTOMaskingTypes = EnumWrapper("CTOMaskingTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CkeThrottlingTypes = EnumWrapper("CkeThrottlingTypes", {
    "ADP": "ADP",
    "Auto": "Auto",
    "Off": "Off",
    "PPD": "PPD",
}).enum_type

ClpOutputTypes = EnumWrapper("ClpOutputTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ClusterOnDieTypes = EnumWrapper("ClusterOnDieTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CollaborativeCpuPerfCtrlTypes = EnumWrapper("CollaborativeCpuPerfCtrlTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ConTermTypeTypes = EnumWrapper("ConTermTypeTypes", {
    "Ansi": "Ansi",
    "Vt100Vt220": "Vt100Vt220",
}).enum_type

ControlledTurboExtendedTypes = EnumWrapper("ControlledTurboExtendedTypes", {
    "ControlledTurboLimitMinus1": "ControlledTurboLimitMinus1",
    "ControlledTurboLimitMinus2": "ControlledTurboLimitMinus2",
    "Disabled": "Disabled",
}).enum_type

ControlledTurboTypes = EnumWrapper("ControlledTurboTypes", {
    "Custom": "Custom",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CorePerfBoostTypes = EnumWrapper("CorePerfBoostTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CorrEccSmiTypes = EnumWrapper("CorrEccSmiTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CpuInterconnectBusLinkPowerTypes = EnumWrapper("CpuInterconnectBusLinkPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CpuInterconnectBusSpeedTypes = EnumWrapper("CpuInterconnectBusSpeedTypes", {
    "MaxDataRate": "MaxDataRate",
    "T_10GTps": "10GTps",
    "T_9GTps": "9GTps",
}).enum_type

CurrentEmbVideoStateTypes = EnumWrapper("CurrentEmbVideoStateTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DataReuseTypes = EnumWrapper("DataReuseTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DcuIpPrefetcherTypes = EnumWrapper("DcuIpPrefetcherTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DcuStreamerPrefetcherTypes = EnumWrapper("DcuStreamerPrefetcherTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DebugErrorLevelTypes = EnumWrapper("DebugErrorLevelTypes", {
    "N_A": "N/A",
}).enum_type

DellAutoDiscoveryTypes = EnumWrapper("DellAutoDiscoveryTypes", {
    "AutoDiscovery": "AutoDiscovery",
    "ManualControl": "ManualControl",
    "PlatformDefault": "PlatformDefault",
}).enum_type

DellWyseP25BIOSAccessTypes = EnumWrapper("DellWyseP25BIOSAccessTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DeviceUnhideTypes = EnumWrapper("DeviceUnhideTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DfxTypes = EnumWrapper("DfxTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DirectMediaInterfaceSpeedTypes = EnumWrapper("DirectMediaInterfaceSpeedTypes", {
    "Default": "Default",
    "Gen1": "Gen1",
    "Gen2": "Gen2",
    "Gen3": "Gen3",
}).enum_type

DmaVirtualizationTypes = EnumWrapper("DmaVirtualizationTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DynamicCoreAllocationTypes = EnumWrapper("DynamicCoreAllocationTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EmbNic1Nic2Types = EnumWrapper("EmbNic1Nic2Types", {
    "Disabled": "Disabled",
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

EmbNic1Types = EnumWrapper("EmbNic1Types", {
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

EmbNic2Types = EnumWrapper("EmbNic2Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "EnabledPxe": "EnabledPxe",
    "EnablediScsi": "EnablediScsi",
}).enum_type

EmbNic3Nic4Types = EnumWrapper("EmbNic3Nic4Types", {
    "Disabled": "Disabled",
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

EmbNic3Types = EnumWrapper("EmbNic3Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "EnabledPxe": "EnabledPxe",
    "EnablediScsi": "EnablediScsi",
}).enum_type

EmbNic4Types = EnumWrapper("EmbNic4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "EnabledPxe": "EnabledPxe",
    "EnablediScsi": "EnablediScsi",
}).enum_type

EmbNicPort1BootProtoTypes = EnumWrapper("EmbNicPort1BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

EmbNicPort2BootProtoTypes = EnumWrapper("EmbNicPort2BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

EmbNicPort3BootProtoTypes = EnumWrapper("EmbNicPort3BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

EmbNicPort4BootProtoTypes = EnumWrapper("EmbNicPort4BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

EmbSataRSTeDebugTypes = EnumWrapper("EmbSataRSTeDebugTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EmbSataShadowTypes = EnumWrapper("EmbSataShadowTypes", {
    "AhciMode": "AhciMode",
    "AtaMode": "AtaMode",
    "Off": "Off",
    "RaidMode": "RaidMode",
}).enum_type

EmbSataTestModeTypes = EnumWrapper("EmbSataTestModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EmbSataTypes = EnumWrapper("EmbSataTypes", {
    "AhciMode": "AhciMode",
    "AtaMode": "AtaMode",
    "Off": "Off",
    "RaidMode": "RaidMode",
}).enum_type

EmbVideoTypes = EnumWrapper("EmbVideoTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EnergyEfficientTurboTypes = EnumWrapper("EnergyEfficientTurboTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EnergyPerformanceBiasTypes = EnumWrapper("EnergyPerformanceBiasTypes", {
    "BalancedEfficiency": "BalancedEfficiency",
    "BalancedPerformance": "BalancedPerformance",
    "LowPower": "LowPower",
    "MaxPower": "MaxPower",
}).enum_type

ErrPromptTypes = EnumWrapper("ErrPromptTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ExtSerialConnectorTypes = EnumWrapper("ExtSerialConnectorTypes", {
    "RemoteAccDevice": "RemoteAccDevice",
    "Serial1": "Serial1",
    "Serial2": "Serial2",
}).enum_type

FailSafeBaudTypes = EnumWrapper("FailSafeBaudTypes", {
    "T_115200": "115200",
    "T_19200": "19200",
    "T_57600": "57600",
    "T_9600": "9600",
}).enum_type

FanPwrPerfTypes = EnumWrapper("FanPwrPerfTypes", {
    "MaxPerf": "MaxPerf",
    "MinPwr": "MinPwr",
}).enum_type

ForceInt10Types = EnumWrapper("ForceInt10Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FrontLcdTypes = EnumWrapper("FrontLcdTypes", {
    "Advanced": "Advanced",
    "ModelNum": "ModelNum",
    "T_None": "None",
    "UserDefined": "UserDefined",
}).enum_type

GlobalSlotDriverDisableTypes = EnumWrapper("GlobalSlotDriverDisableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HddFailoverTypes = EnumWrapper("HddFailoverTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev1EnDisTypes = EnumWrapper("HttpDev1EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev1ProtocolTypes = EnumWrapper("HttpDev1ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

HttpDev1VlanEnDisTypes = EnumWrapper("HttpDev1VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev2EnDisTypes = EnumWrapper("HttpDev2EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev2ProtocolTypes = EnumWrapper("HttpDev2ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

HttpDev2VlanEnDisTypes = EnumWrapper("HttpDev2VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev3EnDisTypes = EnumWrapper("HttpDev3EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev3ProtocolTypes = EnumWrapper("HttpDev3ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

HttpDev3VlanEnDisTypes = EnumWrapper("HttpDev3VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev4EnDisTypes = EnumWrapper("HttpDev4EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpDev4ProtocolTypes = EnumWrapper("HttpDev4ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

HttpDev4VlanEnDisTypes = EnumWrapper("HttpDev4VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IdracDebugModeTypes = EnumWrapper("IdracDebugModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IgnoreIdracCrReqTypes = EnumWrapper("IgnoreIdracCrReqTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IioPcieGlobalSpeedTypes = EnumWrapper("IioPcieGlobalSpeedTypes", {
    "Default": "Default",
    "Gen1": "Gen1",
    "Gen2": "Gen2",
    "Gen3": "Gen3",
}).enum_type

InBandManageabilityInterfaceTypes = EnumWrapper("InBandManageabilityInterfaceTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

InSystemCharacterizationTypes = EnumWrapper("InSystemCharacterizationTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "FastBoot": "FastBoot",
}).enum_type

IntNic1Port1BootProtoTypes = EnumWrapper("IntNic1Port1BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

IntNic1Port2BootProtoTypes = EnumWrapper("IntNic1Port2BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

IntNic1Port3BootProtoTypes = EnumWrapper("IntNic1Port3BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

IntNic1Port4BootProtoTypes = EnumWrapper("IntNic1Port4BootProtoTypes", {
    "Iscsi": "Iscsi",
    "Pxe": "Pxe",
    "T_None": "None",
    "Unknown": "Unknown",
}).enum_type

IntegratedNetwork1Types = EnumWrapper("IntegratedNetwork1Types", {
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

IntegratedNetwork2Types = EnumWrapper("IntegratedNetwork2Types", {
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

IntegratedRaidTypes = EnumWrapper("IntegratedRaidTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IntegratedSasTypes = EnumWrapper("IntegratedSasTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IntelTestEventIioTypes = EnumWrapper("IntelTestEventIioTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IntelTxtTypes = EnumWrapper("IntelTxtTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

InteractivePassword24ATypes = EnumWrapper("InteractivePassword24ATypes", {
    "Default": "Default",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

InternalSdCardPresenceTypes = EnumWrapper("InternalSdCardPresenceTypes", {
    "Both": "Both",
    "SdCard1Only": "SdCard1Only",
    "SdCard2Only": "SdCard2Only",
    "T_None": "None",
}).enum_type

InternalSdCardPrimaryCardTypes = EnumWrapper("InternalSdCardPrimaryCardTypes", {
    "SdCard1": "SdCard1",
    "SdCard2": "SdCard2",
}).enum_type

InternalSdCardRedundancyTypes = EnumWrapper("InternalSdCardRedundancyTypes", {
    "Disabled": "Disabled",
    "Mirror": "Mirror",
}).enum_type

InternalSdCardTypes = EnumWrapper("InternalSdCardTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

InternalUsb1Types = EnumWrapper("InternalUsb1Types", {
    "Off": "Off",
    "On": "On",
}).enum_type

InternalUsb2Types = EnumWrapper("InternalUsb2Types", {
    "Off": "Off",
    "On": "On",
}).enum_type

InternalUsbTypes = EnumWrapper("InternalUsbTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

IoNonPostedPrefetchTypes = EnumWrapper("IoNonPostedPrefetchTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IoatEngineTypes = EnumWrapper("IoatEngineTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con1AuthTypes = EnumWrapper("IscsiDev1Con1AuthTypes", {
    "Chap": "Chap",
    "T_None": "None",
}).enum_type

IscsiDev1Con1ChapTypeTypes = EnumWrapper("IscsiDev1Con1ChapTypeTypes", {
    "Mutual": "Mutual",
    "OneWay": "OneWay",
}).enum_type

IscsiDev1Con1DhcpEnDisTypes = EnumWrapper("IscsiDev1Con1DhcpEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con1EnDisTypes = EnumWrapper("IscsiDev1Con1EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con1ProtocolTypes = EnumWrapper("IscsiDev1Con1ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

IscsiDev1Con1TgtDhcpEnDisTypes = EnumWrapper("IscsiDev1Con1TgtDhcpEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con1VlanEnDisTypes = EnumWrapper("IscsiDev1Con1VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con2AuthTypes = EnumWrapper("IscsiDev1Con2AuthTypes", {
    "Chap": "Chap",
    "T_None": "None",
}).enum_type

IscsiDev1Con2ChapTypeTypes = EnumWrapper("IscsiDev1Con2ChapTypeTypes", {
    "Mutual": "Mutual",
    "OneWay": "OneWay",
}).enum_type

IscsiDev1Con2DhcpEnDisTypes = EnumWrapper("IscsiDev1Con2DhcpEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con2EnDisTypes = EnumWrapper("IscsiDev1Con2EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con2ProtocolTypes = EnumWrapper("IscsiDev1Con2ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

IscsiDev1Con2TgtDhcpEnDisTypes = EnumWrapper("IscsiDev1Con2TgtDhcpEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1Con2VlanEnDisTypes = EnumWrapper("IscsiDev1Con2VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiDev1EnDisTypes = EnumWrapper("IscsiDev1EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

JunoPmEnableTypes = EnumWrapper("JunoPmEnableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LinkDowntrainReportingTypes = EnumWrapper("LinkDowntrainReportingTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LogicalProcTypes = EnumWrapper("LogicalProcTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MRCSerialDbgOutTypes = EnumWrapper("MRCSerialDbgOutTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MeFailureRecoveryEnableTypes = EnumWrapper("MeFailureRecoveryEnableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MeUmaEnableTypes = EnumWrapper("MeUmaEnableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemDynamicPwrTypes = EnumWrapper("MemDynamicPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemFrequencyTypes = EnumWrapper("MemFrequencyTypes", {
    "MaxPerf": "MaxPerf",
    "MaxReliability": "MaxReliability",
    "T_1067MHz": "1067MHz",
    "T_1333MHz": "1333MHz",
    "T_1600MHz": "1600MHz",
    "T_1866": "1866",
    "T_2133": "2133",
    "T_800MHz": "800MHz",
}).enum_type

MemHotThrottlingModeTypes = EnumWrapper("MemHotThrottlingModeTypes", {
    "MemHotDisable": "MemHotDisable",
    "MemHotInputOnly": "MemHotInputOnly",
    "MemHotOutputOnly": "MemHotOutputOnly",
    "MemoryThrottlingModeNone": "MemoryThrottlingModeNone",
}).enum_type

MemLowPowerTypes = EnumWrapper("MemLowPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemOpModeTypes = EnumWrapper("MemOpModeTypes", {
    "AdvEccMode": "AdvEccMode",
    "FaultResilientMode": "FaultResilientMode",
    "MirrorMode": "MirrorMode",
    "OptimizerMode": "OptimizerMode",
    "SpareMode": "SpareMode",
    "SpareWithAdvEccMode": "SpareWithAdvEccMode",
}).enum_type

MemOpVoltageTypes = EnumWrapper("MemOpVoltageTypes", {
    "AutoVolt": "AutoVolt",
    "Volt15V": "Volt15V",
}).enum_type

MemOptimizerTypes = EnumWrapper("MemOptimizerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemPatrolScrubTypes = EnumWrapper("MemPatrolScrubTypes", {
    "Disabled": "Disabled",
    "Extended": "Extended",
    "Standard": "Standard",
}).enum_type

MemPwrMgmtTypes = EnumWrapper("MemPwrMgmtTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemPwrPerfTypes = EnumWrapper("MemPwrPerfTypes", {
    "MaxPerf": "MaxPerf",
    "MinPwr": "MinPwr",
    "T_1067Mhz": "1067Mhz",
    "T_1333Mhz": "1333Mhz",
    "T_800Mhz": "800Mhz",
    "T_978Mhz": "978Mhz",
}).enum_type

MemRefreshRateTypes = EnumWrapper("MemRefreshRateTypes", {
    "T_1x": "1x",
    "T_2x": "2x",
}).enum_type

MemTestOnFastBootTypes = EnumWrapper("MemTestOnFastBootTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemTestTypeTypes = EnumWrapper("MemTestTypeTypes", {
    "Hardware": "Hardware",
    "Software": "Software",
}).enum_type

MemTestTypes = EnumWrapper("MemTestTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "HardwareBasedTest": "HardwareBasedTest",
}).enum_type

MemThrottlingModeTypes = EnumWrapper("MemThrottlingModeTypes", {
    "Cltt": "Cltt",
    "Oltt": "Oltt",
}).enum_type

MemVoltTypes = EnumWrapper("MemVoltTypes", {
    "AutoVolt": "AutoVolt",
    "Volt135V": "Volt135V",
    "Volt15V": "Volt15V",
}).enum_type

MemoryFastBootColdTypes = EnumWrapper("MemoryFastBootColdTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemoryMappedIOHTypes = EnumWrapper("MemoryMappedIOHTypes", {
    "Disabled": "Disabled",
    "T_12TB": "12TB",
    "T_512GB": "512GB",
    "T_56TB": "56TB",
}).enum_type

MemoryMultiThreadTypes = EnumWrapper("MemoryMultiThreadTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemoryPerBitMarginTypes = EnumWrapper("MemoryPerBitMarginTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemoryRmtTypes = EnumWrapper("MemoryRmtTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MemoryThrottlingModeTypes = EnumWrapper("MemoryThrottlingModeTypes", {
    "MemoryThrottlingModeCLTT": "MemoryThrottlingModeCLTT",
    "MemoryThrottlingModeCLTTWithPECI": "MemoryThrottlingModeCLTTWithPECI",
    "MemoryThrottlingModeNone": "MemoryThrottlingModeNone",
    "MemoryThrottlingModeOLTT": "MemoryThrottlingModeOLTT",
}).enum_type

MltRnkSprTypes = EnumWrapper("MltRnkSprTypes", {
    "Auto": "Auto",
    "T_1": "1",
    "T_2": "2",
    "T_3": "3",
}).enum_type

MmioAbove4GbTypes = EnumWrapper("MmioAbove4GbTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MonitorMwaitTypes = EnumWrapper("MonitorMwaitTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MultiThreadedTypes = EnumWrapper("MultiThreadedTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Ndc1PcieLink1Types = EnumWrapper("Ndc1PcieLink1Types", {
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

Ndc1PcieLink2Types = EnumWrapper("Ndc1PcieLink2Types", {
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

Ndc1PcieLink3Types = EnumWrapper("Ndc1PcieLink3Types", {
    "DisabledOs": "DisabledOs",
    "Enabled": "Enabled",
}).enum_type

NdcConfigurationSpeedTypes = EnumWrapper("NdcConfigurationSpeedTypes", {
    "Auto": "Auto",
    "Gen1": "Gen1",
    "Gen2": "Gen2",
    "Gen3": "Gen3",
}).enum_type

NewSetupPasswordTypes = EnumWrapper("NewSetupPasswordTypes", {
    "N_A": "N/A",
}).enum_type

NewSysPasswordTypes = EnumWrapper("NewSysPasswordTypes", {
    "N_A": "N/A",
}).enum_type

NmiButtonTypes = EnumWrapper("NmiButtonTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NodeInterleaveTypes = EnumWrapper("NodeInterleaveTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NumLockTypes = EnumWrapper("NumLockTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

NvdimmFactoryDefault0Types = EnumWrapper("NvdimmFactoryDefault0Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault10Types = EnumWrapper("NvdimmFactoryDefault10Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault11Types = EnumWrapper("NvdimmFactoryDefault11Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault1Types = EnumWrapper("NvdimmFactoryDefault1Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault2Types = EnumWrapper("NvdimmFactoryDefault2Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault3Types = EnumWrapper("NvdimmFactoryDefault3Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault4Types = EnumWrapper("NvdimmFactoryDefault4Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault5Types = EnumWrapper("NvdimmFactoryDefault5Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault6Types = EnumWrapper("NvdimmFactoryDefault6Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault7Types = EnumWrapper("NvdimmFactoryDefault7Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault8Types = EnumWrapper("NvdimmFactoryDefault8Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefault9Types = EnumWrapper("NvdimmFactoryDefault9Types", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmFactoryDefaultTypes = EnumWrapper("NvdimmFactoryDefaultTypes", {
    "NvdimmFactoryDefaultDisable": "NvdimmFactoryDefaultDisable",
    "NvdimmFactoryDefaultEnable": "NvdimmFactoryDefaultEnable",
}).enum_type

NvdimmInterleaveSupportTypes = EnumWrapper("NvdimmInterleaveSupportTypes", {
    "NvdimmInterleaveDisable": "NvdimmInterleaveDisable",
    "NvdimmInterleaveEnable": "NvdimmInterleaveEnable",
}).enum_type

NvdimmReadOnlyTypes = EnumWrapper("NvdimmReadOnlyTypes", {
    "NvdimmReadOnlyDisable_": "NvdimmReadOnlyDisable:",
    "NvdimmReadOnlyEnable": "NvdimmReadOnlyEnable",
}).enum_type

NvmeModeTypes = EnumWrapper("NvmeModeTypes", {
    "NonRaid": "NonRaid",
    "Raid": "Raid",
}).enum_type

OldSetupPasswordTypes = EnumWrapper("OldSetupPasswordTypes", {
    "N_A": "N/A",
}).enum_type

OldSysPasswordTypes = EnumWrapper("OldSysPasswordTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeBiosBootSeqTypes = EnumWrapper("OneTimeBiosBootSeqTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeBootModeTypes = EnumWrapper("OneTimeBootModeTypes", {
    "Disabled": "Disabled",
    "OneTimeBootSeq": "OneTimeBootSeq",
    "OneTimeCustomBootSeqStr": "OneTimeCustomBootSeqStr",
    "OneTimeCustomHddSeqStr": "OneTimeCustomHddSeqStr",
    "OneTimeCustomUefiBootSeqStr": "OneTimeCustomUefiBootSeqStr",
    "OneTimeHddSeq": "OneTimeHddSeq",
    "OneTimeUefiBootSeq": "OneTimeUefiBootSeq",
}).enum_type

OneTimeBootSeqDevTypes = EnumWrapper("OneTimeBootSeqDevTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeCustomBootStrTypes = EnumWrapper("OneTimeCustomBootStrTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeHddSeqDevTypes = EnumWrapper("OneTimeHddSeqDevTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeHddSeqTypes = EnumWrapper("OneTimeHddSeqTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeUefiBootPathTypes = EnumWrapper("OneTimeUefiBootPathTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeUefiBootSeqDevTypes = EnumWrapper("OneTimeUefiBootSeqDevTypes", {
    "N_A": "N/A",
}).enum_type

OneTimeUefiBootSeqTypes = EnumWrapper("OneTimeUefiBootSeqTypes", {
    "N_A": "N/A",
}).enum_type

OppSrefEnTypes = EnumWrapper("OppSrefEnTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

OsWatchdogTimerTypes = EnumWrapper("OsWatchdogTimerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PCIeErrorInjectionTypes = EnumWrapper("PCIeErrorInjectionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PCIeLiveErrorRecoveryTypes = EnumWrapper("PCIeLiveErrorRecoveryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PPRErrInjectionTestTypes = EnumWrapper("PPRErrInjectionTestTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PasswordStatusTypes = EnumWrapper("PasswordStatusTypes", {
    "Locked": "Locked",
    "Unlocked": "Unlocked",
}).enum_type

PcieAspmL1Types = EnumWrapper("PcieAspmL1Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PerfMonitorDevicesTypes = EnumWrapper("PerfMonitorDevicesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PersistentMemoryModeTypes = EnumWrapper("PersistentMemoryModeTypes", {
    "NVDIMM": "NVDIMM",
    "PersistentMemoryOff": "PersistentMemoryOff",
}).enum_type

PersistentMemoryScrubbingTypes = EnumWrapper("PersistentMemoryScrubbingTypes", {
    "Auto": "Auto",
    "Enable": "Enable",
    "OneShot": "OneShot",
}).enum_type

PostPackageRepairTypes = EnumWrapper("PostPackageRepairTypes", {
    "Disabled": "Disabled",
    "HardPPR": "HardPPR",
    "SoftPPR": "SoftPPR",
    "SystemPPR": "SystemPPR",
}).enum_type

PowerCycleRequestTypes = EnumWrapper("PowerCycleRequestTypes", {
    "T_None": "None",
    "VirtualAC": "VirtualAC",
}).enum_type

PowerDeliveryTypes = EnumWrapper("PowerDeliveryTypes", {
    "MaxReliability": "MaxReliability",
    "MinPwr": "MinPwr",
}).enum_type

PowerMgmtTypes = EnumWrapper("PowerMgmtTypes", {
    "ActivePwrCtrl": "ActivePwrCtrl",
    "Custom": "Custom",
    "MaxPerf": "MaxPerf",
    "OsCtrl": "OsCtrl",
}).enum_type

PowerSaverTypes = EnumWrapper("PowerSaverTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Proc1BrandTypes = EnumWrapper("Proc1BrandTypes", {
    "N_A": "N/A",
}).enum_type

Proc1ControlledTurboTypes = EnumWrapper("Proc1ControlledTurboTypes", {
    "ControlledTurboLimit": "ControlledTurboLimit",
    "ControlledTurboLimitMinus1": "ControlledTurboLimitMinus1",
    "ControlledTurboLimitMinus2": "ControlledTurboLimitMinus2",
    "ControlledTurboLimitMinus3": "ControlledTurboLimitMinus3",
    "Disabled": "Disabled",
}).enum_type

Proc1CoresTypes = EnumWrapper("Proc1CoresTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc1IdTypes = EnumWrapper("Proc1IdTypes", {
    "N_A": "N/A",
}).enum_type

Proc1L2CacheTypes = EnumWrapper("Proc1L2CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc1L3CacheTypes = EnumWrapper("Proc1L3CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc1NumCoresTypes = EnumWrapper("Proc1NumCoresTypes", {
    "N_A": "N/A",
}).enum_type

Proc1TurboCoreNumTypes = EnumWrapper("Proc1TurboCoreNumTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc2BrandTypes = EnumWrapper("Proc2BrandTypes", {
    "N_A": "N/A",
}).enum_type

Proc2ControlledTurboTypes = EnumWrapper("Proc2ControlledTurboTypes", {
    "ControlledTurboLimit": "ControlledTurboLimit",
    "ControlledTurboLimitMinus1": "ControlledTurboLimitMinus1",
    "ControlledTurboLimitMinus2": "ControlledTurboLimitMinus2",
    "ControlledTurboLimitMinus3": "ControlledTurboLimitMinus3",
    "Disabled": "Disabled",
}).enum_type

Proc2CoresTypes = EnumWrapper("Proc2CoresTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc2IdTypes = EnumWrapper("Proc2IdTypes", {
    "N_A": "N/A",
}).enum_type

Proc2L2CacheTypes = EnumWrapper("Proc2L2CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc2L3CacheTypes = EnumWrapper("Proc2L3CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc2NumCoresTypes = EnumWrapper("Proc2NumCoresTypes", {
    "N_A": "N/A",
}).enum_type

Proc2TurboCoreNumTypes = EnumWrapper("Proc2TurboCoreNumTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc3BrandTypes = EnumWrapper("Proc3BrandTypes", {
    "N_A": "N/A",
}).enum_type

Proc3ControlledTurboTypes = EnumWrapper("Proc3ControlledTurboTypes", {
    "ControlledTurboLimit": "ControlledTurboLimit",
    "ControlledTurboLimitMinus1": "ControlledTurboLimitMinus1",
    "ControlledTurboLimitMinus2": "ControlledTurboLimitMinus2",
    "ControlledTurboLimitMinus3": "ControlledTurboLimitMinus3",
    "Disabled": "Disabled",
}).enum_type

Proc3CoresTypes = EnumWrapper("Proc3CoresTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc3IdTypes = EnumWrapper("Proc3IdTypes", {
    "N_A": "N/A",
}).enum_type

Proc3L2CacheTypes = EnumWrapper("Proc3L2CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc3L3CacheTypes = EnumWrapper("Proc3L3CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc3NumCoresTypes = EnumWrapper("Proc3NumCoresTypes", {
    "N_A": "N/A",
}).enum_type

Proc3TurboCoreNumTypes = EnumWrapper("Proc3TurboCoreNumTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc4BrandTypes = EnumWrapper("Proc4BrandTypes", {
    "N_A": "N/A",
}).enum_type

Proc4ControlledTurboTypes = EnumWrapper("Proc4ControlledTurboTypes", {
    "ControlledTurboLimit": "ControlledTurboLimit",
    "ControlledTurboLimitMinus1": "ControlledTurboLimitMinus1",
    "ControlledTurboLimitMinus2": "ControlledTurboLimitMinus2",
    "ControlledTurboLimitMinus4": "ControlledTurboLimitMinus4",
    "Disabled": "Disabled",
}).enum_type

Proc4CoresTypes = EnumWrapper("Proc4CoresTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc4IdTypes = EnumWrapper("Proc4IdTypes", {
    "N_A": "N/A",
}).enum_type

Proc4L2CacheTypes = EnumWrapper("Proc4L2CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc4L3CacheTypes = EnumWrapper("Proc4L3CacheTypes", {
    "N_A": "N/A",
}).enum_type

Proc4NumCoresTypes = EnumWrapper("Proc4NumCoresTypes", {
    "N_A": "N/A",
}).enum_type

Proc4TurboCoreNumTypes = EnumWrapper("Proc4TurboCoreNumTypes", {
    "All": "All",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

Proc64bitTypes = EnumWrapper("Proc64bitTypes", {
    "N_A": "N/A",
}).enum_type

ProcATSTypes = EnumWrapper("ProcATSTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcAdjCacheLineTypes = EnumWrapper("ProcAdjCacheLineTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcBusSpeedTypes = EnumWrapper("ProcBusSpeedTypes", {
    "N_A": "N/A",
}).enum_type

ProcC1ETypes = EnumWrapper("ProcC1ETypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcCStatesTypes = EnumWrapper("ProcCStatesTypes", {
    "Autonomous": "Autonomous",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcConfigTdpTypes = EnumWrapper("ProcConfigTdpTypes", {
    "Level1": "Level1",
    "Level2": "Level2",
    "Nominal": "Nominal",
}).enum_type

ProcCoreSpeedTypes = EnumWrapper("ProcCoreSpeedTypes", {
    "N_A": "N/A",
}).enum_type

ProcCoresTypes = EnumWrapper("ProcCoresTypes", {
    "All": "All",
    "Custom": "Custom",
    "Dual": "Dual",
    "Quad": "Quad",
    "Single": "Single",
    "T_1": "1",
    "T_10": "10",
    "T_12": "12",
    "T_14": "14",
    "T_16": "16",
    "T_18": "18",
    "T_2": "2",
    "T_20": "20",
    "T_22": "22",
    "T_24": "24",
    "T_4": "4",
    "T_6": "6",
    "T_8": "8",
}).enum_type

ProcDpatProDebugTypes = EnumWrapper("ProcDpatProDebugTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcDramPrefetcherTypes = EnumWrapper("ProcDramPrefetcherTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcEmbMemModeTypes = EnumWrapper("ProcEmbMemModeTypes", {
    "Cache": "Cache",
    "Hybrid": "Hybrid",
    "Memory": "Memory",
}).enum_type

ProcExecuteDisableTypes = EnumWrapper("ProcExecuteDisableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcHpcModeTypes = EnumWrapper("ProcHpcModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcHtAssistTypes = EnumWrapper("ProcHtAssistTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcHwPrefetcherTypes = EnumWrapper("ProcHwPrefetcherTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcHyperTransportTypes = EnumWrapper("ProcHyperTransportTypes", {
    "HT1": "HT1",
    "HT3": "HT3",
}).enum_type

ProcMtrrPatDebugTypes = EnumWrapper("ProcMtrrPatDebugTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcPwrPerfTypes = EnumWrapper("ProcPwrPerfTypes", {
    "HwpDbpm": "HwpDbpm",
    "MaxPerf": "MaxPerf",
    "MinPwr": "MinPwr",
    "OsDbpm": "OsDbpm",
    "SysDbpm": "SysDbpm",
}).enum_type

ProcSoftwarePrefetcherTypes = EnumWrapper("ProcSoftwarePrefetcherTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcTurboModeTypes = EnumWrapper("ProcTurboModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcVirtualizationTypes = EnumWrapper("ProcVirtualizationTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ProcX2ApicTypes = EnumWrapper("ProcX2ApicTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PwrButtonTypes = EnumWrapper("PwrButtonTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev1EnDisTypes = EnumWrapper("PxeDev1EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev1ProtocolTypes = EnumWrapper("PxeDev1ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

PxeDev1VlanEnDisTypes = EnumWrapper("PxeDev1VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev2EnDisTypes = EnumWrapper("PxeDev2EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev2ProtocolTypes = EnumWrapper("PxeDev2ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

PxeDev2VlanEnDisTypes = EnumWrapper("PxeDev2VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev3EnDisTypes = EnumWrapper("PxeDev3EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev3ProtocolTypes = EnumWrapper("PxeDev3ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

PxeDev3VlanEnDisTypes = EnumWrapper("PxeDev3VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev4EnDisTypes = EnumWrapper("PxeDev4EnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PxeDev4ProtocolTypes = EnumWrapper("PxeDev4ProtocolTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

PxeDev4VlanEnDisTypes = EnumWrapper("PxeDev4VlanEnDisTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

QpiBandwidthPriorityTypes = EnumWrapper("QpiBandwidthPriorityTypes", {
    "Compute": "Compute",
    "InputOutput": "InputOutput",
}).enum_type

QpiSpeedTypes = EnumWrapper("QpiSpeedTypes", {
    "MaxDataRate": "MaxDataRate",
    "T_6GTps": "6GTps",
    "T_7GTps": "7GTps",
    "T_8GTps": "8GTps",
    "T_9GTps": "9GTps",
}).enum_type

RebootTestCountTypes = EnumWrapper("RebootTestCountTypes", {
    "N_A": "N/A",
}).enum_type

RebootTestModeTypes = EnumWrapper("RebootTestModeTypes", {
    "RebootTestModeCold": "RebootTestModeCold",
    "RebootTestModeOff": "RebootTestModeOff",
    "RebootTestModePowerCycle": "RebootTestModePowerCycle",
}).enum_type

RebootTestPointTypes = EnumWrapper("RebootTestPointTypes", {
    "RebootTestPointMemInit": "RebootTestPointMemInit",
    "RebootTestPointPciInit": "RebootTestPointPciInit",
}).enum_type

RedirAfterBootTypes = EnumWrapper("RedirAfterBootTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RedundantMemCfgValidTypes = EnumWrapper("RedundantMemCfgValidTypes", {
    "Invalid": "Invalid",
    "Valid": "Valid",
}).enum_type

RedundantMemInUseTypes = EnumWrapper("RedundantMemInUseTypes", {
    "InUse": "InUse",
    "NotInUse": "NotInUse",
}).enum_type

RedundantMemTypes = EnumWrapper("RedundantMemTypes", {
    "Dddc": "Dddc",
    "DimmSpare": "DimmSpare",
    "Disabled": "Disabled",
    "IntraNodeMirror": "IntraNodeMirror",
    "Mirror": "Mirror",
    "Spare": "Spare",
}).enum_type

RedundantOsBootTypes = EnumWrapper("RedundantOsBootTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RedundantOsLocationTypes = EnumWrapper("RedundantOsLocationTypes", {
    "InternalSd": "InternalSd",
    "InternalUsb": "InternalUsb",
    "PortA": "PortA",
    "PortB": "PortB",
    "PortC": "PortC",
    "PortD": "PortD",
    "PortE": "PortE",
    "PortF": "PortF",
    "PortG": "PortG",
    "PortH": "PortH",
    "PortI": "PortI",
    "PortJ": "PortJ",
    "PortK": "PortK",
    "PortL": "PortL",
    "PortM": "PortM",
    "PortN": "PortN",
    "Slot1": "Slot1",
    "Slot2": "Slot2",
    "Slot3": "Slot3",
    "Slot4": "Slot4",
    "Slot5": "Slot5",
    "Slot6": "Slot6",
    "Slot7": "Slot7",
    "Slot8": "Slot8",
    "Slot9_____14": "Slot9 ... 14",
    "T_None": "None",
}).enum_type

RedundantOsStateTypes = EnumWrapper("RedundantOsStateTypes", {
    "Hidden": "Hidden",
    "Visible": "Visible",
}).enum_type

ReportKbdErrTypes = EnumWrapper("ReportKbdErrTypes", {
    "NoReport": "NoReport",
    "Report": "Report",
}).enum_type

RipsPresenceTypes = EnumWrapper("RipsPresenceTypes", {
    "RipsPresenceNo": "RipsPresenceNo",
    "RipsPresenceYes": "RipsPresenceYes",
}).enum_type

RtidSettingTypes = EnumWrapper("RtidSettingTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

S4SupportDebugTypes = EnumWrapper("S4SupportDebugTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SHA256SetupPasswordSaltTypes = EnumWrapper("SHA256SetupPasswordSaltTypes", {
    "N_A": "N/A",
}).enum_type

SHA256SetupPasswordTypes = EnumWrapper("SHA256SetupPasswordTypes", {
    "N_A": "N/A",
}).enum_type

SHA256SystemPasswordSaltTypes = EnumWrapper("SHA256SystemPasswordSaltTypes", {
    "N_A": "N/A",
}).enum_type

SHA256SystemPasswordTypes = EnumWrapper("SHA256SystemPasswordTypes", {
    "N_A": "N/A",
}).enum_type

SNCTypes = EnumWrapper("SNCTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SataPortACapacityTypes = EnumWrapper("SataPortACapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortADriveTypeTypes = EnumWrapper("SataPortADriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortAModelTypes = EnumWrapper("SataPortAModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortATypes = EnumWrapper("SataPortATypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortBCapacityTypes = EnumWrapper("SataPortBCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortBDriveTypeTypes = EnumWrapper("SataPortBDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortBModelTypes = EnumWrapper("SataPortBModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortBTypes = EnumWrapper("SataPortBTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortCCapacityTypes = EnumWrapper("SataPortCCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortCDriveTypeTypes = EnumWrapper("SataPortCDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortCModelTypes = EnumWrapper("SataPortCModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortCTypes = EnumWrapper("SataPortCTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortDCapacityTypes = EnumWrapper("SataPortDCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortDDriveTypeTypes = EnumWrapper("SataPortDDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortDModelTypes = EnumWrapper("SataPortDModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortDTypes = EnumWrapper("SataPortDTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortECapacityTypes = EnumWrapper("SataPortECapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortEDriveTypeTypes = EnumWrapper("SataPortEDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortEModelTypes = EnumWrapper("SataPortEModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortETypes = EnumWrapper("SataPortETypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortFCapacityTypes = EnumWrapper("SataPortFCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortFDriveTypeTypes = EnumWrapper("SataPortFDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortFModelTypes = EnumWrapper("SataPortFModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortFTypes = EnumWrapper("SataPortFTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortGCapacityTypes = EnumWrapper("SataPortGCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortGDriveTypeTypes = EnumWrapper("SataPortGDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortGModelTypes = EnumWrapper("SataPortGModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortGTypes = EnumWrapper("SataPortGTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortHCapacityTypes = EnumWrapper("SataPortHCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortHDriveTypeTypes = EnumWrapper("SataPortHDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortHModelTypes = EnumWrapper("SataPortHModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortHTypes = EnumWrapper("SataPortHTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortICapacityTypes = EnumWrapper("SataPortICapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortIDriveTypeTypes = EnumWrapper("SataPortIDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortIModelTypes = EnumWrapper("SataPortIModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortITypes = EnumWrapper("SataPortITypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortJCapacityTypes = EnumWrapper("SataPortJCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortJDriveTypeTypes = EnumWrapper("SataPortJDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortJModelTypes = EnumWrapper("SataPortJModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortJTypes = EnumWrapper("SataPortJTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortKCapacityTypes = EnumWrapper("SataPortKCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortKDriveTypeTypes = EnumWrapper("SataPortKDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortKModelTypes = EnumWrapper("SataPortKModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortKTypes = EnumWrapper("SataPortKTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortLCapacityTypes = EnumWrapper("SataPortLCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortLDriveTypeTypes = EnumWrapper("SataPortLDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortLModelTypes = EnumWrapper("SataPortLModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortLTypes = EnumWrapper("SataPortLTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortMCapacityTypes = EnumWrapper("SataPortMCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortMDriveTypeTypes = EnumWrapper("SataPortMDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortMModelTypes = EnumWrapper("SataPortMModelTypes", {
    "N_A": "N/A",
}).enum_type

SataPortMTypes = EnumWrapper("SataPortMTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SataPortNCapacityTypes = EnumWrapper("SataPortNCapacityTypes", {
    "N_A": "N/A",
}).enum_type

SataPortNDriveTypeTypes = EnumWrapper("SataPortNDriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

SataPortNModelTypes = EnumWrapper("SataPortNModelTypes", {
    "N_A": "N/A",
    "SATA_MODEL": "SATA_MODEL",
}).enum_type

SataPortNTypes = EnumWrapper("SataPortNTypes", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type

SccDebugEnabledTypes = EnumWrapper("SccDebugEnabledTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SecureBootModeTypes = EnumWrapper("SecureBootModeTypes", {
    "AuditMode": "AuditMode",
    "DeployedMode": "DeployedMode",
    "SetupMode": "SetupMode",
    "UserMode": "UserMode",
}).enum_type

SecureBootPolicyTypes = EnumWrapper("SecureBootPolicyTypes", {
    "Custom": "Custom",
    "Standard": "Standard",
}).enum_type

SecureBootTypes = EnumWrapper("SecureBootTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SecurityFreezeLockTypes = EnumWrapper("SecurityFreezeLockTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SerialCommTypes = EnumWrapper("SerialCommTypes", {
    "Off": "Off",
    "OnConRedir": "OnConRedir",
    "OnConRedirAuto": "OnConRedirAuto",
    "OnConRedirCom1": "OnConRedirCom1",
    "OnConRedirCom2": "OnConRedirCom2",
    "OnNoConRedir": "OnNoConRedir",
}).enum_type

SerialPortAddressTypes = EnumWrapper("SerialPortAddressTypes", {
    "Com1": "Com1",
    "Com2": "Com2",
    "Serial1Com1Serial2Com2": "Serial1Com1Serial2Com2",
    "Serial1Com2Serial2Com1": "Serial1Com2Serial2Com1",
}).enum_type

SetBootOrderFqdd10Types = EnumWrapper("SetBootOrderFqdd10Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd11Types = EnumWrapper("SetBootOrderFqdd11Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd12Types = EnumWrapper("SetBootOrderFqdd12Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd13Types = EnumWrapper("SetBootOrderFqdd13Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd14Types = EnumWrapper("SetBootOrderFqdd14Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd15Types = EnumWrapper("SetBootOrderFqdd15Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd16Types = EnumWrapper("SetBootOrderFqdd16Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd1Types = EnumWrapper("SetBootOrderFqdd1Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd2Types = EnumWrapper("SetBootOrderFqdd2Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd3Types = EnumWrapper("SetBootOrderFqdd3Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd4Types = EnumWrapper("SetBootOrderFqdd4Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd5Types = EnumWrapper("SetBootOrderFqdd5Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd6Types = EnumWrapper("SetBootOrderFqdd6Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd7Types = EnumWrapper("SetBootOrderFqdd7Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd8Types = EnumWrapper("SetBootOrderFqdd8Types", {
    "N_A": "N/A",
}).enum_type

SetBootOrderFqdd9Types = EnumWrapper("SetBootOrderFqdd9Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd10Types = EnumWrapper("SetLegacyHddOrderFqdd10Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd11Types = EnumWrapper("SetLegacyHddOrderFqdd11Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd12Types = EnumWrapper("SetLegacyHddOrderFqdd12Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd13Types = EnumWrapper("SetLegacyHddOrderFqdd13Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd14Types = EnumWrapper("SetLegacyHddOrderFqdd14Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd15Types = EnumWrapper("SetLegacyHddOrderFqdd15Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd16Types = EnumWrapper("SetLegacyHddOrderFqdd16Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd1Types = EnumWrapper("SetLegacyHddOrderFqdd1Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd2Types = EnumWrapper("SetLegacyHddOrderFqdd2Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd3Types = EnumWrapper("SetLegacyHddOrderFqdd3Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd4Types = EnumWrapper("SetLegacyHddOrderFqdd4Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd5Types = EnumWrapper("SetLegacyHddOrderFqdd5Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd6Types = EnumWrapper("SetLegacyHddOrderFqdd6Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd7Types = EnumWrapper("SetLegacyHddOrderFqdd7Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd8Types = EnumWrapper("SetLegacyHddOrderFqdd8Types", {
    "N_A": "N/A",
}).enum_type

SetLegacyHddOrderFqdd9Types = EnumWrapper("SetLegacyHddOrderFqdd9Types", {
    "N_A": "N/A",
}).enum_type

SetupPasswordTypes = EnumWrapper("SetupPasswordTypes", {
    "N_A": "N/A",
}).enum_type

SignedFirmwareUpdateTypes = EnumWrapper("SignedFirmwareUpdateTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot10BifTypes = EnumWrapper("Slot10BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot10Types = EnumWrapper("Slot10Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot11BifTypes = EnumWrapper("Slot11BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot11Types = EnumWrapper("Slot11Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot12BifTypes = EnumWrapper("Slot12BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot12Types = EnumWrapper("Slot12Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot13BifTypes = EnumWrapper("Slot13BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot13Types = EnumWrapper("Slot13Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot14BifTypes = EnumWrapper("Slot14BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot1BifTypes = EnumWrapper("Slot1BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot1Types = EnumWrapper("Slot1Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot2BifTypes = EnumWrapper("Slot2BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot2Types = EnumWrapper("Slot2Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot3BifTypes = EnumWrapper("Slot3BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot3Types = EnumWrapper("Slot3Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot4BifTypes = EnumWrapper("Slot4BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot4Types = EnumWrapper("Slot4Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot5BifTypes = EnumWrapper("Slot5BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot5Types = EnumWrapper("Slot5Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot6BifTypes = EnumWrapper("Slot6BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot6Types = EnumWrapper("Slot6Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot7BifTypes = EnumWrapper("Slot7BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot7Types = EnumWrapper("Slot7Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot8BifTypes = EnumWrapper("Slot8BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot8Types = EnumWrapper("Slot8Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Slot9BifTypes = EnumWrapper("Slot9BifTypes", {
    "DefaultBifurcation": "DefaultBifurcation",
    "Allx16": "Allx16",
    "Allx4": "Allx4",
    "Allx8": "Allx8",
    "x4x4x8": "x4x4x8",
    "x8x4x4": "x8x4x4",
}).enum_type

Slot9Types = EnumWrapper("Slot9Types", {
    "BootDriverDisabled": "BootDriverDisabled",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SnoopFilterTypes = EnumWrapper("SnoopFilterTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SnoopModeTypes = EnumWrapper("SnoopModeTypes", {
    "ClusterOnDie": "ClusterOnDie",
    "EarlySnoop": "EarlySnoop",
    "HomeSnoop": "HomeSnoop",
    "OpportunisticSnoopBroadcast": "OpportunisticSnoopBroadcast",
}).enum_type

SrefProgrammingTypes = EnumWrapper("SrefProgrammingTypes", {
    "Auto": "Auto",
    "Manual": "Manual",
}).enum_type

SriovGlobalEnableTypes = EnumWrapper("SriovGlobalEnableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SubNumaClusterTypes = EnumWrapper("SubNumaClusterTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SysMemSizeTypes = EnumWrapper("SysMemSizeTypes", {
    "N_A": "N/A",
}).enum_type

SysMemSpeedTypes = EnumWrapper("SysMemSpeedTypes", {
    "N_A": "N/A",
}).enum_type

SysMemTypeTypes = EnumWrapper("SysMemTypeTypes", {
    "N_A": "N/A",
}).enum_type

SysMemVoltTypes = EnumWrapper("SysMemVoltTypes", {
    "N_A": "N/A",
}).enum_type

SysMfrContactInfoTypes = EnumWrapper("SysMfrContactInfoTypes", {
    "N_A": "N/A",
}).enum_type

SysMgmtNVByte1Types = EnumWrapper("SysMgmtNVByte1Types", {
    "N_A": "N/A",
}).enum_type

SysMgmtNVByte2Types = EnumWrapper("SysMgmtNVByte2Types", {
    "N_A": "N/A",
}).enum_type

SysPasswordTypes = EnumWrapper("SysPasswordTypes", {
    "N_A": "N/A",
}).enum_type

SysProfileTypes = EnumWrapper("SysProfileTypes", {
    "Custom": "Custom",
    "DenseCfgOptimized": "DenseCfgOptimized",
    "PerfOptimized": "PerfOptimized",
    "PerfOptimizedHwp": "PerfOptimizedHwp",
    "PerfPerWattOptimizedDapc": "PerfPerWattOptimizedDapc",
    "PerfPerWattOptimizedOs": "PerfPerWattOptimizedOs",
    "PerfWorkStationOptimized": "PerfWorkStationOptimized",
}).enum_type

SystemBiosVersionTypes = EnumWrapper("SystemBiosVersionTypes", {
    "N_A": "N/A",
}).enum_type

SystemCpldVersionTypes = EnumWrapper("SystemCpldVersionTypes", {
    "N_A": "N/A",
}).enum_type

SystemManufacturerTypes = EnumWrapper("SystemManufacturerTypes", {
    "N_A": "N/A",
}).enum_type

SystemMeVersionTypes = EnumWrapper("SystemMeVersionTypes", {
    "N_A": "N/A",
}).enum_type

SystemMemoryModelTypes = EnumWrapper("SystemMemoryModelTypes", {
    "All2All": "All2All",
    "Hemisphere": "Hemisphere",
    "Quadrant": "Quadrant",
    "SNC_2": "SNC-2",
    "SNC_4": "SNC-4",
}).enum_type

SystemModelNameTypes = EnumWrapper("SystemModelNameTypes", {
    "N_A": "N/A",
}).enum_type

SystemServiceTagTypes = EnumWrapper("SystemServiceTagTypes", {
    "N_A": "N/A",
}).enum_type

SystemUefiShellTypes = EnumWrapper("SystemUefiShellTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TXEQWATypes = EnumWrapper("TXEQWATypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TcmActivationTypes = EnumWrapper("TcmActivationTypes", {
    "Activate": "Activate",
    "Deactivate": "Deactivate",
    "NoChange": "NoChange",
}).enum_type

TcmClearTypes = EnumWrapper("TcmClearTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

TcmSecurityTypes = EnumWrapper("TcmSecurityTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

Tpm2AlgorithmTypes = EnumWrapper("Tpm2AlgorithmTypes", {
    "SHA1": "SHA1",
    "SHA256": "SHA256",
    "SHA384": "SHA384",
    "SHA512": "SHA512",
    "SM3": "SM3",
}).enum_type

Tpm2HierarchyTypes = EnumWrapper("Tpm2HierarchyTypes", {
    "Clear": "Clear",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TpmActivationTypes = EnumWrapper("TpmActivationTypes", {
    "Activate": "Activate",
    "Deactivate": "Deactivate",
    "NoChange": "NoChange",
}).enum_type

TpmBindingResetTypes = EnumWrapper("TpmBindingResetTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

TpmClearTypes = EnumWrapper("TpmClearTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

TpmCommandTypes = EnumWrapper("TpmCommandTypes", {
    "Activate": "Activate",
    "Clear": "Clear",
    "Deactivate": "Deactivate",
    "T_None": "None",
}).enum_type

TpmPpiBypassClearTypes = EnumWrapper("TpmPpiBypassClearTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TpmPpiBypassProvisionTypes = EnumWrapper("TpmPpiBypassProvisionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TpmSecurityTypes = EnumWrapper("TpmSecurityTypes", {
    "Off": "Off",
    "On": "On",
    "OnNoPbm": "OnNoPbm",
    "OnPbm": "OnPbm",
}).enum_type

TpmStatusTypes = EnumWrapper("TpmStatusTypes", {
    "N_A": "N/A",
}).enum_type

TraceHubDebugTypes = EnumWrapper("TraceHubDebugTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

UefiComplianceVersionTypes = EnumWrapper("UefiComplianceVersionTypes", {
    "N_A": "N/A",
}).enum_type

UefiPxeIpVersionTypes = EnumWrapper("UefiPxeIpVersionTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

UefiVariableAccessTypes = EnumWrapper("UefiVariableAccessTypes", {
    "Controlled": "Controlled",
    "Standard": "Standard",
}).enum_type

UncoreFrequencyTypes = EnumWrapper("UncoreFrequencyTypes", {
    "DynamicUFS": "DynamicUFS",
    "MaxUFS": "MaxUFS",
}).enum_type

UnusedPcieClkTypes = EnumWrapper("UnusedPcieClkTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Usb3SettingTypes = EnumWrapper("Usb3SettingTypes", {
    "Auto": "Auto",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

UsbManagedPortTypes = EnumWrapper("UsbManagedPortTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

UsbPortsTypes = EnumWrapper("UsbPortsTypes", {
    "AllOff": "AllOff",
    "AllOffDynamic": "AllOffDynamic",
    "AllOn": "AllOn",
    "OnlyBackPortsOn": "OnlyBackPortsOn",
}).enum_type

UserLcdStrTypes = EnumWrapper("UserLcdStrTypes", {
    "N_A": "N/A",
}).enum_type

VideoMemTypes = EnumWrapper("VideoMemTypes", {
    "N_A": "N/A",
}).enum_type

WorkloadProfileTypes = EnumWrapper("WorkloadProfileTypes", {
    "DbOptimizedProfile": "DbOptimizedProfile",
    "DbPerWattOptimizedProfile": "DbPerWattOptimizedProfile",
    "HpcProfile": "HpcProfile",
    "LowLatencyOptimizedProfile": "LowLatencyOptimizedProfile",
    "NotAvailable": "NotAvailable",
    "SdsOptimizedProfile": "SdsOptimizedProfile",
    "SdsPerWattOptimizedProfile": "SdsPerWattOptimizedProfile",
    "VtOptimizedProfile": "VtOptimizedProfile",
    "VtPerWattOptimizedProfile": "VtPerWattOptimizedProfile",
}).enum_type

WriteCacheTypes = EnumWrapper("WriteCacheTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WriteDataCrcTypes = EnumWrapper("WriteDataCrcTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

eSataPort1CapacityTypes = EnumWrapper("eSataPort1CapacityTypes", {
    "N_A": "N/A",
}).enum_type

eSataPort1DriveTypeTypes = EnumWrapper("eSataPort1DriveTypeTypes", {
    "N_A": "N/A",
}).enum_type

eSataPort1ModelTypes = EnumWrapper("eSataPort1ModelTypes", {
    "N_A": "N/A",
}).enum_type

eSataPort1Types = EnumWrapper("eSataPort1Types", {
    "Auto": "Auto",
    "Off": "Off",
}).enum_type
