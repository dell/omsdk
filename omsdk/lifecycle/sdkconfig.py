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
import glob
import re
import io
import os
from enum import Enum
from sys import stdout
import sys
from omsdk.sdkcenum import TypeHelper, EnumWrapper
from omsdk.sdkcunicode import UnicodeWriter, UnicodeStringWriter, UnicodeHelper
import threading
import logging

logger = logging.getLogger(__name__)


class ConfigFactory(object):
    configmap = {}
    configmap_lock = threading.Lock()

    @staticmethod
    def get_config(config_dir, comp_spec):
        cf = ConfigFactory
        if not config_dir in cf.configmap:
            with cf.configmap_lock:
                if not config_dir in cf.configmap:
                    cf.configmap[config_dir] = Config(config_dir, comp_spec)
        if config_dir in cf.configmap:
            return cf.configmap[config_dir]


class AttribRegistryNames(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Config:
    def __init__(self, direct, complist):

        # self.defs contains mapping between AttribRegistry ==> AttribRegistry.json
        self.defs = {}
        # self.complist contains compspec
        self.complist = complist

        # load self.defs from config directory
        for file1 in glob.glob(os.path.join(direct, "*.json")):
            with open(file1) as enum_data:
                myjson = json.load(enum_data)
                comp = re.sub("^.*/", "", myjson["$ref"])
                self.defs[comp] = myjson

        # self.compen is the enum for AttribRegistry's
        compens = {}
        for i in self.defs:
            compens[i] = i
        self.compen = EnumWrapper("ConfigComp", compens).enum_type

        arspec = {}
        for cenum in self.compen:
            ens = {}
            cvalue = TypeHelper.resolve(cenum)
            for i in self.get_fields(cvalue):
                ens[i] = i
            arspec[cvalue] = EnumWrapper(cvalue + "ConfigEnum", ens).enum_type
        self.arspec = AttribRegistryNames(arspec)

    def get_groups(self, comp):
        return self.defs[comp]["definitions"][comp]["config_groups"]

    def get_fields(self, comp):
        return self.defs[comp]["definitions"][comp]["properties"].keys()

    def get_def_value(self, comp, prop):
        myprop = self.defs[comp]["definitions"][comp]["properties"][prop]
        defval = None
        if "default" in myprop:
            defval = myprop["default"]
        if "type" in myprop:
            if myprop["type"] in self.defs[comp]["definitions"]:
                defval = self.defs[comp]["definitions"][myprop["type"]]["enum"][0]
        if defval is None:
            defval = ""
        return defval

    def get_comp_from_fqdd(self, fqdd):
        for comp in self.complist:
            if "pattern" in self.complist[comp]:
                if re.match(self.complist[comp]["pattern"], fqdd):
                    return comp
        return "invalid"

    def print_default(self, fqdd):
        comp = self.get_comp_from_fqdd(fqdd)
        if comp == "invalid":
            logger.debug("Invalid Component defined!")
            return
        if not "registry" in self.complist[comp]:
            logger.debug("Invalid Registry defined!")
            return
        grps = self.get_groups(self.complist[comp]["registry"])
        self._write_output(stdout, "<Component FQDD=\"" + fqdd + "\">")
        mygrps = []
        srcgroups = grps
        if "groups" in self.complist[comp]:
            srcgroups = self.complist[comp]["groups"]
        for g in srcgroups:
            mygrps.append(g)
        if "excl_groups" in self.complist[comp]:
            for g in self.complist[comp]["excl_groups"]:
                if g in mygrps:
                    mygrps.remove(g)
        for group in mygrps:
            if not group in grps:
                # logger.debug("Invalid Group defined!")
                continue
            for i in grps[group]:
                defval = self.get_def_value(self.complist[comp]["registry"], i)
                if 'nogroup' in self.complist[comp] and self.complist[comp]['nogroup']:
                    self._write_output(stdout, "    <Attribute Name=\"" + i + "\">" + defval + "</Attribute>")
                else:
                    self._write_output(stdout,
                                       "    <Attribute Name=\"" + group + ".1#" + i + "\">" + defval + "</Attribute>")
        self._write_output(stdout, "</Component>")

    def _spit_scp(self, desiredcfg, output, depth=""):
        if depth == "":
            output._write_output("<SystemConfiguration>\n")
        for fqdd in desiredcfg:
            _comp = self.get_comp_from_fqdd(fqdd)
            if _comp == "invalid":
                logger.debug("Invalid Component defined!")
                continue
            if not "registry" in self.complist[_comp]:
                logger.debug("Invalid Registry defined!")
                continue
            comp = self.complist[_comp]["registry"]
            grps = self.get_groups(comp)
            output._write_output(depth + "  <Component FQDD=\"" + fqdd + "\">\n")
            for compen in desiredcfg[fqdd]:
                props = self.defs[comp]["definitions"][comp]["properties"]
                compen = UnicodeHelper.stringize(compen)
                if isinstance(compen, str):
                    self._spit_scp({compen: desiredcfg[fqdd][compen]}, output, depth + "  ")
                    continue
                if not TypeHelper.resolve(compen) in props:
                    logger.debug(TypeHelper.resolve(compen) + " is not found in props")
                    continue
                cvalue = TypeHelper.resolve(compen)
                idx = 1
                if not isinstance(desiredcfg[fqdd][compen], list):
                    idx = self._attr_print(output, depth, _comp, cvalue, props,
                                           desiredcfg[fqdd][compen], idx)
                else:
                    for ent in desiredcfg[fqdd][compen]:
                        idx = self._attr_print(output, depth, _comp, cvalue, props, ent, idx)
            output._write_output(depth + "  </Component>\n")
        if depth == "":
            output._write_output("</SystemConfiguration>\n")

    def _attr_print(self, output, depth, _comp, cvalue, props, desired, idx):
        if desired is None:
            return (idx + 1)
        if isinstance(desired, tuple):
            idx = desired[0]
            desired = desired[1]
        if "name" in props[cvalue]:
            atname_postfix = props[cvalue]["name"]
        else:
            atname_postfix = cvalue

        if 'nogroup' in self.complist[_comp] and \
                self.complist[_comp]['nogroup']:
            atname = ""
        else:
            atname = props[cvalue]["qualifier"] + "." + str(idx) + "#"
        atname = atname + atname_postfix
        output._write_output(depth + "    <Attribute Name=\"" + atname + "\">")
        output._write_output(str(desired))
        output._write_output("</Attribute>\n")
        return (idx + 1)

    def format_scp(self, desiredcfg):
        with UnicodeStringWriter() as output:
            self._spit_scp(desiredcfg, output)
            return output.getvalue()

    def save_scp(self, desiredcfg, outputfile):
        with UnicodeWriter(outputfile) as output:
            self._spit_scp(desiredcfg, output)
