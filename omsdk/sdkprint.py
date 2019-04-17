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
from __future__ import print_function
import io
import logging
import threading
import time
import json
from enum import Enum
from json import JSONEncoder
from omsdk.sdkcenum import EnumWrapper, TypeHelper, PY2Enum
from pprint import pprint
from datetime import datetime
import xml.etree.ElementTree as ET
import traceback

import sys
import logging


logger = logging.getLogger(__name__)

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    from pysnmp.proto import rfc1902
    from pysnmp import debug
    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2Enum:
    from enum import EnumValue


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, str):
            return o
        if PySnmpPresent:
            if isinstance(o, rfc1902.Integer):
                return str(o)
            if isinstance(o, rfc1902.OctetString):
                return str(o)
        if isinstance(o, type):
            return str(type)
        if PY2Enum and isinstance(o, EnumValue):
            return o.key
        if isinstance(o, datetime):
            return str(datetime)
        return o.json_encode()


class Prettifyer:
    def prettify_json(self, json_object):
        return "<empty json>" if json_object is None else json.dumps(json_object,
                                                                     sort_keys=True,
                                                                     indent=4,
                                                                     separators=(',', ': '),
                                                                     cls=MyEncoder)


PrettyPrint = Prettifyer()
