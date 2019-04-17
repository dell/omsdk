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
import os
import re
import time
import xml.etree.ElementTree as ET
from enum import Enum
from datetime import datetime
from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkfile import FileOnShare, Share
from omsdk.sdkcreds import UserCredentials
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdkconfigapi import iBaseConfigApi
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    from pysnmp.proto import rfc1902
    from pysnmp import debug

    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False

ConfigFileTypeEnum = EnumWrapper("CFT", {"FTOS": 1,
                                         "RunningConfig": 2,
                                         "StartupConfig": 3,
                                         }).enum_type

ConfigFileLocationEnum = EnumWrapper("CFLE", {
    "Flash": 1,
    "Slot0": 2,
    "Tftp": 3,
    "FTP": 4,
    "SCP": 5,
    "USBFlash": 6
}).enum_type

if PySnmpPresent:
    F10SNMPCmds = {
        #######
        ## Config Export
        #######
        "config_export": {
            "ResourceURI": None,
            "Action": None,
            "SelectorSet": {
                "indexField": '1.3.6.1.4.1.6027.3.5.1.1.1.1.15',  # rfc1902.Integer(6)
                "defaultIdx": '5',
                "startIdx": '1',
                "endIdx": '10',
                "cleanupAfterCreate": True,
            },
            "Args": {
                "share": FileOnShare,
                "creds": UserCredentials,
                "srcType": ConfigFileTypeEnum,
                "destType": ConfigFileTypeEnum,
            },
            "Return": {
                "File": "file"
            },
            "Parameters": [
                # copySrcFileType :: ConfigFileType
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.2', "srcType", None, ConfigFileTypeEnum, rfc1902.Integer),
                # copyDestFileType :: ConfigFileType
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.5', "destType", None, ConfigFileTypeEnum, rfc1902.Integer),
                # TODO copyDestFileLocation :: ConfigFileLocation
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.6', "share", "remote_share_type", Share.ShareType, rfc1902.Integer),
                # copyDestFileName :: str get_filepath_full()
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.7', "share", "remote_full_path", str, rfc1902.OctetString),
                # copyServerAddress :: ipaddr -- deprecated
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.8', "share", "remote_ipaddr", str, rfc1902.IpAddress),
                # copyUserName :: username
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.9', "creds", "username", str, rfc1902.OctetString),
                # copyUserPAssword :: password
                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.10', "creds", "password", str, rfc1902.OctetString),
                # TODO cpyServerInetAddressType :: 
                #                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.16', "share", "remote_iptype", Share.IPAddressTypeEnum, rfc1902.Integer),
                # cpyServerInetAddress :: 
                #                ('1.3.6.1.4.1.6027.3.5.1.1.1.1.17', "share", "remote_ipaddr", str, rfc1902.IpAddress),
            ]
        },
    }


class F10Config(iBaseConfigApi):
    def __init__(self, entity):
        if PY2:
            super(F10Config, self).__init__(entity)
        else:
            super().__init__(entity)

    def config_export_async(self, myshare,
                            srcType=ConfigFileTypeEnum.StartupConfig,
                            destType=ConfigFileTypeEnum.FTOS):
        share = myshare.format(ip=self.entity.ipaddr)
        rjson = self.entity.config_export(share=share, creds=myshare.creds,
                                          srcType=srcType, destType=destType)
        rjson['file'] = str(share)
        return rjson
