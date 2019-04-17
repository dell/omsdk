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
import imp
import logging
import socket
import sys, glob
from collections import OrderedDict
from omsdk.sdkcenum import EnumWrapper, TypeHelper

logger = logging.getLogger(__name__)


class sdkinfra:
    """
    Class to initilaize and load the device drivers
    """
    def __init__(self):
        self.drivers = {}
        self.disc_modules = OrderedDict()
        self.driver_names = {}
    
    def load_from_file(self, filepath):
        mod_name = None
        mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])
        logger.debug("Loading " + filepath + "...")
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)
        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)
        return {"name": mod_name, "module": py_mod}
    
    def importPath(self, srcdir=None):
        oldpaths = sys.path
        if not srcdir is None:
            oldpaths = [srcdir]
        counter = 0
        paths = []
        for k in oldpaths:
            if not k in paths:
                paths.append(k)

        for psrcdir in paths:
            pypath = os.path.join(psrcdir, 'omdrivers', '__DellDrivers__.py')
            pyglobpath = os.path.join(psrcdir, 'omdrivers', '*.py')
            pydrivers = os.path.join(psrcdir, 'omdrivers')
            if not os.path.exists(pypath):
                continue
            fl = glob.glob(pyglobpath)
            for i in range(len(fl)):
                if fl[i].endswith("__.py"):
                    continue
                counter = counter + 1
                logger.debug("Loading: " + str(counter) + "::" + fl[i])
                module_loaded = self.load_from_file(fl[i])
                self.drivers[module_loaded["name"]] = module_loaded["module"]
                self.driver_names[module_loaded["name"]] = module_loaded["name"]
                discClass = getattr(module_loaded["module"], module_loaded["name"])
                self.disc_modules[module_loaded["name"]] = discClass(pydrivers)
                aliases = self.disc_modules[module_loaded["name"]].my_aliases()
                mname = module_loaded["name"]
                for alias in aliases:
                    self.disc_modules[alias] = self.disc_modules[mname]
                    self.drivers[alias] = self.drivers[mname]
                    self.driver_names[alias] = self.driver_names[mname]

        tempdict = OrderedDict(sorted(self.disc_modules.items(), key=lambda t: t[1].prefDiscOrder))
        self.disc_modules = tempdict
        self.driver_enum = EnumWrapper("Driver", self.driver_names).enum_type
    
    def find_driver(self, ipaddr, creds, protopref=None, pOptions=None, msgFlag=False):
        """Find a device driver for the given IPAddress or host name

                :param ipaddr: ipaddress or hostname of the device
                :param creds: bundle of credentials for finding the device driver.
                :param protopref: the preferred protocol to be used if the device supports the protocol
                :param pOptions: protocol specific options to be passed, port, timeout etc
                :type ipaddr: str
                :type creds: dict of obj <Snmpv2Credentials or UserCredentials>
                :type protopref: enumeration of preferred protocol
                :type pOptions: object <SNMPOptions or WSMANOptions or REDFISHOptions>
                :return: a driver handle for further configuration/monitoring
                :rtype: object <iBaseDriver>

        """
        duplicSet = set()
        msg = ipaddr + " : Connection to Dell EMC device failed, please check device status and credentials."
        drv = None
        for mod in self.disc_modules:
            if (self.disc_modules[mod] in duplicSet) or (str(mod) == "FileList"):
                continue
            drv = self._create_driver(mod, ipaddr, creds, protopref, pOptions)
            if drv:
                msg = ipaddr + " : Connected to Dell EMC device"
                break
            duplicSet.add(self.disc_modules[mod])

        if msgFlag:
            return drv, msg
        return drv

    # Return:
    #    None - if driver not found, not classifed
    #    instance of iBaseEntity  - if device of the proper type
    def get_driver(self, driver_en, ipaddr, creds, protopref=None, pOptions=None):
        """Get a device driver for the given IPAddress or host name, also checking for a particular device type

            :param ipaddr: ipaddress or hostname of the device
            :param driver_en: enumeration of the device type
            :param creds: bundle of credentials for finding the device driver.
            :param protopref: the preferred protocol to be used if the device supports the protocol
            :param pOptions: protocol specific options to be passed, port, timeout etc
            :type ipaddr: str
            :type driver_en: enumerate of the device type
            :type creds: dict of obj <Snmpv2Credentials or UserCredentials>
            :type protopref: enumeration of preferred protocol
            :type pOptions: object <SNMPOptions or WSMANOptions or REDFISHOptions>
            :return: a driver handle for further configuration/monitoring
            :rtype: object <iBaseDriver>

        """
        mod = TypeHelper.resolve(driver_en)
        logger.debug("get_driver(): Asking for " + mod)
        return self._create_driver(mod, ipaddr, creds, protopref, pOptions)

    def _create_driver(self, mod, host, creds, protopref, pOptions):
        msg = "Connection to Dell EMC device failed, please check device status and credentials."
        logger.debug("get_driver(): Asking for " + mod)
        ipaddr = host
        try:
            result = socket.getaddrinfo(host, None)
            lastuple = result[-1]
            ipaddress = lastuple[-1][0]
            if ipaddress:
                ipaddr = ipaddress
        except socket.gaierror as err:
            logger.error("{}: {}: {}".format(host, err, "cannot resolve hostname!"))
        if not mod in self.disc_modules:
            # TODO: Change this to exception
            logger.error("{}: {}".format(host, msg))
            logger.debug(mod + " not found!")
            return None
        try:
            logger.debug(mod + " driver found!")
            drv = self.disc_modules[mod].is_entitytype(self, ipaddr, creds, protopref, mod, pOptions)
            if drv is None:
                logger.info("{}: {}".format(host, msg))
            if drv:
                logger.info("{}: {}".format(host, "Connection to Dell EMC device success!"))
                hostname = None
                try:
                    hostname, aliaslist, addresslist = socket.gethostbyaddr(ipaddr)
                    logger.debug("Found host name for " + ipaddr + " as " + hostname)
                except socket.herror:
                    hostname = None
                    logger.debug("No host name found for " + ipaddr)
                drv.hostname = hostname
            return drv
        except AttributeError as attrerror:
            logger.debug(mod + " is not device or console")
            logger.debug(attrerror)
            return None

    def _driver(self, driver_en):
        mod = TypeHelper.resolve(driver_en)
        logger.debug("_driver(): Asking for " + mod)
        if not mod in self.disc_modules:
            # TODO: Change this to exception
            logger.debug(mod + " not found!")
            return None
        try:
            logger.debug(mod + " driver found!")
            drv = self.disc_modules[mod]._get(self)
            return drv
        except AttributeError as attrerror:
            logger.debug(mod + " is not device or console")
            logger.debug(attrerror)
            return None

    def setPrefProtocolDriver(self, driver_name, protopref):
        drv = self.disc_modules.get(driver_name, None)
        if drv:
            drv.protofactory.prefProtocol = protopref

    def excludeDrivers(self, excList):
        for drv in excList:
            self.disc_modules.pop(drv)

    def includeDriversOnly(self, incList):
        drvkeys = self.disc_modules.keys()
        for drv in drvkeys:
            if drv not in incList:
                self.disc_modules.pop(drv)

    def removeProtoDriver(self, driver_name, protList):
        drv = self.disc_modules.get(driver_name, None)
        if drv:
            for protoenum in protList:
                drv.protofactory.removeProto(protoenum)