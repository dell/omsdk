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

import os
import pprint
import json
import re
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse
import xml.dom.minidom

from omsdk.sdkprint import PrettyPrint
import logging

logger = logging.getLogger(__name__)


class DellPDKCatalog:
    OSTypes = {
        "WIN": "LWXP",
    }

    def __init__(self, source_file):
        self.source_file = source_file
        if not os.path.isfile(self.source_file):
            logger.debug(self.source_file + " does not exist!")
            self.root = ET.Element("Manifest")
            self.tree = ET.ElementTree(self.root)
            self.valid = False
        else:
            self.tree = ET.parse(self.source_file)
            self.root = self.tree.getroot()
            self.valid = True

    # ostype = None => all os types
    # ostype = "WIN" => only win32
    # ostype = ["WIN", "LIN"] => only win32 and Lin32
    def filter_bundle(self, model, ostype="WIN", tosource=None):
        # Find all Software Bundles for this model
        model = model.upper()
        model_path = "./SoftwareBundle/TargetSystems/Brand/Model[@systemID='{0}']/.../.../...".format(model)
        os_path = "./TargetOSes/OperatingSystem"
        if ostype:
            lostype = ostype
            if not isinstance(ostype, list):
                lostype = [lostype]
            for os in lostype:
                os_path += "[@osCode='{0}']".format(os)
        cnodes = self.root.findall(model_path)
        count = 0
        for node in cnodes:
            if len(node.findall(os_path)) <= 0:
                continue
            count += 1
            if tosource:
                tosource.addBundle(model, node)
        return count

    def _filter_byid(self, model, ostype, compid_path, firm, tosource):
        model = model.upper()
        model_path = "./SupportedSystems/Brand/Model[@systemID='{0}']".format(model)
        comp_path = "./SoftwareComponent"
        lostype = [""]
        if ostype:
            _ostype = ostype
            lostype = []
            if not isinstance(ostype, list):
                _ostype = [_ostype]
            for os in _ostype:
                lostype.append("[@packageType='{0}']".format(self.OSTypes[os]))
        count = 0
        for oses in lostype:
            xpth = comp_path + oses + "/SupportedDevices/Device" + compid_path + "/.../..."
            cnodes = self.root.findall(xpth)
            for node in cnodes:
                if len(node.findall(model_path)) <= 0:
                    continue
                count = count + 1
                if tosource:
                    tosource.addComponent(model, node, firm)
        return count

    def filter_by_model(self, model, ostype="WIN", firm=None, tosource=None):
        model = model.upper()
        return self._filter_byid(model, ostype, "", firm, tosource)

    def filter_by_compid(self, model, cid, ostype="WIN", firm=None, tosource=None):
        model = model.upper()
        compid_path = ""
        if cid:
            compid_path = "[@componentID='{0}']".format(cid)
        return self._filter_byid(model, ostype, compid_path, firm, tosource)

    def filter_by_pci(self, model, pcispec, ostype="WIN", firm=None, tosource=None):
        model = model.upper()
        compid_path = "/PCIInfo"
        for field in ['deviceID', 'subDeviceID', 'subVendorID', 'vendorID']:
            if field not in pcispec or not pcispec[field]:
                logger.debug(field + " is not present or null")
                continue
            compid_path += "[@" + field + "='" + pcispec[field] + "']"
        compid_path += "/..."
        return self._filter_byid(model, ostype, compid_path, firm, tosource)
