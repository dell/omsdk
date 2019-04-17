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
import json
import os

sys.path.append(os.getcwd())

from pprint import pprint

from sys import stdout, path
from omsdk.sdkenum import ComponentScope
from omsdk.sdkenum import CreateMonitorScopeFilter
from omsdk.sdkenum import MonitorScopeFilter, MonitorScope
from omsdk.sdkinfra import sdkinfra
import logging

logger = logging.getLogger(__name__)


class XMLFormatter:
    def __init__(self):
        self.mystring = ""

    def init(self, comp):
        self.mystring += '  <component name="' + comp + '">\n'

    def start(self, index):
        if index != -1:
            self.mystring += '    <instance index="' + str(index) + '">\n'
        else:
            self.mystring += '    <instance>\n'

    def append_nvpair(self, name, value):
        self.mystring += '      <attribute name="' + name + '">' + value + '</attribute>\n'
        self.comma = ", "

    def end(self, comp):
        self.mystring += "    </instance>\n"

    def finish(self):
        self.mystring += "  </component>"


class StringFormatter:
    def __init__(self, eol="\n"):
        self.eol = eol

    def init(self, comp):
        self.mystring = ""

    def start(self, index):
        if index != -1:
            self.mystring += "#" + str(index) + " "
        self.comma = ""

    def append_nvpair(self, name, value):
        self.mystring += self.comma + name + " = " + value
        self.comma = ", "

    def end(self, comp):
        self.mystring += self.eol

    def finish(self):
        pass


class SDKVisitor(object):
    def __init__(self, entity, mfilter=None):
        self.entity = entity
        self.data = self.entity.get_json_device(mfilter)

    def _start(self, comp):
        pass

    def _do_continue(self, comp, obj):
        return True

    def _process(self, comp, obj, index=-1):
        pass

    def _end(self, comp):
        pass

    def visitAll(self):
        for comp in self.data:
            if comp in ['Subsystem']: continue
            self.visit(comp)
        return self

    def visit(self, comp):
        self._start(comp)
        for index in range(0, len(self.data[comp])):
            if self._do_continue(comp, self.data[comp][index]):
                self._process(comp, self.data[comp][index], index + 1)
        self._end(comp)
        return self


class EntitySerializer(SDKVisitor):
    def __init__(self, entity, formatter):
        super(EntitySerializer, self).__init__(entity)
        self.formatter = formatter

    def _start(self, comp):
        self.formatter.init(comp)

    def _process(self, comp, obj, index=-1):
        self.formatter.start(index)
        defs = self.entity.ref.defs
        for field in ["MainHealth", "Key", "BasicInventory", "Inventory"]:
            if field not in defs[comp]:
                continue
            if not isinstance(defs[comp][field], list):
                continue
            for field_name in defs[comp][field]:
                self.formatter.append_nvpair(field_name, obj[field_name])
        self.formatter.end(comp)

    def _end(self, comp):
        self.formatter.finish()


class HealthStateMachine:
    def __init__(self):
        self.algo = {}

    def add_transition(self, curstate, instate, outstate):
        if curstate not in self.algo:
            self.algo[curstate] = {}
        if instate not in self.algo[curstate]:
            self.algo[curstate][instate] = outstate
        else:
            logger.debug("Duplicate State : " + curstate + "." + instate)

    def worstCase(self):
        self.add_transition('Unknown', 'Healthy', 'Healthy')
        self.add_transition('Unknown', 'Warning', 'Warning')
        self.add_transition('Unknown', 'Critical', 'Critical')
        self.add_transition('Healthy', 'Warning', 'Warning')
        self.add_transition('Healthy', 'Critical', 'Critical')
        self.add_transition('Warning', 'Critical', 'Critical')
        return self

    def transition(self, comp, curstate, instate):
        # logger.debug("[{0}] curstate={1} instate={2}".format(comp,curstate,instate))
        if curstate not in self.algo:
            return curstate
        if instate not in self.algo[curstate]:
            return curstate
        return self.algo[curstate][instate]


class WorstCaseHealth:
    Algorithm = HealthStateMachine().worstCase()


class SDKHealthVisitor(SDKVisitor):
    health_states = {
        'Healthy': 0,
        'Warning': 1,
        'Critical': 2,
        'Unknown': 3
    }
    HealthFilter = MonitorScopeFilter(MonitorScope.MainHealth)

    def __init__(self, entity):
        super(SDKHealthVisitor, self).__init__(entity, self.HealthFilter)
        self.health = {}

    def _get_subsystem_health(self, comp):
        if 'Subsystem' in self.data:
            for cjson in self.data['Subsystem']:
                if cjson['Key'] == comp and 'PrimaryStatus' in cjson:
                    return cjson['PrimaryStatus']
        return None

    def _start(self, comp):
        self.subsystem_health = self._get_subsystem_health(comp)
        self.health[comp] = 'Unknown'

    def _do_continue(self, comp, obj):
        if self.subsystem_health or self.health[comp] == 'Critical':
            return False
        return True

    def _process(self, comp, obj, index=-1):
        if self.subsystem_health:
            return False

        comp_health = 'Unknown'
        for health_field in obj:
            if health_field == 'Key': continue
            comp_health = obj[health_field]
            if comp_health not in self.health_states:
                comp_health = 'Unknown'

        self.health[comp] = WorstCaseHealth.Algorithm.transition(comp,
                                                                 self.health[comp], comp_health)
        return True

    def _health_code(self, comp):
        return self.health_states[self.health[comp]]

    def printx(self):
        for i in self.health:
            print("    {0:20.20s} <> {1:20.20s}".format(i, self.health[i]))
        return self
