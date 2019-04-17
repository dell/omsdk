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
import re
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class RedfishRequest:
    def __init__(self):
        self.root = {}
        self.selector = None

    def enumerate(self, to, ruri, selectors, envSize=512000, mid=None, opTimeout=60):
        return self

    def set_header(self, to, ruri, action, envSize=512000, mid=None, opTimeout=60):
        return self

    def add_selectors(self, selectors):
        return self

    def add_body(self, ruri, action, args):
        self.root = {}
        return self

    def add_error(self, ex):
        return self

    def identify(self):
        return self

    def get_text(self):
        return json.dumps(self.root)


class RedfishResponse:
    def __init__(self):
        pass

    def strip_ns(self, s, stripNS):
        return (re.sub(".*:", "", s) if stripNS else s)

    def execute_str(self, value, stripNS=True):
        return json.loads(value)

    def get_message(self, fault):
        msg = None
        return msg
