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

AddressingModeTypes = EnumWrapper("AddressingModeTypes", {
    "FPMA": "FPMA",
    "SPMA": "SPMA",
}).enum_type

BootOptionROMTypes = EnumWrapper("BootOptionROMTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BootRetryCntTypes = EnumWrapper("BootRetryCntTypes", {
    "IndefiniteRetries": "IndefiniteRetries",
    "NoRetry": "NoRetry",
    "T_1Retry": "1Retry",
    "T_2Retries": "2Retries",
    "T_3Retries": "3Retries",
    "T_4Retries": "4Retries",
    "T_5Retries": "5Retries",
    "T_6Retries": "6Retries",
}).enum_type

BootStrapTypeTypes = EnumWrapper("BootStrapTypeTypes", {
    "AutoDetect": "AutoDetect",
    "BBS": "BBS",
    "Int18h": "Int18h",
    "Int19h": "Int19h",
}).enum_type

ChapAuthEnableTypes = EnumWrapper("ChapAuthEnableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ChapMutualAuthTypes = EnumWrapper("ChapMutualAuthTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ConfigureLogicalPortsSupportTypes = EnumWrapper("ConfigureLogicalPortsSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

CongestionNotificationTypes = EnumWrapper("CongestionNotificationTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

ConnectFirstFCoETargetTypes = EnumWrapper("ConnectFirstFCoETargetTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ConnectFirstTgtTypes = EnumWrapper("ConnectFirstTgtTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ConnectSecondTgtTypes = EnumWrapper("ConnectSecondTgtTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DCBXSupportTypes = EnumWrapper("DCBXSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

EEEControlTypes = EnumWrapper("EEEControlTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "varies": "varies",
}).enum_type

EVBModesSupportTypes = EnumWrapper("EVBModesSupportTypes", {
    "Multi_channel": "Multi-channel",
    "PE": "PE",
    "VEB": "VEB",
    "VEPA": "VEPA",
}).enum_type

EnergyEfficientEthernetTypes = EnumWrapper("EnergyEfficientEthernetTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

EnhancedTransmissionSelectionTypes = EnumWrapper("EnhancedTransmissionSelectionTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

FCoEBootScanSelectionTypes = EnumWrapper("FCoEBootScanSelectionTypes", {
    "Disabled": "Disabled",
    "FabricDiscovered": "FabricDiscovered",
    "FirstLUN": "FirstLUN",
    "FirstLUN0": "FirstLUN0",
    "FirstNOTLUN0": "FirstNOTLUN0",
    "SpecifiedLUN": "SpecifiedLUN",
}).enum_type

FCoEBootSupportTypes = EnumWrapper("FCoEBootSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

FCoEFirstHddTargetTypes = EnumWrapper("FCoEFirstHddTargetTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FCoEOffloadModePartitionTypes = EnumWrapper("FCoEOffloadModePartitionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FCoEOffloadModeTypes = EnumWrapper("FCoEOffloadModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FCoEOffloadSupportTypes = EnumWrapper("FCoEOffloadSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

FCoETgtBootTypes = EnumWrapper("FCoETgtBootTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "OneTimeDisabled": "OneTimeDisabled",
}).enum_type

FeatureLicensingSupportTypes = EnumWrapper("FeatureLicensingSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

FirstHddTargetTypes = EnumWrapper("FirstHddTargetTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FirstTgtIpVerTypes = EnumWrapper("FirstTgtIpVerTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

FlexAddressingTypes = EnumWrapper("FlexAddressingTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

FlowControlSettingTypes = EnumWrapper("FlowControlSettingTypes", {
    "Auto": "Auto",
    "RXFlowControl": "RXFlowControl",
    "TXFlowControl": "TXFlowControl",
    "TXRXFlowControl": "TXRXFlowControl",
    "T_None": "None",
}).enum_type

HairpinModeTypes = EnumWrapper("HairpinModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HideSetupPromptTypes = EnumWrapper("HideSetupPromptTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IpAutoConfigTypes = EnumWrapper("IpAutoConfigTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IpVerTypes = EnumWrapper("IpVerTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
    "T_None": "None",
}).enum_type

IscsiTgtBootTypes = EnumWrapper("IscsiTgtBootTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "OneTimeDisabled": "OneTimeDisabled",
}).enum_type

IscsiVLanModeTypes = EnumWrapper("IscsiVLanModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IscsiViaDHCPTypes = EnumWrapper("IscsiViaDHCPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LegacyBootProtoTypes = EnumWrapper("LegacyBootProtoTypes", {
    "FCoE": "FCoE",
    "NONE": "NONE",
    "PXE": "PXE",
    "iSCSI": "iSCSI",
    "iSCSIPrimary": "iSCSIPrimary",
    "iSCSISecondary": "iSCSISecondary",
    "varies": "varies",
}).enum_type

LinkStatusTypes = EnumWrapper("LinkStatusTypes", {
    "Connected": "Connected",
    "Disconnected": "Disconnected",
}).enum_type

LnkSpeedTypes = EnumWrapper("LnkSpeedTypes", {
    "AutoNeg": "AutoNeg",
    "T_100Gbps": "100Gbps",
    "T_100MbpsFull": "100MbpsFull",
    "T_100MbpsHalf": "100MbpsHalf",
    "T_10Gbps": "10Gbps",
    "T_10MbpsFull": "10MbpsFull",
    "T_10MbpsHalf": "10MbpsHalf",
    "T_1Gbps": "1Gbps",
    "T_25Gbps": "25Gbps",
    "T_40Gbps": "40Gbps",
    "T_50Gbps": "50Gbps",
}).enum_type

LocalDCBXWillingModeTypes = EnumWrapper("LocalDCBXWillingModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LogicalPortEnableTypes = EnumWrapper("LogicalPortEnableTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MTUParamsTypes = EnumWrapper("MTUParamsTypes", {
    "Global": "Global",
    "PerDCBPriority": "PerDCBPriority",
    "PerVLAN": "PerVLAN",
}).enum_type

MTUReconfigurationSupportTypes = EnumWrapper("MTUReconfigurationSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

NPCPTypes = EnumWrapper("NPCPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NParEPTypes = EnumWrapper("NParEPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NWManagementPassThroughTypes = EnumWrapper("NWManagementPassThroughTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

NetworkPartitioningModeTypes = EnumWrapper("NetworkPartitioningModeTypes", {
    "SDP": "SDP",
    "SIP": "SIP",
}).enum_type

NicModePartitionTypes = EnumWrapper("NicModePartitionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Varies": "Varies",
}).enum_type

NicModeTypes = EnumWrapper("NicModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Varies": "Varies",
}).enum_type

NicPartitioningSupportTypes = EnumWrapper("NicPartitioningSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

NicPartitioningTypes = EnumWrapper("NicPartitioningTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

OSBMCManagementPassThroughTypes = EnumWrapper("OSBMCManagementPassThroughTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

OnChipThermalSensorTypes = EnumWrapper("OnChipThermalSensorTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

PXEBootSupportTypes = EnumWrapper("PXEBootSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

PartitionStateInterpretationTypes = EnumWrapper("PartitionStateInterpretationTypes", {
    "Fixed": "Fixed",
    "Variable": "Variable",
}).enum_type

PartitionStatePartitionTypes = EnumWrapper("PartitionStatePartitionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PriorityFlowControlTypes = EnumWrapper("PriorityFlowControlTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

PriorityGroup0ProtocolAssignmentTypes = EnumWrapper("PriorityGroup0ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup15ProtocolAssignmentTypes = EnumWrapper("PriorityGroup15ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup1ProtocolAssignmentTypes = EnumWrapper("PriorityGroup1ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup2ProtocolAssignmentTypes = EnumWrapper("PriorityGroup2ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup3ProtocolAssignmentTypes = EnumWrapper("PriorityGroup3ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup4ProtocolAssignmentTypes = EnumWrapper("PriorityGroup4ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup5ProtocolAssignmentTypes = EnumWrapper("PriorityGroup5ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup6ProtocolAssignmentTypes = EnumWrapper("PriorityGroup6ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

PriorityGroup7ProtocolAssignmentTypes = EnumWrapper("PriorityGroup7ProtocolAssignmentTypes", {
    "AllOtherLAN": "AllOtherLAN",
    "FCoE": "FCoE",
    "RoCE": "RoCE",
    "T_None": "None",
    "iSCSI": "iSCSI",
}).enum_type

RDMAApplicationProfileTypes = EnumWrapper("RDMAApplicationProfileTypes", {
    "HPCC": "HPCC",
    "RoCE1": "RoCE1",
    "RoCE2": "RoCE2",
    "Storage": "Storage",
}).enum_type

RDMANICModeOnPartitionPartitionTypes = EnumWrapper("RDMANICModeOnPartitionPartitionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Varies": "Varies",
}).enum_type

RDMANICModeOnPortTypes = EnumWrapper("RDMANICModeOnPortTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Varies": "Varies",
}).enum_type

RDMAProtocolSupportTypes = EnumWrapper("RDMAProtocolSupportTypes", {
    "RoCE": "RoCE",
    "iWARP": "iWARP",
    "iWARP_RoCE": "iWARP+RoCE",
}).enum_type

RDMASupportTypes = EnumWrapper("RDMASupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

RXFlowControlTypes = EnumWrapper("RXFlowControlTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

RemotePHYTypes = EnumWrapper("RemotePHYTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

SRIOVSupportTypes = EnumWrapper("SRIOVSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

SecondTgtIpVerTypes = EnumWrapper("SecondTgtIpVerTypes", {
    "IPv4": "IPv4",
    "IPv6": "IPv6",
}).enum_type

SwitchDepPartitioningSupportTypes = EnumWrapper("SwitchDepPartitioningSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

TOESupportTypes = EnumWrapper("TOESupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

TXBandwidthControlMaximumTypes = EnumWrapper("TXBandwidthControlMaximumTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

TXBandwidthControlMinimumTypes = EnumWrapper("TXBandwidthControlMinimumTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

TXFlowControlTypes = EnumWrapper("TXFlowControlTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

TcpIpViaDHCPTypes = EnumWrapper("TcpIpViaDHCPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TcpTimestmpTypes = EnumWrapper("TcpTimestmpTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TotalNumberLogicalPortsTypes = EnumWrapper("TotalNumberLogicalPortsTypes", {
    "T_2": "2",
    "T_8": "8",
}).enum_type

UseIndTgtNameTypes = EnumWrapper("UseIndTgtNameTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

UseIndTgtPortalTypes = EnumWrapper("UseIndTgtPortalTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

VFAllocBasisTypes = EnumWrapper("VFAllocBasisTypes", {
    "Device": "Device",
    "Port": "Port",
}).enum_type

VLanModeTypes = EnumWrapper("VLanModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

VirtualizationModeTypes = EnumWrapper("VirtualizationModeTypes", {
    "NONE": "NONE",
    "NPAR": "NPAR",
    "NPARSRIOV": "NPARSRIOV",
    "SRIOV": "SRIOV",
}).enum_type

WakeOnLanLnkSpeedTypes = EnumWrapper("WakeOnLanLnkSpeedTypes", {
    "AutoNeg": "AutoNeg",
    "T_100Gbps": "100Gbps",
    "T_100MbpsFull": "100MbpsFull",
    "T_100MbpsHalf": "100MbpsHalf",
    "T_10Gbps": "10Gbps",
    "T_10MbpsFull": "10MbpsFull",
    "T_10MbpsHalf": "10MbpsHalf",
    "T_1Gbps": "1Gbps",
    "T_25Gbps": "25Gbps",
    "T_40Gbps": "40Gbps",
    "T_50Gbps": "50Gbps",
}).enum_type

WakeOnLanTypes = EnumWrapper("WakeOnLanTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WinHbaBootModeTypes = EnumWrapper("WinHbaBootModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

iSCSIBootSupportTypes = EnumWrapper("iSCSIBootSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

iSCSIDualIPVersionSupportTypes = EnumWrapper("iSCSIDualIPVersionSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

iSCSIOffloadSupportTypes = EnumWrapper("iSCSIOffloadSupportTypes", {
    "Available": "Available",
    "Unavailable": "Unavailable",
}).enum_type

iScsiOffloadModePartitionTypes = EnumWrapper("iScsiOffloadModePartitionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

iScsiOffloadModeTypes = EnumWrapper("iScsiOffloadModeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type
