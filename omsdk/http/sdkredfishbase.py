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
# Authors: Jagadeesh N V
#
import sys
import logging
import json

import requests
import requests.adapters
import requests.exceptions
import requests.packages.urllib3
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
# from requests_oauthlib import OAuth1Session, OAuth2Session

from omsdk.sdkprotobase import ProtocolBase
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.sdkprotopref import ProtoPreference, ProtocolEnum
from omsdk.http.sdkhttpep import HttpEndPoint, HttpEndPointOptions, AuthenticationType
import time

logger = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

class RedfishOptions(HttpEndPointOptions):
    """
           Options to establish REDFISH communication
    """
    def __init__(
                 self, urlbase='redfish/v1', authentication = AuthenticationType.Basic, port = 443, connection_timeout = 20,
                 read_timeout = 30, max_retries = 1, verify_ssl = False, cacheTimeout=180 
                ):
        """
                :param authentication: HTTP Authentication type 'Basic', 'Digest'
                :param port: https Port number for Redfish communication
                :param connection_timeout: time in seconds to wait for the server to connect before giving up
                :param read_timeout: time in seconds to wait for the server to read data before giving up
                :param max_retries: Http connection retries in case of failures
                :param verify_ssl: SSL Certificate verification
                :type authentication: Enum omsdk.http.sdkhttpep.AuthenticationType
                :type port: Int
                :type connection_timeout: Int
                :type read_timeout: Int
                :type verify_ssl: Boolean
        """
        if PY2:
            super(RedfishOptions, self).__init__(
                 ProtocolEnum.REDFISH, authentication, port, connection_timeout,
                 read_timeout, max_retries, verify_ssl
                )
        else:
            super().__init__(
                 ProtocolEnum.REDFISH, authentication, port, connection_timeout,
                 read_timeout, max_retries, verify_ssl
                )
        self.enid = ProtocolEnum.REDFISH
        self.urlbase = urlbase
        self.cacheTimeout = cacheTimeout #cache timeout in seconds

