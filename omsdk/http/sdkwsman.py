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

from omsdk.http.sdkwsmanbase import WsManProtocolBase
from omsdk.http.sdkhttpep import HttpEndPoint, HttpEndPointOptions

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class WsManProtocol(WsManProtocolBase):
    def __init__(self, ipaddr, creds, pOptions):
        if PY2:
            super(WsManProtocol, self).__init__(ipaddr, creds, pOptions)
        else:
            super().__init__(ipaddr, creds, pOptions)
        headers = {
            'Content-Type': 'application/soap+xml;charset=UTF-8'
        }
        self.proto = HttpEndPoint(ipaddr, creds, pOptions, headers)

    def _proto_connect(self):
        self.proto.connect()

    def _proto_ship_payload(self, payload):
        return self.proto.ship_payload(payload)

    def _proto_endpoint(self):
        return self.proto.endpoint

    def _proto_reset(self):
        return self.proto.reset()
