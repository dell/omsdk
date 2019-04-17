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
import math


class iUnitsFactory(object):

    def __init__(self):
        self.units_spec = {
            "Bytes": [
                ("B", 1024),
                ("KB", 1024),
                ("MB", 1024),
                ("GB", 1024),
                ("TB", 1024)
            ],
            "Voltage": [
                ("V", 1000),
                ("KV", 1000),
            ],
            "Bandwidth": [
                ("Bps", 1024),
                ("KBps", 1024),
                ("MBps", 1024),
                ("GBps", 1024),
                ("TBps", 1024)
            ],
            "Watts": [
                ("W", 1000),
                ("KW", 1000),
                ("MW", 1000),
                ("GW", 1000),
                ("TW", 1000)
            ],
            "ClockSpeed": [
                ("Hz", 1000),
                ("KHz", 1000),
                ("MHz", 1000),
                ("GHz", 1000),
                ("THz", 1000)
            ],
            "MetricDistance": [
                ("MM", 10),
                ("CM", 100),
                ("M", 1000),
                ("KM", 1000),
            ]
        }

    def Convert(self, rjson):
        for field in ['Type', 'InUnits', 'Value']:
            if not field in rjson:
                raise Exception("No " + field + " in the json")

        if not (isinstance(rjson['Value'], int) or \
                isinstance(rjson['Value'], float)):
            raise Exception("invalid value type!")

        if not rjson['Type'] in self.units_spec:
            raise Exception("Units for " + rjson['Type'] + " not defined")
        uspec = self.units_spec[rjson['Type']]

        cur_index = -1
        for i in range(0, len(uspec)):
            if rjson['InUnits'] == uspec[i][0]:
                cur_index = i
        if cur_index < 0:
            raise Exception("Invalid Value Units Specified")

        tgt_index = -1
        expected_units = None
        if 'OutUnits' in rjson:
            expected_units = rjson['OutUnits']
        if 'Metrics' in rjson:
            expected_units = rjson['Metrics']

        if not expected_units:
            tgt_index = len(uspec)
        else:
            for i in range(0, len(uspec)):
                if expected_units == uspec[i][0]:
                    tgt_index = i
            if tgt_index < 0:
                tgt_index = len(uspec)
        if tgt_index < 0:
            raise Exception("Invalid Value Units Specified for target")

        final_value = rjson['Value']
        found = False
        if tgt_index == cur_index:
            found = True
            final_spec = uspec[tgt_index][0]
        elif tgt_index > cur_index:
            k = rjson['Value']
            for i in range(cur_index, tgt_index + 1):
                k1 = k / uspec[i][1]
                if (expected_units == None and k1 < 1) or (i == tgt_index):
                    found = True
                    final_value = k
                    final_spec = uspec[i][0]
                    break
                k = k1
        elif tgt_index < cur_index:
            k = rjson['Value']
            for i in range(tgt_index, cur_index):
                k = k * uspec[i][1]
            found = True
            final_value = k
            final_spec = uspec[i][0]

        final_value = round(final_value, 2)
        if not found:
            return rjson['Value']
        if 'Metrics' in rjson:
            return final_value
        else:
            return str(final_value) + " " + final_spec

    def append_sensors_unit(self, reading, unitmodifier, unitstr):
        if reading :
            if str(reading).isdigit() :
                retval = float(reading) * math.pow(10, int(unitmodifier))
                s = str(retval).rstrip('0').rstrip('.')
                if unitstr:
                    s = s + " " + unitstr
                return s
        return "Not Available"

UnitsFactory = iUnitsFactory()
