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
import os
import re
import json
import time
import glob
import xml.etree.ElementTree as ET
from enum import Enum
from datetime import datetime
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdkupdate import Update
from omsdk.catalog.sdkupdatemgr import UpdateManager
from omsdk.catalog.updaterepo import RepoComparator, UpdateFilterCriteria
from omsdk.catalog.updaterepo import UpdatePresenceEnum, UpdateNeededEnum, UpdateTypeEnum
from omdrivers.enums.iDRAC.iDRACEnums import *
from omsdk.sdkcunicode import UnicodeWriter
from omsdk.sdkfile import FileOnShare

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *

    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False


class iDRACUpdate(Update):
    def __init__(self, entity):
        if PY2:
            super(iDRACUpdate, self).__init__(entity, iDRACFirmEnum)
        else:
            super().__init__(entity, iDRACFirmEnum)
        self.reset()
        self._job_mgr = entity.job_mgr

    def _sw_instance(self, comp):
        ilist = []
        clist = self._comp_to_fqdd(comp)
        for firmware in self.firmware_json["Firmware"]:
            if firmware['FQDD'] in clist and firmware['Status'] == "Installed":
                ilist.append(firmware['InstanceID'])
        return ilist

    def _update_from_uri(self, firm_image_path, componentFQDD, job_wait=True):
        rjson = self.entity._install_from_uri(uri=firm_image_path, target=componentFQDD)
        rjson['file'] = str(share)
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        return rjson

    def reset(self):
        self.sw_inited = False
        self._swidentity = {}
        self.firmware_json = {}
        self.installed_firmware = {}

    def get_swidentity(self):
        if self.sw_inited:
            logger.debug("Already present")
            return self.firmware_json
        self.entity._get_entries(self.firmware_json, self.firmware_enum)
        logger.debug(self.firmware_json)
        for obj in self.firmware_json:
            self.installed_firmware[obj] = []
            for entry in self.firmware_json[obj]:
                if 'Status' in entry and entry['Status'] == 'Installed':
                    self.installed_firmware[obj].append(entry)
        return self.firmware_json

    def _get_swidentity_hash(self):
        self.get_swidentity()
        for comp in self.firmware_json:
            for swentry in self.firmware_json[comp]:
                if not "FQDD" in swentry:
                    continue
                if swentry["FQDD"] in self._swidentity:
                    if not isinstance(self._swidentity[swentry["FQDD"]], list):
                        self._swidentity[swentry["FQDD"]] = [self._swidentity[swentry["FQDD"]]]
                else:
                    self._swidentity[swentry["FQDD"]] = {}
                self._swidentity[swentry["FQDD"]] = {}
                if "ComponentID" in swentry and swentry["ComponentID"]:
                    for val in ["ComponentID"]:
                        self._swidentity[swentry["FQDD"]][val] = swentry[val]
                else:
                    for val in ["VendorID", "SubVendorID", "DeviceID", "SubDeviceID"]:
                        self._swidentity[swentry["FQDD"]][val] = swentry[val]

                for val in ["ComponentType", "InstanceID", "VersionString", "Status"]:
                    self._swidentity[swentry["FQDD"]][val] = swentry[val]
                self._swidentity[swentry["FQDD"]]["ComponentClass"] = "unknown"
                # TODO RESTORE
                # for mycomp in self.protocolspec.compmap:
                #    if re.match(self.protocolspec.compmap[mycomp],swentry["FQDD"]):
                #        self.swidentity[swentry["FQDD"]]["ComponentClass"] = mycomp
        self.sw_inited = True
        return self._swidentity

    def get_installed_fw_redfish(self):
        try:
            rjson = self.entity._list_fw_inventory_redfish()
            if rjson['Status'] != 'Success':
                return rjson
            members_uris = self.get_redfishjson_using_responsecode(rjson)
            if not members_uris:
                logger.debug("Failed to get installed firmware")
                return {"Status": "Failed", "Message": "Unable to get Installed Firmware"}
            fwlist = []
            for member in members_uris:
                member_uri = member['@odata.id']
                if "Previous" not in member_uri:
                    rjson = self.get_fwdetail_using_uri(str(member_uri))
                    if rjson:
                        fwlist.append(rjson)
            return {"Firmware": fwlist}
        except:
            logger.debug("Failed to get installed firmware")
            return {"Status": "Failed", "Message": "Unable to get Installed Firmware"}

    def get_fwdetail_using_uri(self, r_uri):
        try:
            rjson = self.entity._get_resource_redfish(resource_uri=r_uri)
            if 'Data' not in rjson or rjson['Status'] != 'Success' or 'body' not in rjson['Data']:
                return None
            fw_json = {}
            fw_json['Name'] = rjson['Data']['body']['Name']
            fw_json['Id'] = rjson['Data']['body']['Id']
            fw_json['Status'] = rjson['Data']['body']['Status']
            fw_json['Updateable'] = rjson['Data']['body']['Updateable']
            fw_json['Version'] = rjson['Data']['body']['Version']
            return fw_json
        except:
            logger.debug("Error in getting fw deatil from uri:" + r_uri)
            return None

    def get_redfishjson_using_responsecode(self, r_json):
        try:
            if 'Data' not in r_json:
                logger.debug("Failed to get json from response")
                return None
            if 'body' not in r_json['Data']:
                logger.debug("reponse body is not present")
                return None
            if 'Members' not in r_json['Data']['body']:
                logger.debug("No installed firmware found")
                return None
            return r_json['Data']['body']['Members']
        except Exception:
            logger.debug("Failed to get installed firmware, exception:")
            return None

    @property
    def InstalledFirmware(self):
        if self.entity.use_redfish:
            return self.get_installed_fw_redfish()
        self.get_swidentity()
        return self.installed_firmware

    @property
    def AllUpdates(self):
        return self.get_updates_matching(catalog='Catalog')

    @property
    def AvailableUpdates(self):
        criteria = UpdateFilterCriteria()
        criteria.include_packages(UpdatePresenceEnum.Present)
        return self.get_updates_matching(catalog='Catalog', criteria=criteria)

    @property
    def NeededUpdates(self):
        criteria = UpdateFilterCriteria()
        criteria.include_update_needed(UpdateNeededEnum.Needed)
        return self.get_updates_matching(catalog='Catalog', criteria=criteria)

    def get_updates_matching(self, catalog='Catalog', criteria=None):
        updmgr = UpdateManager.get_instance()
        if not updmgr:
            updates = RepoComparator(self.InstalledFirmware).final()
        else:
            (ignore, cache_cat) = updmgr.getCatalogScoper(catalog)
            updates = cache_cat.compare(self.entity.SystemIDInHex,
                                        self.InstalledFirmware)
        if not criteria:
            return updates

        retval = {}
        for comp in updates:
            for update in updates[comp]:
                if not criteria.meets(update):
                    continue
                if comp not in retval:
                    retval[comp] = []
                retval[comp].append(update)
        return retval

    def save_invcollector_file(self, invcol_output_file):
        with UnicodeWriter(invcol_output_file) as output:
            self._save_invcollector(output)

    def serialize_inventory(self, myshare):
        share = myshare.format(ip=self.entity.ipaddr)
        swfqdd_list = [firmware['FQDD'] for firmware in \
                       self.InstalledFirmware["Firmware"]]
        with UnicodeWriter(share.local_full_path) as f:
            f._write_output(json.dumps({
                'Model_Hex': self.entity.SystemIDInHex,
                'Model': self.entity.Model,
                'IPAddress': self.entity.ipaddr,
                'ServiceTag': self.entity.ServiceTag,
                'Firmware': self.InstalledFirmware['Firmware'],
                'ComponentMap': self.entity.config_mgr._fqdd_to_comp_map(swfqdd_list)},
                sort_keys=True, indent=4, separators=(',', ': ')))

    def update_from_repo(self, catalog_path, apply_update=True, reboot_needed=False, job_wait=True):
        if isinstance(catalog_path, str):
            # Catalog name
            updmgr = UpdateManager.get_instance()
            if not updmgr: return {}
            (cache_share, ignore) = updmgr.getCatalogScoper(catalog_path)
        else:
            # DRM Repo
            cache_share = catalog_path
        catalog_dir = FileOnShare(remote=cache_share.remote_folder_path, isFolder=True, creds=cache_share.creds)
        catalog_file = cache_share.remote_file_name
        if self.entity.use_redfish:
            if isinstance(catalog_path, FileOnShare) and catalog_path.mount_point is None:
                raise ValueError("Share path or mount point does not exist")
            rjson = self.entity._update_from_repo_using_redfish(ipaddress=catalog_dir.remote_ipaddr,
                                                                share_name=catalog_dir.remote.share_name,
                                                                share_type=IFRShareTypeEnum[catalog_dir.remote_share_type.name.lower()],
                                                                username=catalog_dir.creds.username,
                                                                password=catalog_dir.creds.password,
                                                                reboot_needed=reboot_needed,
                                                                catalog_file=catalog_file,
                                                                apply_update=ApplyUpdateEnum[str(apply_update)],
                                                                ignore_cert_warning=IgnoreCertWarnEnum['On'])
        if TypeHelper.resolve(catalog_dir.remote_share_type) == TypeHelper.resolve(ShareTypeEnum.NFS):
            rjson = self.entity._update_repo_nfs(share=catalog_dir, creds=catalog_dir.creds, catalog=catalog_file,
                                                 apply=URLApplyUpdateEnum[str(apply_update)].value,
                                                 reboot=RebootEnum[str(reboot_needed)].value)
        else:
            rjson = self.entity._update_repo(share=catalog_dir, creds=catalog_dir.creds, catalog=catalog_file,
                                             apply=URLApplyUpdateEnum[str(apply_update)].value,
                                             reboot=RebootEnum[str(reboot_needed)].value)
        rjson['file'] = str(cache_share)
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        if not self.entity.use_redfish:
            rjson['job_details'] = self.entity._update_get_repolist()
        return rjson

    def update_from_dell_repo_url(self, ipaddress=None, share_name=None, share_type=None,
                                  catalog_file="Catalog.xml", apply_update=True, reboot_needed=False,
                                  ignore_cert_warning=True, job_wait=True):
        rjson = self.entity._update_dell_repo_url(ipaddress=ipaddress, share_type=URLShareTypeEnum[share_type].value,
                                                  catalog_file=catalog_file,
                                                  apply_update=URLApplyUpdateEnum[str(apply_update)].value,
                                                  reboot_needed=RebootEnum[str(reboot_needed)].value,
                                                  ignore_cert_warning=URLCertWarningEnum[str(ignore_cert_warning)].value)

        file_format = "{0}://{1}/{2}/{3}" if share_name else "{0}://{1}{2}/{3}"
        rjson['file'] = file_format.format(share_type, ipaddress, share_name, catalog_file)
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        if not self.entity.use_redfish:
            rjson['job_details'] = self.entity._update_get_repolist()
        return rjson

    def update_from_repo_url(self, ipaddress=None, share_type=None, share_name=None, share_user=None,
                             share_pwd=None, catalog_file="Catalog.xml", apply_update=True, reboot_needed=False,
                             ignore_cert_warning=True, job_wait=True):
        if self.entity.use_redfish:
            warning = IgnoreCertWarnEnum["On"] if ignore_cert_warning else IgnoreCertWarnEnum["Off"]
            rjson = self.entity._update_from_repo_using_redfish(ipaddress=ipaddress, share_name=share_name,
                                                                share_type=IFRShareTypeEnum[share_type],
                                                                username=share_user, password=share_pwd,
                                                                reboot_needed=reboot_needed, catalog_file=catalog_file,
                                                                apply_update=ApplyUpdateEnum[str(apply_update)],
                                                                ignore_cert_warning=warning.value)
        else:
            rjson = self.entity._update_repo_url(ipaddress=ipaddress, share_type=URLShareTypeEnum[share_type].value,
                                                 share_name=share_name, catalog_file=catalog_file,
                                                 apply_update=URLApplyUpdateEnum[str(apply_update)].value,
                                                 reboot_needed=RebootEnum[str(reboot_needed)].value,
                                                 ignore_cert_warning=URLCertWarningEnum[str(ignore_cert_warning)].value)
        file_format = "{0}://{1}/{2}/{3}" if share_name else "{0}://{1}{2}/{3}"
        rjson['file'] = file_format.format(share_type, ipaddress, share_name, catalog_file)
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        if not self.entity.use_redfish:
            rjson['job_details'] = self.entity._update_get_repolist()
        return rjson

    ##below methods to update firmware using redfish will be reimplemented using Type Manager system
    def _get_scp_path(self, catalog_dir):
        """

        :param catalog_dir: object for Folder containing Catalog on share.
        :param catalog_dir: FileOnShare.
        :returns: returns a tuple containing remote scp path(full) and the scp file name

        """
        catalog_path_str = catalog_dir.remote_full_path
        scp_file = 'scp_' + self.entity.ServiceTag + '_' + datetime.now().strftime('%Y%m%d_%H%M%S') + ".xml"
        scp_path = catalog_path_str + os.path.sep + scp_file
        return (scp_path, scp_file)

    def update_from_repo_usingscp_redfish(self, catalog_dir, catalog_file, mount_point, apply_update=True,
                                          reboot_needed=False, job_wait=True):
        """Performs firmware update on target server using scp RepositoyUpdate attribute

        :param catalog_dir: object for Folder containing Catalog on share.
        :param catalog_dir: FileOnShare.
        :param catalog_file: Catalog file name
        :param catalog_file: str.
        :param mount_point: local share on which remote(catalog_dir) folder has been mounted
        :param mount_point: str.
        :returns: returns status of firmware update through scp

        """
        (scp_path, scp_file) = self._get_scp_path(catalog_dir)
        myshare = FileOnShare(scp_path).addcreds(catalog_dir.creds)
        # exports only that component which contains RepositoryUpdate attribute
        rjson = self.entity.config_mgr.scp_export(share_path=myshare, target='System.Embedded.1')
        if 'Status' not in rjson or rjson['Status'] != 'Success':
            return {'Status': 'Failed', 'Message': 'Export of scp failed for firmware update'}
        scpattrval = {'RepositoryUpdate': catalog_file}
        localfile = mount_point.share_path + os.path.sep + scp_file
        self.edit_xml_file(localfile, scpattrval)
        if reboot_needed:
            shutdown = ShutdownTypeEnum.Graceful
        else:
            shutdown = ShutdownTypeEnum.NoReboot
        rjson = self.entity.config_mgr.scp_import(share_path=myshare, shutdown_type=shutdown, job_wait=job_wait)
        if job_wait:
            rjson['file'] = localfile
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        rjson['job_details'] = self.entity._update_get_repolist()
        return rjson

    def edit_xml_file(self, file_location, attr_val_dict):
        """Edit and save exported scp's attributes which are passed in attr_val_dict

        :param file_location: locally mounted location(full path) of the exported scp .
        :param file_location: str.
        :param attr_val_dict: attribute and value pairs as dict
        :param attr_val_dict: dict.
        :returns: returns None

        """
        tree = ET.parse(file_location)
        root = tree.getroot()
        for attr in attr_val_dict:
            xpath = ".//*[@Name='" + str(attr) + "']"
            attribute_element = root.find(xpath)
            attribute_element.text = str(attr_val_dict.get(attr))
        tree.write(file_location)
        return

    def update_get_repolist(self):
        return self.entity._update_get_repolist()

    def _save_invcollector(self, output):
        # self.entity.get_entityjson()
        # if not "System" in self.entity.entityjson:
        #    logger.debug("ERROR: Entityjson is empty")
        #    return
        self._get_swidentity_hash()
        output._write_output('<SVMInventory>\n')
        output._write_output('    <System')
        if "System" in self.entity.entityjson:
            for (invstr, field) in [("Model", "Model"), ("systemID", "SystemID"), ("Name", "HostName")]:
                if field in self.entity.entityjson["System"]:
                    output._write_output(" " + invstr + "=\"" + self.entity.entityjson["System"][field] + "\"")
        output._write_output(
            ' InventoryTime="{0}">\n'.format(str(datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S"))))
        for ent in self._swidentity:
            output._write_output('        <Device')
            for (invstr, field) in [("componentID", "ComponentID"),
                                    ("vendorID", "VendorID"),
                                    ("deviceID", "DeviceID"),
                                    ("subVendorID", "SubVendorID"),
                                    ("subDeviceID", "SubDeviceID")]:
                if field in self._swidentity[ent]:
                    output._write_output(" " + invstr + "=\"" + self._swidentity[ent][field] + "\"")
            output._write_output(' bus="" display="">\n')
            output._write_output('            <Application componentType="{0}" version="{1}" display="" />\n'.format(
                self._swidentity[ent]["ComponentType"], self._swidentity[ent]["VersionString"]))
            output._write_output('        </Device>\n')
        output._write_output('    </System>\n')
        output._write_output('</SVMInventory>\n')
