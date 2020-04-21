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
from omsdk.http.sdkwsmanpdu import WsManRequest, WsManResponse
from omsdk.http.sdkhttpep import HttpEndPoint, HttpEndPointOptions, AuthenticationType
from omsdk.sdkprotopref import ProtoPreference, ProtocolEnum
from omsdk.sdkprint import PrettyPrint
import logging

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


class WsManOptions(HttpEndPointOptions):
    """
        Options to establish WSMAN communication
    """

    def __init__(
            self, authentication=AuthenticationType.Basic, port=443, connection_timeout=20,
            read_timeout=30, max_retries=1, verify_ssl=False
    ):
        """
        :param authentication: HTTP Authentication type 'Basic', 'Digest'
        :param port: https Port number for WSMAN communication
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
            super(WsManOptions, self).__init__(
                ProtocolEnum.WSMAN, authentication, port, connection_timeout,
                read_timeout, max_retries, verify_ssl
            )
        else:
            super().__init__(
                ProtocolEnum.WSMAN, authentication, port, connection_timeout,
                read_timeout, max_retries, verify_ssl
            )
        self.enid = ProtocolEnum.WSMAN


class WsManProtocolBase(ProtocolBase):

    def __init__(self, ipaddr, creds, pOptions):
        if PY2:
            super(WsManProtocolBase, self).__init__()
        else:
            super().__init__()
        headers = None
        self._logger = logging.getLogger(__name__)

    def reset(self, ignore=True):
        self._proto_reset()

    def identify(self):
        """ Identifies the target product """
        wsm = WsManRequest()
        wsm.identify()
        return self._communicate(wsm)

    def enumerate(self, clsName, resource, select={}, resetTransport=False, filter=None):
        wsm = WsManRequest()
        wsm.enumerate(to=self._proto_endpoint(), ruri=resource,
                      selectors=select, filter=filter)
        return self._communicate(wsm)

    # Operation Invoke
    def opget(self, ruri, name, args):
        act = "http://schemas.xmlsoap.org/ws/2004/09/transfer/Get"
        wsm = WsManRequest()
        wsm.set_header(self._proto_endpoint(), ruri, act)
        wsm.add_selectors(args)
        return self._communicate(wsm, name)

    def operation(self, wsmancmds, cmdname, *args):
        ##########################Below are redfish codes, need to be removed once prtocol issue is addressed#####################
        cmmd = str(cmdname)
        if cmmd.endswith("_redfish"):
            return self.redfish_operation(wsmancmds, cmdname, *args)
        ##########################Above are redfish codes, need to be removed once prtocol issue is addressed#####################
        ruri = wsmancmds[cmdname]["ResourceURI"]
        act = wsmancmds[cmdname]["Action"]
        sset = {}
        tset = wsmancmds[cmdname]["SelectorSet"]
        for i in tset["w:Selector"]:
            sset[i['@Name']] = i['#text']
        toargs = self._build_ops(wsmancmds, cmdname, *args)

        wsm = WsManRequest()
        wsm.set_header(self._proto_endpoint(), ruri, (ruri + "/" + act))
        wsm.add_selectors(sset)
        wsm.add_body(ruri, act, toargs['retval'])
        return self._communicate(wsm)

    ##########################Below are redfish codes, need to be moved once prtocol issue is addressed#####################
    def _build_attribute_config_payload(self, toargs_dict):
        if not toargs_dict:
            return None
        payload = {}
        if toargs_dict.__contains__("parentattr"):
            payload[toargs_dict["parentattr"]] = toargs_dict["payload_param"]
        else:
            if not toargs_dict["payload_param"]:
                return None
            payload = toargs_dict["payload_param"]
        return payload

    def _build_redfish_payload(self, toargs_dict):
        """Prepare the payload for http methods body

        :param toargs_dict: name and value of arguments as dictionary.
        :param path: dict.         .
        :returns: returns a json/dict body for http method

        """
        # status = toargs_dict['Status']
        retval = toargs_dict['retval']
        if not retval:
            return None
        payload = {}
        for key in retval:
            val = retval[key]
            if "/" in key:
                tokens = key.split("/")
                ''' right now implementation is only for params containing single "/", it will be extented for generic numbers of "/"'''
                if not tokens[0] in payload:
                    param_key = tokens[0]
                    param_val = {}
                    param_val[tokens[1]] = val
                    payload[param_key] = param_val
                else:
                    param_key = payload[tokens[0]]
                    param_key[tokens[1]] = val

            else:
                payload[key] = val
        return payload

    def _pack_http_method_args(self, resource_path, http_headers, http_body=None, http_args=None):
        """Pack the arguments required for the redfish client methods (post/get/put/patch ...) as a key value pair in a dictionary

        :param resource_path: resource path on the device.
        :param resource_path: str.
        :param http_headers: header for http....
        :param http_headers: str.
        :param http_body: body for http request
        :param http_body: dict/json.
        :returns: returns a key-value pair as a dictionary for arguemnts

        """
        method_args = {}
        method_args['path'] = resource_path
        method_args['args'] = http_args
        method_args['headers'] = http_headers
        if not http_body is None:
            method_args['body'] = http_body
        return method_args

    def _pack_rest_method_args(self, auth, verify=False, data={}, headers=None):
        """Pack the arguments required for the rest methods (post/get/put/patch ...) as a key value pair in a dictionary

        :param auth: authentication object.
        :param auth: HttpAuth.
        :param verify: verify certificate
        :param verify: boolean.
        :param data: payload
        :param data: dict/json.
        :param headers: http headers
        :param headers: str.
        :returns: returns a key-value pair as a dictionary for arguemnts

        """
        method_args = {}
        method_args['auth'] = auth
        method_args['verify'] = verify
        if headers:
            method_args['headers'] = headers
        if data is not None:
            method_args['data'] = json.dumps(data)
        else:
            method_args['data'] = '{}'
        return method_args

    def _get_base_url(self, ipaddr, resouce_path, port=443):
        baseurl = "https://" + ipaddr + ':' + str(port) + resouce_path
        return baseurl

    def _get_redfish_jobid(self, headers):
        """Search jobid in the redfish_op

        :param headers: response header.
        :param headers: dict.         .
        :returns: returns jobid

        """
        joblocation = headers['Location']
        tokens = joblocation.split("/")
        if tokens and tokens.__len__() > 0:
            return tokens[-1]
        return None

    def _remove_dummyparams(self, redfish_cmdlist, redfish_cmdname, argdict):
        """Remove dummy params which are not required by the actual redfish command,
            these dummy params are required for ceratin URI's and other supporting purposes

        :param redfish_cmdlist: redfish command list.
        :param redfish_cmdlist: list.
        :param redfish_cmdname: name of the redfish operation to be performed
        :param redfish_cmdname: str.
        :param argdict: arguments for the redfish operation to be performed along with dummy args
        :param args: dict.
        :returns: returns a tuple containing required arguments for redfish call and uri

        """
        dummyargs = redfish_cmdlist[redfish_cmdname]['DummyParams']
        paramtuples = redfish_cmdlist[redfish_cmdname]['Parameters']
        newargdict = argdict['retval']
        uriarg = ''
        for i in range(0, dummyargs):
            key = paramtuples[i][0]
            val = newargdict[key]
            newargdict.pop(key)
            if val.startswith("/"):
                uriarg = uriarg + val
            else:
                uriarg = uriarg + '/' + val
        argdict['retval'] = newargdict
        return (argdict, uriarg)

    def redfish_operation(self, redfish_cmdlist, redfish_cmdname, *args):
        """Perform redfish operation as mentioned in redfish_cmdname

        :param redfish_cmdlist: redfish command list.
        :param redfish_cmdlist: list.
        :param redfish_cmdname: name of the redfish operation to be performed
        :param redfish_cmdname: str.
        :param args: arguments for the redfish operation to be performed
        :param args: list.
        :returns: returns redfish command operation response

        """
        resource_uri = redfish_cmdlist[redfish_cmdname]["ResourceURI"]
        action = redfish_cmdlist[redfish_cmdname]["Action"]
        http_method = redfish_cmdlist[redfish_cmdname]["HttpMethod"]

        if "SuccessCode" in redfish_cmdlist[redfish_cmdname]:
            success_code = redfish_cmdlist[redfish_cmdname]["SuccessCode"]
        else:
            success_code = [200]

        if "ReturnsJobid" in redfish_cmdlist[redfish_cmdname]:
            returns_job_id = redfish_cmdlist[redfish_cmdname]["ReturnsJobid"]
        else:
            returns_job_id = False

        rpath = resource_uri
        if action:
            rpath = rpath + '.' + action

        toargs = self._build_ops(redfish_cmdlist, redfish_cmdname, *args)

        if redfish_cmdlist[redfish_cmdname].__contains__("DummyParams") and redfish_cmdlist[redfish_cmdname][
            'DummyParams'] > 0:
            (toargs, uriarg) = self._remove_dummyparams(redfish_cmdlist, redfish_cmdname, toargs)
            rpath = rpath + uriarg
        if redfish_cmdname.endswith("attributes_redfish") and toargs['retval']:
            toargdict = toargs['retval']
            redfish_payload = self._build_attribute_config_payload(toargdict)
            rpath = rpath + toargs['retval']['r_path']
        else:
            redfish_payload = self._build_redfish_payload(toargs)

        url = self._get_base_url(ipaddr=self.proto.ipaddr, resouce_path=rpath, port=self.proto.pOptions.port)
        auth = HTTPBasicAuth(self.proto.creds.username, self.proto.creds.password)
        cert_verify = False
        headers = {'content-type': 'application/json'}
        kwargs = self._pack_rest_method_args(auth=auth, verify=cert_verify, data=redfish_payload, headers=headers)
        retval = {}
        try:
            response = requests.request(method=http_method, url=url, **kwargs)
        except Exception as exp:
            logger.error(self.proto.ipaddr+" : Exception while executing redfish request: {}".format(exp))
            retval["Status"] = "Failed"
            retval["Data"] = {"Status": "Failed", "Message": "Failed to execute redfish request: {}".format(exp)}
            return retval
        retval = self._parse_redfish_output(response, success_code, returns_job_id)
        return retval

    def _parse_redfish_output(self, response, success_code, returns_jobid=False):
        """Parse redfish response

        :param redfish_response: response from redfish command.
        :param success_code: status code expected.         .
        :returns: returns a json/dict

        """
        retval = {}
        Data = {}
        if response == None:
            logger.error(self.proto.ipaddr+" : redfish response is None")
            retval["Status"] = "Failed"
            retval["Data"] = {"Status": "Failed",
                              "Message": "redfish response is None"}
            return retval
        headers = response.headers
        retval["StatusCode"] = response.status_code
        if response.status_code not in success_code:
            print("response.status_code:" + str(response.status_code) + ", success_code:" + str(success_code))
            logger.debug(self.proto.ipaddr+" : returned status code doesn't match with the expected success code")
            logger.debug(self.proto.ipaddr+" : Expected:" + str(success_code) + ", returned status code:" + str(response.status_code))
            retval["Status"] = "Failed"
            retval["Data"] = {"Status": "Failed",
                              "Message": "returned status code doesn't match with the expected success code"}
            retval["Data"]['StatusCode'] = response.status_code
            if 'Content-Length' in headers and int(headers['Content-Length']) > 0:
                if 'application/json' in headers['Content-Type']:
                    error = response.json()
                else:
                    error = response.text
                retval['error'] = error
            return retval
        retval["Status"] = "Success"

        if 'Content-Length' in headers and int(headers['Content-Length']) > 0:
            if 'application/json' in headers['Content-Type']:
                body = response.json()
            else:
                body = response.text
            Data['body'] = body
        # Data['headers']=headers
        Data['StatusCode'] = response.status_code
        if 'Location' in headers:
            Data['next_ruri'] = headers['Location']
        if returns_jobid:
            jobid = self._get_redfish_jobid(headers)
            if jobid:
                Data['jobid'] = jobid
                job = {'JobId': jobid, 'ResourceURI': headers['Location']}
                retval['Job'] = job
                retval['Return'] = 'JobCreated'
        retval['Data'] = Data
        return retval

    ##########################Above are redfish codes, need to be moved once prtocol issue is addressed#####################

    def _proto_connect(self):
        pass

    def _proto_ship_payload(self, payload):
        pass

    def _proto_endpoint(self):
        pass

    def _proto_reset(self):
        pass

    def _communicate(self, wsm, name=None):
        try:
            self._proto_connect()
            #self._logger.debug("Sending: " + wsm.get_text())
            result = self._proto_ship_payload(wsm.get_text())
            self._logger.debug("Received: " + str(result))
            en = WsManResponse().execute_str(result)
            out = self._parse_output(en, name)

            if out['Status'] != 'Success':
                self._logger.debug(out)

            return out
        except Exception as ex:
            self._logger.debug(str(ex))
            # fake as if the error came from the WsMan subsystem
            sx = WsManRequest()
            sx.add_error(ex)
            self._logger.debug(sx.get_text())
            en = WsManResponse().execute_str(sx.get_text())
            out = self._parse_output(en)
            self._logger.debug(out)
            return out

    def printx(self, json_object):
        if json_object is None:
            logger.debug("<empty json>")
            return False
        logger.debug(json.dumps(json_object, sort_keys=True, indent=4, \
                                separators=(',', ': ')))

    # retVal['Status'] = Success, Failed, Invalid JSON,
    # retval['Data'][component] = {}
    # retval['Fault.Data']['Reason'] = Reason
    # retval['Fault.Data']['Text'] = Message
    # retval['Message'] = Message
    # retval['Return'] = enum(ReturnValue).value
    # retval['Job']['JobId'] = jobid
    def _parse_output(self, en, name=None):
        retval = {}
        if "Header" in en:
            rgsp = "http://schemas.xmlsoap.org/ws/2004/09/transfer/GetResponse"
            if "Action" in en["Header"] and en["Header"]["Action"] == rgsp:
                retval['Status'] = 'Success'
                retval['Data'] = en['Body']
            rfault = "http://schemas.xmlsoap.org/ws/2004/08/addressing/fault"
            if "Action" in en["Header"] and en["Header"]["Action"] == rfault:
                retval['Status'] = 'Failed'
        if not "Body" in en:
            retval['Status'] = 'Invalid JSON. Does not have Body!'
        elif "ClientFault" in en["Body"]:
            retval['Status'] = 'Found Client (SDK) Side Fault'
            retval['Fault.Data'] = en["Body"]["ClientFault"]
            if "Reason" in en["Body"]["ClientFault"] and \
                    "Text" in en["Body"]["ClientFault"]["Reason"]:
                retval['Message'] = WsManResponse().get_message(en["Body"]["ClientFault"]["Reason"])
        elif "Fault" in en["Body"]:
            retval['Status'] = 'Found Fault'
            retval['Fault.Data'] = en["Body"]["Fault"]
            if "Reason" in en["Body"]["Fault"]:
                retval['Message'] = WsManResponse().get_message(en["Body"]["Fault"]["Reason"])
            if retval['Message'] == "" and "Detail" in en["Body"]["Fault"]:
                retval['Message'] = WsManResponse().get_message(en["Body"]["Fault"]["Detail"])
        elif "EnumerateResponse" in en["Body"]:
            retval['Status'] = 'Success'
            retval['Data'] = en["Body"]["EnumerateResponse"]["Items"]
        elif "IdentifyResponse" in en["Body"]:
            retval['Status'] = 'Success'
            retval['Data'] = en["Body"]
        else:
            for entry in en["Body"]:
                if not entry.endswith("_OUTPUT"):
                    continue
                retval['Data'] = en["Body"]
                retval['Status'] = 'Not understood the message. Sorry!'
                if "Message" in en["Body"][entry]:
                    retval['Status'] = en["Body"][entry]["Message"]
                    retval['Message'] = en["Body"][entry]["Message"]
                if "MessageID" in en["Body"][entry]:
                    retval['MessageID'] = en["Body"][entry]["MessageID"]
                if "ReturnValue" in en["Body"][entry]:
                    ret = int(en["Body"][entry]["ReturnValue"])
                    retval['Return'] = TypeHelper.get_name(ret, ReturnValueMap)
                    retval['Status'] = retval['Return']
                    if ret == TypeHelper.resolve(ReturnValue.JobCreated):
                        retval['Job'] = {"ResourceURI": "", "JobId": ""}
                        ss = en["Body"][entry]
                        if "Job" in ss:
                            ss = ss["Job"]
                        if 'RebootJobID' in ss:
                            ss = ss['RebootJobID']
                        if "EndpointReference" in ss:
                            ss = ss["EndpointReference"]
                        if "ReferenceParameters" in ss:
                            ss = ss["ReferenceParameters"]
                        if "ResourceURI" in ss:
                            retval['Job']['ResourceURI'] = ss["ResourceURI"]
                        if "SelectorSet" in ss:
                            ss = ss["SelectorSet"]
                        if "Selector" in ss:
                            ss = ss["Selector"]
                        if len(ss) >= 1:
                            retval['Job']['JobId'] = ss[0]
                            retval['Job']['JobIdRest'] = [ss[i] for i in range(1, len(ss))]
                        else:
                            retval['Job']['JobId'] = 'Unknown'
                            retval['Job']['JobIdRest'] = ss
                        retval['Status'] = 'Success'
        if not 'Status' in retval:
            retval['Status'] = 'Dont understand the message'
            retval['Data'] = en["Body"]
        return retval
