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
import json
import logging
import re
from enum import Enum
from datetime import datetime
from omsdk.sdkenum import MonitorScope, MonitorScopeMap
from omsdk.sdkenum import MonitorScopeFilter, ComponentScope
from omsdk.sdkenum import MonitorScopeFilter_All
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkproto import ProtocolFactory, ProtocolEnum
from omsdk.sdkcenum import TypeHelper, EnumWrapper
from omsdk.sdkconnfactory import ConnectionFactory
from omsdk.sdkprotopref import ProtoMethods
import sys

logger = logging.getLogger(__name__)


class iBaseRegistry(object):

    def __init__(self, name, srcdir, compenum):
        self.name = name
        self.defs = {}
        self.ComponentEnum = compenum
        self.my_load(srcdir)

    def print_components(self):
        for comp in self.ComponentEnum:
            print(TypeHelper.resolve(comp))

    def convert_comp_to_enum(self, comps, comp_union_spec, merge_join_spec, misc_join_spec, more_details_spec):
        en = []
        for i in comps:
            found = False
            for j in self.ComponentEnum:
                if TypeHelper.resolve(j) == TypeHelper.resolve(i):
                    en.append(j)
                    found = True
                    break
            if not found:
                en.append(i)
        processedComp = self.find_merge_components(en, comp_union_spec, merge_join_spec, misc_join_spec,
                                                   more_details_spec)
        return processedComp

    def find_merge_components(self, comps, comp_union_spec, merge_join_spec, misc_join_spec, more_details_spec):
        tempList = []
        for i in comps:
            str_type = TypeHelper.resolve(i)
            replacedFlag = False
            if comp_union_spec:
                mystr = str_type
                if '_' in str_type:
                    tempmystr = str_type.split('_')
                    mystr = tempmystr[0]
                    if str_type in comp_union_spec:
                        mystr = str_type
                    xComp = comp_union_spec[mystr]
                    myList = xComp['_components_enum']
                    tempList = tempList + myList
                    replacedFlag = False
            if merge_join_spec:
                if str_type in merge_join_spec:
                    xComp = merge_join_spec[str_type]
                    myList = xComp['_components_enum']
                    tempList = tempList + myList
                    replacedFlag = True
            if misc_join_spec:
                if str_type in misc_join_spec:
                    xComp = misc_join_spec[str_type]
                    myList = xComp['_components_enum']
                    tempList = tempList + myList
                    # Not replacing just addition of the new profiles
                    replacedFlag = False
            if more_details_spec:
                #if str in more_details_spec:
                for str_type in more_details_spec:
                    myList = more_details_spec[str_type]['_components_enum']
                    tempList = tempList + myList
                    replacedFlag = False
            if not replacedFlag:
                tempList.append(i)
        return list(set(tempList))

    def my_load(self, srcdir):
        fname = os.path.join(srcdir, self.name, self.name + ".Monitor")
        if os.path.exists(fname) and not os.path.isdir(fname):
            logger.info(self.name + ":: Loading defs")
            with open(fname) as enum_data:
                self.defs = json.load(enum_data)
        else:
            logger.info(fname + " does not exist!!")
        # comps = {}
        # for comp in self.defs:
        #    comps[comp] = comp

    def Translate(self, component, field, value):
        if isinstance(value, list):
            value = ','.join(map(str, value))
        if (component in self.defs):
            if (field in self.defs[component]):
                if (str(value) in self.defs[component][field]):
                    return self.defs[component][field][str(value).strip()]
        return str(value).strip()


class iBaseDiscovery(object):
    def __init__(self, registry):
        # TODO: Pass srcdir so we can add it to entitytype
        self.ref = registry
        self.protofactory = ProtocolFactory()
        self.prefDiscOrder = 999  # default

    def is_entitytype(self, pinfra, ipaddr, creds, protopref, driver_en, pOptions):
        protofactory = self.protofactory.clone()
        if self.protofactory.prefProtocol:
            protofactory.copy(self.protofactory.prefProtocol)
        elif protopref:
            protofactory.copy(protopref)
        entity = self.my_entitytype(pinfra, ipaddr, creds, protofactory)
        if not entity is None:
            entity.driver_en = driver_en
            entity.pOptions = pOptions
            if entity.connect():
                return entity
        return None

    def _get(self, pinfra):
        protofactory = self.protofactory.clone()
        return self.my_entitytype(pinfra, "ip", None, protofactory)

    def my_entitytype(self, pinfra, ipaddr, creds, pFactory):
        return None

    def my_aliases(self):
        return []


