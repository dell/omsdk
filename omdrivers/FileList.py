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
import io
import logging
import threading
import time
from omsdk.sdkconsole import iConsoleRegistry, iConsoleDriver, iConsoleDiscovery
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkproto import PCONSOLE
import sys
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


# logging.basicConfig(level=logging.DEBUG,
#    format='[%(levelname)s] (%(threadName)-10s) %(message)s',)



class FileList(iConsoleDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(FileList, self).__init__(iConsoleRegistry("FileList", srcdir, None))
        else:
            super().__init__(iConsoleRegistry("FileList", srcdir, None))
        self.protofactory.add(PCONSOLE(obj=self))

    def my_entitytype(self, pinfra, listfile, creds, protofactory):
        return FileListEntity(self.ref, pinfra, protofactory, listfile, creds)


class FileListEntity(iConsoleDriver):
    def __init__(self, ref, pinfra, protofactory, listfile, creds):
        if PY2:
            super(FileListEntity, self).__init__(ref, protofactory, listfile, creds)
        else:
            super().__init__(ref, protofactory, listfile, creds)
        self.listfile = listfile
        self.maplist = {}
        self.myentitylistlock = threading.Lock()
        self.pinfra = pinfra
        # SDK Infrastructure
        self.entitylist = []
        self.success = {}
        self.failed = {}

    def _worker(self, device):
        logger.debug("Starting")
        devEntity = self.pinfra.find_driver(device, self.creds, True)
        with self.myentitylistlock:
            if not devEntity is None:
                self.entitylist.append(devEntity)
        # if devEntity is None:
        #    logger.debug("None is  " + device)
        # else:
        #    devEntity.get_entityjson()
        logger.debug("Exiting")

    def process(self):
        self.threadlist = []
        with open(self.listfile, "r") as mylist:
            for line in mylist:
                device = line.rstrip()
                thr = threading.Thread(name=device, \
                                       target=self._worker, args=(device,))
                self.threadlist.append(thr)
                thr.start()
        logger.debug('Waiting for _worker threads')
        for t in self.threadlist:
            t.join()
        for hgroup in self.maplist:
            tst = {}
            tst["Name"] = hgroup
            tst["ID"] = hgroup
            tst["Description"] = hgroup
            tst["Devices"] = self.maplist[hgroup]
            tst["DevicesCount"] = len(self.maplist[hgroup])
            self.entityjson["topology"]["DeviceGroups"][hgroup] = tst
        return self

    def printx(self):
        with self.myentitylistlock:
            for device in self.entityjson["devices"]["Devices"]:
                logger.debug("-======" + str(device) + "----------")
                if not device is None:
                    logger.debug(device.entityjson)
                logger.debug("-==================-------")

    def my_connect(self, pOptions):
        status = False
        try:
            if os.path.isfile(self.listfile):
                status = True
        except:
            status = False
        logger.debug(self.ref.name + '::connect(' + self.listfile + ', ' + str(self.creds) + ")=" + str(status))
        return status

    def my_get_entityjson(self):
        self.process()
        return True

    def _do_function(self, entity, function, *args):
        logger.debug("Executing for " + entity.ipaddr + str(*args))
        (retval, fname, msg) = function(entity, *args)
        if retval:
            with self.myentitylistlock:
                self.success[function] = self.success[function] + 1
            logger.debug("INFO: factory_config_export success! File=" + fname)
        else:
            with self.myentitylistlock:
                self.failed[function] = self.failed[function] + 1
            logger.debug(msg)
            logger.debug("ERROR: factory_config_export failed with message: " + msg['Message'])

    def runit(self, function, *arguments):
        logger.debug("Running: " + str(function))
        with self.myentitylistlock:
            if function in self.success:
                logger.debug("another runit with same funciton in progress!!")
                # wait 
            self.success[function] = 0
            self.failed[function] = 0
        for entity in self.entitylist:
            thr = threading.Thread(name=entity.ipaddr, \
                                   target=self._do_function, \
                                   args=(entity, function, arguments))
            self.threadlist.append(thr)
            thr.start()
        for t in self.threadlist:
            t.join()
        retval = True
        fname = "<none>"
        status = 'Success'
        with self.myentitylistlock:
            if self.success[function] == 0:
                retval = False
                status = 'Failed'
            msg = str(self.success[function]) + " succeeded. "
            msg = msg + str(self.failed[function]) + " failed."
            del self.success[function]
            del self.failed[function]
        return (retval, fname, {'Status': status, 'Message': msg})

    def get_service_tag(self):
        return "TEST-FileList"
