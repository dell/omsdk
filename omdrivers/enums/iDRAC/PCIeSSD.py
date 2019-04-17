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

BusProtocolTypes = EnumWrapper("BusProtocolTypes", {
    "PCIe": "PCIe",
}).enum_type

BusProtocolVersionTypes = EnumWrapper("BusProtocolVersionTypes", {
    "T_2_0": "2.0",
    "T_2_1": "2.1",
    "T_3_0": "3.0",
    "T_3_1": "3.1",
    "Unknown": "Unknown",
}).enum_type

CapableSpeedTypes = EnumWrapper("CapableSpeedTypes", {
    "T_2_5_GT_s": "2.5 GT/s",
    "T_5_0_GT_s": "5.0 GT/s",
    "T_8_0_GT_s": "8.0 GT/s",
    "Unknown": "Unknown",
}).enum_type

CryptographicEraseTypes = EnumWrapper("CryptographicEraseTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

DeviceProtocolTypes = EnumWrapper("DeviceProtocolTypes", {
    "NVMe_1_1": "NVMe 1.1",
    "Nvme1_0": "Nvme1.0",
    "Unknown": "Unknown",
}).enum_type

FailurePredictedTypes = EnumWrapper("FailurePredictedTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

PcieMaxLinkWidthTypes = EnumWrapper("PcieMaxLinkWidthTypes", {
    "Unknown": "Unknown",
    "x1": "x1",
    "x2": "x2",
    "x4": "x4",
    "x8": "x8",
}).enum_type

PcieNegotiatedLinkSpeedTypes = EnumWrapper("PcieNegotiatedLinkSpeedTypes", {
    "T_2_5_GT_s": "2.5 GT/s",
    "T_5_0_GT_s": "5.0 GT/s",
    "T_8_0_GT_s": "8.0 GT/s",
    "Unknown": "Unknown",
}).enum_type

PcieNegotiatedLinkWidthTypes = EnumWrapper("PcieNegotiatedLinkWidthTypes", {
    "Unknown": "Unknown",
    "x1": "x1",
    "x2": "x2",
    "x4": "x4",
    "x8": "x8",
}).enum_type

SecureEraseTypes = EnumWrapper("SecureEraseTypes", {
    "No": "No",
    "Yes": "Yes",
}).enum_type

SmartStatusTypes = EnumWrapper("SmartStatusTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

StateTypes = EnumWrapper("StateTypes", {
    "Failed": "Failed",
    "Not_Ready_Locked": "Not Ready/Locked",
    "Overheat": "Overheat",
    "ReadOnly": "ReadOnly",
    "Ready": "Ready",
    "Unknown": "Unknown",
}).enum_type
