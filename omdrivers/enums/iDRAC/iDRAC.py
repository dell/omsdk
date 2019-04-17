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

ACRestoreState_PrivateStoreTypes = EnumWrapper("ACRestoreState_PrivateStoreTypes", {
    "Power_down": "Power-down",
    "Power_up": "Power-up",
    "Restore_to_ex_state": "Restore-to-ex-state",
}).enum_type

AccessPrivilege_VirtualConsoleTypes = EnumWrapper("AccessPrivilege_VirtualConsoleTypes", {
    "Deny_Access": "Deny Access",
    "Full_Access": "Full Access",
    "Read_Only_Access": "Read Only Access",
}).enum_type

AccessType_vFlashPartitionTypes = EnumWrapper("AccessType_vFlashPartitionTypes", {
    "Read_Only": "Read Only",
    "Read_Write": "Read Write",
}).enum_type

Access_QuickSyncTypes = EnumWrapper("Access_QuickSyncTypes", {
    "Disabled": "Disabled",
    "Read_only": "Read-only",
    "Read_write": "Read-write",
}).enum_type

ActiveNIC_CurrentNICTypes = EnumWrapper("ActiveNIC_CurrentNICTypes", {
    "Dedicated": "Dedicated",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
    "LOM5": "LOM5",
    "LOM6": "LOM6",
    "LOM7": "LOM7",
    "LOM8": "LOM8",
    "T_None": "None",
}).enum_type

ActiveSessions_VNCServerTypes = EnumWrapper("ActiveSessions_VNCServerTypes", {
    "T_0_1_2": "0,1,2",
}).enum_type

ActiveSharedLOM_CurrentNICTypes = EnumWrapper("ActiveSharedLOM_CurrentNICTypes", {
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
    "LOM5": "LOM5",
    "LOM6": "LOM6",
    "LOM7": "LOM7",
    "LOM8": "LOM8",
    "T_None": "None",
}).enum_type

AddressState_IPv6Types = EnumWrapper("AddressState_IPv6Types", {
    "Active": "Active",
    "Deprecated": "Deprecated",
    "Disabled": "Disabled",
    "Failed": "Failed",
    "Invalid": "Invalid",
    "Pending": "Pending",
}).enum_type

