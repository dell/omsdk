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
import xml.etree.ElementTree as ET
import re
import os
import sys
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcenum import EnumWrapper

RowStatus = EnumWrapper("MS", {
    'Row_With_Valid_Key': 1,
    'Partial': 2,
    'Row_With_Invalid_Key': 3,
}).enum_type


class ConfigEntries(object):
    def __init__(self, keyfield):
        self.valuemap = {}
        self.compmap = {}
        self.slotmap = {}
        self.keyfield = keyfield
        self.loaded = False

    def process(self, fname, incremental):
        valuemap = {}
        domtree = ET.parse(fname)
        system = domtree.getroot()

        for component in system.findall("./Component"):
            fqdd = component.get("FQDD")
            if not incremental and fqdd in self.compmap:
                del self.compmap[fqdd]
            if fqdd not in self.compmap:
                self.compmap[fqdd] = {}
            for attribute in component.findall("./Attribute"):
                self.compmap[fqdd][attribute.get("Name")] = attribute.text

        for component in system.findall("./Component"):
            for attribute in component.findall("./Attribute"):
                for comp in self.keyfield:
                    pattern = self.keyfield[comp]['Pattern']
                    result = re.search(pattern, attribute.get("Name"))
                    if not result: continue
                    index = 1
                    if len(result.groups()) == 1:
                        field = result.group(1)
                    if len(result.groups()) == 2:
                        index = int(result.group(1))
                        field = result.group(2)
                        self._add_entry(valuemap, comp, index,
                                        field, attribute.text)
        self._merge(valuemap)
        if not incremental:
            self.loaded = True

    def _add_entry(self, valuemap, comp, index, field, value):
        if not comp in valuemap:
            valuemap[comp] = []
        n = len(valuemap[comp])
        if n < index:
            valuemap[comp].extend([{} for i in range(n, index)])
        valuemap[comp][index - 1][field] = value
        valuemap[comp][index - 1]['_slot'] = index

    def _locate(self, valuemap, entry):
        for v in valuemap:
            if v['_slot'] == entry['_slot']:
                return v
        return None

    def _update_fields(self, vslot, entry):
        for i in entry:
            if i not in vslot or vslot[i] != entry[i]:
                vslot[i] = entry[i]

    def _merge(self, vmap):

        # cleanup vmap
        for comp in vmap:
            if comp not in self.valuemap:
                self.valuemap[comp] = []
            if comp not in self.slotmap:
                self.slotmap[comp] = []

            n = len(vmap[comp])
            for entry in vmap[comp]:
                if not '_slot' in entry:
                    # this slot is not present in the file!!
                    continue
                loc = self._locate(self.valuemap[comp], entry)
                nret = RowStatus.Row_With_Invalid_Key
                if comp in self.keyfield and \
                        'Validate' in self.keyfield[comp]:
                    nret = self.keyfield[comp]['Validate'](entry)
                if loc is None:
                    if nret == RowStatus.Row_With_Valid_Key:
                        self.valuemap[comp].append(entry)
                        if entry['_slot'] in self.slotmap[comp]:
                            self.slotmap[comp].remove(entry['_slot'])
                    elif entry['_slot'] not in self.slotmap[comp]:
                        self.slotmap[comp].append(entry['_slot'])
                elif nret == RowStatus.Row_With_Invalid_Key:
                    self.valuemap[comp].remove(loc)
                    if entry['_slot'] not in self.slotmap[comp]:
                        self.slotmap[comp].append(entry['_slot'])
                else:
                    self._update_fields(loc, entry)

    def find_existing(self, comp, key):
        if key is None: key = ""
        if comp not in self.valuemap:
            return {'Status': 'Failed',
                    'Message': 'This component is not supported by the SDK'}
        if comp not in self.slotmap:
            return {'Status': 'Failed',
                    'Message': 'This component is not supported by the SDK'}
        if comp not in self.keyfield:
            return {'Status': 'Failed',
                    'Message': 'This component is not supported by the SDK'}
        if 'Key' not in self.keyfield[comp]:
            return {'Status': 'Failed',
                    'Message': 'This component does not have specification'}
        for entry in self.valuemap[comp]:
            if self.keyfield[comp]['Key'] in entry and \
                    entry[self.keyfield[comp]['Key']] == key:
                return {'Status': 'Success', 'retval': entry}
        return {'Status': 'Failed',
                'Message': 'Entry does not exists'}

    def check_and_get_empty_slot(self, comp, key):
        if key is None: key = ""
        if comp not in self.valuemap:
            return {'Status': 'Failed',
                    'Message': 'This component is not supported by the SDK'}
        if comp not in self.slotmap:
            return {'Status': 'Failed',
                    'Message': 'This component is not supported by the SDK'}
        if comp not in self.keyfield:
            return {'Status': 'Failed',
                    'Message': 'This component is not supported by the SDK'}
        if 'Key' not in self.keyfield[comp]:
            return {'Status': 'Failed',
                    'Message': 'This component does not have specification'}
        for entry in self.valuemap[comp]:
            if self.keyfield[comp]['Key'] in entry and \
                    entry[self.keyfield[comp]['Key']] == key:
                return {'Status': 'Failed',
                        'Message': 'Existing entry'}
        if len(self.slotmap[comp]) > 0:
            return {'Status': 'Success',
                    'retval': self.slotmap[comp][0]}

        return {'Status': 'Failed', 'Message': 'No empty slot found'}

    def get_component(self, comp):
        if comp in self.valuemap:
            return self.valuemap[comp]
        if comp in self.compmap:
            return self.compmap[comp]
        return None

    def get_comp_field(self, comp, field):
        if comp in self.valuemap:
            if field in self.valuemap[comp]:
                return self.valuemap[comp][field]
        if comp in self.compmap:
            if field in self.compmap[comp]:
                return self.compmap[comp][field]
        return None
