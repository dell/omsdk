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

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class RestRequest:
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
        self.root = {}
        self.selector = None

    def enumerate(self, to, ruri, selectors, envSize=512000, mid=None, opTimeout=60):
        return self

    def set_header(self, to, ruri, action, envSize=512000, mid=None, opTimeout=60):
        return self

    def add_selectors(self, selectors):
        return self