AdminState_OS_BMCTypes = EnumWrapper("AdminState_OS_BMCTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AgentEnable_SNMPTypes = EnumWrapper("AgentEnable_SNMPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AirExhaustTempSupport_ThermalSettingsTypes = EnumWrapper("AirExhaustTempSupport_ThermalSettingsTypes", {
    "Not_Supported": "Not Supported",
    "Supported": "Supported",
}).enum_type

AirExhaustTemp_ThermalSettingsTypes = EnumWrapper("AirExhaustTemp_ThermalSettingsTypes", {
    "T_40": "40",
    "T_45": "45",
    "T_50": "50",
    "T_55": "55",
    "T_60": "60",
    "T_65": "65",
    "T_70": "70",
}).enum_type

AlertAddrMigration_PrivateStoreTypes = EnumWrapper("AlertAddrMigration_PrivateStoreTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

AlertEnable_IPMILanTypes = EnumWrapper("AlertEnable_IPMILanTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AllowableLicenses_PlatformLicenseTypes = EnumWrapper("AllowableLicenses_PlatformLicenseTypes", {
    "T_0x1000": "0x1000",
    "T_0x2000": "0x2000",
}).enum_type

ApplyNICSelection_NICTypes = EnumWrapper("ApplyNICSelection_NICTypes", {
    "NotSet": "NotSet",
    "Set": "Set",
    "T_None": "None",
}).enum_type

ApplyReboot_AutoUpdateTypes = EnumWrapper("ApplyReboot_AutoUpdateTypes", {
    "T_0_1": "0-1",
}).enum_type

AssetTagSetByDCMI_ServerInfoTypes = EnumWrapper("AssetTagSetByDCMI_ServerInfoTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

AttachMode_RFSTypes = EnumWrapper("AttachMode_RFSTypes", {
    "Attach": "Attach",
    "Auto_Attach": "Auto Attach",
}).enum_type

AttachState_VirtualConsoleTypes = EnumWrapper("AttachState_VirtualConsoleTypes", {
    "Attached": "Attached",
    "Auto_Attach": "Auto-Attach",
    "Auto_attach": "Auto-attach",
    "Detached": "Detached",
}).enum_type

AttachState_vFlashPartitionTypes = EnumWrapper("AttachState_vFlashPartitionTypes", {
    "Attached": "Attached",
    "Detached": "Detached",
}).enum_type

Attached_VirtualMediaTypes = EnumWrapper("Attached_VirtualMediaTypes", {
    "Attached": "Attached",
    "AutoAttach": "AutoAttach",
    "Detached": "Detached",
}).enum_type

AuthenticationProtocol_UsersTypes = EnumWrapper("AuthenticationProtocol_UsersTypes", {
    "MD5": "MD5",
    "SHA": "SHA",
    "T_None": "None",
}).enum_type

Authentication_IPMISOLTypes = EnumWrapper("Authentication_IPMISOLTypes", {
    "T_0": "0",
    "T_128": "128",
    "T_192": "192",
    "T_64": "64",
}).enum_type

AutoBackup_LCAttributesTypes = EnumWrapper("AutoBackup_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoConfigIPV6_NICTypes = EnumWrapper("AutoConfigIPV6_NICTypes", {
    "Disabled": "Disabled",
    "Enable_Once": "Enable Once",
    "Enable_Once_After_Reset": "Enable Once After Reset",
}).enum_type

AutoConfig_CurrentIPv6Types = EnumWrapper("AutoConfig_CurrentIPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoConfig_IPv6Types = EnumWrapper("AutoConfig_IPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoConfig_NICTypes = EnumWrapper("AutoConfig_NICTypes", {
    "Disabled": "Disabled",
    "Enable_Once": "Enable Once",
    "Enable_Once_After_Reset": "Enable Once After Reset",
}).enum_type

AutoDetect_CurrentNICTypes = EnumWrapper("AutoDetect_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoDetect_NICTypes = EnumWrapper("AutoDetect_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoDiscovery_LCAttributesTypes = EnumWrapper("AutoDiscovery_LCAttributesTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

AutoEnable_SerialRedirectionTypes = EnumWrapper("AutoEnable_SerialRedirectionTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

AutoNegotiate_SECONDARYNICTypes = EnumWrapper("AutoNegotiate_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

AutoOSLockState_AutoOSLockGroupTypes = EnumWrapper("AutoOSLockState_AutoOSLockGroupTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoRestore_LCAttributesTypes = EnumWrapper("AutoRestore_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AutoUpdate_LCAttributesTypes = EnumWrapper("AutoUpdate_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Autoduplex_NICTypes = EnumWrapper("Autoduplex_NICTypes", {
    "Full": "Full",
    "Half": "Half",
}).enum_type

Autoneg_CurrentNICTypes = EnumWrapper("Autoneg_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Autoneg_NICTypes = EnumWrapper("Autoneg_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

AvailableSpareAlertThreshold_StorageTypes = EnumWrapper("AvailableSpareAlertThreshold_StorageTypes", {
    "T_1_99": "1-99",
}).enum_type

BIOSRTDRequested_LCAttributesTypes = EnumWrapper("BIOSRTDRequested_LCAttributesTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

BackplaneBusMode_BackplaneTypes = EnumWrapper("BackplaneBusMode_BackplaneTypes", {
    "I2C": "I2C",
    "SGPIO": "SGPIO",
    "Unknown": "Unknown",
}).enum_type

BackplaneCapable_PlatformCapabilityTypes = EnumWrapper("BackplaneCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BaudRate_IPMISOLTypes = EnumWrapper("BaudRate_IPMISOLTypes", {
    "T_115200": "115200",
    "T_19200": "19200",
    "T_38400": "38400",
    "T_57600": "57600",
    "T_9600": "9600",
}).enum_type

BaudRate_IPMISerialTypes = EnumWrapper("BaudRate_IPMISerialTypes", {
    "T_115200": "115200",
    "T_19200": "19200",
    "T_38400": "38400",
    "T_57600": "57600",
    "T_9600": "9600",
}).enum_type

BaudRate_SerialTypes = EnumWrapper("BaudRate_SerialTypes", {
    "T_115200": "115200",
    "T_19200": "19200",
    "T_38400": "38400",
    "T_57600": "57600",
    "T_9600": "9600",
}).enum_type

Begin_UpdateTypes = EnumWrapper("Begin_UpdateTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BladeInsertionPrompt_LCDTypes = EnumWrapper("BladeInsertionPrompt_LCDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BlinkPattern_IndicatorLCPTypes = EnumWrapper("BlinkPattern_IndicatorLCPTypes", {
    "Blink_1": "Blink-1",
    "Blink_2": "Blink-2",
    "Blink_Off": "Blink-Off",
}).enum_type

BlockEnable_IPBlockingTypes = EnumWrapper("BlockEnable_IPBlockingTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BluetoothCapable_PlatformCapabilityTypes = EnumWrapper("BluetoothCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BootOnce_ServerBootTypes = EnumWrapper("BootOnce_ServerBootTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BootOnce_VirtualMediaTypes = EnumWrapper("BootOnce_VirtualMediaTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

BootToMaser_LCAttributesTypes = EnumWrapper("BootToMaser_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ButtonDisable_FrontPanelTypes = EnumWrapper("ButtonDisable_FrontPanelTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CIPHERSuiteDisable_PrivateStoreTypes = EnumWrapper("CIPHERSuiteDisable_PrivateStoreTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

CMCResetState_NICTypes = EnumWrapper("CMCResetState_NICTypes", {
    "Failover": "Failover",
    "Reset": "Reset",
}).enum_type

CSIORLaunched_LCAttributesTypes = EnumWrapper("CSIORLaunched_LCAttributesTypes", {
    "Completed": "Completed",
    "Not_Completed": "Not Completed",
}).enum_type

CUPSCapable_PlatformCapabilityTypes = EnumWrapper("CUPSCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CertValidationEnable_ActiveDirectoryTypes = EnumWrapper("CertValidationEnable_ActiveDirectoryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

CertValidationEnable_LDAPTypes = EnumWrapper("CertValidationEnable_LDAPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ChanPrivLimit_IPMISerialTypes = EnumWrapper("ChanPrivLimit_IPMISerialTypes", {
    "Administrator": "Administrator",
    "Operator": "Operator",
    "User": "User",
}).enum_type

ChassisIdentifyEnable_LCDTypes = EnumWrapper("ChassisIdentifyEnable_LCDTypes", {
    "ForceOn": "ForceOn",
    "Interval_Driven": "Interval-Driven",
}).enum_type

ChassisIntrusionCapable_PlatformCapabilityTypes = EnumWrapper("ChassisIntrusionCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ChassisLEDState_ChassisPwrStateTypes = EnumWrapper("ChassisLEDState_ChassisPwrStateTypes", {
    "Blinking": "Blinking",
    "Off": "Off",
    "Unknown": "Unknown",
}).enum_type

ChassisManagementMonitoring_ChassisControlTypes = EnumWrapper("ChassisManagementMonitoring_ChassisControlTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ChassisManagementatServer_ChassisControlTypes = EnumWrapper("ChassisManagementatServer_ChassisControlTypes", {
    "Manage_and_Monitor": "Manage and Monitor",
    "Monitor": "Monitor",
    "T_None": "None",
}).enum_type

ChassisPSUInfoCapability_RSMTypes = EnumWrapper("ChassisPSUInfoCapability_RSMTypes", {
    "DCS": "DCS",
    "EC": "EC",
    "PE": "PE",
}).enum_type

ChassisPowerInfoCapability_RSMTypes = EnumWrapper("ChassisPowerInfoCapability_RSMTypes", {
    "DCS": "DCS",
    "EC": "EC",
    "PE": "PE",
}).enum_type

ChassisPowerPolicy_InfoTypes = EnumWrapper("ChassisPowerPolicy_InfoTypes", {
    "Always_Power_Off_Policy": "Always Power Off Policy",
    "Always_Power_On_Policy": "Always Power On Policy",
    "Last_Power_Policy": "Last Power Policy",
}).enum_type

ChassisPowerStatus_InfoTypes = EnumWrapper("ChassisPowerStatus_InfoTypes", {
    "Chassis_Aux_Power_State": "Chassis Aux Power State",
    "Chassis_Power_On_State": "Chassis Power On State",
    "Chassis_Powering_Off_State": "Chassis Powering Off State",
    "Chassis_Powering_On_State": "Chassis Powering On State",
    "Chassis_Standby_Power_State": "Chassis Standby Power State",
}).enum_type

ChassisResetOperation_InfoTypes = EnumWrapper("ChassisResetOperation_InfoTypes", {
    "Chassis_Reset_In_Progress": "Chassis Reset In Progress",
    "Chassis_Reset_Not_Requested": "Chassis Reset Not Requested",
}).enum_type

ChassisSubType_InfoTypes = EnumWrapper("ChassisSubType_InfoTypes", {
    "Interposer": "Interposer",
    "T_None": "None",
    "compute": "compute",
    "multinodecompute": "multinodecompute",
    "storage": "storage",
}).enum_type

ChassisSystemInfoCapability_RSMTypes = EnumWrapper("ChassisSystemInfoCapability_RSMTypes", {
    "DCS": "DCS",
    "EC": "EC",
    "PE": "PE",
}).enum_type

ChassisType_ChassisInfoTypes = EnumWrapper("ChassisType_ChassisInfoTypes", {
    "Enclosure": "Enclosure",
    "Expansion": "Expansion",
    "Module": "Module",
    "SideCar": "SideCar",
    "Sled": "Sled",
    "none": "none",
}).enum_type

ChassisType_InfoTypes = EnumWrapper("ChassisType_InfoTypes", {
    "Enclosure": "Enclosure",
    "Expansion": "Expansion",
    "Module": "Module",
    "SideCar": "SideCar",
    "Sled": "Sled",
    "none": "none",
}).enum_type

CloneStatus_GroupManagerTypes = EnumWrapper("CloneStatus_GroupManagerTypes", {
    "Complete": "Complete",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ClusterState_ECTypes = EnumWrapper("ClusterState_ECTypes", {
    "Active": "Active",
    "Computing": "Computing",
    "Not_Present": "Not_Present",
    "Offline": "Offline",
    "Standby": "Standby",
}).enum_type

ClusterState_MSMTypes = EnumWrapper("ClusterState_MSMTypes", {
    "Active": "Active",
    "Computing": "Computing",
    "Not_Present": "Not_Present",
    "Offline": "Offline",
    "Standby": "Standby",
}).enum_type

CollectSystemInventoryOnRestart_LCAttributesTypes = EnumWrapper("CollectSystemInventoryOnRestart_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ConfigChangedByUser_NICTypes = EnumWrapper("ConfigChangedByUser_NICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

ConfigurationXML_USBTypes = EnumWrapper("ConfigurationXML_USBTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Enabled_only_for_compressed_configuration_files": "Enabled only for compressed configuration files",
    "Enabled_while_server_has_default_credential_settings_only": "Enabled while server has default credential settings only",
}).enum_type

Configuration_LCDTypes = EnumWrapper("Configuration_LCDTypes", {
    "ADComp": "ADComp",
    "ADErr": "ADErr",
    "ADStat": "ADStat",
    "ADTime": "ADTime",
    "Airflow": "Airflow",
    "Ambient_Temperature": "Ambient Temperature",
    "Asset_Tag": "Asset Tag",
    "IPv6_Address": "IPv6 Address",
    "Model_Name": "Model Name",
    "OS_System_Name": "OS System Name",
    "Post": "Post",
    "Service_Tag": "Service Tag",
    "System_Watts": "System Watts",
    "T_None": "None",
    "User_Defined": "User Defined",
    "iDRAC_IPv4_Address": "iDRAC IPv4 Address",
    "iDRAC_MAC_Address": "iDRAC MAC Address",
}).enum_type

ConnectionMode_IPMISerialTypes = EnumWrapper("ConnectionMode_IPMISerialTypes", {
    "Basic": "Basic",
    "Terminal": "Terminal",
}).enum_type

CsrKeySize_SecurityTypes = EnumWrapper("CsrKeySize_SecurityTypes", {
    "T_2048": "2048",
    "T_4096": "4096",
}).enum_type

CustomUI_DCSCustomTypes = EnumWrapper("CustomUI_DCSCustomTypes", {
    "Custom_UI_Enabled": "Custom UI Enabled",
    "DefaultUI": "DefaultUI",
}).enum_type

DCLookupByUserDomain_ActiveDirectoryTypes = EnumWrapper("DCLookupByUserDomain_ActiveDirectoryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DCLookupEnable_ActiveDirectoryTypes = EnumWrapper("DCLookupEnable_ActiveDirectoryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DCMIDHCPopt12_NICTypes = EnumWrapper("DCMIDHCPopt12_NICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

DCMIDHCPopt60opt43_NICTypes = EnumWrapper("DCMIDHCPopt60opt43_NICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

DCMIDHCPrandombackoff_NICTypes = EnumWrapper("DCMIDHCPrandombackoff_NICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

DHCPEnable_CurrentIPv4Types = EnumWrapper("DHCPEnable_CurrentIPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DHCPEnable_IPv4Types = EnumWrapper("DHCPEnable_IPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DHCPEnable_SECONDARYNICTypes = EnumWrapper("DHCPEnable_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

DNSDomainFromDHCP_CurrentNICTypes = EnumWrapper("DNSDomainFromDHCP_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSDomainFromDHCP_NICStaticTypes = EnumWrapper("DNSDomainFromDHCP_NICStaticTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSDomainFromDHCP_NICTypes = EnumWrapper("DNSDomainFromDHCP_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSDomainNameFromDHCP_NICTypes = EnumWrapper("DNSDomainNameFromDHCP_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP6_CurrentIPv6Types = EnumWrapper("DNSFromDHCP6_CurrentIPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP6_IPv6StaticTypes = EnumWrapper("DNSFromDHCP6_IPv6StaticTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP6_IPv6Types = EnumWrapper("DNSFromDHCP6_IPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP_CurrentIPv4Types = EnumWrapper("DNSFromDHCP_CurrentIPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP_IPv4StaticTypes = EnumWrapper("DNSFromDHCP_IPv4StaticTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP_IPv4Types = EnumWrapper("DNSFromDHCP_IPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSFromDHCP_SECONDARYNICTypes = EnumWrapper("DNSFromDHCP_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

DNSRegister_CurrentNICTypes = EnumWrapper("DNSRegister_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DNSRegister_NICTypes = EnumWrapper("DNSRegister_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DPCapable_PlatformCapabilityTypes = EnumWrapper("DPCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DayofMonth_AutoBackupTypes = EnumWrapper("DayofMonth_AutoBackupTypes", {
    "____1_31": "* , 1-31",
}).enum_type

DayofMonth_AutoUpdateTypes = EnumWrapper("DayofMonth_AutoUpdateTypes", {
    "____1_31": "* , 1-31",
}).enum_type

DayofWeek_AutoBackupTypes = EnumWrapper("DayofWeek_AutoBackupTypes", {
    "__Mon_Tue_Wed_Thu_Fri_Sat_Sun": "*,Mon,Tue,Wed,Thu,Fri,Sat,Sun",
}).enum_type

DayofWeek_AutoUpdateTypes = EnumWrapper("DayofWeek_AutoUpdateTypes", {
    "__Mon_Tue_Wed_Thu_Fri_Sat_Sun": "*,Mon,Tue,Wed,Thu,Fri,Sat,Sun",
}).enum_type

DedicatedNICCapable_PlatformCapabilityTypes = EnumWrapper("DedicatedNICCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DefaultCredentialMitigation_DefaultCredentialMitigationConfigGroupTypes = EnumWrapper(
    "DefaultCredentialMitigation_DefaultCredentialMitigationConfigGroupTypes", {
        "Disabled": "Disabled",
        "Enabled": "Enabled",
    }).enum_type

DefaultLicenseFeatures_PlatformLicenseTypes = EnumWrapper("DefaultLicenseFeatures_PlatformLicenseTypes", {
    "T_0x0200": "0x0200",
    "T_0x0400": "0x0400",
    "T_0x0800": "0x0800",
    "T_0x2000": "0x2000",
    "T_0x4000": "0x4000",
}).enum_type

DefaultProtocol_SupportAssistTypes = EnumWrapper("DefaultProtocol_SupportAssistTypes", {
    "CIFS": "CIFS",
    "NFS": "NFS",
    "NONE": "NONE",
}).enum_type

DefaultScreen_LCDTypes = EnumWrapper("DefaultScreen_LCDTypes", {
    "Alerts": "Alerts",
    "MainMenu": "MainMenu",
}).enum_type

DefaultUserCreated_SecureDefaultPasswordTypes = EnumWrapper("DefaultUserCreated_SecureDefaultPasswordTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

DeleteControl_IPMISerialTypes = EnumWrapper("DeleteControl_IPMISerialTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DeliveryRetryAttempts_RedfishEventingTypes = EnumWrapper("DeliveryRetryAttempts_RedfishEventingTypes", {
    "T_0_5": "0-5",
}).enum_type

DeliveryRetryIntervalInSeconds_RedfishEventingTypes = EnumWrapper("DeliveryRetryIntervalInSeconds_RedfishEventingTypes",
                                                                  {
                                                                      "T_5_60": "5-60",
                                                                  }).enum_type

DiagsJobScheduled_LCAttributesTypes = EnumWrapper("DiagsJobScheduled_LCAttributesTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

DisablePowerButton_ChassisPowerTypes = EnumWrapper("DisablePowerButton_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

DiscoveryEnable_IntegratedDatacenterTypes = EnumWrapper("DiscoveryEnable_IntegratedDatacenterTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "NA": "NA",
}).enum_type

DiscoveryFactoryDefaults_LCAttributesTypes = EnumWrapper("DiscoveryFactoryDefaults_LCAttributesTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

DisplayToeTagError_SecureDefaultPasswordTypes = EnumWrapper("DisplayToeTagError_SecureDefaultPasswordTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

DomainNameDHCP_SECONDARYNICTypes = EnumWrapper("DomainNameDHCP_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

Duplex_CurrentNICTypes = EnumWrapper("Duplex_CurrentNICTypes", {
    "Half": "Half",
    "full": "full",
}).enum_type

Duplex_NICTypes = EnumWrapper("Duplex_NICTypes", {
    "Full": "Full",
    "Half": "Half",
}).enum_type

Duplex_SECONDARYNICTypes = EnumWrapper("Duplex_SECONDARYNICTypes", {
    "Full": "Full",
    "Half": "Half",
}).enum_type

DynamicStepUp_ServerPwrTypes = EnumWrapper("DynamicStepUp_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

E_12GBackplaneon13GCapable_PlatformCapabilityTypes = EnumWrapper("E_12GBackplaneon13GCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

E_3rdPartyCard_PCIeSlotLFMTypes = EnumWrapper("E_3rdPartyCard_PCIeSlotLFMTypes", {
    "N_A": "N/A",
    "No": "No",
    "Yes": "Yes",
}).enum_type

EchoControl_IPMISerialTypes = EnumWrapper("EchoControl_IPMISerialTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Eject_IntegratedDatacenterTypes = EnumWrapper("Eject_IntegratedDatacenterTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

EmailOptIn_SupportAssistTypes = EnumWrapper("EmailOptIn_SupportAssistTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

EmulationType_vFlashPartitionTypes = EnumWrapper("EmulationType_vFlashPartitionTypes", {
    "CD_DVD": "CD-DVD",
    "Floppy": "Floppy",
    "HDD": "HDD",
}).enum_type

EnableChassisConsoleAccess_VirtualConsoleTypes = EnumWrapper("EnableChassisConsoleAccess_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EnableSharedCompUpdate_UpdateTypes = EnumWrapper("EnableSharedCompUpdate_UpdateTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EnableStatus_MgmtNetworkInterfaceTypes = EnumWrapper("EnableStatus_MgmtNetworkInterfaceTypes", {
    "Detected": "Detected",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Unknown": "Unknown",
}).enum_type

Enable_ASRConfigTypes = EnumWrapper("Enable_ASRConfigTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_ActiveDirectoryTypes = EnumWrapper("Enable_ActiveDirectoryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_CurrentIPv4Types = EnumWrapper("Enable_CurrentIPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_CurrentIPv6Types = EnumWrapper("Enable_CurrentIPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_CurrentNICTypes = EnumWrapper("Enable_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_EmailAlertTypes = EnumWrapper("Enable_EmailAlertTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_IPMILanTypes = EnumWrapper("Enable_IPMILanTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_IPMISOLTypes = EnumWrapper("Enable_IPMISOLTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_IPv4Types = EnumWrapper("Enable_IPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_IPv6Types = EnumWrapper("Enable_IPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_LDAPTypes = EnumWrapper("Enable_LDAPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_NICTypes = EnumWrapper("Enable_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_RFSTypes = EnumWrapper("Enable_RFSTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_RacadmTypes = EnumWrapper("Enable_RacadmTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_RedfishTypes = EnumWrapper("Enable_RedfishTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_SNMPAlertTypes = EnumWrapper("Enable_SNMPAlertTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_SSHTypes = EnumWrapper("Enable_SSHTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_SerialRedirectionTypes = EnumWrapper("Enable_SerialRedirectionTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_SerialTypes = EnumWrapper("Enable_SerialTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_SwitchConnectionViewTypes = EnumWrapper("Enable_SwitchConnectionViewTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_TelnetTypes = EnumWrapper("Enable_TelnetTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_UsersTypes = EnumWrapper("Enable_UsersTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_VNCServerTypes = EnumWrapper("Enable_VNCServerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_VirtualConsoleTypes = EnumWrapper("Enable_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_WebServerTypes = EnumWrapper("Enable_WebServerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enable_vFlashSDTypes = EnumWrapper("Enable_vFlashSDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EnabledOnFrontPanel_VirtualConsoleTypes = EnumWrapper("EnabledOnFrontPanel_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Enabled_STPTypes = EnumWrapper("Enabled_STPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

EncryptEnable_VirtualConsoleTypes = EnumWrapper("EncryptEnable_VirtualConsoleTypes", {
    "AES": "AES",
    "Enabled": "Enabled",
    "Disabled": "Disabled",
    "T_None": "None",
}).enum_type

EncryptEnable_VirtualMediaTypes = EnumWrapper("EncryptEnable_VirtualMediaTypes", {
    "AES": "AES",
    "Enabled": "Enabled",
    "Disabled": "Disabled",
    "T_None": "None",
}).enum_type

EncryptionStatus_GroupManagerTypes = EnumWrapper("EncryptionStatus_GroupManagerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ErrorDisplayMode_LCDTypes = EnumWrapper("ErrorDisplayMode_LCDTypes", {
    "SEL": "SEL",
    "simple": "simple",
}).enum_type

EventBasedAutoCollection_SupportAssistTypes = EnumWrapper("EventBasedAutoCollection_SupportAssistTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FIPSMode_SecurityTypes = EnumWrapper("FIPSMode_SecurityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FTRCapable_PlatformCapabilityTypes = EnumWrapper("FTRCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Failover_CurrentNICTypes = EnumWrapper("Failover_CurrentNICTypes", {
    "ALL": "ALL",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
    "T_None": "None",
}).enum_type

Failover_NICTypes = EnumWrapper("Failover_NICTypes", {
    "ALL": "ALL",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
    "T_None": "None",
}).enum_type

FanHealth_InfoTypes = EnumWrapper("FanHealth_InfoTypes", {
    "Critical": "Critical",
    "Ok": "Ok",
    "Warning": "Warning",
}).enum_type

FanRedundancy_InfoTypes = EnumWrapper("FanRedundancy_InfoTypes", {
    "Full": "Full",
    "Lost": "Lost",
    "N_A": "N/A",
}).enum_type

FanSpeedOffset_ThermalSettingsTypes = EnumWrapper("FanSpeedOffset_ThermalSettingsTypes", {
    "High_Fan_Speed": "High Fan Speed",
    "Low_Fan_Speed": "Low Fan Speed",
    "Max_Fan_Speed": "Max Fan Speed",
    "Medium_Fan_Speed": "Medium Fan Speed",
    "Off": "Off",
}).enum_type

FilterAutoCollections_SupportAssistTypes = EnumWrapper("FilterAutoCollections_SupportAssistTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

FirstBootDevice_ServerBootTypes = EnumWrapper("FirstBootDevice_ServerBootTypes", {
    "BIOS": "BIOS",
    "CD_DVD": "CD-DVD",
    "F10": "F10",
    "F11": "F11",
    "FDD": "FDD",
    "HDD": "HDD",
    "Normal": "Normal",
    "PXE": "PXE",
    "SD": "SD",
    "UEFIDevicePath": "UEFIDevicePath",
    "VCD_DVD": "VCD-DVD",
    "vFDD": "vFDD",
}).enum_type

FlexMacCompleted_NICTypes = EnumWrapper("FlexMacCompleted_NICTypes", {
    "Notstarted": "Notstarted",
    "completed": "completed",
}).enum_type

FloppyEmulation_VirtualMediaTypes = EnumWrapper("FloppyEmulation_VirtualMediaTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FlowControl_IPMISerialTypes = EnumWrapper("FlowControl_IPMISerialTypes", {
    "RTS_CTS": "RTS/CTS",
    "T_None": "None",
}).enum_type

FormatType_vFlashPartitionTypes = EnumWrapper("FormatType_vFlashPartitionTypes", {
    "EXT2EXT3": "EXT2EXT3",
    "FAT16": "FAT16",
    "FAT32": "FAT32",
    "RAW": "RAW",
}).enum_type

FreshAirCapable_PlatformCapabilityTypes = EnumWrapper("FreshAirCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FreshAirCompliantConfiguration_ThermalConfigTypes = EnumWrapper("FreshAirCompliantConfiguration_ThermalConfigTypes", {
    "No": "No",
    "Not_Applicable": "Not Applicable",
    "Yes": "Yes",
}).enum_type

FrontPanelCapable_PlatformCapabilityTypes = EnumWrapper("FrontPanelCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FrontPanelLocking_LCDTypes = EnumWrapper("FrontPanelLocking_LCDTypes", {
    "Full_Access": "Full-Access",
    "Locked": "Locked",
    "View_Only": "View-Only",
}).enum_type

FrontPanelUSBCapable_PlatformCapabilityTypes = EnumWrapper("FrontPanelUSBCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FwUpdateTFTPEnable_UpdateTypes = EnumWrapper("FwUpdateTFTPEnable_UpdateTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

G5KxcablePresence_NICTypes = EnumWrapper("G5KxcablePresence_NICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

GCLookupEnable_ActiveDirectoryTypes = EnumWrapper("GCLookupEnable_ActiveDirectoryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

GatewaySelector_IPMILANPEFConfigTypes = EnumWrapper("GatewaySelector_IPMILANPEFConfigTypes", {
    "Backup": "Backup",
    "Default": "Default",
}).enum_type

GroupAttributeIsDN_LDAPTypes = EnumWrapper("GroupAttributeIsDN_LDAPTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HandshakeControl_IPMISerialTypes = EnumWrapper("HandshakeControl_IPMISerialTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HardwareIdentityCertStatus_CertificateTypes = EnumWrapper("HardwareIdentityCertStatus_CertificateTypes", {
    "Absent": "Absent",
    "Corrupted": "Corrupted",
    "Not_Applicable": "Not Applicable",
    "Valid": "Valid",
}).enum_type

HealthStatus_MSMTypes = EnumWrapper("HealthStatus_MSMTypes", {
    "Critical": "Critical",
    "OK": "OK",
    "Unknown": "Unknown",
    "Warning": "Warning",
}).enum_type

Health_vFlashSDTypes = EnumWrapper("Health_vFlashSDTypes", {
    "Critical": "Critical",
    "OK": "OK",
    "Unknown": "Unknown",
    "Warning": "Warning",
}).enum_type

HideErrs_LCDTypes = EnumWrapper("HideErrs_LCDTypes", {
    "hide": "hide",
    "unhide": "unhide",
}).enum_type

HostFrontPortStatus_USBTypes = EnumWrapper("HostFrontPortStatus_USBTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HostFrontPortsDynamicMode_USBTypes = EnumWrapper("HostFrontPortsDynamicMode_USBTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HostOSProxyConfigured_SupportAssistTypes = EnumWrapper("HostOSProxyConfigured_SupportAssistTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

HostSNMPAlert_ServiceModuleTypes = EnumWrapper("HostSNMPAlert_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

HttpsRedirection_WebServerTypes = EnumWrapper("HttpsRedirection_WebServerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IDSDMCapable_PlatformCapabilityTypes = EnumWrapper("IDSDMCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IDSDMState_PrivateStoreTypes = EnumWrapper("IDSDMState_PrivateStoreTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

IOIDOptEnable_IOIDOptTypes = EnumWrapper("IOIDOptEnable_IOIDOptTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IPChangeNotifyPS_LCAttributesTypes = EnumWrapper("IPChangeNotifyPS_LCAttributesTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

IPv4Enable_SECONDARYNICTypes = EnumWrapper("IPv4Enable_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

IgnoreCertWarning_LCAttributesTypes = EnumWrapper("IgnoreCertWarning_LCAttributesTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

IgnoreCertificateErrors_RedfishEventingTypes = EnumWrapper("IgnoreCertificateErrors_RedfishEventingTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

InactivityTimeoutEnable_VirtualConsoleTypes = EnumWrapper("InactivityTimeoutEnable_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

InactivityTimerEnable_QuickSyncTypes = EnumWrapper("InactivityTimerEnable_QuickSyncTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

IndicatorColor_ChassisHealthIndicatorTypes = EnumWrapper("IndicatorColor_ChassisHealthIndicatorTypes", {
    "Amber": "Amber",
    "Blue": "Blue",
    "Green": "Green",
}).enum_type

IndicatorColor_IdentifyButtonTypes = EnumWrapper("IndicatorColor_IdentifyButtonTypes", {
    "Amber": "Amber",
    "Blue": "Blue",
    "Green": "Green",
}).enum_type

IndicatorColor_PowerButtonTypes = EnumWrapper("IndicatorColor_PowerButtonTypes", {
    "Amber": "Amber",
    "Blue": "Blue",
    "Green": "Green",
}).enum_type

IndicatorColor_PowerHealthIndicatorTypes = EnumWrapper("IndicatorColor_PowerHealthIndicatorTypes", {
    "Amber": "Amber",
    "Blue": "Blue",
    "Green": "Green",
}).enum_type

IndicatorColor_ThermalHealthIndicatorTypes = EnumWrapper("IndicatorColor_ThermalHealthIndicatorTypes", {
    "Amber": "Amber",
    "Blue": "Blue",
    "Green": "Green",
}).enum_type

IndicatorLED_InfoTypes = EnumWrapper("IndicatorLED_InfoTypes", {
    "BLINK_1": "BLINK-1",
    "BLINK_2": "BLINK-2",
    "BLINK_OFF": "BLINK-OFF",
}).enum_type

IndicatorState_ChassisHealthIndicatorTypes = EnumWrapper("IndicatorState_ChassisHealthIndicatorTypes", {
    "Blinking": "Blinking",
    "Off": "Off",
    "On": "On",
}).enum_type

IndicatorState_IdentifyButtonTypes = EnumWrapper("IndicatorState_IdentifyButtonTypes", {
    "Blinking": "Blinking",
    "Off": "Off",
    "On": "On",
}).enum_type

IndicatorState_PowerButtonTypes = EnumWrapper("IndicatorState_PowerButtonTypes", {
    "Blinking": "Blinking",
    "Off": "Off",
    "On": "On",
}).enum_type

IndicatorState_PowerHealthIndicatorTypes = EnumWrapper("IndicatorState_PowerHealthIndicatorTypes", {
    "Blinking": "Blinking",
    "Off": "Off",
    "On": "On",
}).enum_type

IndicatorState_ThermalHealthIndicatorTypes = EnumWrapper("IndicatorState_ThermalHealthIndicatorTypes", {
    "Blinking": "Blinking",
    "Off": "Off",
    "On": "On",
}).enum_type

Initialized_vFlashSDTypes = EnumWrapper("Initialized_vFlashSDTypes", {
    "Initialized": "Initialized",
    "Not_Initialized": "Not Initialized",
}).enum_type

InitiatorPersistencePolicy_IOIDOptTypes = EnumWrapper("InitiatorPersistencePolicy_IOIDOptTypes", {
    "ACPowerLoss": "ACPowerLoss",
    "ColdReset": "ColdReset",
    "ColdReset__ACPowerLoss": "ColdReset, ACPowerLoss",
    "T_None": "None",
    "WarmReset": "WarmReset",
    "WarmReset__ACPowerLoss": "WarmReset, ACPowerLoss",
    "WarmReset__ColdReset": "WarmReset, ColdReset",
    "WarmReset__ColdReset__ACPowerLoss": "WarmReset, ColdReset, ACPowerLoss",
}).enum_type

InputNewLineSeq_IPMISerialTypes = EnumWrapper("InputNewLineSeq_IPMISerialTypes", {
    "Enter": "Enter",
    "Null": "Null",
}).enum_type

InputVoltageType_InfoTypes = EnumWrapper("InputVoltageType_InfoTypes", {
    "AC": "AC",
    "DC": "DC",
}).enum_type

IpmiLanPrivilege_UsersTypes = EnumWrapper("IpmiLanPrivilege_UsersTypes", {
    "Administrator": "Administrator",
    "No_Access": "No Access",
    "Operator": "Operator",
    "User": "User",
}).enum_type

IpmiSerialPrivilege_UsersTypes = EnumWrapper("IpmiSerialPrivilege_UsersTypes", {
    "Administrator": "Administrator",
    "No_Access": "No Access",
    "Operator": "Operator",
    "User": "User",
}).enum_type

IsEmptyEntry_GpGPUTableTypes = EnumWrapper("IsEmptyEntry_GpGPUTableTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

IsOCPcardActive_CurrentNICTypes = EnumWrapper("IsOCPcardActive_CurrentNICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

KeepPhyLinkUp_DCSCustomTypes = EnumWrapper("KeepPhyLinkUp_DCSCustomTypes", {
    "T_False": "False",
    "T_True": "True",
    "T_0": "0",
    "T_1": "1",
}).enum_type

KeyEnable_VirtualMediaTypes = EnumWrapper("KeyEnable_VirtualMediaTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LCDCapable_PlatformCapabilityTypes = EnumWrapper("LCDCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LCDriveEnable_LCAttributesTypes = EnumWrapper("LCDriveEnable_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LCLReplication_ServiceModuleTypes = EnumWrapper("LCLReplication_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LCWipe_LCAttributesTypes = EnumWrapper("LCWipe_LCAttributesTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

LFMMode_PCIeSlotLFMTypes = EnumWrapper("LFMMode_PCIeSlotLFMTypes", {
    "Automatic": "Automatic",
    "Custom": "Custom",
    "Disabled": "Disabled",
}).enum_type

LM_AUTO_DISCOVERY_PMLicensingTypes = EnumWrapper("LM_AUTO_DISCOVERY_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_AUTO_UPDATE_PMLicensingTypes = EnumWrapper("LM_AUTO_UPDATE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_AVOTON_4CORE_PMLicensingTypes = EnumWrapper("LM_AVOTON_4CORE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_AVOTON_8CORE_PMLicensingTypes = EnumWrapper("LM_AVOTON_8CORE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_BACKUP_RESTORE_PMLicensingTypes = EnumWrapper("LM_BACKUP_RESTORE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_BASE_IPMI_GUI_PMLicensingTypes = EnumWrapper("LM_BASE_IPMI_GUI_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_BASIC_REMOTE_INVENTORY_EXPORT_PMLicensingTypes = EnumWrapper("LM_BASIC_REMOTE_INVENTORY_EXPORT_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_BMC_PLUS_PMLicensingTypes = EnumWrapper("LM_BMC_PLUS_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_BOOT_CAPTURE_PMLicensingTypes = EnumWrapper("LM_BOOT_CAPTURE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_CONNECTION_VIEW_PMLicensingTypes = EnumWrapper("LM_CONNECTION_VIEW_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_CONSOLE_COLLABORATION_PMLicensingTypes = EnumWrapper("LM_CONSOLE_COLLABORATION_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_DCS_GUI_PMLicensingTypes = EnumWrapper("LM_DCS_GUI_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_DEDICATED_NIC_PMLicensingTypes = EnumWrapper("LM_DEDICATED_NIC_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_DEVICE_MONITORING_PMLicensingTypes = EnumWrapper("LM_DEVICE_MONITORING_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_DHCP_CONFIGURE_PMLicensingTypes = EnumWrapper("LM_DHCP_CONFIGURE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_DIRECTORY_SERVICES_PMLicensingTypes = EnumWrapper("LM_DIRECTORY_SERVICES_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_DYNAMIC_DNS_PMLicensingTypes = EnumWrapper("LM_DYNAMIC_DNS_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_EMAIL_ALERTING_PMLicensingTypes = EnumWrapper("LM_EMAIL_ALERTING_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_FULL_UI_PMLicensingTypes = EnumWrapper("LM_FULL_UI_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_GROUP_MANAGER_PMLicensingTypes = EnumWrapper("LM_GROUP_MANAGER_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_IDRAC_ENTERPRISE_PMLicensingTypes = EnumWrapper("LM_IDRAC_ENTERPRISE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_IDRAC_EXPRESS_BLADES_PMLicensingTypes = EnumWrapper("LM_IDRAC_EXPRESS_BLADES_PMLicensingTypes", {
    "T_0xFF": "0xFF",
}).enum_type

LM_IDRAC_EXPRESS_PMLicensingTypes = EnumWrapper("LM_IDRAC_EXPRESS_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_INBAND_FIRMWARE_UPDATE_PMLicensingTypes = EnumWrapper("LM_INBAND_FIRMWARE_UPDATE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_IPV6_PMLicensingTypes = EnumWrapper("LM_IPV6_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_LAST_CRASH_SCREEN_CAPTURE_PMLicensingTypes = EnumWrapper("LM_LAST_CRASH_SCREEN_CAPTURE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_LAST_CRASH_VIDEO_CAPTURE_PMLicensingTypes = EnumWrapper("LM_LAST_CRASH_VIDEO_CAPTURE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_LC_UI_PMLicensingTypes = EnumWrapper("LM_LC_UI_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_LICENSE_UI_PMLicensingTypes = EnumWrapper("LM_LICENSE_UI_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_LOCKDOWN_MODE_PMLicensingTypes = EnumWrapper("LM_LOCKDOWN_MODE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_NTP_PMLicensingTypes = EnumWrapper("LM_NTP_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_OME_PMLicensingTypes = EnumWrapper("LM_OME_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_OOB_PMLicensingTypes = EnumWrapper("LM_OOB_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_PART_REPLACEMENT_PMLicensingTypes = EnumWrapper("LM_PART_REPLACEMENT_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_POWER_BUDGETING_PMLicensingTypes = EnumWrapper("LM_POWER_BUDGETING_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_POWER_MONITORING_PMLicensingTypes = EnumWrapper("LM_POWER_MONITORING_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_QUALITY_BANDWIDTH_CONTROL_PMLicensingTypes = EnumWrapper("LM_QUALITY_BANDWIDTH_CONTROL_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_RACADM_CLI_PMLicensingTypes = EnumWrapper("LM_RACADM_CLI_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REDFISH_PMLicensingTypes = EnumWrapper("LM_REDFISH_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REMOTE_ASSET_INVENTORY_PMLicensingTypes = EnumWrapper("LM_REMOTE_ASSET_INVENTORY_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REMOTE_CONFIGURATION_PMLicensingTypes = EnumWrapper("LM_REMOTE_CONFIGURATION_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REMOTE_FILE_SHARE_PMLicensingTypes = EnumWrapper("LM_REMOTE_FILE_SHARE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REMOTE_FIRWARE_UPDATE_PMLicensingTypes = EnumWrapper("LM_REMOTE_FIRWARE_UPDATE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REMOTE_OS_DEPLOYMENT_PMLicensingTypes = EnumWrapper("LM_REMOTE_OS_DEPLOYMENT_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_REMOTE_SYSLOG_PMLicensingTypes = EnumWrapper("LM_REMOTE_SYSLOG_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_RESTORE_PMLicensingTypes = EnumWrapper("LM_RESTORE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_SECURITY_LOCKOUT_PMLicensingTypes = EnumWrapper("LM_SECURITY_LOCKOUT_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_SMASH_CLP_PMLicensingTypes = EnumWrapper("LM_SMASH_CLP_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_SNMP_GET_PMLicensingTypes = EnumWrapper("LM_SNMP_GET_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_SSH_PK_AUTHEN_PMLicensingTypes = EnumWrapper("LM_SSH_PK_AUTHEN_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_SSH_PMLicensingTypes = EnumWrapper("LM_SSH_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_SSO_PMLicensingTypes = EnumWrapper("LM_SSO_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_STORAGE_MONITORING_PMLicensingTypes = EnumWrapper("LM_STORAGE_MONITORING_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_TELNET_PMLicensingTypes = EnumWrapper("LM_TELNET_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_TWO_FACTOR_AUTHEN_PMLicensingTypes = EnumWrapper("LM_TWO_FACTOR_AUTHEN_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_UPDATE_FROM_REPO_PMLicensingTypes = EnumWrapper("LM_UPDATE_FROM_REPO_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_USC_ASSISTED_OS_DEPLOYEMENT_PMLicensingTypes = EnumWrapper("LM_USC_ASSISTED_OS_DEPLOYEMENT_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_USC_DEVICE_CONFIGURATION_PMLicensingTypes = EnumWrapper("LM_USC_DEVICE_CONFIGURATION_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_USC_EMBEDDED_DIAGNOSTICS_PMLicensingTypes = EnumWrapper("LM_USC_EMBEDDED_DIAGNOSTICS_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_USC_FIRMWARE_UPDATE_PMLicensingTypes = EnumWrapper("LM_USC_FIRMWARE_UPDATE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VCONSOLE_CHAT_PMLicensingTypes = EnumWrapper("LM_VCONSOLE_CHAT_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VCONSOLE_HTML5_ACCESS_PMLicensingTypes = EnumWrapper("LM_VCONSOLE_HTML5_ACCESS_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VCONSOLE_PMLicensingTypes = EnumWrapper("LM_VCONSOLE_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VFOLDER_PMLicensingTypes = EnumWrapper("LM_VFOLDER_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VIRTUAL_FLASH_PARTITIONS_PMLicensingTypes = EnumWrapper("LM_VIRTUAL_FLASH_PARTITIONS_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VMEDIA_PMLicensingTypes = EnumWrapper("LM_VMEDIA_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_VNC_PMLicensingTypes = EnumWrapper("LM_VNC_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LM_WSMAN_PMLicensingTypes = EnumWrapper("LM_WSMAN_PMLicensingTypes", {
    "T_0": "0",
    "T_0xFF": "0xFF",
    "T_1": "1",
}).enum_type

LastPwrState_PrivateStoreTypes = EnumWrapper("LastPwrState_PrivateStoreTypes", {
    "Off": "Off",
    "On": "On",
}).enum_type

LaunchSSM_LCAttributesTypes = EnumWrapper("LaunchSSM_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LicenseMsgEnable_LCDTypes = EnumWrapper("LicenseMsgEnable_LCDTypes", {
    "Display_Licens_Msg": "Display-Licens-Msg",
    "No_License_Msg": "No-License-Msg",
}).enum_type

LicenseUpsellCapable_PlatformCapabilityTypes = EnumWrapper("LicenseUpsellCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Licensed_LCAttributesTypes = EnumWrapper("Licensed_LCAttributesTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

Licensed_vFlashSDTypes = EnumWrapper("Licensed_vFlashSDTypes", {
    "Licensed": "Licensed",
    "Not_Licensed": "Not Licensed",
}).enum_type

LifecycleControllerState_LCAttributesTypes = EnumWrapper("LifecycleControllerState_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Recovery": "Recovery",
}).enum_type

LifecyclecontrollerCapable_PlatformCapabilityTypes = EnumWrapper("LifecyclecontrollerCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LineEdit_IPMISerialTypes = EnumWrapper("LineEdit_IPMISerialTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LinkStatus_CurrentNICTypes = EnumWrapper("LinkStatus_CurrentNICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

LinkStatus_MgmtNetworkInterfaceTypes = EnumWrapper("LinkStatus_MgmtNetworkInterfaceTypes", {
    "LinkDown": "LinkDown",
    "LinkUp": "LinkUp",
    "NoLink": "NoLink",
    "Unknown": "Unknown",
}).enum_type

LinkStatus_NICTypes = EnumWrapper("LinkStatus_NICTypes", {
    "Down": "Down",
    "Unknown": "Unknown",
    "Up": "Up",
}).enum_type

LocalConfig_LocalSecurityTypes = EnumWrapper("LocalConfig_LocalSecurityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LocalDisable_VirtualConsoleTypes = EnumWrapper("LocalDisable_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LocalVideo_VirtualConsoleTypes = EnumWrapper("LocalVideo_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Locale_LCDTypes = EnumWrapper("Locale_LCDTypes", {
    "de": "de",
    "en": "en",
    "es": "es",
    "fr": "fr",
    "ja": "ja",
    "zh": "zh",
}).enum_type

Location_SlotConfigTypes = EnumWrapper("Location_SlotConfigTypes", {
    "front": "front",
    "rear": "rear",
}).enum_type

LowerEncryptionBitLength_VNCServerTypes = EnumWrapper("LowerEncryptionBitLength_VNCServerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

LowerEncryptionBitLength_WebServerTypes = EnumWrapper("LowerEncryptionBitLength_WebServerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MBSELRestoreState_SupportAssistTypes = EnumWrapper("MBSELRestoreState_SupportAssistTypes", {
    "Available": "Available",
    "Failed": "Failed",
    "InProgress": "InProgress",
    "NotAvailable": "NotAvailable",
    "Partial": "Partial",
}).enum_type

MEAutoResetDisable_PlatformCapabilityTypes = EnumWrapper("MEAutoResetDisable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ManagementPortMode_USBTypes = EnumWrapper("ManagementPortMode_USBTypes", {
    "Automatic": "Automatic",
    "Standard_OS_Use": "Standard OS Use",
    "iDRAC_Direct_Only": "iDRAC Direct Only",
}).enum_type

MaxConservationMode_ChassisPowerTypes = EnumWrapper("MaxConservationMode_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MaxSessions_VNCServerTypes = EnumWrapper("MaxSessions_VNCServerTypes", {
    "T_1_2": "1,2",
}).enum_type

MediaAttachState_RFSTypes = EnumWrapper("MediaAttachState_RFSTypes", {
    "Attached": "Attached",
    "Detached": "Detached",
}).enum_type

MezzLOMCapable_PlatformCapabilityTypes = EnumWrapper("MezzLOMCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MgtNetworkNicConfig_ServerInfoTypes = EnumWrapper("MgtNetworkNicConfig_ServerInfoTypes", {
    "CableDetect": "CableDetect",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

MinPrivilege_IPMISOLTypes = EnumWrapper("MinPrivilege_IPMISOLTypes", {
    "Administrator": "Administrator",
    "Operator": "Operator",
    "User": "User",
}).enum_type

Mode_RedundancyTypes = EnumWrapper("Mode_RedundancyTypes", {
    "Failover": "Failover",
}).enum_type

ModularLinkstatus_NICTypes = EnumWrapper("ModularLinkstatus_NICTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

ModularSharedLOMCapable_PlatformCapabilityTypes = EnumWrapper("ModularSharedLOMCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NDCMisconfig_PrivateStoreTypes = EnumWrapper("NDCMisconfig_PrivateStoreTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

NGMPlatform_PlatformCapabilityTypes = EnumWrapper("NGMPlatform_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NICEnable_SECONDARYNICTypes = EnumWrapper("NICEnable_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

NICFailover_SECONDARYNICTypes = EnumWrapper("NICFailover_SECONDARYNICTypes", {
    "All": "All",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
    "T_None": "None",
}).enum_type

NICSelection_SECONDARYNICTypes = EnumWrapper("NICSelection_SECONDARYNICTypes", {
    "Dedicated": "Dedicated",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
}).enum_type

NICSpeed_SECONDARYNICTypes = EnumWrapper("NICSpeed_SECONDARYNICTypes", {
    "T_10": "10",
    "T_100": "100",
    "T_1000": "1000",
}).enum_type

NMCapable_PlatformCapabilityTypes = EnumWrapper("NMCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NMIResetOverride_LCDTypes = EnumWrapper("NMIResetOverride_LCDTypes", {
    "DIsabled": "DIsabled",
    "IDButtonDoesNotReset": "IDButtonDoesNotReset",
    "IDButtonResets": "IDButtonResets",
}).enum_type

NMPTASCapable_PlatformCapabilityTypes = EnumWrapper("NMPTASCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NMSubSystemPwrMonitoringCapable_PlatformCapabilityTypes = EnumWrapper(
    "NMSubSystemPwrMonitoringCapable_PlatformCapabilityTypes", {
        "Disabled": "Disabled",
        "Enabled": "Enabled",
    }).enum_type

NOBladethrottleDuringCMCrebootCapable_PlatformCapabilityTypes = EnumWrapper(
    "NOBladethrottleDuringCMCrebootCapable_PlatformCapabilityTypes", {
        "Disabled": "Disabled",
        "Enabled": "Enabled",
    }).enum_type

NTPEnable_NTPConfigGroupTypes = EnumWrapper("NTPEnable_NTPConfigGroupTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

NativeOSLogsCollectionOverride_SupportAssistTypes = EnumWrapper("NativeOSLogsCollectionOverride_SupportAssistTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

NativeOSLogsCollectionSupported_SupportAssistTypes = EnumWrapper("NativeOSLogsCollectionSupported_SupportAssistTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

NetworkConnection_ServiceModuleTypes = EnumWrapper("NetworkConnection_ServiceModuleTypes", {
    "Available": "Available",
    "Not_Available": "Not Available",
}).enum_type

NewLineSeq_IPMISerialTypes = EnumWrapper("NewLineSeq_IPMISerialTypes", {
    "CR": "CR",
    "CR_LF": "CR-LF",
    "LF": "LF",
    "LF_CR": "LF-CR",
    "NULL": "NULL",
    "T_None": "None",
}).enum_type

NoAuth_SerialTypes = EnumWrapper("NoAuth_SerialTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

OMSAPresence_ServiceModuleTypes = EnumWrapper("OMSAPresence_ServiceModuleTypes", {
    "NA": "NA",
    "Not_Present": "Not Present",
    "Present": "Present",
}).enum_type

OSBMCPassthroughCapable_PlatformCapabilityTypes = EnumWrapper("OSBMCPassthroughCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

OSInfo_ServiceModuleTypes = EnumWrapper("OSInfo_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Occupied_CMCSlotTypes = EnumWrapper("Occupied_CMCSlotTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

Occupied_FanSlotTypes = EnumWrapper("Occupied_FanSlotTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

Occupied_IOMInterposerTypes = EnumWrapper("Occupied_IOMInterposerTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

Occupied_IOMSlotTypes = EnumWrapper("Occupied_IOMSlotTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

Occupied_PSUSlotTypes = EnumWrapper("Occupied_PSUSlotTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

Occupied_SledInterposerTypes = EnumWrapper("Occupied_SledInterposerTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

Occupied_SledSlotTypes = EnumWrapper("Occupied_SledSlotTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

OperationMode_IntegratedDatacenterTypes = EnumWrapper("OperationMode_IntegratedDatacenterTypes", {
    "Default": "Default",
    "Discovered": "Discovered",
}).enum_type

Order_PSUSlotSeqTypes = EnumWrapper("Order_PSUSlotSeqTypes", {
    "BT": "BT",
    "LR": "LR",
    "RL": "RL",
    "TB": "TB",
}).enum_type

Order_SlotConfigTypes = EnumWrapper("Order_SlotConfigTypes", {
    "BT": "BT",
    "LR": "LR",
    "RL": "RL",
    "TB": "TB",
}).enum_type

Orientation_SlotConfigTypes = EnumWrapper("Orientation_SlotConfigTypes", {
    "Horizontal": "Horizontal",
    "Vertical": "Vertical",
}).enum_type

OverTemperatureCLSTOverride_ChassisPowerTypes = EnumWrapper("OverTemperatureCLSTOverride_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

OverTemperatureCLSTOverride_ServerPwrTypes = EnumWrapper("OverTemperatureCLSTOverride_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PCIeSlotLFMSupport_ThermalSettingsTypes = EnumWrapper("PCIeSlotLFMSupport_ThermalSettingsTypes", {
    "Not_Supported": "Not Supported",
    "Supported": "Supported",
}).enum_type

PEFFilterDefaultsSet_IPMIPefSeldomTypes = EnumWrapper("PEFFilterDefaultsSet_IPMIPefSeldomTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

PMAllowableLicenses_PMLicensingTypes = EnumWrapper("PMAllowableLicenses_PMLicensingTypes", {
    "T_02000": "02000",
    "T_0x0200": "0x0200",
    "T_0x1000": "0x1000",
    "T_0x4000": "0x4000",
    "T_0xFFFF": "0xFFFF",
}).enum_type

PMBUSCapablePSU_InfoTypes = EnumWrapper("PMBUSCapablePSU_InfoTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PMBUSCapablePSU_PlatformCapabilityTypes = EnumWrapper("PMBUSCapablePSU_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PMBUSVRCapable_PlatformCapabilityTypes = EnumWrapper("PMBUSVRCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PMDefaultLicenseFeatures_PMLicensingTypes = EnumWrapper("PMDefaultLicenseFeatures_PMLicensingTypes", {
    "T_02000": "02000",
    "T_0x0200": "0x0200",
    "T_0x1000": "0x1000",
    "T_0x4000": "0x4000",
    "T_0xFFFF": "0xFFFF",
}).enum_type

PMDrivenLicensing_PMLicensingTypes = EnumWrapper("PMDrivenLicensing_PMLicensingTypes", {
    "T_0": "0",
    "T_1": "1",
}).enum_type

PSPFCEnabled_ChassisPowerTypes = EnumWrapper("PSPFCEnabled_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSPFCEnabled_ServerPwrTypes = EnumWrapper("PSPFCEnabled_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSRapidOn_ChassisPowerTypes = EnumWrapper("PSRapidOn_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSRapidOn_ServerPwrTypes = EnumWrapper("PSRapidOn_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSRedPolicy_ChassisPowerTypes = EnumWrapper("PSRedPolicy_ChassisPowerTypes", {
    "A_B_Grid__Redundant": "A/B Grid  Redundant",
    "Not_Redundant": "Not Redundant",
    "PSU_Redundant": "PSU Redundant",
}).enum_type

PSRedPolicy_ServerPwrTypes = EnumWrapper("PSRedPolicy_ServerPwrTypes", {
    "A_B_Grid_Redundant": "A/B Grid Redundant",
    "Not_Redundant": "Not Redundant",
}).enum_type

PSUMismatchCapable_PlatformCapabilityTypes = EnumWrapper("PSUMismatchCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSUMismatchOverride_ChassisPowerTypes = EnumWrapper("PSUMismatchOverride_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSUMismatchOverride_ServerPwrTypes = EnumWrapper("PSUMismatchOverride_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PSURedundancyCapable_PlatformCapabilityTypes = EnumWrapper("PSURedundancyCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PTCapability_OS_BMCTypes = EnumWrapper("PTCapability_OS_BMCTypes", {
    "Capable": "Capable",
    "Not_Capable": "Not Capable",
    "Unavailable": "Unavailable",
}).enum_type

PTMode_OS_BMCTypes = EnumWrapper("PTMode_OS_BMCTypes", {
    "lom_p2p": "lom-p2p",
    "usb_p2p": "usb-p2p",
}).enum_type

PartConfigurationUpdate_LCAttributesTypes = EnumWrapper("PartConfigurationUpdate_LCAttributesTypes", {
    "Apply_Always": "Apply Always",
    "Apply_always": "Apply always",
    "Apply_only_if_Firmware_Match": "Apply only if Firmware Match",
    "Disabled": "Disabled",
}).enum_type

PartFirmwareUpdate_LCAttributesTypes = EnumWrapper("PartFirmwareUpdate_LCAttributesTypes", {
    "Allow_version_upgrade_only": "Allow version upgrade only",
    "Disable": "Disable",
    "Match_firmware_of_replaced_part": "Match firmware of replaced part",
}).enum_type

PartReplacement_LCAttributesTypes = EnumWrapper("PartReplacement_LCAttributesTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PendingActiveNIC_CurrentNICTypes = EnumWrapper("PendingActiveNIC_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PendingSelection_NICTypes = EnumWrapper("PendingSelection_NICTypes", {
    "Dedicated": "Dedicated",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
}).enum_type

PerformFactoryIdentityCertValidation_MachineTrustTypes = EnumWrapper(
    "PerformFactoryIdentityCertValidation_MachineTrustTypes", {
        "Not_Supported": "Not Supported",
        "Optional": "Optional",
        "Required": "Required",
    }).enum_type

PluginType_VirtualConsoleTypes = EnumWrapper("PluginType_VirtualConsoleTypes", {
    "ActiveX": "ActiveX",
    "HTML5": "HTML5",
    "Java": "Java",
}).enum_type

PortStatus_USBTypes = EnumWrapper("PortStatus_USBTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PostPoneNICSelectionCapable_PlatformCapabilityTypes = EnumWrapper("PostPoneNICSelectionCapable_PlatformCapabilityTypes",
                                                                  {
                                                                      "Disabled": "Disabled",
                                                                      "Enabled": "Enabled",
                                                                  }).enum_type

PowerBudgetCapable_PlatformCapabilityTypes = EnumWrapper("PowerBudgetCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerBudgetOverride_ServerPwrTypes = EnumWrapper("PowerBudgetOverride_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerCapSetting_ServerPwrTypes = EnumWrapper("PowerCapSetting_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerCapState_PrivateStoreTypes = EnumWrapper("PowerCapState_PrivateStoreTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

PowerConfigReset_ServerPwrMonTypes = EnumWrapper("PowerConfigReset_ServerPwrMonTypes", {
    "ClrAll": "ClrAll",
    "ClrCumulaPowerAndTime": "ClrCumulaPowerAndTime",
    "ClrPeaKValueAndTIme": "ClrPeaKValueAndTIme",
    "ClrPeakAndCumulaValue": "ClrPeakAndCumulaValue",
    "T_None": "None",
}).enum_type

PowerConfigurationCapable_PlatformCapabilityTypes = EnumWrapper("PowerConfigurationCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerConfigurationRemovalCapable_PlatformCapabilityTypes = EnumWrapper(
    "PowerConfigurationRemovalCapable_PlatformCapabilityTypes", {
        "Disabled": "Disabled",
        "Enabled": "Enabled",
    }).enum_type

PowerInventoryCapable_PlatformCapabilityTypes = EnumWrapper("PowerInventoryCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerLogEnable_SysLogTypes = EnumWrapper("PowerLogEnable_SysLogTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerMonitoringCapable_PlatformCapabilityTypes = EnumWrapper("PowerMonitoringCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PowerRedundancy_InfoTypes = EnumWrapper("PowerRedundancy_InfoTypes", {
    "grid_redundancy": "grid redundancy",
    "non_redundant": "non redundant",
    "psu_redundant": "psu redundant",
}).enum_type

PowerState_InfoTypes = EnumWrapper("PowerState_InfoTypes", {
    "Off": "Off",
    "On": "On",
    "PoweringOff": "PoweringOff",
    "PoweringOn": "PoweringOn",
}).enum_type

PrebootConfig_LocalSecurityTypes = EnumWrapper("PrebootConfig_LocalSecurityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PreferredLanguage_SupportAssistTypes = EnumWrapper("PreferredLanguage_SupportAssistTypes", {
    "English": "English",
    "French": "French",
    "German": "German",
    "Japanese": "Japanese",
    "Simplified_Chinese": "Simplified Chinese",
    "Spanish": "Spanish",
}).enum_type

Presence_QuickSyncTypes = EnumWrapper("Presence_QuickSyncTypes", {
    "Absent": "Absent",
    "Not_Supported": "Not Supported",
    "Present": "Present",
}).enum_type

Presence_vFlashSDTypes = EnumWrapper("Presence_vFlashSDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PrivLimit_IPMILanTypes = EnumWrapper("PrivLimit_IPMILanTypes", {
    "Administrator": "Administrator",
    "Operator": "Operator",
    "User": "User",
}).enum_type

PrivacyProtocol_UsersTypes = EnumWrapper("PrivacyProtocol_UsersTypes", {
    "AES": "AES",
    "DES": "DES",
    "T_None": "None",
}).enum_type

Privilege_UsersTypes = EnumWrapper("Privilege_UsersTypes", {
    "NoAccess": "0",
    "Readonly": "1",
    "Operator": "499",
    "Administrator": "511",
}).enum_type

ProSupportPlusRecommendationsReport_SupportAssistTypes = EnumWrapper(
    "ProSupportPlusRecommendationsReport_SupportAssistTypes", {
        "Disabled": "Disabled",
        "Enabled": "Enabled",
    }).enum_type

ProtocolEnable_UsersTypes = EnumWrapper("ProtocolEnable_UsersTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

QualifierTemp_LCDTypes = EnumWrapper("QualifierTemp_LCDTypes", {
    "C": "C",
    "F": "F",
}).enum_type

QualifierWatt_LCDTypes = EnumWrapper("QualifierWatt_LCDTypes", {
    "BTU_hr": "BTU/hr",
    "Watts": "Watts",
}).enum_type

QuickSyncButtonEnable_QuickSyncTypes = EnumWrapper("QuickSyncButtonEnable_QuickSyncTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RSMCapability_RSMTypes = EnumWrapper("RSMCapability_RSMTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RSMSetting_RSMTypes = EnumWrapper("RSMSetting_RSMTypes", {
    "Manage_and_Monitor": "Manage and Monitor",
    "Monitor": "Monitor",
    "T_None": "None",
}).enum_type

RSPICapable_PlatformCapabilityTypes = EnumWrapper("RSPICapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RangeEnable_IPBlockingTypes = EnumWrapper("RangeEnable_IPBlockingTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RapidOnPrimaryPSU_ChassisPowerTypes = EnumWrapper("RapidOnPrimaryPSU_ChassisPowerTypes", {
    "GRID1": "GRID1",
    "GRID2": "GRID2",
}).enum_type

RapidOnPrimaryPSU_ServerPwrTypes = EnumWrapper("RapidOnPrimaryPSU_ServerPwrTypes", {
    "PSU1": "PSU1",
    "PSU2": "PSU2",
}).enum_type

ReadAuthentication_QuickSyncTypes = EnumWrapper("ReadAuthentication_QuickSyncTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

RedundancyEnabled_ThermalConfigTypes = EnumWrapper("RedundancyEnabled_ThermalConfigTypes", {
    "Full": "Full",
    "Lost": "Lost",
    "Not_Applicable": "Not Applicable",
}).enum_type

Redundancy_InfoTypes = EnumWrapper("Redundancy_InfoTypes", {
    "ac_redundant": "ac redundant",
    "non_redunant": "non redunant",
    "psu_and_ac_redundant": "psu and ac redundant",
    "psu_redundant": "psu redundant",
}).enum_type

RegisterHostDNS_SECONDARYNICTypes = EnumWrapper("RegisterHostDNS_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

RemainingRatedWriteEnduranceAlertThreshold_StorageTypes = EnumWrapper(
    "RemainingRatedWriteEnduranceAlertThreshold_StorageTypes", {
        "T_1_99": "1-99",
    }).enum_type

RemoteEnablementCapable_PlatformCapabilityTypes = EnumWrapper("RemoteEnablementCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Repeat_AutoBackupTypes = EnumWrapper("Repeat_AutoBackupTypes", {
    "T_1_366": "1-366",
}).enum_type

Repeat_AutoUpdateTypes = EnumWrapper("Repeat_AutoUpdateTypes", {
    "T_1_366": "1-366",
}).enum_type

ResetType_SecureDefaultPasswordTypes = EnumWrapper("ResetType_SecureDefaultPasswordTypes", {
    "Default": "Default",
    "Legacy": "Legacy",
}).enum_type

Role_GroupManagerTypes = EnumWrapper("Role_GroupManagerTypes", {
    "Member": "Member",
    "Primary": "Primary",
    "Secondary": "Secondary",
    "Unconfigured": "Unconfigured",
}).enum_type

SCFWUpdateState_SC_BMCTypes = EnumWrapper("SCFWUpdateState_SC_BMCTypes", {
    "Availiable_to_SC": "Availiable to SC",
    "Complete": "Complete",
    "Downloaded": "Downloaded",
    "Failed": "Failed",
    "Not_in_progress": "Not in progress",
}).enum_type

SCPwrMonitoringCapable_PlatformCapabilityTypes = EnumWrapper("SCPwrMonitoringCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SDCardCapable_PlatformCapabilityTypes = EnumWrapper("SDCardCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SELOEMEventFilterEnable_LoggingTypes = EnumWrapper("SELOEMEventFilterEnable_LoggingTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SLBAllocOverride_ServerPwrTypes = EnumWrapper("SLBAllocOverride_ServerPwrTypes", {
    "Disable_Next_PowerOn": "Disable Next PowerOn",
    "Enable_Next_PowerOn": "Enable Next PowerOn",
    "Enable_this_PowerOn": "Enable this PowerOn",
}).enum_type

SLBBoundsCheck_ServerPwrTypes = EnumWrapper("SLBBoundsCheck_ServerPwrTypes", {
    "Not_Suppressed": "Not Suppressed",
    "Suppressed": "Suppressed",
}).enum_type

SLBPersistence_ServerPwrTypes = EnumWrapper("SLBPersistence_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SLBState_ServerPwrTypes = EnumWrapper("SLBState_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SMTPAuthentication_RemoteHostsTypes = EnumWrapper("SMTPAuthentication_RemoteHostsTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SNMPOnHostOS_ServiceModuleTypes = EnumWrapper("SNMPOnHostOS_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SNMPProtocol_SNMPTypes = EnumWrapper("SNMPProtocol_SNMPTypes", {
    "All": "All",
    "SNMPv3": "SNMPv3",
}).enum_type

SSLEncryptionBitLength_VNCServerTypes = EnumWrapper("SSLEncryptionBitLength_VNCServerTypes", {
    "Auto_Negotiate": "Auto Negotiate",
    "Disabled": "Disabled",
    "T_128_Bit_or_higher": "128-Bit or higher",
    "T_168_Bit_or_higher": "168-Bit or higher",
    "T_256_Bit_or_higher": "256-Bit or higher",
}).enum_type

SSLEncryptionBitLength_WebServerTypes = EnumWrapper("SSLEncryptionBitLength_WebServerTypes", {
    "Auto_Negotiate": "Auto-Negotiate",
    "T_128_Bit_or_higher": "128-Bit or higher",
    "T_168_Bit_or_higher": "168-Bit or higher",
    "T_256_Bit_or_higher": "256-Bit or higher",
}).enum_type

SSOEnable_ActiveDirectoryTypes = EnumWrapper("SSOEnable_ActiveDirectoryTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SWRaidMonitoring_ServiceModuleTypes = EnumWrapper("SWRaidMonitoring_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ScheduleBasedAutoCollection_SupportAssistTypes = EnumWrapper("ScheduleBasedAutoCollection_SupportAssistTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Schema_ActiveDirectoryTypes = EnumWrapper("Schema_ActiveDirectoryTypes", {
    "Extended_Schema": "Extended Schema",
    "Standard_Schema": "Standard Schema",
}).enum_type

SecurityMode_LCDTypes = EnumWrapper("SecurityMode_LCDTypes", {
    "Disabled": "Disabled",
    "ViewAndModify": "ViewAndModify",
    "ViewOnly": "ViewOnly",
}).enum_type

Selection_CurrentNICTypes = EnumWrapper("Selection_CurrentNICTypes", {
    "Dedicated": "Dedicated",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
}).enum_type

Selection_NICTypes = EnumWrapper("Selection_NICTypes", {
    "Dedicated": "Dedicated",
    "LOM1": "LOM1",
    "LOM2": "LOM2",
    "LOM3": "LOM3",
    "LOM4": "LOM4",
}).enum_type

ServerGen_InfoTypes = EnumWrapper("ServerGen_InfoTypes", {
    "T_12G": "12G",
    "T_13G": "13G",
    "T_14G": "14G",
}).enum_type

ServiceEnabled_FWUpdateServiceTypes = EnumWrapper("ServiceEnabled_FWUpdateServiceTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

ServiceModuleEnable_ServiceModuleTypes = EnumWrapper("ServiceModuleEnable_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ServiceModuleState_ServiceModuleTypes = EnumWrapper("ServiceModuleState_ServiceModuleTypes", {
    "Not_Running": "Not Running",
    "Running": "Running",
}).enum_type

SledConfig_ServerInfoTypes = EnumWrapper("SledConfig_ServerInfoTypes", {
    "T_0": "0",
    "T_1": "1",
    "T_2": "2",
    "T_255": "255",
    "T_3": "3",
}).enum_type

SlotNumber_ECTypes = EnumWrapper("SlotNumber_ECTypes", {
    "T_1": "1",
    "T_2": "2",
}).enum_type

SlotPowerPriority_ChassisPowerTypes = EnumWrapper("SlotPowerPriority_ChassisPowerTypes", {
    "High": "High",
    "Low": "Low",
    "Shutdown": "Shutdown",
}).enum_type

SlotState_PCIeSlotLFMTypes = EnumWrapper("SlotState_PCIeSlotLFMTypes", {
    "Defined": "Defined",
    "Not_Defined": "Not-Defined",
}).enum_type

SmartCardCRLEnable_SmartCardTypes = EnumWrapper("SmartCardCRLEnable_SmartCardTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SmartCardLoginCapable_PlatformCapabilityTypes = EnumWrapper("SmartCardLoginCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SmartCardLogonEnable_SmartCardTypes = EnumWrapper("SmartCardLogonEnable_SmartCardTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "Enabled_With_Racadm": "Enabled With Racadm",
}).enum_type

SolEnable_UsersTypes = EnumWrapper("SolEnable_UsersTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Speed_CurrentNICTypes = EnumWrapper("Speed_CurrentNICTypes", {
    "T_10": "10",
    "T_100": "100",
    "T_1000": "1000",
}).enum_type

Speed_NICTypes = EnumWrapper("Speed_NICTypes", {
    "T_10": "10",
    "T_100": "100",
    "T_1000": "1000",
}).enum_type

State_CMCSNMPTrapIPv6Types = EnumWrapper("State_CMCSNMPTrapIPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_InfoTypes = EnumWrapper("State_InfoTypes", {
    "Absent": "Absent",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "InTest": "InTest",
    "StandbyOffline": "StandbyOffline",
    "StandbySpare": "StandbySpare",
    "Starting": "Starting",
}).enum_type

State_LDAPRoleGroupTypes = EnumWrapper("State_LDAPRoleGroupTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_MSMSNMPAlertTypes = EnumWrapper("State_MSMSNMPAlertTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_MSMSNMPTrapIPv4Types = EnumWrapper("State_MSMSNMPTrapIPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_MSMSNMPTrapIPv6Types = EnumWrapper("State_MSMSNMPTrapIPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_RedundancyTypes = EnumWrapper("State_RedundancyTypes", {
    "Absent": "Absent",
    "Deferring": "Deferring",
    "Disabled": "Disabled",
    "Enabled": "Enabled",
    "InTest": "InTest",
    "Quiesced": "Quiesced",
    "StandbyOffline": "StandbyOffline",
    "StandbySpare": "StandbySpare",
    "Starting": "Starting",
    "UnavailableOffline": "UnavailableOffline",
    "Updating": "Updating",
}).enum_type

State_SNMPAlertTypes = EnumWrapper("State_SNMPAlertTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_SNMPTrapIPv4Types = EnumWrapper("State_SNMPTrapIPv4Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

State_SNMPTrapIPv6Types = EnumWrapper("State_SNMPTrapIPv6Types", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Status_GroupManagerTypes = EnumWrapper("Status_GroupManagerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Status_QuickSyncTypes = EnumWrapper("Status_QuickSyncTypes", {
    "Degraded": "Degraded",
    "Error": "Error",
    "Ok": "Ok",
    "Unknown": "Unknown",
}).enum_type

Status_RFSTypes = EnumWrapper("Status_RFSTypes", {
    "Done": "Done",
    "Error": "Error",
    "Pending": "Pending",
}).enum_type

Status_UpdateTypes = EnumWrapper("Status_UpdateTypes", {
    "T_1": "1",
    "T_10": "10",
    "T_11": "11",
    "T_12": "12",
    "T_13": "13",
    "T_14": "14",
    "T_15": "15",
    "T_16": "16",
    "T_17": "17",
    "T_2": "2",
    "T_3": "3",
    "T_4": "4",
    "T_5": "5",
    "T_6": "6",
    "T_7": "7",
    "T_8": "8",
    "T_9": "9",
    "_1": "-1",
}).enum_type

StorageTargetPersistencePolicy_IOIDOptTypes = EnumWrapper("StorageTargetPersistencePolicy_IOIDOptTypes", {
    "ACPowerLoss": "ACPowerLoss",
    "ColdReset": "ColdReset",
    "ColdReset__ACPowerLoss": "ColdReset, ACPowerLoss",
    "T_None": "None",
    "WarmReset": "WarmReset",
    "WarmReset__ACPowerLoss": "WarmReset, ACPowerLoss",
    "WarmReset__ColdReset": "WarmReset, ColdReset",
    "WarmReset__ColdReset__ACPowerLoss": "WarmReset, ColdReset, ACPowerLoss",
}).enum_type

SubSystemPowerMonitoringCapable_PlatformCapabilityTypes = EnumWrapper(
    "SubSystemPowerMonitoringCapable_PlatformCapabilityTypes", {
        "Disabled": "Disabled",
        "Enabled": "Enabled",
    }).enum_type

SupportAssistEULAAccepted_SupportAssistTypes = EnumWrapper("SupportAssistEULAAccepted_SupportAssistTypes", {
    "T_False": "False",
    "T_True": "True",
}).enum_type

SupportAssistEnableState_SupportAssistTypes = EnumWrapper("SupportAssistEnableState_SupportAssistTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SysLogEnable_SysLogTypes = EnumWrapper("SysLogEnable_SysLogTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

SystemCFMSupport_ThermalSettingsTypes = EnumWrapper("SystemCFMSupport_ThermalSettingsTypes", {
    "Not_Supported": "Not Supported",
    "Supported": "Supported",
}).enum_type

SystemLockdown_LockdownTypes = EnumWrapper("SystemLockdown_LockdownTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

TLSProtocol_WebServerTypes = EnumWrapper("TLSProtocol_WebServerTypes", {
    "TLS_1_0_and_Higher": "TLS 1.0 and Higher",
    "TLS_1_1_and_Higher": "TLS 1.1 and Higher",
    "TLS_1_2_Only": "TLS 1.2 Only",
}).enum_type

TempPowerThresholdCapable_PlatformCapabilityTypes = EnumWrapper("TempPowerThresholdCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ThermalManagementCapable_PlatformCapabilityTypes = EnumWrapper("ThermalManagementCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ThermalProfile_ThermalSettingsTypes = EnumWrapper("ThermalProfile_ThermalSettingsTypes", {
    "Acoustic_Optimized": "Acoustic Optimized",
    "Default_Thermal_Profile_Settings": "Default Thermal Profile Settings",
    "Maximum_Performance": "Maximum Performance",
    "Minimum_Power": "Minimum Power",
}).enum_type

ThermalStatus_InfoTypes = EnumWrapper("ThermalStatus_InfoTypes", {
    "Critical": "Critical",
    "OK": "OK",
    "Warning": "Warning",
}).enum_type

Time_AutoBackupTypes = EnumWrapper("Time_AutoBackupTypes", {
    "hh_mm_Represents_hour_and_minute_of_day_to_run": "hh:mm Represents hour and minute of day to run",
}).enum_type

Time_AutoUpdateTypes = EnumWrapper("Time_AutoUpdateTypes", {
    "hh_mm_Represents_hour_and_minute_of_day_to_run": "hh:mm Represents hour and minute of day to run",
}).enum_type

TitleBarOption_WebServerTypes = EnumWrapper("TitleBarOption_WebServerTypes", {
    "Auto": "Auto",
    "Custom": "Custom",
    "DNS_RAC_Name": "DNS RAC Name",
    "IP_Address": "IP Address",
    "Service_Tag": "Service Tag",
    "System_Host_Name": "System Host Name",
}).enum_type

TrapFormat_SNMPTypes = EnumWrapper("TrapFormat_SNMPTypes", {
    "SNMPv1": "SNMPv1",
    "SNMPv2": "SNMPv2",
    "SNMPv3": "SNMPv3",
}).enum_type

TroubleshootingMode_IntegratedDatacenterTypes = EnumWrapper("TroubleshootingMode_IntegratedDatacenterTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Type_BrandingTypes = EnumWrapper("Type_BrandingTypes", {
    "DeBrand": "DeBrand",
    "Default": "Default",
    "ReBrand": "ReBrand",
}).enum_type

Type_ButtonLCPTypes = EnumWrapper("Type_ButtonLCPTypes", {
    "Identify": "Identify",
    "Invalid": "Invalid",
    "Power": "Power",
}).enum_type

Type_ButtonRCPTypes = EnumWrapper("Type_ButtonRCPTypes", {
    "Identify": "Identify",
    "Invalid": "Invalid",
    "Power": "Power",
}).enum_type

Type_IndicatorLCPTypes = EnumWrapper("Type_IndicatorLCPTypes", {
    "Bar": "Bar",
    "Chassis": "Chassis",
    "Fan": "Fan",
    "IOM": "IOM",
    "Invalid": "Invalid",
    "StackGroup": "StackGroup",
    "Temperature": "Temperature",
}).enum_type

Type_InfoTypes = EnumWrapper("Type_InfoTypes", {
    "T_12G_13G_14G": "12G/13G/14G",
    "T_12G_DCS": "12G DCS",
    "T_12G_Modular": "12G Modular",
    "T_12G_Monolithic": "12G Monolithic",
    "T_13G_DCS": "13G DCS",
    "T_13G_Modular": "13G Modular",
    "T_13G_Monolithic": "13G Monolithic",
    "T_14G_DCS": "14G DCS",
    "T_14G_Modular": "14G Modular",
    "T_14G_Monolithic": "14G Monolithic",
}).enum_type

Type_SlotConfigTypes = EnumWrapper("Type_SlotConfigTypes", {
    "CMC": "CMC",
    "Fan": "Fan",
    "IOM": "IOM",
    "PSU": "PSU",
    "Sled": "Sled",
}).enum_type

UnderVoltageCLSTOverride_ChassisPowerTypes = EnumWrapper("UnderVoltageCLSTOverride_ChassisPowerTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

UnderVoltageCLSTOverride_ServerPwrTypes = EnumWrapper("UnderVoltageCLSTOverride_ServerPwrTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

Updateable_FPGAFWInventoryTypes = EnumWrapper("Updateable_FPGAFWInventoryTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

Updateable_FReDFWInventoryTypes = EnumWrapper("Updateable_FReDFWInventoryTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

Updateable_FWInventoryTypes = EnumWrapper("Updateable_FWInventoryTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

UserPowerCapBoundCapable_PlatformCapabilityTypes = EnumWrapper("UserPowerCapBoundCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

UserPowerCapCapable_PlatformCapabilityTypes = EnumWrapper("UserPowerCapCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

UserProxyType_LCAttributesTypes = EnumWrapper("UserProxyType_LCAttributesTypes", {
    "HTTP": "HTTP",
    "SOCKS": "SOCKS",
}).enum_type

VLANEnable_SECONDARYNICTypes = EnumWrapper("VLANEnable_SECONDARYNICTypes", {
    "Disable": "Disable",
    "Enable": "Enable",
}).enum_type

VLanEnable_CurrentNICTypes = EnumWrapper("VLanEnable_CurrentNICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

VLanEnable_NICTypes = EnumWrapper("VLanEnable_NICTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

VLanPort_NICTypes = EnumWrapper("VLanPort_NICTypes", {
    "Both": "Both",
    "Dedicated_port_only": "Dedicated port only",
    "LOM_ports_only": "LOM ports only",
}).enum_type

VLanSetting_CurrentNICTypes = EnumWrapper("VLanSetting_CurrentNICTypes", {
    "Both_Enable": "Both Enable",
    "Disabled_on_Dedicated": "Disabled on Dedicated",
    "Disabled_on_share": "Disabled on share",
}).enum_type

VLanSetting_NICTypes = EnumWrapper("VLanSetting_NICTypes", {
    "Both_Enable": "Both Enable",
    "Disabled_on_Dedicated": "Disabled on Dedicated",
    "Disabled_on_share": "Disabled on share",
}).enum_type

VideoCaptureEnable_VirtualConsoleTypes = EnumWrapper("VideoCaptureEnable_VirtualConsoleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

ViewAssetServiceExpressTag_LCDTypes = EnumWrapper("ViewAssetServiceExpressTag_LCDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

VirtualAddressManagement_LCAttributesTypes = EnumWrapper("VirtualAddressManagement_LCAttributesTypes", {
    "Console": "Console",
    "FlexAddress": "FlexAddress",
}).enum_type

VirtualAddressPersistencePolicyAuxPwrd_IOIDOptTypes = EnumWrapper("VirtualAddressPersistencePolicyAuxPwrd_IOIDOptTypes",
                                                                  {
                                                                      "ACPowerLoss": "ACPowerLoss",
                                                                      "ColdReset": "ColdReset",
                                                                      "ColdReset__ACPowerLoss": "ColdReset, ACPowerLoss",
                                                                      "T_None": "None",
                                                                      "WarmReset": "WarmReset",
                                                                      "WarmReset__ACPowerLoss": "WarmReset, ACPowerLoss",
                                                                      "WarmReset__ColdReset": "WarmReset, ColdReset",
                                                                      "WarmReset__ColdReset__ACPowerLoss": "WarmReset, ColdReset, ACPowerLoss",
                                                                  }).enum_type

VirtualAddressPersistencePolicyNonAuxPwrd_IOIDOptTypes = EnumWrapper(
    "VirtualAddressPersistencePolicyNonAuxPwrd_IOIDOptTypes", {
        "ACPowerLoss": "ACPowerLoss",
        "ColdReset": "ColdReset",
        "ColdReset__ACPowerLoss": "ColdReset, ACPowerLoss",
        "T_None": "None",
        "WarmReset": "WarmReset",
        "WarmReset__ACPowerLoss": "WarmReset, ACPowerLoss",
        "WarmReset__ColdReset": "WarmReset, ColdReset",
        "WarmReset__ColdReset__ACPowerLoss": "WarmReset, ColdReset, ACPowerLoss",
    }).enum_type

WMIInfo_ServiceModuleTypes = EnumWrapper("WMIInfo_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WatchdogRecoveryAction_ServiceModuleTypes = EnumWrapper("WatchdogRecoveryAction_ServiceModuleTypes", {
    "Powercycle": "Powercycle",
    "Poweroff": "Poweroff",
    "Reboot": "Reboot",
    "T_None": "None",
}).enum_type

WatchdogState_ServiceModuleTypes = EnumWrapper("WatchdogState_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WeekofMonth_AutoBackupTypes = EnumWrapper("WeekofMonth_AutoBackupTypes", {
    "__1_4__L_Default__": "*,1-4, L,Default:*",
}).enum_type

WeekofMonth_AutoUpdateTypes = EnumWrapper("WeekofMonth_AutoUpdateTypes", {
    "__1_4__L_Default__": "*,1-4, L,Default:*",
}).enum_type

WiFiCapable_PlatformCapabilityTypes = EnumWrapper("WiFiCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WifiEnable_QuickSyncTypes = EnumWrapper("WifiEnable_QuickSyncTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WizardEnable_LCDTypes = EnumWrapper("WizardEnable_LCDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WriteProtect_vFlashSDTypes = EnumWrapper("WriteProtect_vFlashSDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

WriteProtected_RFSTypes = EnumWrapper("WriteProtected_RFSTypes", {
    "Read_Only": "Read Only",
    "Read_Write": "Read Write",
}).enum_type

d9netsettingstate_NICTypes = EnumWrapper("d9netsettingstate_NICTypes", {
    "Completed": "Completed",
    "Idle": "Idle",
    "InProgress": "InProgress",
}).enum_type

d9netusbsettingstate_NICTypes = EnumWrapper("d9netusbsettingstate_NICTypes", {
    "Completed": "Completed",
    "Idle": "Idle",
    "InProgress": "InProgress",
    "Initialized": "Initialized",
}).enum_type

iDRACDirectUSBNICCapable_PlatformCapabilityTypes = EnumWrapper("iDRACDirectUSBNICCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

iDRACHardReset_ServiceModuleTypes = EnumWrapper("iDRACHardReset_ServiceModuleTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

iDRACRev_SysInfoTypes = EnumWrapper("iDRACRev_SysInfoTypes", {
    "ARev": "ARev",
    "XRev": "XRev",
}).enum_type

vConsoleIndication_LCDTypes = EnumWrapper("vConsoleIndication_LCDTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

vFlashCapable_PlatformCapabilityTypes = EnumWrapper("vFlashCapable_PlatformCapabilityTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type
