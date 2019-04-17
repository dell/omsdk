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
from omsdk.typemgr.ClassType import ClassType
from omsdk.typemgr.ArrayType import ArrayType, FQDDHelper
from omsdk.typemgr.BuiltinTypes import RootClassType
from omdrivers.types.iDRAC.iDRAC import *
from omdrivers.types.iDRAC.BIOS import *
from omdrivers.types.iDRAC.NIC import *
from omdrivers.types.iDRAC.FCHBA import *
from omdrivers.types.iDRAC.RAID import *
import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class SystemConfiguration(RootClassType):
    def __init__(self, parent=None, loading_from_scp=False):
        if PY2:
            super(SystemConfiguration, self).__init__("SystemConfiguration", None, parent)
        else:
            super().__init__("SystemConfiguration", None, parent)
        self.LifecycleController = LifecycleController(parent=self, loading_from_scp=loading_from_scp)
        self.System = System(parent=self, loading_from_scp=loading_from_scp)
        self.iDRAC = iDRAC(parent=self, loading_from_scp=loading_from_scp)
        self.FCHBA = ArrayType(FCHBA, parent=self, index_helper=FQDDHelper(), loading_from_scp=loading_from_scp)
        self.NIC = ArrayType(NetworkInterface, parent=self, index_helper=FQDDHelper(),
                             loading_from_scp=loading_from_scp)
        self.BIOS = BIOS(parent=self, loading_from_scp=loading_from_scp)
        self.Controller = ArrayType(Controller, parent=self, index_helper=FQDDHelper(),
                                    loading_from_scp=loading_from_scp)
        self._ignore_attribs('ServiceTag', 'Model', 'TimeStamp')
        self.commit(loading_from_scp)