class RedfishProtocolBase(ProtocolBase):
    def __init__(self, ipaddr, creds, pOptions):
        if PY2:
            super(RedfishProtocolBase, self).__init__()
        else:
            super().__init__()
        headers = None
        self._logger = logging.getLogger(__name__)
        self.cache = {}
        self.data_cache = {}
        self.session = requests.session()
        self.pOptions = pOptions
        self.session.verify = self.pOptions.verify_ssl
        if not self.pOptions.verify_ssl: 
            requests.packages.urllib3.disable_warnings()
        if self.pOptions.authentication == AuthenticationType.Basic:
            self.session.auth = HTTPBasicAuth(creds.username, creds.password)
        if self.pOptions.authentication == AuthenticationType.Digest:
            print("Digest authentication not yet implimented")
            self.session.auth = HTTPDigestAuth(creds.username, creds.password)
        if self.pOptions.authentication == AuthenticationType.OAuth1:
            print("OAuth1 authentication not yet implimented")
        if self.pOptions.authentication == AuthenticationType.OAuth2:
            print("Not yet implimented", self.pOptions.authentication)

    def reset(self, ignore=True):
        if self.session:
            self.session.close()
            self.session = None

    def identify(self):
        """
        Identifies the target product
        Curently _communicate has hardcoded data
        """
        return None

    def enumerate(self, clsName, resource, select = {}, resetTransport = False, filter=filter):
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

    def fetch_cache(self, url):
        if url in self.cache:
            respDict = self.cache[url]
            rt = respDict['time']
            ct = int(time.time())
            if (ct-rt) < self.pOptions.cacheTimeout:
                return respDict['response']
        return None

    def add_cache(self, url, response):
        ts = time.time()
        respDict = {}
        respDict['time'] = int(ts)
        respDict['response'] = response
        self.cache[url] = respDict

    def _communicate(self, clsName, resource):
        out = self._parse_output(clsName, resource)
        return out

    def printx(self, json_object):
        if json_object is None:
            print("<empty json>")
            return False
        print(json.dumps(json_object, sort_keys=True, indent=4, \
              separators=(',', ': ')))

    def _parse_output(self, clsName, resource):
        urlConcat = '/'
        # authttp = HTTPBasicAuth(self.username, self.password)
        retval = {}
        xcomp = []
        retval['Data'] = {}
        retval['Status'] = 'Failure'

        ix = 0
        odataid = "@odata.id"
        if isinstance(resource, dict):
            if 'url' in resource:
                url = "https://" + self.ipaddr + ':' + str(self.pOptions.port) + resource['url']
                if ':' in self.ipaddr:
                    url = "https://[" + self.ipaddr + ']:' + str(self.pOptions.port) + resource['url']
                try:
                    
                    self.session.headers['datatype'] = 'json'
                    memResponse = self.session.get(url, timeout=(
                    self.pOptions.connection_timeout, self.pOptions.read_timeout))
                    if (memResponse.ok):
                        # retval['Status'] = 'Success'
                        compjData = json.loads(memResponse.content)

                        if resource.get('attribute', None):
                            if compjData.get(resource['attribute'], None):
                                xcomp = xcomp + compjData[resource['attribute']]
                        else:
                            xcomp = xcomp + [compjData]
                        if 'filter' in resource:
                            listparam = resource.get('filter_param', None)
                            xcomp = resource['filter'](xcomp, self.ipaddr, listparam)
                    else:
                        # retval['Status'] = 'Failure'
                        logger.debug("GET Request Failed - URL : {0}  Status Code : {1}  Reason : {2}".format(
                            memResponse.url, memResponse.status_code, memResponse.reason))
                    memResponse.close()
                except requests.exceptions.ConnectionError as err:
                    logger.debug(err)
                except requests.exceptions.Timeout as err:
                    logger.debug(err)
                if xcomp:
                    retval['Status'] = 'Success'
            else:
                cdict = self.data_cache.get(self.ipaddr, None)
                if cdict:
                    # print(cdict)
                    clist = cdict[resource['device']]
                    xcomp = []
                    for xc in clist:
                        if 'condition' in resource:
                            (attr, value) = resource['condition']
                            if xc[attr] != value:
                                continue
                        key = xc[resource['key']]
                        apiuri = resource['gen_func'](key, resource['comp'])
                        url = "https://" + self.ipaddr + ':' + str(self.pOptions.port) + apiuri
                        if ':' in self.ipaddr:
                            url = "https://[" + self.ipaddr + ']:' + str(self.pOptions.port) + apiuri
                        try:
                            memResponse = self.session.get(url, timeout=(
                            self.pOptions.connection_timeout, self.pOptions.read_timeout))
                            if (memResponse.ok):
                                # retval['Status'] = 'Success'
                                compjData = json.loads(memResponse.content)
                                if resource.get('attribute', None):
                                    xcomp = xcomp + compjData[resource['attribute']]
                                else:
                                    xcomp = xcomp + [compjData]
                            else:
                                # retval['Status'] = 'Failure'
                                logger.debug("GET Request Failed - URL : {0}  Status Code : {1}  Reason : {2}".format(
                                    memResponse.url, memResponse.status_code, memResponse.reason))
                            memResponse.close()
                        except requests.exceptions.ConnectionError as err:
                            logger.debug(err)
                        except requests.exceptions.Timeout as err:
                            logger.debug(err)
                if xcomp:
                    retval['Status'] = 'Success'
        elif isinstance(resource, list):
            redfurl = urlConcat + self.pOptions.urlbase + urlConcat + resource[ix]
            oDataDict = {}
            oDataDict[odataid] = redfurl
            oDataList = []
            oDataList.append(oDataDict)
            rlen = len(resource)
            xcomp = []
            while ix<rlen:
                xcomp = []
                tflag = False
                ix = ix + 1
                for mem in oDataList:
                    url = "https://" + self.ipaddr + ':' + str(self.pOptions.port) + mem[odataid]
                    if ':' in self.ipaddr:
                        url = "https://[" + self.ipaddr + ']:' + str(self.pOptions.port) + mem[odataid]
                    cachData = self.fetch_cache(url)
                    if cachData:
                        compjData = cachData
                        xcomp.append(compjData)
                        retval['Status'] = 'Success'
                    else:
                        try:
                            memResponse = self.session.get(url, timeout=(self.pOptions.connection_timeout, self.pOptions.read_timeout))
                            if (memResponse.ok):
                                retval['Status'] = 'Success'
                                compjData = json.loads(memResponse.content)
                                self.add_cache(url,compjData)
                                xcomp.append(compjData)
                            else:
                                retval['Status'] = 'Failure'
                                logger.debug("GET Request Failed - URL : {0}  Status Code : {1}  Reason : {2}".format(memResponse.url, memResponse.status_code, memResponse.reason))
                            memResponse.close()
                        except requests.exceptions.ConnectionError as err:
                            logger.debug(err)
                        except requests.exceptions.Timeout as err:
                            logger.debug(err)
                intrmOdataList = []
                for xc in xcomp:##Members flow
                    if ix < rlen:
                        if resource[ix] in xc:
                            res = xc[resource[ix]]
                            tflag = True
                            while(tflag == True):
                                if isinstance(res, dict):
                                    if resource[ix+1] in res:
                                        res = res[resource[ix+1]]
                                        tflag = True
                                        ix = ix + 1
                                        if isinstance(res, list):
                                            intrmOdataList = intrmOdataList + res
                                            tflag = False
                                    else:
                                        if odataid in res:
                                            intrmOdataList.append(res)
                                        tflag = False
                                elif isinstance(res, list):
                                    intrmOdataList = intrmOdataList + res
                                    tflag = False
                oDataList = intrmOdataList
        retval['Data'][clsName] = xcomp
        cdict = self.data_cache.setdefault(self.ipaddr, {})
        cdict[clsName] = xcomp
        return retval

