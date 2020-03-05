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
import io
import logging
import json
from omsdk.sdkcenum import EnumWrapper
from omsdk.http.sdkrestpdu import RestRequest
from omsdk.http.sdkhttpep import HttpEndPointOptions, AuthenticationType
from omsdk.http.sdkrestbase import RestProtocolBase
from omsdk.http.sdkhttpep import HttpEndPoint
from omsdk.sdkprotopref import ProtocolEnum
logger = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

ReturnValueMap = {
    'Success': 0,
    'Error': 2,
    'JobCreated': 4096,
    'Invalid': -1
}

ReturnValue = EnumWrapper('ReturnValue', ReturnValueMap).enum_type


class RestOptions(HttpEndPointOptions):
    def __init__(
            self, authentication=AuthenticationType.Basic, port=443, connection_timeout=10,
            read_timeout=10, max_retries=1, verify_ssl=False
    ):
        if PY2:
            super(RestOptions, self).__init__(
                ProtocolEnum.REST, authentication, port, connection_timeout,
                read_timeout, max_retries, verify_ssl
            )
        else:
            super().__init__(
                ProtocolEnum.REST, authentication, port, connection_timeout,
                read_timeout, max_retries, verify_ssl
            )


class RestProtocol(RestProtocolBase):
    def __init__(self, ipaddr, creds, pOptions):
        if PY2:
            super(RestProtocol, self).__init__(ipaddr, creds, pOptions)
        else:
            super().__init__(ipaddr, creds, pOptions)
        headers = {'Content-Type': 'application/json'}
        self.proto = HttpEndPoint(ipaddr, creds, pOptions, headers)
        self.ipaddr = ipaddr
        self.username = creds.username
        self.password = creds.password
        self._logger = logging.getLogger(__name__)

    def identify(self):
        """ Identifies the target product """
        wsm = RestRequest()
        wsm.identify()
        return self._communicate(wsm)


    def printx(self, json_object):
        if json_object is None:
            logger.debug("<empty json>")
            return False
        logger.debug(json.dumps(json_object, sort_keys=True, indent=4,
                                separators=(',', ': ')))

