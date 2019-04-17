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
import re
import json
import sys
import logging
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkprotobase import ProtocolBase

import traceback
import time

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    from pysnmp.proto import rfc1902
    from pysnmp import debug

    PySnmpPresent = True
    # debug.setLogger(debug.Debug('dsp', 'msgproc'))

except ImportError:
    PySnmpPresent = False


class SNMPProtocol(ProtocolBase):
    def __init__(self, host, cstring="public", rwstring=None, pOptions=None, useSNMPGetFlag=False):
        if PySnmpPresent:
            self.snmpe = SnmpEngine()
            self.cmdGen = cmdgen.CommandGenerator()
        else:
            self.cmdGen = None
            self.snmpe = None
        self.host = host
        self.cstring = cstring
        self.rwstring = rwstring
        if rwstring is None:
            self.rwstring = cstring
        self.pOptions = pOptions
        if pOptions is None:
            self.pOptions = pOptions
        if ':' in host:
            self.udpx = Udp6TransportTarget((self.host, self.pOptions.port),
                                            timeout=self.pOptions.timeout, retries=self.pOptions.nretries)
        else:
            self.udpx = UdpTransportTarget((self.host, self.pOptions.port),
                                           timeout=self.pOptions.timeout, retries=self.pOptions.nretries)
        self.useSNMPGetFlag = useSNMPGetFlag

    def reset_connection(self):
        pass

    def reset(self, resetTransport=False):
        pass

    def enumerate(self, clsName, resource, select={}, resetTransport=False, filter=None):
        retval = {}
        retval['Status'] = 'Success'
        # print("USESNMPPGET Flag is ",self.useSNMPGetFlag)
        if self.useSNMPGetFlag:
            retval['Data'] = self._snmp_builder_UseSNMPGet(clsName, resource)
        else:
            retval['Data'] = self._snmp_builder(clsName, resource)
        # return { 'Status' : 'Error', 'Message' : 'Not implemented' }
        return retval

    def _snmpset(self, defaultIdx, var):
        try:
            newvar = []
            for i in var:
                newvar.append((i + "." + str(defaultIdx), var[i]))
            logger.debug(newvar)
            logger.debug("host=" + self.host + ":community=" + self.rwstring)
            errorIndication, errorStatus, errorIndex, varBinds = self.cmdGen.setCmd(
                cmdgen.CommunityData(self.rwstring),
                self.udpx,
                *newvar)
            if errorIndication:
                rjson = {'Status': 'Failed', 'Message': str(errorIndication)}
            elif errorStatus:
                rjson = {'Status': 'Failed', 'Message': ('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1] or '?'
                )
                                                         )}
            else:
                rjson = {'Status': 'Success', 'Message': 'None'}
        except Exception as tst:
            rjson = {'Status': 'Failed', 'Message': 'Exception:' + str(tst)}
        return rjson

    def _clean_table(self, protocmds, cmdname, *args):
        indexField = None
        cleanupAfterCreate = False
        if "SelectorSet" in protocmds[cmdname]:
            if "indexField" in protocmds[cmdname]["SelectorSet"]:
                indexField = protocmds[cmdname]["SelectorSet"]["indexField"]

        rjson = {}
        counter = 0
        if not indexField is None:
            indices = []
            try:
                oids = [ObjectType(ObjectIdentity(indexField))]
                for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(self.snmpe,
                                                                                    CommunityData(self.cstring,
                                                                                                  mpModel=0),
                                                                                    self.udpx,
                                                                                    ContextData(),
                                                                                    *oids, lexicographicMode=False):
                    counter = counter + 1
                    if errorIndication:
                        logger.debug(errorIndication)
                        return {
                            'Status': 'Failed',
                            'Message': str(errorIndication)
                        }
                    elif errorStatus:
                        logger.debug('%s at %s' % (errorStatus.prettyPrint(),
                                                   errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                        break
                    else:
                        try:
                            for varBind in varBinds:
                                ifield = str(varBind[0])
                                indices.append(int(re.sub(indexField + ".", "", ifield)))
                        except Exception as exp2:
                            logger.debug("Exception: " + str(exp2))
            except Exception as exp:
                logger.debug("Exception: " + str(exp))
            for i in indices:
                indexVars = {indexField: rfc1902.Integer(6)}
                try:
                    rjson2 = self._snmpset(i, indexVars)
                except Exception as exp2:
                    logger.debug("here: " + str(exp2))
        return {'Status': 'Success', 'Message': 'Cleanedup'}

    def operation(self, protocmds, cmdname, *args):
        indexField = None
        defaultIdx = None
        nextIdx = None
        startIdx = 1
        endIdx = 10
        cleanupAfterCreate = False
        if "SelectorSet" in protocmds[cmdname]:
            if "indexField" in protocmds[cmdname]["SelectorSet"]:
                indexField = protocmds[cmdname]["SelectorSet"]["indexField"]
            if "defaultIdx" in protocmds[cmdname]["SelectorSet"]:
                defaultIdx = int(protocmds[cmdname]["SelectorSet"]["defaultIdx"])
            if "startIdx" in protocmds[cmdname]["SelectorSet"]:
                startIdx = int(protocmds[cmdname]["SelectorSet"]["startIdx"])
            if "endIdx" in protocmds[cmdname]["SelectorSet"]:
                endIdx = int(protocmds[cmdname]["SelectorSet"]["endIdx"])
            if "nextIdx" in protocmds[cmdname]["SelectorSet"]:
                nextIdx = protocmds[cmdname]["SelectorSet"]["nextIdx"]
            if "cleanupAfterCreate" in protocmds[cmdname]["SelectorSet"]:
                cleanupAfterCreate = protocmds[cmdname]["SelectorSet"]["cleanupAfterCreate"]

        rjson = {}
        currentIdx = None
        counter = 0
        if not (indexField is None and nextIdx is None):
            indices = []
            currentIdx = defaultIdx
            try:
                if not indexField is None:
                    oids = [ObjectType(ObjectIdentity(indexField))]
                else:
                    oids = [ObjectType(ObjectIdentity(nextIdx))]
                for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(self.snmpe,
                                                                                    CommunityData(self.cstring,
                                                                                                  mpModel=0),
                                                                                    self.udpx,
                                                                                    ContextData(),
                                                                                    *oids, lexicographicMode=False):
                    counter = counter + 1
                    if errorIndication:
                        logger.debug(errorIndication)
                        return {
                            'Status': 'Failed',
                            'Message': str(errorIndication)
                        }
                    elif errorStatus:
                        logger.debug('%s at %s' % (errorStatus.prettyPrint(),
                                                   errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                        break
                    else:
                        try:
                            for varBind in varBinds:
                                ifield = str(varBind[0])
                                indices.append(int(re.sub(indexField + ".", "", ifield)))
                        except Exception as exp2:
                            logger.debug("Exception: " + str(exp2))
                # no entries found! so pick the first one!
                currentIdx = startIdx
            except Exception as exp:
                logger.debug("Exception: " + str(exp))
            if not indexField is None and len(indices) > 0:
                for i in range(startIdx, endIdx):
                    if not i in indices:
                        currentIdx = i
                        break
            elif not nextIdx is None and len(indices) > 0:
                currentIdx = indices[0]
        logger.debug("Found Index:" + str(currentIdx))
        try:
            rjson = self._build_ops(protocmds, cmdname, *args)
            if rjson['Status'] == 'Success':
                rjson = self._snmpset(currentIdx, rjson['retval'])
        except Exception as exp:
            logger.debug(str(exp))
            rjson = {'Status': 'Failed', 'Message': str(exp)}
        if rjson['Status'] == 'Success':
            time.sleep(2)
        if cleanupAfterCreate:
            indexVars = {indexField: rfc1902.Integer(6)}
            try:
                rjson2 = self._snmpset(currentIdx, indexVars)
            except Exception as exp2:
                logger.debug("here: " + str(exp2))
                rjson2 = {'Status': 'Failed', 'Message': str(exp2)}
            if rjson2['Status'] != 'Success':
                rjson['Message'] = rjson['Message'] + ". Index Removal failed: "
                rjson['Message'] = rjson['Message'] + rjson2['Message']
        return rjson

    def _snmp_builder(self, clsName, snmpview):
        ifMibRevVars = {}
        entity_raw = {}
        entity_raw[clsName] = []
        oids = []
        boolPrint = False
        for attr in snmpview:
            oids.append(ObjectType(snmpview[attr]))
        if len(oids) <= 0:
            logger.debug("::" + clsName + " is empty")
            return entity_raw
        try:
            for (errorIndication,
                 errorStatus,
                 errorIndex,
                 varBinds) in nextCmd(self.snmpe,
                                      CommunityData(self.cstring, mpModel=0),
                                      self.udpx,
                                      ContextData(),
                                      *oids,
                                      lexicographicMode=False):
                mibViewC = self.snmpe.getUserContext('mibViewController')
                for attr in snmpview:
                    ifMibRevVars[str(snmpview[attr]) + "."] = attr
                    ifMibRevVars[snmpview[attr].prettyPrint()] = attr
                if errorIndication:
                    logger.debug(errorIndication)
                    continue
                elif errorStatus:
                    logger.debug('%s at %s' % (errorStatus.prettyPrint(),
                                               errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    continue
                else:
                    entry = {}
                    idx = None
                    for varBind in varBinds:
                        (modName, symName, indices) = varBind[0].getMibSymbol()
                        if modName == "SNMPv2-SMI" and symName == "enterprises":
                            # MIB is not resolved!!
                            vname = None
                            vvarn = str(varBind[0])
                            for vvar in ifMibRevVars:
                                if vvar in vvarn:
                                    vname = ifMibRevVars[vvar]
                                    idx = vvarn.replace(vvar, "")
                                    break
                        else:
                            vn = ObjectIdentity(modName, symName)
                            vn.resolveWithMib(mibViewC)
                            myvar = vn.prettyPrint()
                            if not myvar in ifMibRevVars:
                                logger.debug("WARN: " + str(myvar) + " not found in ifMibRevVars")
                                logger.debug("WARN: " + varBind[0].prettyPrint())
                                vname = str(myvar)
                            else:
                                vname = ifMibRevVars[myvar]
                        val = varBind[1].prettyPrint()
                        if vname is None:
                            vname = "notsure"
                        if val != "":
                            entry[vname] = re.sub("^'|'$", "", val)
                        if idx and not "_SNMPIndex" in entry:
                            entry["_SNMPIndex"] = idx
                    entity_raw[clsName].append(entry)
        except Exception as exp:
            logger.debug(clsName + " is not present!!")
            logger.debug(str(exp))
            # traceback.print_exc()
        if (len(entity_raw[clsName]) <= 0):
            return {}
        elif (len(entity_raw[clsName]) > 1):
            return entity_raw
        else:
            return {clsName: entity_raw[clsName][0]}

    def _snmp_builder_UseSNMPGet(self, clsName, snmpview):
        ifMibRevVars = {}
        entity_raw = {}
        entity_raw[clsName] = []
        oids = []
        entry = {}
        try:
            for attr in snmpview:
                tmpoid = ObjectType(snmpview[attr])
                oids.append(tmpoid)
                errorIndication, errorStatus, errorIndex, varBinds = next(
                    nextCmd(self.snmpe, CommunityData(self.cstring, mpModel=0), self.udpx, ContextData(),
                            ObjectType(snmpview[attr]), lexicographicMode=False))
                if errorIndication:
                    logger.debug(errorIndication)
                    continue
                elif errorStatus:
                    logger.debug('%s at %s' % (errorStatus.prettyPrint(),
                                               errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    continue
                else:
                    for varBind in varBinds:
                        # pprint(varBind)
                        # print(' = '.join([x.prettyPrint() for x in varBind]))
                        entry[attr] = varBind[1].prettyPrint()
            entry["_SNMPIndex"] = '0'
            entity_raw[clsName].append(entry)
        except Exception as exp:
            logger.debug(clsName + " is not present!!")
            logger.debug(str(exp))
            # traceback.print_exc()

        if (len(entity_raw[clsName]) <= 0):
            return {}
        elif (len(entity_raw[clsName]) > 1):
            return entity_raw
        else:
            return {clsName: entity_raw[clsName][0]}


class EntityMibConvertor(object):
    def _checkit(self, tree, value):
        if value in tree:
            return tree
        for k in tree:
            if not "children" in tree[k]:
                continue
            node = self._checkit(tree[k]["children"], value)
            if not node is None:
                return node
        return None

    def _named_entity_tree(self, entity_tree, new_entity_tree):
        for i in entity_tree:
            field = i
            if "Name" in entity_tree[i] and entity_tree[i]["Name"] != "":
                field = entity_tree[i]["Name"]
            new_entity_tree[field] = entity_tree[i]
            if not "children" in entity_tree[i]:
                continue
            new_entity_tree[field]["child"] = {}
            self._named_entity_tree(entity_tree[i]["children"],
                                    new_entity_tree[field]["child"])
            del new_entity_tree[field]["children"]
        return new_entity_tree

    def build_entity_tree(self, entity_raw):
        if not "Entity" in entity_raw:
            return entity_raw
        if len(entity_raw["Entity"]) == 0:
            logger.debug("no entity present")
            return entity_raw
        entity_tree = {}
        entity_tree['1'] = entity_raw["Entity"][0]
        entity_tree['1']["children"] = {}
        counter = 0
        for i in entity_raw["Entity"]:
            counter = counter + 1
            if i['ContainedIn'] == '0':
                continue
            node = self._checkit(entity_tree, i['ContainedIn'])
            if not node is None:
                if not "children" in node[i['ContainedIn']]:
                    node[i['ContainedIn']]['children'] = {}
                node[i['ContainedIn']]['children'][str(counter)] = i
        entity_tree = self._named_entity_tree(entity_tree, {})
        return entity_tree

    def build_entity_json(self, entity_raw, entity_json):
        if not "Entity" in entity_raw:
            return entity_raw
        if len(entity_raw["Entity"]) == 0:
            logger.debug("no entity present")
            return entity_raw
        counter = 0
        for entry in entity_raw["Entity"]:
            counter = counter + 1
            if not "Class" in entry:
                logger.debug("Class is not populated for :" + str(entry))
                continue
            cls = entry["Class"]
            entry["MyPos"] = counter
            if not cls in entity_json:
                entity_json[cls] = []
            entity_json[cls].append(entry)
        dlist = []
        for cls in entity_json:
            if len(entity_json[cls]) <= 0:
                dlist.append(entity_json[cls])
                pass
            elif len(entity_json[cls]) == 1 and isinstance(entity_json[cls], list):
                entity_json[cls] = entity_json[cls][0]
        for idl in dlist:
            del idl
        return entity_json
