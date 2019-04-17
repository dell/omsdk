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
import json
import glob
import re
import os
from enum import Enum
from sys import stdout
from datetime import datetime
from omsdk.sdkprint import PrettyPrint
import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class Update(object):

    def __init__(self, entity, firmware_enum):
        self.entity = entity
        self.firmware_enum = firmware_enum
        self.reset()

    def reset(self):
        self.sw_inited = False
        self._swidentity = {}
        self.firmware_json = {}

    def get_swidentity(self):
        if self.sw_inited:
            logger.debug("Already present")
            return self.firmware_json
        self.entity._get_entries(self.firmware_json, self.firmware_enum)
        logger.debug(self.firmware_json)
        return self.firmware_json

    def _get_swidentity_hash(self):
        self.get_swidentity()
        for comp in self.firmware_json:
            for swentry in self.firmware_json[comp]:
                if not "FQDD" in swentry:
                    continue
                if swentry["FQDD"] in self._swidentity:
                    if not isinstance(self._swidentity[swentry["FQDD"]], list):
                        self._swidentity[swentry["FQDD"]] = [self._swidentity[swentry["FQDD"]]]
                else:
                    self._swidentity[swentry["FQDD"]] = {}
                self._swidentity[swentry["FQDD"]] = {}
                if "ComponentID" in swentry and swentry["ComponentID"]:
                    for val in ["ComponentID"]:
                        self._swidentity[swentry["FQDD"]][val] = swentry[val]
                else:
                    for val in ["VendorID", "SubVendorID", "DeviceID", "SubDeviceID"]:
                        self._swidentity[swentry["FQDD"]][val] = swentry[val]

                for val in ["ComponentType", "InstanceID", "VersionString", "Status"]:
                    self._swidentity[swentry["FQDD"]][val] = swentry[val]
                self._swidentity[swentry["FQDD"]]["ComponentClass"] = "unknown"
                # TODO RESTORE
                # for mycomp in self.protocolspec.compmap:
                #    if re.match(self.protocolspec.compmap[mycomp],swentry["FQDD"]):
                #        self.swidentity[swentry["FQDD"]]["ComponentClass"] = mycomp
        self.sw_inited = True
        return self._swidentity

    def save_invcollector_file(self, invcol_output_file):
        with open(invcol_output_file, "w") as output:
            self._save_invcollector(output)

    def _save_invcollector(self, output):
        # self.entity.get_entityjson()
        # if not "System" in self.entity.entityjson:
        #    logger.debug("ERROR: Entityjson is empty")
        #    return
        self._get_swidentity_hash()
        output.write('<SVMInventory>\n')
        output.write('    <System')
        if "System" in self.entity.entityjson:
            for (invstr, field) in [("Model", "Model"), ("systemID", "SystemID"), ("Name", "HostName")]:
                if field in self.entity.entityjson["System"]:
                    output.write(" " + invstr + "=\"" + self.entity.entityjson["System"][field] + "\"")
        output.write(' InventoryTime="{0}">\n'.format(str(datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S"))))
        for ent in self._swidentity:
            output.write('        <Device')
            for (invstr, field) in [("componentID", "ComponentID"),
                                    ("vendorID", "VendorID"),
                                    ("deviceID", "DeviceID"),
                                    ("subVendorID", "SubVendorID"),
                                    ("subDeviceID", "SubDeviceID")]:
                if field in self._swidentity[ent]:
                    output.write(" " + invstr + "=\"" + self._swidentity[ent][field] + "\"")
            output.write(' bus="" display="">\n')
            output.write('            <Application componentType="{0}" version="{1}" display="" />\n'.format(
                self._swidentity[ent]["ComponentType"], self._swidentity[ent]["VersionString"]))
            output.write('        </Device>\n')
        output.write('    </System>\n')
        output.write('</SVMInventory>\n')
