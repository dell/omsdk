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
import os
import glob
import logging
from omsdk.sdkproto import PCONSOLE
from omsdk.sdkconsole import iConsoleRegistry, iConsoleDriver, iConsoleDiscovery
from omsdk.sdkfile import cfgprocessor
from omsdk.sdkprint import PrettyPrint

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class Nagios(iConsoleDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(Nagios, self).__init__(iConsoleRegistry("Nagios", srcdir, None))
        else:
            super().__init__(iConsoleRegistry("Nagios", srcdir, None))
        self.protofactory.add(PCONSOLE(obj=self))

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return NagiosEntity(self.ref, protofactory, ipaddr, creds)


class NagiosEntity(iConsoleDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(NagiosEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.proc = cfgprocessor()

    def my_connect(self, pOptions):
        status = False
        try:
            if os.path.isfile("d\\" + self.ipaddr + "\\nagios.topology"):
                status = True
        except:
            status = False
        logger.debug(self.ref.name + '::connect(' + self.ipaddr + ', ' + str(self.creds) + ")=" + str(status))
        return status

    def my_disconnect(self):
        try:
            self.proc.reset()
        except:
            pass

    def my_get_entityjson(self):
        logger.debug("Loading entity")
        for file1 in glob.glob("d\\" + self.ipaddr + "\\cfg\\*.cfg"):
            self.proc.process(file1)
        for file1 in glob.glob("d\\" + self.ipaddr + "\\cfg\\Templates\\*.cfg"):
            self.proc.process(file1)
        self.proc.hostit()
        self.entityjson["topology"] = self.proc.topology
        self.entityjson["devmap"] = self.proc.devmap
        with open("d\\" + self.ipaddr + "\\devices") as idrac_data:
            self.entityjson["devices"] = json.load(idrac_data)
        return True

    def my_add_or_update_group(self, groupname):
        logger.debug(">>  Creating or update Group:" + groupname)
        with open("d\\" + self.ipaddr + "\\cfg\\Templates\\ome_hostgroup.cfg", "a") as f:
            f.write("define hostgroup {\n")
            f.write("    hostgroup_name\t{0}\n".format(groupname))
            f.write("    alias\t{0}\n".format(groupname))
            f.write("}\n")
        return True

    def my_add_or_update_device(self, device, devmap, groupname=None):
        svctag = device
        ipaddr = device
        if not devmap is None:
            if "System" in devmap and "ServiceTag" in devmap["System"]:
                svctag = devmap["System"]["ServiceTag"]
            if "doc.prop" in devmap and "ipaddr" in devmap["doc.prop"]:
                ipaddr = devmap["doc.prop"]["ipaddr"]

        logger.debug(">>--->>---add " + str(device) + " to " + groupname)
        with open("d\\" + self.ipaddr + "\\cfg\\ome_" + ipaddr + ".host.cfg", "a") as f:
            f.write("define host {\n")
            f.write("    host_name            " + svctag + "\n")
            f.write("    use                xiwizard_" + groupname + "\n")
            f.write("    alias                " + svctag + "\n")
            f.write("    display_name            idrac-R330PTS\n")
            f.write("    address                " + ipaddr + "\n")
            f.write("    hostgroups            " + groupname + "\n")
            f.write("    check_command            check-dell-host-alive\n")
            f.write("    max_check_attempts        3\n")
            f.write("    check_interval            5\n")
            f.write("    retry_interval            3\n")
            f.write("    check_period            Dell-24x7\n")
            f.write("    contacts            nagiosadmin\n")
            f.write("    notification_interval        120\n")
            f.write("    notification_period        dellworkhours\n")
            f.write("    notification_options        d,u,r\n")
            f.write("    notes                Protocol selected : WSMAN\n")
            f.write("    action_url            http://" + ipaddr + "\n")
            f.write("    icon_image            dell_idrac.png\n")
            f.write("    statusmap_image            dell_idrac.png\n")
            f.write("    _INDEX                NA\n")
            f.write("    _servicetag            " + svctag + "\n")
            f.write("    _xiwizard            Dell_OM_NagiosXI_monitoring_wizard\n")
            f.write("    register            1\n")
            f.write("}\n")
        return ipaddr

    def my_update_device_group(self, device, devmap, gname):
        svctag = device
        ipaddr = device
        if not devmap is None:
            if "System" in devmap and "ServiceTag" in devmap["System"]:
                svctag = devmap["System"]["ServiceTag"]
            if "doc.prop" in devmap and "ipaddr" in devmap["doc.prop"]:
                ipaddr = devmap["doc.prop"]["ipaddr"]
        if ipaddr in self.entityjson["topology"]["DeviceGroups"][gname]["Devices"]:
            logger.debug(device + " in already in target group " + gname)
            return ipaddr
        logger.debug("Updating " + device + " to group: " + gname)
        return ipaddr

    def get_service_tag(self):
        return self.ipaddr
