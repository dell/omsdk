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
from omdrivers.enums.iDRAC.RAID import *
from omsdk.typemgr.ClassType import ClassType
from omsdk.typemgr.ArrayType import ArrayType, FQDDHelper
from omsdk.typemgr.BuiltinTypes import *
import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class Controller(ClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(Controller, self).__init__("Component", None, parent)
        else:
            super().__init__("Component", None, parent)
        # readonly attribute populated by iDRAC
        self.BackplaneType = EnumTypeField(None, BackplaneTypeTypes, parent=self, modifyAllowed=False,
                                           deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.CurrentControllerMode = EnumTypeField(None, CurrentControllerModeTypes, parent=self, modifyAllowed=False,
                                                   deleteAllowed=False)
        # readonly attribute
        self.EncryptionMode = EnumTypeField(None, EncryptionModeTypes, parent=self, modifyAllowed=False,
                                            deleteAllowed=False)
        # readonly attribute
        self.KeyID = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.NewControllerKey = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.OldControllerKey = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDAssetTag = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.RAIDControllerBootMode = EnumTypeField(None, RAIDControllerBootModeTypes, parent=self)
        self.RAIDEnhancedAutoImportForeignConfig = EnumTypeField(None, RAIDEnhancedAutoImportForeignConfigTypes,
                                                                 parent=self)
        # readonly attribute populated by iDRAC
        self.RAIDMaxCapableSpeed = EnumTypeField(None, RAIDMaxCapableSpeedTypes, parent=self, modifyAllowed=False,
                                                 deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDNegotiatedSpeed = EnumTypeField(RAIDNegotiatedSpeedTypes.T_None, RAIDNegotiatedSpeedTypes, parent=self,
                                                 modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDSupportedRAIDLevels = EnumTypeField(None, RAIDSupportedRAIDLevelsTypes, parent=self,
                                                     modifyAllowed=False, deleteAllowed=False)
        self.RAIDbatteryLearnMode = EnumTypeField(RAIDbatteryLearnModeTypes.T_None, RAIDbatteryLearnModeTypes,
                                                  parent=self)
        self.RAIDbgiRate = IntRangeField(100, 1, 100, parent=self)
        self.RAIDccMode = EnumTypeField(None, RAIDccModeTypes, parent=self)
        self.RAIDccRate = IntRangeField(100, 1, 100, parent=self)
        self.RAIDcopybackMode = EnumTypeField(None, RAIDcopybackModeTypes, parent=self)
        self.RAIDforeignConfig = EnumTypeField(None, RAIDforeignConfigTypes, parent=self)
        self.RAIDloadBalancedMode = EnumTypeField(RAIDloadBalancedModeTypes.Automatic, RAIDloadBalancedModeTypes,
                                                  parent=self)
        # readonly attribute populated by iDRAC
        self.RAIDmaxPDsInSpan = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDmaxSpansInVD = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDmaxSupportedVD = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.RAIDprMode = EnumTypeField(None, RAIDprModeTypes, parent=self)
        # readonly attribute populated by iDRAC
        self.RAIDprRate = IntRangeField(30, 1, 100, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.RAIDrebuildRate = IntRangeField(100, 1, 100, parent=self)
        self.RAIDreconstructRate = IntRangeField(100, 1, 100, parent=self)
        self.RAIDrekey = EnumTypeField(RAIDrekeyTypes.T_False, RAIDrekeyTypes, parent=self)
        self.RAIDremovecontrollerKey = EnumTypeField(RAIDremovecontrollerKeyTypes.T_False, RAIDremovecontrollerKeyTypes,
                                                     parent=self)
        self.RAIDresetConfig = EnumTypeField(RAIDresetConfigTypes.T_False, RAIDresetConfigTypes, parent=self,
                                             rebootRequired=True)
        # readonly attribute populated by iDRAC
        self.RAIDspinDownIdleTime = IntRangeField(30, 1, 65535, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDsupportedDiskProt = EnumTypeField(None, RAIDsupportedDiskProtTypes, parent=self, modifyAllowed=False,
                                                   deleteAllowed=False)
        self.Enclosure = ArrayType(Enclosure, parent=self, index_helper=FQDDHelper(), loading_from_scp=loading_from_scp)
        self.VirtualDisk = ArrayType(VirtualDisk, parent=self, index_helper=FQDDHelper(),
                                     loading_from_scp=loading_from_scp)
        self.PhysicalDisk = ArrayType(PhysicalDisk, parent=self, index_helper=FQDDHelper(),
                                      loading_from_scp=loading_from_scp)
        self.commit(loading_from_scp)


class Enclosure(ClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(Enclosure, self).__init__("Component", None, parent)
        else:
            super().__init__("Component", None, parent)
        # readonly attribute populated by iDRAC
        self.RAIDEffectiveSASAddress = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDEnclosureCurrentCfgMode = EnumTypeField(None, RAIDEnclosureCurrentCfgModeTypes, parent=self,
                                                         modifyAllowed=False, deleteAllowed=False)
        self.RAIDEnclosureRequestedCfgMode = EnumTypeField(RAIDEnclosureRequestedCfgModeTypes.T_None,
                                                           RAIDEnclosureRequestedCfgModeTypes, parent=self)
        self.PhysicalDisk = ArrayType(PhysicalDisk, parent=self, index_helper=FQDDHelper(),
                                      loading_from_scp=loading_from_scp)
        self.commit(loading_from_scp)


class PhysicalDisk(ClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(PhysicalDisk, self).__init__("Component", None, parent)
        else:
            super().__init__("Component", None, parent)
        self.PCIeSSDSecureErase = EnumTypeField(PCIeSSDSecureEraseTypes.T_False, PCIeSSDSecureEraseTypes, parent=self)
        # readonly attribute
        self.RAIDHotSpareStatus = EnumTypeField(None, RAIDHotSpareStatusTypes, parent=self, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.RAIDNominalMediumRotationRate = IntRangeField(None, 2, 4294967295, parent=self, modifyAllowed=False,
                                                           deleteAllowed=False)
        # readonly attribute
        self.RAIDPDState = EnumTypeField(None, RAIDPDStateTypes, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.commit(loading_from_scp)


class VirtualDisk(ClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(VirtualDisk, self).__init__("Component", None, parent)
        else:
            super().__init__("Component", None, parent)
        # readonly attribute
        self.Cachecade = EnumTypeField(None, CachecadeTypes, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.DiskCachePolicy = EnumTypeField(None, DiskCachePolicyTypes, parent=self)
        # readonly attribute
        self.IncludedPhysicalDiskID = ListField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.LockStatus = EnumTypeField(None, LockStatusTypes, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute populated by iDRAC
        self.Name = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.RAIDTypes = EnumTypeField(None, RAIDTypesTypes, parent=self, modifyAllowed=False, deleteAllowed=False)
        # action attribute
        self.RAIDaction = EnumTypeField(RAIDactionTypes.Update, RAIDactionTypes, parent=self, rebootRequired=True)
        # readonly attribute
        self.RAIDdedicatedSpare = ListField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.RAIDdefaultReadPolicy = EnumTypeField(RAIDdefaultReadPolicyTypes.Adaptive, RAIDdefaultReadPolicyTypes,
                                                   parent=self)
        self.RAIDdefaultWritePolicy = StringField("", parent=self, modifyAllowed=False, deleteAllowed=False)
        self.RAIDinitOperation = EnumTypeField(None, RAIDinitOperationTypes, parent=self)
        # readonly attribute
        self.Size = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.SpanDepth = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.SpanLength = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        # readonly attribute
        self.StripeSize = IntField(None, parent=self, modifyAllowed=False, deleteAllowed=False)
        self.T10PIStatus = EnumTypeField(None, T10PIStatusTypes, parent=self)
        self.commit(loading_from_scp)
