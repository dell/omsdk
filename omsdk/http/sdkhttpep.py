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
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from omsdk.sdkcenum import EnumWrapper, TypeHelper
import logging


AuthenticationTypeMap = {
    'Basic' : 1,
    'Digest' : 2,
    'OAuth1' : 3,
    'OAuth2' : 4
}
AuthenticationType = EnumWrapper('AT', AuthenticationTypeMap).enum_type


class HttpEndPointOptions(object):
    def __init__(self, enid, authentication, port, connection_timeout, read_timeout, max_retries, verify_ssl):
        self.enid = enid
        self.connection_timeout = connection_timeout # establish a connection
        self.read_timeout = read_timeout # how long to wait for response from client
        self.max_retries = max_retries 
        self.verify_ssl = verify_ssl 
        self.authentication = authentication 
        self.port = port 
		#self.skip_ca_check = True
        #self.skip_cn_check = True

class HttpEndPointProtocolException(Exception):
    pass

class HttpEndPointTransportException(Exception):
    pass

class HttpEndPointProtocolAuthException(Exception):
    pass

class HttpEndPoint(object):
    def __init__(self, ipaddr, creds, pOptions, headers = {}):
        self.ipaddr = ipaddr
        self.creds = creds
        self.pOptions = pOptions
        self.session = None
        self.headers = headers
        self._logger = logging.getLogger(__name__)
        url_form = "https://{0}:{1}/wsman"
        if ':' in self.ipaddr:
            url_form = "https://[{0}]:{1}/wsman"
        self.endpoint = url_form.format(self.ipaddr, self.pOptions.port)

    def reset(self):
        if not self.session is None:
            self.session.close()
            self.session = None

    def reconnect(self):
        self.reset()
        return self.connect()

    def connect(self):
        if self.session:
            return True
        self._logger.debug("Attempting a connection to device")
        requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
        requests.packages.urllib3.disable_warnings(SNIMissingWarning)
        if not self.pOptions.verify_ssl:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.adapter = requests.adapters.HTTPAdapter(
                pool_connections = 1,
                max_retries = self.pOptions.max_retries)
        self.session = requests.Session()
        self.session.auth = None
        if self.pOptions.authentication == AuthenticationType.Basic:
            self.session.auth = requests.auth.HTTPBasicAuth(self.creds.username,
                                                    self.creds.password)
        self.session.headers.update(self.headers)
        self.session.mount("https", self.adapter)
        self._logger.debug("Connection to device: complete")
        return True

    def ship_payload(self, payload):

        self._logger.debug("Begin doing HTTP POST with SOAP message")

        if self.session:
        # Prepare the http request
            #self._logger.debug("Begin preparing POST request with payload:\n%s", payload)
            try:
                request = requests.Request('POST', self.endpoint, data=str(payload))
                prepared_request = self.session.prepare_request(request)
            except requests.exceptions.RequestException:
                error_message = "Error preparing HTTP request"
                #self._logger.exception(error_message)
                raise HttpEndPointProtocolException(error_message)
            else:
                self._logger.debug("Finished preparing POST request")

            # Submit the http request
            self._logger.debug("Begin submitting POST request")
            try:
                response = self.session.send(prepared_request, verify=self.pOptions.verify_ssl,
                    timeout=(self.pOptions.connection_timeout, self.pOptions.read_timeout))
            except requests.exceptions.ConnectionError:
                error_message = "HTTP connection error"
                self._logger.debug(error_message)
                raise HttpEndPointProtocolException(error_message)
            except requests.exceptions.Timeout:
                error_message = "HTTP Timeout error"
                self._logger.debug(error_message)
                raise HttpEndPointProtocolException(error_message)
            except requests.exceptions.RequestException:
                error_message = "Error preparing HTTP request"
                self._logger.exception(error_message)
                raise HttpEndPointTransportException(error_message)
            else:
                self._logger.debug("Finished submitting POST request")

            # now check response for errors
            self._logger.debug("Begin checking POST response")
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                error_message = (
                    "DRAC WSMAN endpoint returned HTTP code '{}' Reason '{}'"
                    ).format(response.status_code, response.reason)
                # response.content
                #self._logger.exception(error_message)
                if response.status_code == 401:
                    raise HttpEndPointProtocolAuthException(error_message)
                else:
                    raise HttpEndPointProtocolException(error_message)
            else:
                self._logger.debug("Received non-error HTTP response")
            finally:
                self._logger.debug("Finished checking POST response")

            # make sure its a string
            reply = response.content # Avoid unicode difficulties
            self._logger.debug("Received SOAP reply:\n%s", reply)

        # return it
        return reply
