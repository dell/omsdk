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
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdklicenseapi import iBaseLicenseApi
from omdrivers.lifecycle.iDRAC.iDRACConfig import LicenseApiOptionsEnum
import base64
import sys
import logging

logger = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *

    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False
from omdrivers.enums.iDRAC.iDRACEnums import *


class iDRACLicense(iBaseLicenseApi):
    def __init__(self, entity):
        if PY2:
            super(iDRACLicense, self).__init__(entity)
        else:
            super().__init__(entity)
        self._job_mgr = entity.job_mgr
        self._config_mgr = entity.config_mgr
        self._license_fqdds = []

    def _get_license_json(self):
        if not hasattr(self, 'license') or "License" not in self.license:
            self.license = {}
            self.entity._get_entries(self.license, iDRACLicenseEnum)
            if "LicensableDevice" in self.license:
                entries = self.license["LicensableDevice"]
                if isinstance(entries, dict):
                    entries = [entries]
                for entry in entries:
                    self._license_fqdds.append(entry["FQDD"])
        return self.license

    def _get_license_text(self, entitlementId):
        retVal = self.entity._export_license(id=entitlementId)
        ltext = self.entity._get_field_from_action(retVal,
                                                   "Data", "ExportLicense_OUTPUT", "LicenseFile")
        if ltext:
            retVal['License'] = base64.b64decode(ltext).decode("utf-8")
        return retVal

    def _save_license_text(self, entitlementId, folder):
        retVal = self._get_license_text(entitlementId)
        with open(os.path.join(folder, entitlementId), "wb") as output:
            output.write(retVal['License'].encode('UTF-8'))
            output.flush()
        return os.path.join(folder, entitlementId)

    def export_license(self, folder):
        expLic = []
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif not os.path.isdir(folder):
            # replace with exception
            return []

        self._get_license_json()
        if not "License" in self.license:
            # replace with exception
            return []

        llist = self.license["License"]
        if isinstance(self.license["License"], dict):
            llist = [llist]
        for i in llist:
            entitlementId = i["EntitlementID"]
            expLic.append(self._save_license_text(entitlementId, folder))
        return expLic

    def export_license_share(self, license_share_path):
        self._get_license_json()
        if not "License" in self.license:
            return {"l": False}

        llist = self.license["License"]
        if isinstance(self.license["License"], dict):
            llist = [llist]
        retval = {'Status': 'Success', 'Exported': 0, 'Failed to Export': 0}
        for i in llist:
            entitlementId = i["EntitlementID"]
            rjson = self.entity._export_license_share(share=license_share_path,
                                                      creds=license_share_path.creds, id=entitlementId)
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)
            if rjson['Status'] == 'Success':
                retval['Exported'] += 1
            else:
                retval['Failed to Export'] += 1
            if retval['Exported'] == 0 and retval['Failed to Export'] > 0:
                retval['Status'] = 'Failed'

        return retval

    def _import_license_fqdd(self, license_file, fqdd="iDRAC.Embedded.1", options=LicenseApiOptionsEnum.NoOptions):
        if not os.path.exists(license_file) or not os.path.isfile(license_file):
            logger.debug(license_file + " is not a file!")
            return False
        content = ''
        with open(license_file, 'rb') as f:
            content = f.read()
        content = bytearray(base64.b64encode(content))
        for i in range(0, len(content) + 65, 65):
            content[i:i] = '\n'.encode()

        return self.entity._import_license(fqdd=fqdd,
                                           options=options, file=content.decode())

    def _import_license_share_fqdd(self, license_share_path, fqdd="iDRAC.Embedded.1",
                                   options=LicenseApiOptionsEnum.NoOptions):
        self._get_license_json()
        if not "License" in self.license:
            return False
        llist = self.license["License"]
        if isinstance(self.license["License"], dict):
            llist = [llist]
        retval = {'Status': 'Success', 'Imported': 0, 'Failed to Import': 0}
        for i in llist:
            entitlementId = i["EntitlementID"]
            rjson = self.entity._import_license_share(share=license_share_path,
                                                      creds=license_share_path.creds, name="Import",
                                                      fqdd=fqdd, options=options)
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)
            logger.debug(rjson)
            if rjson['Status'] == 'Success':
                retval['Imported'] += 1
            else:
                retval['Failed to Import'] += 1
            if retval['Imported'] == 0 and retval['Failed to Import'] > 0:
                retval['Status'] = 'Failed'

        return retval

    def _replace_license_fqdd(self, license_file, entitlementId, fqdd="iDRAC.Embedded.1",
                              options=LicenseApiOptionsEnum.NoOptions):
        if not os.path.exists(license_file) or not os.path.isfile(license_file):
            logger.debug(license_file + " is not a file!")
            return False
        content = ''
        with open(license_file) as f:
            content = f.read()

        return self.entity._replace_license(id=entitlementId,
                                            fqdd=fqdd, options=options, file=content)

    def _delete_license_fqdd(self, entitlementId, fqdd="iDRAC.Embedded.1", options=LicenseApiOptionsEnum.NoOptions):
        return self.entity._delete_license(id=entitlementId,
                                           fqdd=fqdd, options=options)

    @property
    def LicensableDeviceFQDDs(self):
        self._get_license_json()
        return self._license_fqdds

    @property
    def LicensableDevices(self):
        self._get_license_json()
        return list(self._config_mgr._fqdd_to_comp(self._license_fqdds))

    @property
    def Licenses(self):
        self._get_license_json()
        return self.license["License"]

    def import_license(self, license_file, component="iDRAC", options=LicenseApiOptionsEnum.NoOptions):
        fqddlist = self._config_mgr._comp_to_fqdd(self.LicensableDeviceFQDDs, component, default=[component])
        return self._import_license_fqdd(license_file, fqdd=fqddlist[0], options=options)

    def import_license_share(self, license_share_path, component="iDRAC", options=LicenseApiOptionsEnum.NoOptions):
        fqddlist = self._config_mgr._comp_to_fqdd(self.LicensableDeviceFQDDs, component, default=[component])
        return self._import_license_share_fqdd(license_share_path, fqdd=fqddlist[0], options=options)

    def replace_license(self, license_file, entitlementId, component="iDRAC", options=LicenseApiOptionsEnum.NoOptions):
        fqddlist = self._config_mgr._comp_to_fqdd(self.LicensableDeviceFQDDs, component, default=[component])
        return self._replace_license_fqdd(license_file, entitlementId, fqdd=fqddlist[0], options=options)

    def delete_license(self, entitlementId, component="iDRAC", options=LicenseApiOptionsEnum.NoOptions):
        fqddlist = self._config_mgr._comp_to_fqdd(self.LicensableDeviceFQDDs, component, default=[component])
        return self._delete_license_fqdd(entitlementId, fqdd=fqddlist[0], options=options)