class RegistryDefs:
    pass


class iBaseDriver(object):

    def __init__(self, registry, protofactory, ipaddr, creds):
        self.ref = registry
        self.ipaddr = ipaddr
        self.hostname = None
        self.creds = creds
        self.device_type = self.ref.name

        # Facts
        self.facts = {}
        self.facts["HandlesManyDevices"] = False
        self.facts["IsADevice"] = False

        # Protocol
        self.protofactory = protofactory
        self.cfactory = None

        # Add commands to this object
        self._make_all_methods()

        # Components Map
        self.ComponentEnum = self.ref.ComponentEnum
        self.components = {}
        for comp in self.ref.defs:
            self.components[comp] = {}
            for en in MonitorScope:
                self.components[comp][en] = []
                mon = TypeHelper.get_name(en, MonitorScopeMap)
                if mon in self.ref.defs[comp]:
                    self.components[comp][en] = self.ref.defs[comp][mon]

        # Entity JSON
        self.entityjson = {}
        # SNMP Entity MIB JSON
        self.emib_json = {}
        self.supports_entity_mib = False

        # Reset
        self.reset()

    def get_facts(self):
        return self.facts

    def reset(self):
        # Connection
        if self.cfactory:
            self.cfactory.disconnect()
        self.cfactory = None

        # Init Flags
        self.inited = False

        # Initialize EnityJSON
        self.emib_json = {}
        self.entityjson = {}
        self.entityjson["topology"] = {}
        self.entityjson["devices"] = {}
        self.entityjson["doc.prop"] = {}
        self.entityjson["doc.prop"]["ipaddr"] = self.ipaddr
        self.entityjson["doc.prop"]["creds"] = str(self.creds)

        self.my_reset()

    def my_reset(self):
        pass

    def get_doc_props(self):
        return self.entityjson["doc.prop"]

    def _request_device_features(self):
        self.facts["IsADevice"] = True

    def _request_console_features(self):
        self.facts["HandlesManyDevices"] = True

    def handles_many_devices(self):
        return self.facts["HandlesManyDevices"]

    # Connection APIs
    def connect(self, pOptions=None):
        if self.cfactory is None:
            self.cfactory = ConnectionFactory(self)
        if pOptions == None:
            pOptions = self.pOptions
        return self.my_connect(pOptions)

    def my_connect(self, pOptions):
        if not self.cfactory.connect(self.ref.name, self.ipaddr, self.creds, self.protofactory, pOptions):
            logger.debug("Connection failed to " + self.ipaddr)
            return False

        retval = self.cfactory.identify(self.entityjson)
        if 'System' in self.entityjson and len(self.entityjson['System']) > 0:
            if '_Type' not in self.entityjson['System'][0]:
                self.entityjson['System'][0]['_Type'] = self.device_type
        return retval

    def my_disconnect(self):
        return True

    def disconnect(self):
        if self.cfactory:
            self.cfactory.disconnect()
        self.cfactory = None

    def reconnect(self, pOptions=None):
        self.disconnect()
        return self.connect(pOptions)

    # End Connection APIs

    # Containment Tree APIs
    @property
    def ContainmentTree(self):
        """
        Creates and returns the component tree of the device with Keys of the Components organized in a tree structure
        """
        device_json = self.get_json_device()
        return self._build_ctree(self.protofactory.ctree, device_json)

    def _build_ctree(self, mTree, device_json):
        comp_tree = {}
        if not mTree:
            return comp_tree
        system = None
        system_cname = None
        for ctree in mTree:
            compname = TypeHelper.resolve(ctree)
            comp_tree[compname] = self._build_tree(mTree, device_json, ctree)
            if compname == 'System':
                system = comp_tree[compname]
                system_cname = ctree
        # Populate with subsystem names!
        self._populate_component_tree(system_cname, system, device_json)
        return comp_tree

    def _is_comp_in_subsystem(self, device_json, comp):
        if 'Subsystem' not in device_json:
            return False
        for cjson in device_json['Subsystem']:
            if cjson['Key'] == comp:
                return True
        return False

    def _populate_component_tree(self, compn, comp_tree, device_json):
        counter = 0
        for comp in self.protofactory.ctree[compn]:
            c = TypeHelper.resolve(comp)
            if (comp not in self.protofactory.ctree):
                # comp is simple component - not container
                if self._is_comp_in_subsystem(device_json, c):
                    counter += 1
                    if c not in comp_tree:
                        comp_tree[c] = []
                continue
            # comp is container, can contain multiple subcomponents
            toadd = {}
            if c in comp_tree:
                toadd = comp_tree[c]
            n = self._populate_component_tree(comp, toadd, device_json)
            if self._is_comp_in_subsystem(device_json, c):
                counter = n + 1
            if counter > 0 and c not in comp_tree:
                comp_tree[c] = toadd
        return counter

    def _get_obj_index(self, clsName, js):
        retval = None
        if js is None:
            return retval
        if not clsName in self.ref.defs:
            return retval
        if not 'Key' in self.ref.defs[clsName] \
                or len(self.ref.defs[clsName]['Key']) <= 0:
            return "[" + clsName + "]"
        retval = ""
        comma = ""
        for key in self.ref.defs[clsName]["Key"]:
            if key not in js or js[key] is None:
                js[key] = self.my_fix_obj_index(clsName, key, js)
            if js[key] is None:
                js[key] = clsName + "_" + key + "_null"
            retval = retval + comma + str(js[key])
            comma = ","
        if retval == "":
            retval = self.my_get_key_index(clsName, js)
        return retval

    def my_get_key_index(self, clsName, js):
        # Redfish specific code - need to handle Key renames before merges
        if 'Id' in js:
            idx = js['Id']
        elif 'MemberID' in js:
            idx = js['MemberID']
        return idx

    def my_fix_obj_index(self, clsName, key, js):
        return clsName + "_" + key + "_null"

    def _get_cls_presence(self, clsName):
        if clsName in self.ref.defs:
            return True
        return False

    # Must be overridden by base class
    def _isin(self, parentClsName, parent, childClsName, child):
        pass

    def _build_tree(self, mTree, device_json, ctree, parent=None, parentClsName=None):

        comp_tree = {}
        if not ctree in mTree:
            return comp_tree
        for entry in mTree[ctree]:
            if isinstance(entry, str):
                comp_tree[entry] = self._build_tree(mTree, device_json, entry)
                continue

            # Enum
            enname = TypeHelper.resolve(entry)
            if not enname in device_json:
                logger.debug("Component " + enname + " is not present in device!")
                continue

            if isinstance(device_json[enname], dict):
                if len(device_json[enname]) <= 0:
                    # Empty entry
                    continue
                child_index = self._get_obj_index(enname, device_json[enname])

                if parent == None or self._isin(parentClsName, parent, enname, device_json[enname]):
                    if not entry in mTree:
                        # entry is a leaf node
                        comp_tree[enname] = child_index
                    else:
                        # entry is not a leaf node
                        comp_tree[enname] = {
                            child_index: self._build_tree(mTree, device_json, entry, device_json[enname], enname)
                        }

            elif isinstance(device_json[enname], list):
                if len(device_json[enname]) <= 0:
                    # Empty entry
                    continue

                dict_list = {}
                list_list = []
                for tt in device_json[enname]:
                    child_index = self._get_obj_index(enname, tt)
                    if parent == None or self._isin(parentClsName, parent, enname, tt):
                        if not entry in mTree:
                            # entry is a leaf node
                            list_list.append(child_index)
                        else:
                            # entry is not a leaf node
                            dict_list[child_index] = self._build_tree(mTree, device_json, entry, tt, enname)
                if len(dict_list) != 0 and len(list_list) == 0:
                    comp_tree[enname] = dict_list
                elif len(dict_list) == 0 and len(list_list) != 0:
                    comp_tree[enname] = list_list
                elif len(dict_list) != 0 and len(list_list) != 0:
                    comp_tree[enname] = dict_list
                    comp_tree[enname]["_unknown_"] = list_list
            else:
                logger.debug("Unexpected format!")
        return comp_tree

    # End Containment Tree APIs

    # Entity JSON APIs
    def _get_entries(self, json, en):
        comps = self.ref.convert_comp_to_enum(en, self.comp_union_spec, self.comp_merge_join_spec,
                                              self.comp_misc_join_spec, self.more_details_spec)
        return self.cfactory.enumerate_all(json, comps)

    # Consoles should override this!
    def my_get_entityjson(self):
        plist = []
        for comp in self.ComponentEnum:
            plist.append(comp)
        return self.get_partial_entityjson(*plist)

    def get_partial_entityjson(self, *en):
        """
            Gets the json with components which are passed as argument for this function
        :param en: list of Components of the device whose json is required
        :type en: list of strings or enums of components
        :return: json only the components passed in en
        :rtype: JSON
        """
        # Components with Sensors_*
        comps = self.ref.convert_comp_to_enum(en, self.comp_union_spec, self.comp_merge_join_spec,
                                              self.comp_misc_join_spec, self.more_details_spec)
        # Sensor_* replaced with Sensor enum ServerSensor, NumericSensor, PSNumericSensor
        enjson = self.cfactory.enumerate_list(self.entityjson, *comps)
        # json with ServerSensor, NumericSensor, PSNumericSensor
        self._misc_join_component(enjson, self.comp_misc_join_spec)
        self._merge_join_component(enjson, self.comp_merge_join_spec)
        self._union_component(enjson, self.comp_union_spec)
        # json with One Sensors replacing ServerSensor, NumericSensor, PSNumericSensor
        self._pivot_component(enjson, self.comp_union_spec)
        # call to collect more details
        self._get_more_details(enjson, self.more_details_spec)
        return enjson

    def _get_more_details(self, entityjson, more_details_spec):
        if more_details_spec:
            for item in more_details_spec:
                if item in entityjson:
                    self._call_it(item)

    def get_partial_entityjson_str(self, *comps):
        return self.get_partial_entityjson(*comps)

    def get_entityjson(self):
        """
            Create the json of the device by fetching attributes from the device using the protocol
             Internally creates the raw json of the device
        :return: True if successful
        :rtype: bool
        """
        if self.inited == False and self.connect():
            if not self.my_get_entityjson():
                return False
            self._build_device_map()
            self.inited = True
        elif self.inited == True:
            logger.debug("already present")
        else:
            logger.debug("failed to connect to device!")
        return self.inited

    def get_basic_entityjson(self):
        plist = []
        for comp in self.protofactory.classifier:
            plist.append(comp)
        if self.get_partial_entityjson(*plist):
            return True
        return False

    def _build_device_map(self):
        return True

    def print_components(self):
        self.ref.print_components()

    def _should_i_include(self, component, entry):
        return True

    def _should_i_modify_component(self, finalretjson, component):
        return

    def _call_it(self, more_details_spec):
        pass

    def _get_json_for_device(self, devicejson, monitorfilter=None, compScope=None):
        toret = devicejson
        if (monitorfilter is None):
            monitorfilter = MonitorScopeFilter_All
        # metrics_or_health = monitorfilter.isset(MonitorScope.Metrics) or \
        #                     monitorfilter.isset(MonitorScope.Health)

        invconfig_attrs = monitorfilter.isset(MonitorScope.Key) or \
                          monitorfilter.isset(MonitorScope.Inventory) or \
                          monitorfilter.isset(MonitorScope.ConfigState)

        finalret = {}
        for component in devicejson:
            if not (compScope is None or compScope.isMatch(component)):
                continue
            toret = devicejson[component]
            if not component in self.components:
                if not component in ['topology', 'devices', 'doc.prop']:
                    logger.debug(component + " is not defined in ref!")
                continue
            myret = []
            for entry in toret:
                if (len(entry) <= 0):
                    continue
                tgtentry = {}
                if not self._should_i_include(component, entry):
                    continue
                for en in MonitorScope:
                    if not monitorfilter.isset(en):
                        continue
                    for attr in self.components[component][en]:
                        if (attr in entry) and (entry[attr] != None) and (not str(entry[attr]).isspace()):
                            tval = self.ref.Translate(component, attr, entry[attr])
                            tgtentry[attr] = tval
                        else:
                            xval = monitorfilter.getdefaultMap(en)
                            if xval is not None:
                                tgtentry[attr] = xval
                tgtentry["Key"] = entry["Key"]
                if '_Type' in entry:
                    if invconfig_attrs:
                        tgtentry["_Type"] = entry["_Type"]
                if not invconfig_attrs:
                    # clean dummy entries
                    if len(tgtentry) == 1 and 'Key' in tgtentry:
                        # empty record
                        continue
                myret.append(tgtentry)
            if len(myret) > 0:
                finalret[component] = myret
        for component in devicejson:
            if component in finalret:
                self._should_i_modify_component(finalret, component)
        return finalret

    def _get_topology_info(self):
        return {}

    def _get_topology_influencers(self):
        return []

    # End Entity JSON APIs

    # Entity JSON/Member APIs
    # for members with multiple instances
    def _union_component(self, entityjson, comp_union_spec):
        # Remove duplicates not considered yet
        if comp_union_spec:
            for target_comp, value in comp_union_spec.items():
                tempCompGroup = []
                compTypes = value['_components']
                for compProfileType in compTypes:
                    if compProfileType in entityjson:
                        if isinstance(entityjson[compProfileType], dict):
                            x = entityjson[compProfileType]
                            # This renaming can be moved to func _pivot_component
                            if '_pivot' in value:
                                typen = value['_pivot']
                                if typen in value and x[typen] in value[typen]:
                                    x[typen] = value[typen][x[typen]]
                            tempCompGroup.append(x)
                        else:
                            for x in entityjson[compProfileType]:
                                # lot of 'if's required here, write your union json carefully
                                if '_pivot' in value:
                                    typen = value['_pivot']
                                    if typen in value and x[typen] in value[typen]:
                                        x[typen] = value[typen][x[typen]]
                            tempCompGroup = tempCompGroup + entityjson[compProfileType]
                        if '_remove_duplicates' in value:
                            if value['_remove_duplicates'] == True:
                                del entityjson[compProfileType]
                if tempCompGroup:
                    entityjson[target_comp] = tempCompGroup

    def _pivot_component(self, entityjson, comp_union_spec):
        # already changed to list in union component function, so no need of dict check
        if comp_union_spec:
            for target_comp, value in comp_union_spec.items():
                if target_comp in entityjson:
                    if '_pivot' in value:
                        classifier = value['_pivot']
                        classifieDict = {}
                        for i in entityjson[target_comp]:
                            keyBuilt = target_comp + '_' + str(i[classifier])
                            if keyBuilt not in classifieDict:
                                classifieDict[keyBuilt] = []
                            classifieDict[keyBuilt].append(i)
                        entityjson.update(classifieDict)
                        del entityjson[target_comp]

    def _merge_join_component(self, entityjson, comp_merge_join_spec):
        if comp_merge_join_spec:
            for key, value in comp_merge_join_spec.items():
                compTypes = value['_components']
                overwrite = value.get('_overwrite', True)
                del_misc = value.get('_delmisc', True)
                target_comp = compTypes[0][0]
                target_key = compTypes[0][1]
                tempList = []
                if target_comp in entityjson:
                    for keylist in compTypes:
                        temp = {}
                        # if "FanSlot"
                        if keylist[2] in entityjson and keylist[0] in entityjson:
                            if isinstance(entityjson[keylist[2]], dict):
                                slot = entityjson[keylist[2]]
                                temp[slot[keylist[3]]] = slot
                            else:
                                for slot in entityjson[keylist[2]]:
                                    chk_key = slot[keylist[3]]
                                    if chk_key:
                                        if isinstance(chk_key, list):
                                            for ix in chk_key:
                                                temp[ix] = slot
                                        else:
                                            temp[chk_key] = slot
                            if del_misc:
                                del entityjson[keylist[2]]
                            if temp:
                                tempList.append(temp)
                    # logger.debug(tempList)
                    if isinstance(entityjson[target_comp], dict):
                        fan = entityjson[target_comp]
                        for tmp in tempList:
                            if fan[target_key] in tmp:
                                if overwrite:
                                    fan.update(tmp[fan[target_key]])
                                else:
                                    # a bit complex logic required here
                                    fan = tmp[fan[target_key]].update(fan)
                    else:
                        for fan in entityjson[target_comp]:
                            for tmp in tempList:
                                if fan[target_key] in tmp:
                                    if overwrite:
                                        fan.update(tmp[fan[target_key]])
                                    else:
                                        # a bit complex logic required here
                                        xd = tmp[fan[target_key]]
                                        fan.update({k: v for k, v in xd.items() if not k in fan})
                                        # fan = tmp[fan[target_key]].update(fan)
                    entityjson[key] = entityjson.pop(target_comp)

    def _misc_join_component(self, entityjson, comp_misc_join_spec):
        if comp_misc_join_spec:
            compDelList = []
            for key, value in comp_misc_join_spec.items():
                if '_createFlag' in value:
                    if value['_createFlag'] == True:
                        entityjson[key] = []
                        myList = {}
                        myList["Key"] = key
                        entityjson[key].append(myList)
                if key in entityjson:
                    keytripletsdict = value['_complexkeys']
                    profs = value['_components_enum']
                    if isinstance(entityjson[key], dict):
                        myDict = entityjson[key]
                        for comp, ckeys in keytripletsdict.items():
                            if comp in entityjson:
                                k = ckeys[0]
                                attrName = ckeys[1]
                                if isinstance(entityjson[comp], dict):
                                    attrInst = entityjson[comp]
                                    myDict[attrInst[attrName]] = attrInst[ckeys[2]]
                                else:
                                    for attrInst in entityjson[comp]:
                                        # This check is avoided to accomodate iDRAVcardView FQDD issue
                                        # if(myDict[k] == attrInst[k]):
                                        myDict[attrInst[attrName]] = attrInst[ckeys[2]]
                                # del entityjson[comp]
                                compDelList.append(comp)
                    else:  # assuming list
                        myList = entityjson[key]
                        for comp, ckeys in keytripletsdict.items():
                            if comp in entityjson:
                                k = ckeys[0]
                                attrName = ckeys[1]
                                if isinstance(entityjson[comp], dict):
                                    attrInst = entityjson[comp]
                                    for compInst in myList:
                                        if (compInst[k] == attrInst[k]):
                                            compInst[attrInst[attrName]] = attrInst[ckeys[2]]
                                else:
                                    for attrInst in entityjson[comp]:
                                        for compInst in myList:
                                            if k is None:
                                                compInst[attrInst[attrName]] = attrInst[ckeys[2]]
                                            else:
                                                if (compInst[k] == attrInst[k]) or (attrInst[k] in compInst[
                                                    k]):  # to accomodate iDRACCArdView and iDRACCardString issue iDRAC.Embedded.1-1 and iDRAC.Embedded.1
                                                    if ckeys[
                                                        2] in attrInst:  # Added because iDRACString in one of firmware 3.11.11.11(14G) did not have attribute CurrentValue(SystemLockDown)
                                                        compInst[attrInst[attrName]] = attrInst[ckeys[2]]
                                # del entityjson[comp]
                                compDelList.append(comp)
            for dlcomp in compDelList:
                if dlcomp in entityjson:
                    del entityjson[dlcomp]

    def _get_field(self, myjson, component_en, fieldname, idx=0):
        compfilter = ComponentScope(component_en)
        compname = TypeHelper.resolve(component_en)
        json = self._get_json_for_device(myjson, compScope=compfilter)
        if (compname in json):
            entry = None
            if (isinstance(json[compname], list)):
                if (idx >= 0 and idx < len(json[compname])):
                    entry = json[compname][idx]
            else:
                entry = json[compname]
            if entry and (fieldname in entry):
                return entry[fieldname]
        return "<not_found>"

    def _get_field_for_all(self, myjson, component_en, fieldname):
        retval = []
        compfilter = ComponentScope(component_en)
        compname = TypeHelper.resolve(component_en)
        json = self._get_json_for_device(myjson, compScope=compfilter)
        if (compname in json):
            entry = None
            if (isinstance(json[compname], list)):
                for idx in json[compname]:
                    if fieldname in idx:
                        retval.append(idx[fieldname])
            else:
                entry = json[compname]
                if fieldname in json[compname]:
                    retval.append(json[compname][fieldname])
        return retval

    def _get_field_from_action(self, rjson, *args):
        retval = rjson
        for arg in args:
            if arg in retval:
                retval = retval[arg]
            else:
                return None
        return retval

    # End Member APIs

    def _build_cmd_list(self):
        cmdlist = {}
        for proto in self.protofactory:
            for k in proto.cmds:
                if not k in cmdlist:
                    cmdlist[k] = []
                cmdlist[k].append(proto.cmds[k])
        commands = []
        for cmd in cmdlist:
            commands.append(cmd)
            args = {}
            arg_counter = 0
            inited = False
            for proto_cmd in cmdlist[cmd]:
                if type(proto_cmd) == int:
                    continue
                if 'Args' in proto_cmd:
                    my_counter = 0
                    for arg in proto_cmd['Args']:
                        my_counter = my_counter + 1
                        if not arg in args:
                            if inited:
                                logger.debug("ERROR: " + cmd + " has additional arg" + arg)
                            else:
                                arg_counter = arg_counter + 1
                                args[arg] = proto_cmd['Args'][arg]
                        if arg in args and args[arg] != proto_cmd['Args'][arg]:
                            logger.debug("ERROR: " + cmd + " different argument type")
                    if my_counter != arg_counter:
                        logger.debug("ERROR: " + cmd + " different # of arguments across protocols!")
                inited = True
        return commands

    def _make_all_methods(self):
        fcmds = self._build_cmd_list()
        for fname in fcmds:
            self._make_method(fname)

    def _make_method(self, fname):
        def func1(**kwargs):
            myname = func1.__name__
            if not hasattr(self, 'cfactory') or self.cfactory == None:
                logger.error(self.ipaddr+" : Protocol not initialized!")
                return {'Status': 'Failed', 'Message': 'Protocol not initialized'}
            return self.cfactory.operation(fname, **kwargs)

        func1.__name__ = fname
        setattr(self, fname, func1)


