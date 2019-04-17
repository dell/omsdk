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
from omdrivers.enums.iDRAC.NIC import *
from omsdk.typemgr.ClassType import ClassType
from omsdk.typemgr.ArrayType import ArrayType
from omsdk.typemgr.BuiltinTypes import *
import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class NetworkInterface(ClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(NetworkInterface, self).__init__("Component", None, parent)
        else:
            super().__init__("Component", None, parent)
        # readonly attribute populated by iDRAC
        self.AddressingMode = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.BannerMessageTimeout = IntRangeField(None, 0, 14, parent=self)
        self.BlnkLeds = IntRangeField(15, 0, 15, parent=self)
        self.BootOptionROM = EnumTypeField(None, BootOptionROMTypes, parent=self)
        self.BootOrderFirstFCoETarget = IntField(0, parent=self)
        self.BootOrderFourthFCoETarget = IntField(0, parent=self)
        self.BootOrderSecondFCoETarget = IntField(0, parent=self)
        self.BootOrderThirdFCoETarget = IntField(0, parent=self)
        self.BootRetryCnt = EnumTypeField(BootRetryCntTypes.NoRetry, BootRetryCntTypes, parent=self)
        self.BootStrapType = EnumTypeField(BootStrapTypeTypes.AutoDetect, BootStrapTypeTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.BusDeviceFunction = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.ChapAuthEnable = EnumTypeField(ChapAuthEnableTypes.Disabled, ChapAuthEnableTypes, parent=self)
        self.ChapMutualAuth = EnumTypeField(ChapMutualAuthTypes.Disabled, ChapMutualAuthTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.ChipMdl = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConfigureLogicalPortsSupport = EnumTypeField(ConfigureLogicalPortsSupportTypes.Unavailable,
                                                          ConfigureLogicalPortsSupportTypes, parent=self,
                                                          modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.CongestionNotification = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectEighteenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectEighthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectEleventhFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectFifteenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectFifthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.ConnectFirstFCoETarget = EnumTypeField(ConnectFirstFCoETargetTypes.Disabled, ConnectFirstFCoETargetTypes,
                                                    parent=self)
        self.ConnectFirstTgt = EnumTypeField(ConnectFirstTgtTypes.Disabled, ConnectFirstTgtTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.ConnectFourteenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectFourthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectNineteenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectNinthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectSecondFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.ConnectSecondTgt = EnumTypeField(ConnectSecondTgtTypes.Disabled, ConnectSecondTgtTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.ConnectSeventeenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectSeventhFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectSixteenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectSixthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectThirdFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectThirteenthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectThirtyFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectThirtyFirstFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectThirtySecondFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwelfthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentiethFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentyEighthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentyFifthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentyFirstFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentyFourthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentyNinthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentySecondFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentySeventhFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentySixthFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ConnectTwentyThirdFCoETarget = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ControllerBIOSVersion = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.DCBXSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.DeviceName = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.DhcpVendId = StringField("", parent=self)
        self.EEEControl = EnumTypeField(EEEControlTypes.varies, EEEControlTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.EFIVersion = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EVBModesSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EighteenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EighteenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EighthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EighthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EleventhFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EleventhFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EnergyEfficientEthernet = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.EnhancedTransmissionSelection = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.FCoEBootScanSelection = EnumTypeField(FCoEBootScanSelectionTypes.Disabled, FCoEBootScanSelectionTypes,
                                                   parent=self)
        # readonly attribute populated by iDRAC
        self.FCoEBootSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.FCoEFabricDiscoveryRetryCnt = IntRangeField(None, 0, 60, parent=self)
        self.FCoEFirstHddTarget = EnumTypeField(FCoEFirstHddTargetTypes.Disabled, FCoEFirstHddTargetTypes, parent=self)
        self.FCoELnkUpDelayTime = IntRangeField(None, 0, 255, parent=self)
        self.FCoELunBusyRetryCnt = IntRangeField(None, 0, 60, parent=self)
        self.FCoEOffloadMode = EnumTypeField(FCoEOffloadModeTypes.Disabled, FCoEOffloadModeTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.FCoEOffloadSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.FCoETgtBoot = EnumTypeField(FCoETgtBootTypes.Disabled, FCoETgtBootTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.FIPMacAddr = MacAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FamilyVersion = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FeatureLicensingSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FifteenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FifteenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FifthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FifthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.FirstFCoEBootTargetLUN = IntRangeField(None, 0, 9223372036854775807, parent=self)
        self.FirstFCoEFCFVLANID = IntRangeField(None, 0, 4094, parent=self)
        self.FirstFCoEWWPNTarget = WWPNAddressField(None, parent=self)
        self.FirstHddTarget = EnumTypeField(FirstHddTargetTypes.Disabled, FirstHddTargetTypes, parent=self)
        self.FirstTgtBootLun = IntRangeField(None, 0, 9223372036854775807, parent=self)
        self.FirstTgtChapId = StringField("", parent=self)
        self.FirstTgtChapPwd = StringField("", parent=self)
        self.FirstTgtIpAddress = IPv4AddressField(None, parent=self)
        self.FirstTgtIpVer = EnumTypeField(FirstTgtIpVerTypes.IPv4, FirstTgtIpVerTypes, parent=self)
        self.FirstTgtIscsiName = StringField("", parent=self)
        self.FirstTgtTcpPort = IntRangeField(None, 1, 65535, parent=self)
        # readonly attribute populated by iDRAC
        self.FlexAddressing = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.FlowControlSetting = EnumTypeField(FlowControlSettingTypes.Auto, FlowControlSettingTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.FourteenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FourteenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FourthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FourthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.HairpinMode = EnumTypeField(HairpinModeTypes.Disabled, HairpinModeTypes, parent=self)
        self.HideSetupPrompt = EnumTypeField(HideSetupPromptTypes.Disabled, HideSetupPromptTypes, parent=self)
        self.IpAutoConfig = EnumTypeField(IpAutoConfigTypes.Disabled, IpAutoConfigTypes, parent=self)
        self.IpVer = EnumTypeField(IpVerTypes.IPv4, IpVerTypes, parent=self)
        self.IscsiInitiatorChapId = StringField("", parent=self)
        self.IscsiInitiatorChapPwd = StringField("", parent=self)
        self.IscsiInitiatorGateway = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorIpAddr = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorIpv4Addr = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorIpv4Gateway = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorIpv4PrimDns = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorIpv4SecDns = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorIpv6Addr = IPv6AddressField(None, parent=self)
        self.IscsiInitiatorIpv6Gateway = IPv6AddressField(None, parent=self)
        self.IscsiInitiatorIpv6PrimDns = IPv6AddressField(None, parent=self)
        self.IscsiInitiatorIpv6SecDns = IPv6AddressField(None, parent=self)
        self.IscsiInitiatorName = StringField("", parent=self)
        self.IscsiInitiatorPrimDns = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorSecDns = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorSubnet = IPv4AddressField(None, parent=self)
        self.IscsiInitiatorSubnetPrefix = StringField("", parent=self)
        # readonly attribute populated by iDRAC
        self.IscsiMacAddr = MacAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.IscsiTgtBoot = EnumTypeField(IscsiTgtBootTypes.Disabled, IscsiTgtBootTypes, parent=self)
        self.IscsiVLanId = IntRangeField(None, 0, 4094, parent=self)
        self.IscsiVLanMode = EnumTypeField(IscsiVLanModeTypes.Disabled, IscsiVLanModeTypes, parent=self)
        self.IscsiViaDHCP = EnumTypeField(IscsiViaDHCPTypes.Disabled, IscsiViaDHCPTypes, parent=self)
        self.LegacyBootProto = EnumTypeField(LegacyBootProtoTypes.varies, LegacyBootProtoTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.LinkStatus = EnumTypeField(None, LinkStatusTypes, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.LnkSpeed = EnumTypeField(None, LnkSpeedTypes, parent=self)
        self.LnkUpDelayTime = IntRangeField(0, 0, 255, parent=self)
        self.LocalDCBXWillingMode = EnumTypeField(LocalDCBXWillingModeTypes.Enabled, LocalDCBXWillingModeTypes,
                                                  parent=self)
        self.LogicalPortEnable = EnumTypeField(LogicalPortEnableTypes.Disabled, LogicalPortEnableTypes, parent=self)
        self.LunBusyRetryCnt = IntRangeField(None, 0, 60, parent=self)
        self.MTUParams = EnumTypeField(None, MTUParamsTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.MTUReconfigurationSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MacAddr = MacAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.MaxBandwidth = IntRangeField(100, 0, 100, parent=self)
        # readonly attribute populated by iDRAC
        self.MaxFrameSize = IntRangeField(None, 0, 9223372036854775808, parent=self, modifyAllowed=False,
                                          deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MaxIOsPerSession = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MaxNPIVPerPort = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MaxNumberExchanges = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MaxNumberLogins = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MaxNumberOfFCTargets = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MaxNumberOutStandingCommands = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.MaxNumberVFSupportedByDevice = IntRangeField(0, 0, 9223372036854775808, parent=self, modifyAllowed=False,
                                                          deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.MgmtSVID = IntRangeField(1000, 0, 4095, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.MinBandwidth = IntRangeField(0, 0, 100, parent=self)
        self.NPCP = EnumTypeField(NPCPTypes.Enabled, NPCPTypes, parent=self)
        self.NParEP = EnumTypeField(NParEPTypes.Disabled, NParEPTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.NWManagementPassThrough = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.NetworkPartitioningMode = EnumTypeField(NetworkPartitioningModeTypes.SIP, NetworkPartitioningModeTypes,
                                                     parent=self)
        self.NicMode = EnumTypeField(NicModeTypes.Varies, NicModeTypes, parent=self)
        self.NicPartitioning = EnumTypeField(NicPartitioningTypes.Disabled, NicPartitioningTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.NicPartitioningSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.NineteenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.NineteenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.NinthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.NinthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.NumberPCIFunctionsEnabled = IntRangeField(None, 1, 9223372036854775808, parent=self, modifyAllowed=False,
                                                       deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.NumberPCIFunctionsSupported = IntRangeField(None, 1, 256, parent=self, modifyAllowed=False,
                                                         deleteAllowed=False)
        self.NumberVFAdvertised = IntRangeField(0, 0, 256, parent=self)
        # readonly attribute populated by iDRAC
        self.NumberVFSupported = IntRangeField(0, 0, 256, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.OSBMCManagementPassThrough = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.OnChipThermalSensor = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.PCIDeviceID = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.PXEBootSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.PartitionStateInterpretation = EnumTypeField(None, PartitionStateInterpretationTypes, parent=self,
                                                          modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.PriorityFlowControl = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.PriorityGroup0BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup0ProtocolAssignment = EnumTypeField(None, PriorityGroup0ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup15BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup15ProtocolAssignment = EnumTypeField(None, PriorityGroup15ProtocolAssignmentTypes,
                                                               parent=self)
        self.PriorityGroup1BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup1ProtocolAssignment = EnumTypeField(None, PriorityGroup1ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup2BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup2ProtocolAssignment = EnumTypeField(None, PriorityGroup2ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup3BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup3ProtocolAssignment = EnumTypeField(None, PriorityGroup3ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup4BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup4ProtocolAssignment = EnumTypeField(None, PriorityGroup4ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup5BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup5ProtocolAssignment = EnumTypeField(None, PriorityGroup5ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup6BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup6ProtocolAssignment = EnumTypeField(None, PriorityGroup6ProtocolAssignmentTypes, parent=self)
        self.PriorityGroup7BandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.PriorityGroup7ProtocolAssignment = EnumTypeField(None, PriorityGroup7ProtocolAssignmentTypes, parent=self)
        self.PriorityGroupBandwidthAllocation = IntRangeField(None, 0, 100, parent=self)
        self.RDMAApplicationProfile = EnumTypeField(None, RDMAApplicationProfileTypes, parent=self)
        self.RDMANICModeOnPort = EnumTypeField(RDMANICModeOnPortTypes.Varies, RDMANICModeOnPortTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.RDMAProtocolSupport = EnumTypeField(None, RDMAProtocolSupportTypes, parent=self, modifyAllowed=False,
                                                 deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RDMASupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RXFlowControl = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RemotePHY = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SRIOVSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SecondFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SecondFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.SecondTgtBootLun = IntRangeField(None, 0, 9223372036854775807, parent=self)
        self.SecondTgtChapId = StringField("", parent=self)
        self.SecondTgtChapPwd = StringField("", parent=self)
        self.SecondTgtIpAddress = IPv4AddressField(None, parent=self)
        self.SecondTgtIpVer = EnumTypeField(SecondTgtIpVerTypes.IPv4, SecondTgtIpVerTypes, parent=self)
        self.SecondTgtIscsiName = StringField("", parent=self)
        self.SecondTgtTcpPort = IntRangeField(None, 1, 65535, parent=self)
        self.SecondaryDeviceMacAddr = MacAddressField(None, parent=self)
        # readonly attribute populated by iDRAC
        self.SeventeenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SeventeenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SeventhFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SeventhFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SixteenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SixteenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SixthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SixthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SwitchDepPartitioningSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TOESupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TXBandwidthControlMaximum = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TXBandwidthControlMinimum = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TXFlowControl = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.TcpIpViaDHCP = EnumTypeField(TcpIpViaDHCPTypes.Disabled, TcpIpViaDHCPTypes, parent=self)
        self.TcpTimestmp = EnumTypeField(TcpTimestmpTypes.Disabled, TcpTimestmpTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.TenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirdFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirdFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirteenthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirteenthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirtyFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirtyFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirtyFirstFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirtyFirstFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirtySecondFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ThirtySecondFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.TotalNumberLogicalPorts = EnumTypeField(TotalNumberLogicalPortsTypes.T_2, TotalNumberLogicalPortsTypes,
                                                     parent=self)
        # readonly attribute populated by iDRAC
        self.TwelfthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwelfthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentiethFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentiethFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyEighthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyEighthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyFifthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyFifthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyFirstFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyFirstFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyFourthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyFourthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyNinthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyNinthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentySecondFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentySecondFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentySeventhFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentySeventhFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentySixthFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentySixthFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyThirdFCoEBootTargetLUN = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.TwentyThirdFCoEWWPNTarget = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.UseIndTgtName = EnumTypeField(UseIndTgtNameTypes.Disabled, UseIndTgtNameTypes, parent=self)
        self.UseIndTgtPortal = EnumTypeField(UseIndTgtPortalTypes.Disabled, UseIndTgtPortalTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.VFAllocBasis = EnumTypeField(None, VFAllocBasisTypes, parent=self, modifyAllowed=False,
                                          deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.VFAllocMult = IntRangeField(None, 1, 255, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.VFDistribution = StringField("", parent=self)
        self.VLanId = IntRangeField(None, 0, 4094, parent=self)
        self.VLanMode = EnumTypeField(VLanModeTypes.Disabled, VLanModeTypes, parent=self)
        self.VirtFIPMacAddr = MacAddressField("00:00:00:00:00:00", parent=self)
        self.VirtIscsiMacAddr = MacAddressField("00:00:00:00:00:00", parent=self)
        self.VirtMacAddr = MacAddressField("00:00:00:00:00:00", parent=self)
        self.VirtWWN = WWPNAddressField("00:00:00:00:00:00:00:00", parent=self)
        self.VirtWWPN = WWPNAddressField("00:00:00:00:00:00:00:00", parent=self)
        self.VirtualizationMode = EnumTypeField(VirtualizationModeTypes.NONE, VirtualizationModeTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.WWN = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.WWPN = WWPNAddressField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.WakeOnLan = EnumTypeField(None, WakeOnLanTypes, parent=self)
        self.WakeOnLanLnkSpeed = EnumTypeField(WakeOnLanLnkSpeedTypes.AutoNeg, WakeOnLanLnkSpeedTypes, parent=self)
        self.WinHbaBootMode = EnumTypeField(WinHbaBootModeTypes.Disabled, WinHbaBootModeTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.iSCSIBootSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.iSCSIDualIPVersionSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.iSCSIOffloadSupport = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.iScsiOffloadMode = EnumTypeField(iScsiOffloadModeTypes.Disabled, iScsiOffloadModeTypes, parent=self)
        self.commit(loading_from_scp)
