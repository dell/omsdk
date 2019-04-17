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
from omsdk.sdkbase import iBaseRegistry, iBaseDiscovery, iBaseDriver
import sys
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class iConsoleRegistry(iBaseRegistry):
    pass


class iConsoleDiscovery(iBaseDiscovery):
    pass


class iConsoleDriver(iBaseDriver):

    def __init__(self, registry, protofactory, ipaddr, creds):
        if PY2:
            super(iConsoleDriver, self).__init__(registry, protofactory, ipaddr, creds)
        else:
            super().__init__(registry, protofactory, ipaddr, creds)
        self._request_console_features()

    def my_reset(self):
        self.entityjson["devmap"] = {}
        self.entityjson["unknown_devmap"] = []
        self.entityjson["unknown_svctag"] = []
        self.entityjson["topology"]["DeviceGroups"] = {}
        self.entityjson["devices"]["Devices"] = []

    def get_device_identifier(self, device):
        return None

    def add_device_props(self, device):
        pass

    def _build_device_map(self):
        topoMap = True
        deviceMap = True
        # topoMap = False, deviceMap = False | empty console
        # topoMap = False, deviceMap = True | device map without topology
        # topoMap = True, deviceMap = False | empty topology
        # topoMap = True, deviceMap = True | good topology
        if not ("DeviceGroups" in self.entityjson["topology"]):
            logger.debug("No topology found!")
            topoMap = False
        if not ("Devices" in self.entityjson["devices"]):
            logger.debug("No devices found!")
            deviceMap = False
        if topoMap == False and deviceMap == False:
            logger.debug("empty console")
            return False
        if deviceMap == True:
            for device in self.entityjson["devices"]["Devices"]:
                retval = self.get_device_identifier(device)
                if retval is None:
                    self.entityjson["unknown_devmap"].append(device)
                else:
                    self.entityjson["devmap"][retval] = device
                    self.add_device_props(device)

        for gname in self.entityjson["topology"]["DeviceGroups"]:
            group = self.entityjson["topology"]["DeviceGroups"][gname]
            if "Devices" in group:
                for device in group["Devices"]:
                    if not (device in self.entityjson["devmap"]):
                        self.entityjson["unknown_svctag"].append(device)
            else:
                logger.debug(str(group) + " is empty")

    def print_details(self):
        print("Unknown Tags in Topology:" +
              str(self.entityjson["unknown_svctag"]))
        print("Unknown devices in Device List:" +
              str(self.entityjson["unknown_devmap"]))

    # All Topology APIs
    def get_topology(self):
        return self.entityjson["topology"]

    def get_devmap(self):
        return self.entityjson["devmap"]

    # TODO: Get Topology only for filtered devicegroups, devices!

    def apply_topology(self, topology, devmap):
        self.reset()
        self.get_entityjson()
        if devmap is None or topology is None:
            logger.debug("Error: either devmap or topology or both are none!")
            return False
        for gname in topology["DeviceGroups"]:
            if gname in self.entityjson["topology"]["DeviceGroups"]:
                logger.debug(gname + " already in nagios!")
            else:
                self.my_add_or_update_group(gname)
                self.entityjson["topology"]["DeviceGroups"][gname] = {}
                self.entityjson["topology"]["DeviceGroups"][gname]["ID"] = gname
                self.entityjson["topology"]["DeviceGroups"][gname]["Devices"] = []
            for device in topology["DeviceGroups"][gname]["Devices"]:
                if not device in devmap:
                    logger.debug("Cannot retrieve doc.prop for this device: " + device)
                    continue
                if device in self.entityjson["devmap"]:
                    logger.debug(device + " is already in target.devmap")
                    self.update_device_group(device, devmap[device], gname)
                elif device in self.entityjson["unknown_svctag"]:
                    logger.debug(device + " in already in target.unknown_svctag")
                    self.update_device_group(device, devmap[device], gname)
                else:
                    self.add_device(device, devmap[device], gname)

    def update_device_group(self, device, devmap, gname):
        if gname is None or not gname in self.entityjson["topology"]["DeviceGroups"]:
            logger.debug(groupName + " is not found in topology")
            return False
        dev = self.my_update_device_group(device, devmap, gname)
        self.entityjson["topology"]["DeviceGroups"][gname]["Devices"].append(dev)
        return True

    def add_device(self, device, devmap, groupName=None):
        if devmap is None:
            logger.debug("DevMap is not provided!")
            return False
        if groupName is None:
            groupName = "Ungrouped"
            logger.debug("no group given, changing to: " + groupName)
        if not groupName in self.entityjson["topology"]["DeviceGroups"]:
            logger.debug(groupName + " is not found in topology")
            return False
        dev = self.my_add_or_update_device(device, devmap, groupName)
        if not dev is None:
            self.entityjson["topology"]["DeviceGroups"][groupName]["Devices"].append(dev)
            return True
        else:
            logger.debug("adding device " + device + " to group " + groupName + " failed!")
        return False

    def check_group_exists(self, groupname):
        not_implemented

    def my_add_or_update_group(self, groupname):
        not_implemented

    def remove_group(self, groupname):
        not_implemented

    def my_add_or_update_device(self, device, groupname=None):
        not_implemented

    def my_update_device_group(self, device, devmap, groupname):
        not_implemented

    def my_remove_device(self, device, groupname=None):
        not_implemented

    # End All Topology APIs

    def get_devices(self):
        myl = []
        for dev in self.entityjson["devmap"]:
            myl.append(dev)
        return myl

    def get_json_device(self, device, monitorfilter=None, compScope=None):
        if not (device in self.entityjson["devmap"]):
            print("Not found!")
            return False
        devicejson = self.entityjson["devmap"][device]
        return self._get_json_for_device(devicejson, monitorfilter, compScope)