class iBaseTopologyInfo:
    def __init__(self, mytype, json):
        self.mytype = mytype
        self.json = {}
        self.system = None
        self.static_groups = {}
        self._load(json)

    def _load(self, json):
        if self.my_is_mytype(json):
            self.json = json
            self.system = self.my_load()
        return True

    def _add_myself(self, topobuilder, group):
        topobuilder.add_device([self.system['_Type'], self.system['Key']], group)

    def _add_assoc(self, topobuilder, *args):
        topobuilder.add_assoc(*args)

    def _remove_assoc(self, topobuilder, *args):
        topobuilder.remove_assoc(*args)

    def create_static_groups(self, topobuilder):
        if self.system and (self.system['_Type'] not in self.static_groups):
            self.static_groups[self.system['_Type']] = True
            self.my_static_groups(topobuilder)
        return self

    def create_groups(self, topobuilder):
        if self.system: self.my_groups(topobuilder)
        return self

    def create_assoc(self, topobuilder):
        if self.system: self.my_assoc(topobuilder)
        return self

    def my_is_mytype(self, json):
        return True

    def my_load(self, json):
        pass

    def my_groups(self, topobuilder):
        pass

    def my_static_groups(self, topobuilder):
        pass

    def my_assoc(self, topobuilder):
        pass
