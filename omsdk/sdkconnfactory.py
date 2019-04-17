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
import sys
import os
import logging
sys.path.append(os.getcwd())
from omsdk.sdkproto import ProtocolEnum
from omsdk.sdkprotopref import ProtoPreference, ProtoMethods
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.sdkprint import PrettyPrint

from enum import Enum
import re

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class ConnectionFactory(object):

    CONN_RETRIES = 1

    def __init__(self, sdkobj):
        self.work_connection = []
        self.work_protocols = []
        self.isConnected = False
        self.sdkobj = sdkobj

    def printx(self):
        logger.debug(str(len(self.work_connection)) + " connections in loop!")
        for i in range(0, len(self.work_connection)):
            logger.debug(str(self.work_protocols[i]) + " ... "+ str(self.work_connection[i]))
    
    def disconnect(self):
        for connection in self.work_connection:
            retval = connection.disconnect()
            del connection
        self.work_connection = []
        self.work_protocols = []
        self.isConnected = False

    def connect(self, name, ipaddr, creds, pfactory, pOptions):
        if self.isConnected:
            return True
        self.name = name
        self.ipaddr = ipaddr
        self.creds = creds
        self.pfactory = pfactory
        if PY2:
            pfactory = pfactory.__iter__()

        for spec in pfactory:
            connected = False
            for i in range(0, self.CONN_RETRIES):
                logger.debug("Connecting to " + name + "::" + str(spec) + " for " + str(i) + "th time...")
                if spec.connect(ipaddr, creds, pOptions):
                    connected = True
                    logger.debug(self.name + '::connect(' + self.ipaddr + ', ' + str(spec) + ")=True")
                    break
                else:
                    logger.debug("Connection failed to " + self.ipaddr)
            if connected:
                self.work_connection.append(spec)
                self.work_protocols.append(spec.enumid)
                self.isConnected = True
                # if self.pfactory.pref.mode == ProtoMethods.HuntMode:
                #     break
        return self.isConnected

    def identify(self, ejson):
        status = False
        if len(self.work_connection) <= 0:
            logger.error("No Connection present!!")
            return False

        if self.pfactory.classifier:
            counter = 0
            self.enumerate_list(ejson, *self.pfactory.classifier)
            for i in self.pfactory.classifier:
                obj = TypeHelper.resolve(i)
                if obj in ejson and len(ejson[obj])>0:
                    status = True

        logger.debug(self.name + '::identify(' + self.ipaddr + ', ' + str(self.creds) + ")=" + str(status))
        return status

    def complete(self):
        # skip if already present
        if len(self.sdkobj.emib_json) > 0:
            return True
        for connection in self.work_connection:
            retval = connection.complete(self.sdkobj)

    def enumerate_view(self, index):
        clsName = TypeHelper.resolve(index)

        # view is a URI

        retdoc = {}
        collector = {}
        collector_idseq = {}
        disconnectProto = []
        for connection in self.work_connection:
            retval = connection.enumerate_view(index, True)

            if retval['Status'] != 'Success' or \
                not 'Data' in retval or \
                retval['Data'] is None or \
                len(retval['Data']) <= 0:
                continue

            for retobj in retval['Data']:
                if isinstance(retval['Data'][retobj], dict): 
                   retval['Data'][retobj]= [ retval['Data'][retobj] ]
                    
                if isinstance(retval['Data'][retobj], dict):
                    # Merge System
                    if not clsName in retdoc:
                        retdoc[clsName] = {}
                        idx = self.sdkobj._get_obj_index(clsName, retval['Data'][retobj])
                        retdoc[clsName]["Key"] = idx
                    for i in retval['Data'][retobj]:
                        retdoc[clsName][i] = retval['Data'][retobj][i]
                else:
                    if not clsName in collector:
                        collector[clsName] = {}
                        collector_idseq[clsName] = []
                    for i in retval['Data'][retobj]:
                        idx = self.sdkobj._get_obj_index(clsName, i)
                        if idx is None:
                            idx = "<null_index>"
                        if not idx in collector[clsName]:
                            collector[clsName][idx] = {}
                            collector_idseq[clsName].append(idx)
                        collector[clsName][idx]["Key"] = idx
                        for ob in i:
                            if i[ob] == "Not Available" or i[ob] == "Not Applicable":
                                continue
                            collector[clsName][idx][ob] = i[ob]

            if index in self.pfactory.classifier:
                disconnectProto.append(connection)
                break

        if disconnectProto:
            self.work_connection = []
            self.work_connection.append(disconnectProto[0])
            self.work_protocols = []
            self.work_protocols.append(disconnectProto[0].enumid)

        for clsName in collector:
            if not clsName in retdoc:
                retdoc[clsName] = []
            for i in collector_idseq[clsName]:
                retdoc[clsName].append(collector[clsName][i])
        return retdoc

    def enumerate_all(self, retdoc, comp_enum):
        plist = []
        for comp in comp_enum:
            plist.append(comp)
        return self.enumerate_list(retdoc, *plist)

    def enumerate_list(self, retdoc, *comp_enum):
        for comp in comp_enum:
            # Ignore if component already present
            if TypeHelper.resolve(comp) in retdoc:
                continue
            comp_details = self.enumerate_view(comp)
            for field in comp_details:
                retdoc[field] = comp_details[field]
        self.complete()
        
        if not self.pfactory.sspec is None:
            subsystem = []
            for comp in self.pfactory.sspec:
                subcomp = {}
                if not 'Component' in self.pfactory.sspec[comp]:
                    continue
                if not 'Field' in self.pfactory.sspec[comp]:
                    continue
                cc = TypeHelper.resolve(self.pfactory.sspec[comp]['Component'])
                fld = self.pfactory.sspec[comp]['Field']
                if cc in retdoc and isinstance(retdoc[cc], list) \
                    and len(retdoc[cc]) > 0 and fld in retdoc[cc][0]:
                    # subsystem[TypeHelper.resolve(comp)] = retdoc[cc][0][fld]
                    subcomp["Key"] = TypeHelper.resolve(comp)
                    if retdoc[cc][0][fld]:
                        subcomp["PrimaryStatus"] = retdoc[cc][0][fld]
                    else:
                        subcomp["PrimaryStatus"] = 'Unknown'
                    subsystem.append(subcomp)
            if len(subsystem) > 0 :
                retdoc["Subsystem"] = subsystem
        return retdoc

    def operation(self, fname, **kwargs):
        retdoc = {}
        for connection in self.work_connection:
            if connection.isOpSupported(fname, **kwargs):
                logger.debug(self.ipaddr+" : Operation being done by " + str(connection))
                retval = connection.operation(fname, **kwargs)
                return retval

        return retdoc

    def opget(self, clsName, selector):
        retdoc = {}
        for connection in self.work_connection:
            retval = connection.opget(clsName, selector)
            return retval

        return retdoc
