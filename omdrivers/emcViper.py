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

import sys
import traceback

logger = logging.getLogger(__name__)

try:
    from viperpy import Viperpy, ViperpyException

    OMViperPresent = True
except ImportError:
    OMViperPresent = False

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

emcViperCompEnum = EnumWrapper('emcViperCompEnum', {
    "System": "System",
    "Disk": "Disk",
    "Capacity": "Capacity",
    "Node": "Node",
    "Service": "Service",
    "HealthMonitor": "HealthMonitor",
    "Namespace": "Namespace",
    "Users": "Users",
    "Configuration": "Configuration",
    "Tenants": "Tenants",
    "Projects": "Projects",
    "Volumes": "Volumes",
    "VirtualPools": "VirtualPools",
    "vCenters": "vCenters",
    "License": "License",
}).enum_type


class emcViper(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(emcViper, self).__init__(iDeviceRegistry("emcViper", srcdir, emcViperCompEnum))
        else:
            super().__init__(iDeviceRegistry("emcViper", srcdir, emcViperCompEnum))
        self.protofactory.add(PCONSOLE(obj=self))

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return emcViperEntity(self.ref, protofactory, ipaddr, creds)


class emcViperProtoOptions:
    def __init__(self, request_timeout=15.0, port=4443, token_endpoint=None, verify_ssl=False, token=None,
                 token_filename='ViperPy.tkn', token_location='/tmp'):
        self.request_timeout = request_timeout
        self.token_endpoint = token_endpoint
        self.verify_ssl = verify_ssl
        self.port = port
        self.token = token
        self.token_filename = token_filename
        self.token_location = token_location


class emcViperEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(emcViperEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)

    def my_connect(self, pOptions):
        status = False
        try:
            if not OMViperPresent:
                return status
            if pOptions is None or not isinstance(pOptions, emcViperProtoOptions):
                pOptions = emcViperProtoOptions()
            viper_endpoint = 'https://' + self.ipaddr + ':' + str(pOptions.port)
            if pOptions.token_endpoint is None:
                pOptions.token_endpoint = viper_endpoint + '/login'
            self.sio = Viperpy(vipr_endpoint=viper_endpoint,
                               token_endpoint=pOptions.token_endpoint,
                               username=self.creds.username,
                               password=self.creds.password,
                               request_timeout=pOptions.request_timeout,
                               token=pOptions.token,
                               token_filename=pOptions.token_filename,
                               token_location=pOptions.token_location)
            status = True
        except:
            traceback.print_exc()
            status = False
        logger.debug(self.ref.name + '::connect(' + self.ipaddr + ', ' + str(self.creds) + ")=" + str(status))
        return status

    def my_get_entityjson(self):
        if not OMViperPresent:
            return False
        if OMViperPresent:
            entityjson["Disk"] = self.sio.disk.get_disks()["disk"]
            entityjson["Capacity"] = self.sio.fabric_capacity.get_capacity()["total_capacity"]
            entityjson["Node"] = self.sio.node.get_nodes()["node"]
            entityjson["Service"] = self.sio.services.get_services()["service"]
            entityjson["HealthMonitor"] = self.sio.health_monitor.get_health()["node_health_list"]

            entityjson["Namespace"] = self.sio.namespace.get_namespaces()["namespace"]
            entityjson["Users"] = self.sio.user_management.get_objectusers()["blobuser"]
            entityjson["Configuration"] = self.sio.configuration.get_config_properties()["properties"]

            entityjson["Tenants"] = []
            tenantids = self.sio.tenants.get_tenants_bulk()
            for i in tenantids:
                entityjson["Tenants"].append(self.sio.tenants.get_tenant(i))
                entityjson["Tenants"][-1]["Subtenants"] = self.sio.tenants.get_subtenants(i)

            entityjson["Projects"] = []
            projectids = self.sio.projects.get_projects_bulk()
            for i in projectids:
                entityjson["Projects"].append(self.sio.projects.get_project(i))

            entityjson["Volumes"] = []
            volumeids = self.sio.block_volumes.get_volumes_bulk()
            for i in volumeids:
                entityjson["Volumes"].append(self.sio.block_volumes.get_volume(i))

            entityjson["VirtualPools"] = []
            vpoolids = self.sio.block_vpools.get_vpools_bulk()
            for i in vpoolids:
                entityjson["VirtualPools"].append(self.sio.block_vpools.get_vpool(i))

            entityjson["vCenters"] = []
            vcenterids = self.sio.vcenters.get_vcenters_bulk()
            for i in vcenterids:
                entityjson["vCenters"].append(self.sio.block_vcenters.get_vcenter(i))

            entityjson["License"] = self.sio.license.get_license()

            return True
