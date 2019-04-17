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
import traceback
import json
from enum import Enum

import xml.etree.ElementTree as ET

import requests
import requests.adapters
import requests.exceptions
import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth

from omsdk.sdkprotobase import ProtocolBase
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.http.sdkrestpdu import RestRequest, RestResponse
from omsdk.http.sdkhttpep import HttpEndPoint, HttpEndPointOptions
from pprint import pprint

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class RestOptions(HttpEndPointOptions):
    def __init__(self):
        if PY2:
            super(RestOptions, self).__init__()
        else:
            super().__init__()


class RestProtocolBase(ProtocolBase):
    def __init__(self, ipaddr, creds, pOptions):
        if PY2:
            super(RestProtocolBase, self).__init__()
        else:
            super().__init__()
        headers = None
        self._logger = logging.getLogger(__name__)

    def reset(self, ignore=True):
        self._proto_reset()

    def identify(self):
        """
        Identifies the target product
        Curently _communicate has hardcoded data
        """
        # wsm = RestRequest()
        # wsm.identify()
        system = self._communicate("System", "/redfish/v1/Systems")
        if 'Dell' in str(system['Data']['System'][0]['Manufacturer']):
            return system
        else:
            return None

    def enumerate(self, clsName, resource, select={}, resetTransport=False):
        # wsm = RestRequest()
        # print("sdkrestbase: ",clsName," ",resource," ",self.ipaddr," user ",self.username," pass ",self.password)
        # wsm.enumerate(to = self._proto_endpoint(), ruri=resource, selectors = select)
        return self._communicate(clsName, resource)

    # Operation Invoke
    def opget(self, ruri, name, args):
        pass

    def operation(self, wsmancmds, cmdname, *args):
        pass

    def _proto_connect(self):
        pass

    def _proto_ship_payload(self, payload):
        pass

    def _proto_endpoint(self):
        pass

    def _proto_reset(self):
        pass

    def _communicate(self, clsName, resource):
        out = self._parse_output(clsName, resource)
        return out

    def printx(self, json_object):
        if json_object is None:
            print("<empty json>")
            return False
        print(json.dumps(json_object, sort_keys=True, indent=4,
                         separators=(',', ': ')))

    # retVal['Status'] = Success, Failed, Invalid JSON,
    # retval['Data'][component] = {}
    # retval['Fault.Data']['Reason'] = Reason
    # retval['Fault.Data']['Text'] = Message
    # retval['Message'] = Message
    # retval['Return'] = enum(ReturnValue).value
    # retval['Job']['JobId'] = jobid
    def _parse_output(self, clsName, resource):
        url = "https://" + self.ipaddr + resource[0]
        authttp = HTTPBasicAuth(self.username, self.password)
        myResponse = requests.get(url, auth=authttp, verify=False)
        # print(myResponse.status_code)
        retval = {}
        retval['Data'] = {}
        retval['Status'] = 'Failure'
        if (myResponse.ok):
            retval['Status'] = 'Success'
            jData = json.loads(myResponse.content)
            ix = 1
            oDataList = jData
            interMemb = oDataList
            while interMemb != None:
                oDataList = oDataList[resource[ix]]
                # print("WHILE ODATALIST is ",ix)
                # pprint(oDataList)
                ix = ix + 1
                try:
                    interMemb = oDataList[resource[ix]]
                except IndexError:
                    interMemb = None

            # print("ODATALIST is")
            # pprint(oDataList)
            # if 'Members' in jData:
            comp = []
            for mem in oDataList:
                # print("Member FOUND ", mem)
                url = "https://" + self.ipaddr + mem["@odata.id"]
                memResponse = requests.get(url, auth=authttp, verify=False)
                if (memResponse.ok):
                    compjData = json.loads(memResponse.content)
                    # pprint(compjData)
                    comp.append(compjData)
                memResponse.close()
            retval['Data'][clsName] = comp
        else:
            myResponse.raise_for_status()
        return retval
