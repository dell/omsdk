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
import subprocess
import io
from xml.dom.minidom import parse
import xml.dom.minidom
import json
import re
import uuid
import sys
import xml.etree.ElementTree as ET

import sys
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class WsManRequest:
    envAttrs = {
        'xmlns:enc': 'http://www.w3.org/2003/05/soap-encoding',
        'xmlns:env': 'http://www.w3.org/2003/05/soap-envelope',
        'xmlns:tns': 'http://schemas.microsoft.com/wmx/2005/06',
        # xmlns:a = xmlns:wsa
        'xmlns:a': 'http://schemas.xmlsoap.org/ws/2004/08/addressing',
        'xmlns:wse': 'http://schemas.xmlsoap.org/ws/2004/08/eventing',
        # xmlns:n = xmlns:wsen
        'xmlns:n': 'http://schemas.xmlsoap.org/ws/2004/09/enumeration',
        # xmlns:w = xmlns:wsman
        'xmlns:w': 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd',
        # xmlns:b = xmlns:wsmb
        'xmlns:b': 'http://schemas.dmtf.org/wbem/wsman/1/cimbinding.xsd',
        'xmlns:wsmid': 'http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd',
        # xmlns:x = xmlns:wxf
        'xmlns:x': 'http://schemas.xmlsoap.org/ws/2004/09/transfer',
        'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:p': 'http://schemas.microsoft.com/wbem/wsman/1/wsman.xsd',
    }

    def __init__(self):
        self.root = ET.Element('env:Envelope', self.envAttrs)
        self.header = ET.SubElement(self.root, 'env:Header')
        self.body = ET.SubElement(self.root, 'env:Body')
        self.selector = None

    def enumerate(self, to, ruri, selectors, filter=None, envSize=512000, mid=None, opTimeout=60):
        self.set_header(to, ruri, "http://schemas.xmlsoap.org/ws/2004/09/enumeration/Enumerate", envSize, mid,
                        opTimeout)
        if (len(selectors) > 0):
            self.add_selectors(selectors)
        selset = ET.SubElement(self.body, 'n:Enumerate')
        args = {'OptimizeEnumeration': '', 'MaxElements': 32000}
        for i in args:
            myto = ET.SubElement(selset, 'w:' + i)
            myto.text = str(args[i])

        if filter:
            myto = ET.SubElement(selset, 'w:Filter',
                                 {'Dialect': 'http://schemas.microsoft.com/wbem/wsman/1/WQL'})
            myto.text = str(filter)

        return self

    def set_header(self, to, ruri, action, envSize=512000, mid=None, opTimeout=60):
        myto = ET.SubElement(self.header, 'a:To')
        myto.text = to
        myto = ET.SubElement(self.header, 'w:ResourceURI',
                             {'env:mustUnderstand': 'true'})
        myto.text = ruri
        myto = ET.SubElement(self.header, 'a:ReplyTo')
        myto = ET.SubElement(myto, 'a:Address',
                             {'env:mustUnderstand': 'true'})
        myto.text = "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous"
        myto = ET.SubElement(self.header, 'a:Action',
                             {'env:mustUnderstand': 'true'})
        myto.text = action
        myto = ET.SubElement(self.header, 'w:MaxEnvelopeSize',
                             {'env:mustUnderstand': 'true'})
        myto.text = str(envSize)
        if not mid:
            mid = uuid.uuid4()
        myto = ET.SubElement(self.header, 'a:MessageID')
        myto.text = 'uuid:{0}'.format(mid)
        myto = ET.SubElement(self.header, 'w:Locale',
                             {'env:mustUnderstand': 'false',
                              'xml:lang': 'en-US'})
        myto = ET.SubElement(self.header, 'p:DataLocale',
                             {'env:mustUnderstand': 'false',
                              'xml:lang': 'en-US'})
        myto = ET.SubElement(self.header, 'w:OperationTimeout')
        myto.text = 'PT{0}.000S'.format(int(opTimeout))
        return self

    def add_selectors(self, selectors):
        if self.selector is None:
            self.selector = ET.SubElement(self.header, 'w:SelectorSet')
        for i in selectors:
            myto = ET.SubElement(self.selector, 'w:Selector', {'Name': i})
            myto.text = selectors[i]
        return self

    def add_body(self, ruri, action, args):
        selset = ET.SubElement(self.body, 'p:' + action + "_INPUT", {'xmlns:p': ruri})
        for i in args:
            myto = ET.SubElement(selset, 'p:' + i)
            myto.text = str(args[i])
        return self

    def add_error(self, ex):
        selset = ET.SubElement(self.body, "ClientFault")
        selset = ET.SubElement(selset, "Reason")
        selset = ET.SubElement(selset, "Text")
        selset.text = str(ex)
        return self

    def identify(self):
        ET.SubElement(self.body, 'wsmid:Identify')
        return self

    def get_text(self):
        if PY2:
            return ET.tostring(self.root, encoding="utf8")
        else:
            t = ET.ElementTree(self.root)
            output = io.StringIO()
            t.write(output, encoding="unicode")
            return output.getvalue()

    def printx(self):
        logger.debug(ET.dump(self.root))


