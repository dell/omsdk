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
import os
import sys
import logging

sys.path.append(os.getcwd())
from omsdk.sdkproto import PCONSOLE
from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcenum import EnumWrapper
from omsdk.sdkcreds import UserCredentials, ProtocolCredentialsFactory, CredentialsEnum

import sys
import traceback

logger = logging.getLogger(__name__)

try:
    from scaleiopy.scaleio import ScaleIO

    OMScaleIOPresent = True
except ImportError:
    OMScaleIOPresent = False

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

emcScaleIOCompEnum = EnumWrapper('emcScaleIOCompEnum', {
    "System": "System",
    "SDC": "SDC",
    "SDS": "SDS",
    "Volume": "Volume",
    "ProtectionDomain": "ProtectionDomain",
    "StoragePool": "StoragePool"
}).enum_type


class emcScaleIO(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(emcScaleIO, self).__init__(iDeviceRegistry("emcScaleIO", srcdir, emcScaleIOCompEnum))
        else:
            super().__init__(iDeviceRegistry("emcScaleIO", srcdir, emcScaleIOCompEnum))
        self.protofactory.add(PCONSOLE(obj=self))

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return emcScaleIOEntity(self.ref, protofactory, ipaddr, creds)


class emcScaleIOProtoOptions:
    def __init__(self, verify_ssl=False, debugLevel=None):
        self.verify_ssl = verify_ssl
        self.debugLevel = debugLevel


class emcScaleIOEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(emcScaleIOEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)

    def my_connect(self, pOptions):
        status = False
        try:
            if pOptions is None or not isinstance(pOptions, emcScaleIOProtoOptions):
                pOptions = emcScaleIOProtoOptions()
            creds = None
            if isinstance(self.creds, UserCredentials):
                creds = self.creds
            if isinstance(self.creds, ProtocolCredentialsFactory):
                creds = self.creds.get(CredentialsEnum.User)
            if OMScaleIOPresent and creds:
                self.sio = ScaleIO("https://" + self.ipaddr + "/api", creds.username,
                                   creds.password, pOptions.verify_ssl, pOptions.debugLevel)
                status = True
        except:
            traceback.print_exc()
            status = False
        logger.debug(self.ref.name + '::connect(' + self.ipaddr + ', ' + str(creds) + ")=" + str(status))
        return status

    def my_get_entityjson(self):
        if not OMScaleIOPresent:
            return False

        entityjson["System"] = self.sio.system
        entityjson["SDC"] = self.sio.sdc
        entityjson["SDS"] = self.sio.sds
        entityjson["Volume"] = self.sio.volumes
        entityjson["ProtectionDomain"] = self.sio.protection_domains
        entityjson["StoragePool"] = self.sio.storage_pools
        return True
