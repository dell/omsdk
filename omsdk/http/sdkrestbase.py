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
import logging
import json
import hashlib
import requests
import requests.adapters
import requests.exceptions
import requests.packages.urllib3
from omsdk.sdkprotopref import ProtocolEnum
from omsdk.http.sdkhttpep import AuthenticationType
from omsdk.sdkprotobase import ProtocolBase
from omsdk.http.sdkhttpep import HttpEndPointOptions
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)
class RestOptions(HttpEndPointOptions):
    def __init__(self, authentication = AuthenticationType.Basic, port = 443, connection_timeout = 20,
                 read_timeout = 30, max_retries = 1, verify_ssl = False, cacheTimeout=180 ):
        if PY2:
            super(RestOptions, self).__init__(ProtocolEnum.REST, authentication, port, connection_timeout, read_timeout, max_retries,
                                              verify_ssl)
        else:
            super().__init__(ProtocolEnum.REST, authentication, port, connection_timeout, read_timeout, max_retries,
                             verify_ssl)


class RestProtocolBase(ProtocolBase):
    def __init__(self, ipaddr, creds, pOptions):
        if PY2:
            super(RestProtocolBase, self).__init__()
        else:
            super().__init__()
        headers = None
        self.pOptions = pOptions
        self._logger = logging.getLogger(__name__)
        self.token = None

    def reset(self, ignore=True):
        self._proto_reset()

    def identify(self):
        """
        Identifies the target product
        Curently _communicate has hardcoded data
        """
        system = self._communicate("System", "/redfish/v1/Systems")
        if 'Dell' in str(system['Data']['System'][0]['Manufacturer']):
            return system
        else:
            return None

    def enumerate(self, clsName, resource, select={}, resetTransport=False, filter=filter):
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

    def get_token(self):
        if self.token:
            return self.token
        else:
            try:
                url = "https://" + self.ipaddr
                if ':' in self.ipaddr:
                    url = "https://[" + self.ipaddr + ']:' + str(self.pOptions.port)
                user_details = self.username + '_' + self.password
                auth_string = hashlib.sha256(user_details.encode('utf-8')).hexdigest()
                headers = {'datatype': 'json'}
                login_response = requests.get(url + '/api/login/' + auth_string, headers=headers, verify=False)
                if login_response:
                    response = json.loads(login_response.content)
                    if response['status'][0]['response-type'] == 'Success':
                        self.token = response['status'][0]['response']
            except requests.exceptions.ConnectionError as err:
                logger.debug(err)
            except requests.exceptions.Timeout as err:
                logger.debug(err)

        return self.token

    def _parse_output(self, clsName, resource):
        xcomp = []
        url = "https://" + self.ipaddr
        if ':' in self.ipaddr:
            url = "https://[" + self.ipaddr + ']:' + str(self.pOptions.port)
        sessionKey = self.get_token()
        # Obtain the health of the system
        retval = {}
        retval['Data'] = {}
        retval['Status'] = 'Failure'
        if sessionKey:
            try:
                headers = {'sessionKey': sessionKey, 'datatype': 'json'}
                api_response = requests.get(url + resource['url'], headers=headers, verify=False)
                if api_response.ok:
                    response = json.loads(api_response.content)
                    if api_response.ok:
                        retval['Status'] = 'Success'
                        compjData = json.loads(api_response.content)
                        if resource.get('attribute', None):
                            xcomp += compjData[resource['attribute']]
                        else:
                            xcomp += [compjData]
                    retval['Data'][clsName] = xcomp
            except requests.exceptions.ConnectionError as err:
                logger.debug(err)
            except requests.exceptions.Timeout as err:
                logger.debug(err)

        else:
            retval['Data'][clsName] = xcomp
            logger.debug(url + resource['url'])
            logger.debug("data not found for this url")
        return retval

