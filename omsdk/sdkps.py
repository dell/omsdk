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
import logging

logger = logging.getLogger(__name__)


class PsShell:
    def __init__(self):
        pass

    def execute(self, cmd):
        logger.debug("Executing: " + cmd)
        proc = subprocess.Popen(["powershell", "-outputformat", "XML", "-command", "" + cmd + ""],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wrapper = io.TextIOWrapper(proc.stdout, encoding="utf-8")
        t = wrapper.readline()

        output = io.StringIO()
        for line in wrapper:
            tt = line.rstrip()
            output.write(tt)

        data_json = {}
        if output.getvalue() == "":
            return data_json
        domtree = xml.dom.minidom.parseString(output.getvalue())
        collection = domtree.documentElement
        counter = 0
        for obj in collection.childNodes:
            counter = counter + 1
            mydata = self.print_objx("", obj)
            name = "name" + str(counter)
            if "ToString" in mydata:
                name = mydata["ToString"]
            if "f2" in mydata:
                value = mydata["f2"]
            if not name in data_json:
                data_json[name] = []
            data_json[name].append(value)
        for name in data_json:
            if len(data_json[name]) == 0:
                data_json[name] = None
            elif len(data_json[name]) == 1:
                data_json[name] = data_json[name][0]

        return data_json

    def print_objx(self, n, obj):
        tst = {}
        counter = 0
        if obj.hasAttributes():
            for i in range(0, obj.attributes.length):
                attr = obj.attributes.item(i)
                tst[attr.name] = attr.value
        for objns in obj.childNodes:
            if objns.nodeType == objns.ELEMENT_NODE:
                # empty node
                if objns.firstChild == None:
                    counter = counter + 1
                    tst["f" + str(counter)] = objns.firstChild
                elif objns.firstChild.nodeType == objns.firstChild.TEXT_NODE:
                    var = objns.getAttribute("N")
                    if var is None or var == "":
                        var = objns.tagName
                    if objns.tagName == "ToString":
                        tst[objns.tagName] = objns.firstChild.data
                    else:
                        tst[var] = objns.firstChild.data
                else:
                    k = self.print_objx(n + " ", objns)
                    var = objns.getAttribute("N")
                    if var is None or var == "":
                        counter = counter + 1
                        var = "f" + str(counter)
                    tst[var] = k
                # counter = counter - 1
            else:
                logger.debug(">>> not element>>" + str(objns.tagName))
        return tst
