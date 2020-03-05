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
from omsdk.sdkcenum import EnumWrapper, TypeHelper
import logging

logger = logging.getLogger(__name__)

iDRACLicenseEnum = EnumWrapper("iDRACLicenseEnum", {
    "License": "License",
    "LicensableDevice": "LicensableDevice",
}).enum_type

iDRACFirmEnum = EnumWrapper("iDRACFirmEnum", {
    "Firmware": "Firmware",
}).enum_type

iDRACLogsEnum = EnumWrapper("iDRACLogEnum", {
    "Logs": "Logs",
    "SELLog": "SELLog"
}).enum_type

JobStatusEnum = EnumWrapper("iDRACJSE", {
    'Success': 'Success',
    'InProgress': 'InProgress',
    'Failed': 'Failed',
    'Invalid': 'Invalid',
}).enum_type

ReturnValue = EnumWrapper("RV", {
    "Success": 0,
    "Error": 2,
    "JobCreated": 4096,
    "Invalid": -1,
}).enum_type

iDRACJobsEnum = EnumWrapper("iDRACJobEnum", {
    "Jobs": "Jobs",
}).enum_type

iDRACOSDJobsEnum = EnumWrapper("iDRACOSDJobEnum", {
    "OSDJobs": "OSDJobs",
}).enum_type

PowerStateEnum = EnumWrapper("PSE", {"PowerOn": 2,
                                     "SoftPowerCycle": 5,
                                     "SoftPowerOff": 8,
                                     "PowerCycle": 9,
                                     "HardReset": 10,
                                     "DiagnosticInterrupt": 11,
                                     "GracefulPowerOff": 12
                                     }).enum_type

PowerBootEnum = EnumWrapper("PBE", {"Enabled": 2,
                                    "Disabled": 3,
                                    "Reset": 11,
                                    }).enum_type

ConfigStateEnum = EnumWrapper("CSE", {
    "Enabled": 'Enabled',
    "Disabled": 'Disabled',
    "Unknown": 'Unknown',
}).enum_type

RebootJobType = EnumWrapper("RJT", {
    'PowerCycle': 1,  # 30 s
    'GracefulRebootWithoutShutdown': 2,  # 5 min
    'GracefulRebootWithForcedShutdown': 3  # 5 min
}).enum_type

BootModeEnum = EnumWrapper('BME', {
    'Bios': 'Bios',
    'Uefi': 'Uefi',
    'Unknown': 'Unknown'
}).enum_type

BlinkLEDEnum = EnumWrapper('BL', {
    # Off and Disable are same
    'Off': 0,
    'Disable': 0,
    # On and Enable are same
    'On': 1,
    'Enable': 1,
    # OnForDuration and EnableForDuration are same
    'OnForDuration': 2,
    'EnableForDuration': 2
}).enum_type

BIOSPasswordTypeEnum = EnumWrapper("BIOSPasswordType", {
    'System': 1,
    'Setup': 2
}).enum_type

ExportMethodEnum = EnumWrapper("ExportMethod", {
    'Default': 'Default',
    'Clone': 'Clone',
    'Replace': 'Replace',
}).enum_type

ExportFormatEnum = EnumWrapper("ExportFormatEnum", {
    'XML': 'XML',
    'JSON': 'JSON',
}).enum_type

ExportFormatWsmanEnum = EnumWrapper("ExportFormatWsmanEnum", {
    'XML': 0,
    'JSON': 1,
}).enum_type

ExportFormatRedfishEnum = EnumWrapper("ExportFormatRedfishEnum", {
    'XML': 'XML',
    'JSON': 'JSON',
}).enum_type

ResetToFactoryPreserveEnum = EnumWrapper('ResetToFactoryPreserveEnum', {
    'ResetExceptNICAndUsers': 0,
    'ResetAll': 1,
    'ResetAllExceptDefaultUser': 2
}).enum_type

ResetForceEnum = EnumWrapper('ResetForceEnum', {
    'Graceful': 0,
    'Force': 1,
}).enum_type

SCPTargetEnum = EnumWrapper("SCPTargetEnum", {
    'ALL': 'ALL',
    'IDRAC': 'IDRAC',
    'BIOS': 'BIOS',
    'NIC': 'NIC',
    'RAID': 'RAID',
}).enum_type

RAIDLevelsEnum = EnumWrapper("RLE", {
    'RAID_0': 'RAID 0',
    'RAID_1': 'RAID 1',
    'RAID_5': 'RAID 5',
    'RAID_6': 'RAID 6',
    'RAID_10': 'RAID 10',
    'RAID_50': 'RAID 50',
    'RAID_60': 'RAID 60',
}).enum_type