class WsManResponse:
    def __init__(self):
        pass

    def strip_ns(self, s, stripNS):
        return (re.sub(".*:", "", s) if stripNS else s)

    def execute_str(self, value, stripNS=True):
        domtree = xml.dom.minidom.parseString(value)
        return self._xmltojson(domtree, stripNS)

    def execute(self, fname, stripNS=True):
        domtree = xml.dom.minidom.parse(fname)
        return self._xmltojson(domtree, stripNS)

    def _newxmltojson(self, domtree, stripNS):
        data_json = {}
        counter = 0
        if domobj.items():
            for (attrname, attrvalue) in domobj.items():
                data_json[self.strip_ns(attrname, stripNS)] = attrvalue
        for obj in domobj.find("."):
            data_json[obj.tag] = self.data_depth(obj, stripNS)
        return data_json

    def data_depth(self, domobj, stripNS):
        tst = {}
        counter = 0
        if domobj.items():
            for (attrname, attrvalue) in domobj.items():
                tst[self.strip_ns(attrname, stripNS)] = attrvalue
        for objns in obj.find("."):
            if objns.text is None:
                tst[objns.tag] = self.data_depth(objns, stripNS)
            else:
                if objns.tag in tst and not isinstance(tst[objns.tag], list):
                    tst[objns.tag] = [tst[objns.tag]]
                if objns.tag in tst:
                    tst[objns.tag].append(objns.text)
                else:
                    tst[objns.tag] = objns.text
        return tst

    def _xmltojson(self, domtree, stripNS):
        data_json = {}
        collection = domtree.documentElement
        counter = 0
        if collection.hasAttributes():
            for i in range(0, collection.attributes.length):
                attr = collection.attributes.item(i)
                data_json[self.strip_ns(attr.name, stripNS)] = attr.value
        for obj in collection.childNodes:
            if obj.nodeType == obj.TEXT_NODE:
                if obj.nodeValue.strip() == "":
                    continue
            value = self.print_objx(obj, stripNS)
            data_json[self.strip_ns(obj.nodeName, stripNS)] = value

        return data_json

    def print_objx(self, obj, stripNS):
        tst = {}
        counter = 0
        if (obj.nodeType == obj.TEXT_NODE):
            return {}
        if obj.hasAttributes():
            for i in range(0, obj.attributes.length):
                attr = obj.attributes.item(i)
                tst[self.strip_ns(attr.name, stripNS)] = attr.value
        for objns in obj.childNodes:
            if objns.nodeType == objns.ELEMENT_NODE:
                name = self.strip_ns(objns.nodeName, stripNS)
                value = None
                if objns.firstChild == None:
                    value = objns.firstChild
                elif objns.firstChild.nodeType == objns.firstChild.TEXT_NODE \
                        and len(objns.childNodes) <= 1:
                    value = objns.firstChild.data
                else:
                    value = self.print_objx(objns, stripNS)
                if name in tst and not isinstance(tst[name], list):
                    tst[name] = [tst[name]]
                if name in tst:
                    tst[name].append(value)
                else:
                    tst[name] = value
            elif objns.nodeType == objns.TEXT_NODE:
                if len(objns.nodeValue.strip()) > 0:
                    tst[objns.nodeName] = objns.nodeValue
            elif objns.nodeType == objns.CDATA_SECTION_NODE:
                if len(objns.nodeValue.strip()) > 0:
                    tst[objns.nodeName] = objns.nodeValue
            else:
                logger.debug(">>> not element>>" + str(objns.nodeType))
        return tst

    def get_message(self, fault):
        msg = None
        while fault != None and msg == None:
            if not isinstance(fault, dict):
                msg = fault
            elif "Message" in fault:
                if isinstance(fault["Message"], dict):
                    fault = fault["Message"]
                else:
                    msg = fault["Message"]
            elif "WSManFault" in fault:
                fault = fault["WSManFault"]
            else:
                for field in fault:
                    if field.startswith("Fault"):
                        m = self.get_message(fault[field])
                        if not m is None:
                            msg = m
                            break
                    elif field == "Text":
                        msg = fault[field]
        return msg
