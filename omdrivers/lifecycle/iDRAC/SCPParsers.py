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
import re
import json
import xml.etree.ElementTree as ET
from omsdk.typemgr.ClassType import *
from omdrivers.types.iDRAC.iDRAC import *
from omdrivers.types.iDRAC.BIOS import *
from omdrivers.types.iDRAC.RAID import *
from omdrivers.types.iDRAC.NIC import *
from omdrivers.types.iDRAC.FCHBA import *
from omdrivers.types.iDRAC.SystemConfiguration import *

import logging


# Uncomment valid Attributes and place it inside the tree
class T(ET.TreeBuilder):
    def comment(self, data):
        k = data.strip()
        if re.match('<[^ >]+( [^>]+)*>[^<]*</[^>]+>', k):
            t = ET.fromstring(k)
            self.start(t.tag, dict([(k, v) for (k, v) in t.items()]))
            if not t.text: t.text = ""
            self.data(t.text)
            self.end(t.tag)


class XMLParser(object):
    def __init__(self, cspecfile):
        self.config_spec = {}
        if os.path.exists(cspecfile):
            with open(cspecfile) as f:
                self.config_spec = json.load(f)

    def _get_entry(self, comp_fqdd, sysconfig):
        for i in self.config_spec:
            if 'pattern' in self.config_spec[i]:
                if re.match(self.config_spec[i]['pattern'], comp_fqdd):
                    if i in sysconfig.__dict__:
                        return sysconfig.__dict__[i]
        return None

    def _load_child(self, node, entry):
        for child in node:
            if child.tag == 'Component':
                subnode = self._get_entry(child.get('FQDD'), entry)
                if subnode is None:
                    logger.debug('No component spec found for ' + child.get('FQDD'))
                    continue
                parent = None
                subentry = subnode
                if isinstance(subnode, ArrayType):
                    parent = subnode
                    subentry = parent.find_or_create()

                for attr in child.attrib:
                    subentry.add_attribute(attr, child.attrib[attr])

                self._load_child(child, subentry)
                continue

            attrname = child.get("Name")
            if attrname is None:
                logging.error("ERROR: No attribute found!!")
                continue

            if '.' not in attrname:
                # plain attribute
                if attrname not in entry.__dict__:
                    entry.__setattr__(attrname, StringField(child.text, parent=entry))
                    logging.debug(attrname + ' not found in ' + type(entry).__name__)
                    logging.debug("Ensure the attribute registry is updated.")
                    continue

                if child.text is None or child.text.strip() == '':
                    # empty - what to do?
                    if entry.__dict__[attrname]._type == str:
                        entry.__dict__[attrname]._value = ""
                else:
                    # Log error for unsupported value assignment and continue
                    try:
                        entry.__dict__[attrname]._value = child.text.strip()
                    except Exception as e:
                        logger.debug('Error while loading SCP for attribute "{}" : {}'.format(attrname, str(e)))
                        continue
                continue

            match = re.match('(.*)\.([0-9]+)#(.*)', attrname)
            if not match:
                print(attrname + ' not good ')
                continue

            (group, index, field) = match.groups()
            if group in entry.__dict__:
                grp = entry.__dict__[group]

                subentry = grp
                if isinstance(grp, ArrayType):
                    subentry = grp.find_or_create(index=int(index))

                if field not in subentry.__dict__:
                    field = field + '_' + group
                if field not in subentry.__dict__:
                    subentry.__dict__[field] = StringField(child.text, parent=subentry)
                    logging.debug(field + ' not found in ' + type(subentry).__name__)
                    logging.debug("Ensure the attribute registry is updated.")
                    continue
                if child.text is None or child.text.strip() == '':
                    # empty - what to do?
                    if subentry.__dict__[field]._type == str:
                        subentry.__dict__[field]._value = ""
                else:
                    try:
                        subentry.__dict__[field]._value = child.text.strip()
                    except Exception as ex:
                        print(group + "..." + field)
                        print(subentry._state)
                        print("ERROR:" + str(ex))

    def _load_scp(self, node, sysconfig):
        if sysconfig._alias and node.tag != sysconfig._alias:
            logger.debug(node.tag + " no match to " + sysconfig._alias)

        for attrib in node.attrib:
            sysconfig.add_attribute(attrib, node.attrib[attrib])

        for subnode in node:
            # Component!
            entry = self._get_entry(subnode.get('FQDD'), sysconfig)

            if entry is None:
                logger.debug('No component spec found for ' + subnode.get('FQDD'))
                continue

            parent = None
            if isinstance(entry, ArrayType):
                parent = entry
                entry = parent.find_or_create()

            for attrib in subnode.attrib:
                entry.add_attribute(attrib, subnode.attrib[attrib])

            self._load_child(subnode, entry)

    def parse_scp(self, fname):
        tree = ET.parse(fname, ET.XMLParser(target=T()))
        root = tree.getroot()
        sysconfig = SystemConfiguration(loading_from_scp=True)
        # Do a pre-commit - to save original values
        sysconfig.commit(loading_from_scp=True)
        self._load_scp(tree.getroot(), sysconfig)
        sysconfig._clear_duplicates()
        sysconfig.commit()
        return sysconfig