LicenseApiOptionsEnum = EnumWrapper("LAO", {
    'NoOptions': 0,
    'Force': 1,
    'All': 2
}).enum_type

TLSOptions_Map = {
    'TLS_1_0': 'TLS 1.0 and Higher',
    'TLS_1_1': 'TLS 1.1 and Higher',
    'TLS_1_2': 'TLS 1.2 Only'
}

TLSOptions = EnumWrapper("TLS", TLSOptions_Map).enum_type

SSLBits_Map = {
    'S128': '128-Bit or higher',
    'S168': '168-Bit or higher',
    'S256': '256-Bit or higher',
    'Auto': 'Auto Negotiate'
}

SSLBits = EnumWrapper("SSL", SSLBits_Map).enum_type

SSLCertTypeEnum = EnumWrapper("SSLCertTypeEnum", {
    'Web_Server_Cert': 1,
    'CA_Cert': 2,
    'Custom_Signing_Cert': 3,
    'Client_Trust_Cert': 4
}).enum_type

ShutdownTypeEnum = EnumWrapper('ShutdownTypeEnum', {
    'Graceful': 'Graceful',
    'Forced': 'Forced',
    'NoReboot': 'NoReboot'
}).enum_type

ShutdownTypeWsmanEnum = EnumWrapper('ShutdownTypeWsmanEnum', {
    'Graceful': 0,
    'Forced': 1,
    'NoReboot': 2
}).enum_type

ShutdownTypeRedfishEnum = EnumWrapper('ShutdownTypeRedfishEnum', {
    'Graceful': 'Graceful',
    'Forced': 'Forced',
    'NoReboot': 'NoReboot'
}).enum_type

HostEndPowerStateEnum = EnumWrapper('EPSE', {
    'On': 1,
    'Off': 2,
}).enum_type

UserPrivilegeEnum = EnumWrapper("UserPrivilegeEnum", {
    "Administrator": 511,
    "Operator": 499,
    "ReadOnly": 1,
    "NoPrivilege": 0,
}).enum_type

SNMPTrapFormatEnum = EnumWrapper("SNMPTrapFormatEnum", {
    "SNMPv1": 'SNMPv1',
    "SNMPv2": 'SNMPv2',
    "SNMPv3": 'SNMPv3',
}).enum_type

SNMPProtocolEnum = EnumWrapper("SPE", {
    "All": 'All',
    "SNMPv3": 'SNMPv3',
}).enum_type

ShareTypeEnum = EnumWrapper('ShareTypeEnum', {
    'NFS': 0,
    'CIFS': 2,
    'Local': 4,
    'HTTP': 5,
    'HTTPS': 6
}).enum_type

IFRShareTypeEnum = EnumWrapper('IFRShareTypeEnum', {
    'nfs': 'NFS',
    'cifs': 'CIFS',
    'ftp': 'FTP',
    'http': 'HTTP',
    'https': 'HTTPS',
    'tftp': 'TFTP'
}).enum_type

ApplyUpdateEnum = EnumWrapper('ApplyUpdateEnum', {
    'True': 'True',
    'False': 'False'
}).enum_type

URLApplyUpdateEnum = EnumWrapper('URLApplyUpdateEnum', {
    'True': 1,
    'False': 0
}).enum_type

RebootEnum = EnumWrapper('RebootEnum', {
    'True': 'TRUE',
    'False': 'FALSE'
}).enum_type

URLShareTypeEnum = EnumWrapper('URLShareTypeEnum', {
    'ftp': 1,
    'http': 3,
    'https': 6
}).enum_type

URLCertWarningEnum = EnumWrapper('URLCertWarningEnum', {
    'True': 2,
    'False': 1
}).enum_type

VideoLogsFileTypeEnum = EnumWrapper("VideoLogsFileTypeEnum", {
    'Boot_Capture': 1,
    'Crash_Capture': 2
}).enum_type

FileOperationEnum = EnumWrapper('FileOperationEnum', {
    'Import': 1,
    'Export': 2,
    'Both': 3,
}).enum_type

FileTypeEnum = EnumWrapper('FileTypeEnum', {
    'All': 0,
    'SystemConfigXML': 1,
    'LCLogs': 2,
    'Inventory': 3,
    'FactoryConfig': 4,
    'TSR': 5,
    'BootVideoLogs': 6,
    'Diagnostics': 7,
    'LCFullLogs': 8,
    'CrashVideoLogs': 9
}).enum_type

