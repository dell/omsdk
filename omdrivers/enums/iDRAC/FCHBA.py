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

BootScanSelectionTypes = EnumWrapper("BootScanSelectionTypes", {
    "Disabled": "Disabled",
    "FabricDiscovered": "FabricDiscovered",
    "FirstLUN": "FirstLUN",
    "FirstLUN0": "FirstLUN0",
    "FirstNOTLUN0": "FirstNOTLUN0",
    "SpecifiedLUN": "SpecifiedLUN",
}).enum_type

FCTapeTypes = EnumWrapper("FCTapeTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

FramePayloadSizeTypes = EnumWrapper("FramePayloadSizeTypes", {
    "Auto": "Auto",
    "T_1024": "1024",
    "T_2048": "2048",
    "T_2112": "2112",
    "T_512": "512",
}).enum_type

HardZoneTypes = EnumWrapper("HardZoneTypes", {
    "Disabled": "Disabled",
    "Enabled": "Enabled",
}).enum_type

PortSpeedTypes = EnumWrapper("PortSpeedTypes", {
    "Auto": "Auto",
    "T_16G": "16G",
    "T_1G": "1G",
    "T_2G": "2G",
    "T_32G": "32G",
    "T_4G": "4G",
    "T_8G": "8G",
}).enum_type
