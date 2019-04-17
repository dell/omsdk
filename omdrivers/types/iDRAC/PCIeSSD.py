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
from omdrivers.enums.iDRAC.PCIeSSD import *
from omsdk.typemgr.ClassType import ClassType
from omsdk.typemgr.ArrayType import ArrayType
from omsdk.typemgr.BuiltinTypes import *
import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class PCIeSSD(ClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(PCIeSSD, self).__init__("Component", None, parent)
        else:
            super().__init__("Component", None, parent)
        # readonly attribute populated by iDRAC
        self.BusProtocol = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.BusProtocolVersion = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.CapableSpeed = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.CryptographicErase = EnumTypeField(None, CryptographicEraseTypes, parent=self, modifyAllowed=False,
                                                deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.DeviceProtocol = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.FailurePredicted = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.ModelNumber = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.Name = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.PcieMaxLinkWidth = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.PcieNegotiatedLinkSpeed = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.PcieNegotiatedLinkWidth = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RemainingRatedWriteEndurance = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SecureErase = EnumTypeField(None, SecureEraseTypes, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SerialNumber = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.Size = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.SmartStatus = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.State = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.Version = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.commit(loading_from_scp)