PayLoadEncodingEnum = EnumWrapper('PayLoadEncodingEnum', {
    'Text': 1,
    'Base64': 2,
}).enum_type

ExportUseEnum = EnumWrapper('ExportUseEnum', {
    'Default': 'Default',
    'Clone': 'Clone',
    'Replace': 'Replace'
}).enum_type

ExportUseWsmanEnum = EnumWrapper("ExportUseWsmanEnum", {
    'Default': 0,
    'Clone': 1,
    'Replace': 2,
}).enum_type

ExportUseRedfishEnum = EnumWrapper('ExportUseRedfishEnum', {
    'Default': 'Default',
    'Clone': 'Clone',
    'Replace': 'Replace'
}).enum_type

IncludeInExportEnum = EnumWrapper('IncludeInExportEnum', {
    'Default': 'Default',
    'Include_Read_Only': 'Include_Read_Only',
    'Include_Password_Hash_Values': 'Include_Password_Hash_Values',
    'Include_Both': 'Include_Both'
}).enum_type

IncludeInExportWsmanEnum = EnumWrapper('IncludeInExportWsmanEnum', {
    'Default': 0,
    'Include_Read_Only': 1,
    'Include_Password_Hash_Values': 2,
    'Include_Both': 3
}).enum_type

IncludeInExportRedfishEnum = EnumWrapper('IncludeInExportRedfishEnum', {
    'Default': 'Default',
    'Include_Read_Only': 'IncludeReadOnly',
    'Include_Password_Hash_Values': 'IncludePasswordHashValues',
    'Include_Both': 'IncludeReadOnly,IncludePasswordHashValues'
}).enum_type

ProxySupportEnum = EnumWrapper('ProxySupportEnum', {
    'Off': 1,
    'Use_Default_Settings': 2,
    'Use_Custom_Settings': 3
}).enum_type

ProxyTypeEnum = EnumWrapper('ProxyTypeEnum', {
    'HTTP': 0,
    'SOCKS': 1
}).enum_type

IgnoreCertWarningEnum = EnumWrapper('IgnoreCertWarningEnum', {
    'Off': 1,
    'On': 2
}).enum_type

IgnoreCertWarnEnum = EnumWrapper('IgnoreCertWarnEnum', {
    'Off': 'Off',
    'On': 'On'
}).enum_type

EndHostPowerStateEnum = EnumWrapper('EndHostPowerStateEnum', {
    'Off': 'Off',
    'On': 'On'
}).enum_type

EndHostPowerStateWsmanEnum = EnumWrapper('EndHostPowerStateWsmanEnum', {
    'Off': 0,
    'On': 1
}).enum_type

EndHostPowerStateRedfishEnum = EnumWrapper('EndHostPowerStateRedfishEnum', {
    'Off': 'Off',
    'On': 'On'
}).enum_type

XMLSchemaEnum = EnumWrapper("XMLSchemaEnum", {
    'CIM_XML': 0,
    'Simple': 1
}).enum_type

DataSelectorArrayInEnum = EnumWrapper("DataSelectorArrayInEnum", {
    'HW_Data': 0,
    'OSApp_Data': 1,
    'TTY_Logs': 2,
    'Debug_Logs': 3
}).enum_type

SupportAssistCollectionFilterEnum = EnumWrapper("SupportAssistCollectionFilterEnum", {
    'No': 0,
    'Yes': 1
}).enum_type

SupportAssistCollectionTransmitEnum = EnumWrapper("SupportAssistCollectionTransmitEnum", {
    'No': 0,
    'Yes': 1
}).enum_type

TxfrDescriptorEnum = EnumWrapper('TxfrDescriptorEnum', {
    'StartOfTransmit': 1,
    'NormalTransmission': 2,
    'EndOfPacket': 3,
}).enum_type

ServerGenerationEnum = EnumWrapper('ServerGenerationEnum', {
    'Generation_11': '11G',
    'Generation_12': '12G',
    'Generation_13': '13G',
    'Generation_14': '14G'
}).enum_type

ComputerSystemResetTypesEnum = EnumWrapper("ComputerSystemResetTypesEnum", {
    "On": "On",
    "ForceOff": "ForceOff",
    "GracefulRestart": "GracefulRestart",
    "GracefulShutdown": "GracefulShutdown",
    "PushPowerButton": "PushPowerButton",
    "Nmi": "Nmi",
    "ForceRestart": "ForceRestart"
}).enum_type

ManagerTypesEnum = EnumWrapper("ManagerTypesEnum", {
    "GracefulRestart": "GracefulRestart",
}).enum_type
