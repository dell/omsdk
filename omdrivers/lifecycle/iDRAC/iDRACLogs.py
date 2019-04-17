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
from omsdk.sdkfile import FileOnShare, Share
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdklogapi import iBaseLogApi
from omsdk.sdkfile import LocalFile
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


class iDRACLogs(iBaseLogApi):
    def __init__(self, entity):
        if PY2:
            super(iDRACLogs, self).__init__(entity, iDRACLogsEnum)
        else:
            super().__init__(entity, iDRACLogsEnum)
        self._job_mgr = entity.job_mgr

    def clear_sel_logs(self):
        if hasattr(self, 'SELLog') and "SELLog" not in self.SELLog:
            del self.SELLog
        return self.entity._clear_sel_log()

    def get_sel_logs(self):
        if not hasattr(self, 'SELLog') or "SELLog" not in self.SELLog:
            self.SELLog = {}
            self.entity._get_entries(self.SELLog, iDRACLogsEnum)
        return self.SELLog

    def get_logs_for_last_job(self):
        if self.entity.cfactory == None:
            logger.debug("Protocol not initialized!")
            return {}
        if self._job_mgr.last_job is None:
            return [{"Sequence": "-1", "MessageID": "None", "Message": "No jobid provided"}]

        return self.get_logs_for_job(self._job_mgr.last_job)

    def lclog_export(self, share_path, job_wait=True):
        """
        Exports the log from the Lifecycle Controller to a file on local/remote share

        :param share_path: the share path where file needs to be exported
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            # Export LC Logs - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            lclog_file = nfs_share.new_file(<FILE-NAME>)

            msg = idrac.log_mgr.lclog_export(lclog_file)

            # Export LC Logs - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            lclog_file = cifs_share.new_file(<FILE-NAME>)

            msg = idrac.log_mgr.lclog_export(lclog_file)

            # Export LC Logs - Local Share
            local_share = LocalFile(local=os.path.join(, "path", "to", "lc-logs-file.xml"))
            export_lclog_streaming = idrac.log_mgr.lclog_export(share_path=local_share)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.LCLogs, export_file=export_file)

        else:
            if TypeHelper.resolve(share.remote_share_type) == TypeHelper.resolve(ShareTypeEnum.NFS):
                rjson = self.entity._log_export_nfs(share=share)
            else:
                rjson = self.entity._log_export(share=share, creds=share_path.creds)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson, False)

        return rjson

    def videolog_export(self, share_path, file_type=FileTypeEnum.BootVideoLogs):
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=file_type, export_file=export_file)

            return rjson

        return {
            "Status": "Failure",
            "Message": "Cannot perform export operation. Video Logs can be exported only to iDRAC Local Share."
        }

    def videolog_export_to_local_share(self, video_log_file_type, job_wait=True):
        rjson = self.entity._video_log_export(share_type=ShareTypeEnum.Local, video_log_file_type=video_log_file_type)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson, False)

        return rjson

    def lclog_export_to_local_share(self, job_wait=True):
        rjson = self.entity._log_export_to_local_share(share_type=ShareTypeEnum.Local)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson, False)

        return rjson

    def complete_lclog_export(self, share_path, job_wait=True):
        """
        Exports the full log from the Lifecycle Controller to a file on local/remote share

        :param share_path: share_path: the share path where file needs to be exported
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
            :name: Examples

            # Export LC Full Logs - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            tsr_file = nfs_share.new_file(<FILE-NAME>)

            idrac.log_mgr.complete_lclog_export(tsr_file)

            # Export LC Full Logs - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            tsr_file = cifs_share.new_file(<FILE-NAME>)

            idrac.log_mgr.complete_lclog_export(tsr_file)

            # Export LC Full Logs - Local Share
            local_share = LocalFile(local=os.path.join(, "path", "to", <FILE_NAME>))
            idrac.log_mgr.complete_lclog_export(local_share)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.LCFullLogs, export_file=export_file)
        else:
            rjson = self.entity._complete_log_export(share=share, creds=share_path.creds)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson, False)
        return rjson

    def complete_lclog_export_to_local_share(self, job_wait=True):
        rjson = self.entity._complete_log_export_to_local_share(share_type=ShareTypeEnum.Local)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    def get_logs_for_job(self, jobid):
        if self.entity.cfactory == None:
            logger.debug("Protocol not initialized!")
            return {}
        if not self.liason_share:
            logger.debug("Configuration Liason Share not registered!")
            return {}

        tempshare = self.liason_share.mkstemp(prefix='logs', suffix='.xml')
        rjson = self.entity._log_export(share=tempshare, creds=tempshare.creds)
        rjson['file'] = str(tempshare)
        rjson = self._job_mgr._job_wait(rjson['file'], rjson, False)

        if rjson['Status'] != 'Success':
            logger.debug("ERROR: cannot get logs. Failed with message: " + rjson['Message'])
            tempshare.dispose()
            return {}

        logger.debug("Log file saved to " + rjson['file'])

        try:
            domtree = ET.ElementTree(file=tempshare.local_full_path)
            logs = []
            startlogging = False
            for logent in domtree.getroot().getchildren():
                logentry = {}
                for (attrname, attrvalue) in logent.items():
                    logentry[attrname] = attrvalue
                for field in logent.getchildren():
                    if field.tag == "MessageArgs":
                        cntr = 0
                        for arg in field.getchildren():
                            logentry["MessageArgs." + arg.tag + "." + str(cntr)] = arg.text
                            cntr = cntr + 1
                    logentry[field.tag] = field.text
                if startlogging:
                    logs.append(logentry)
                if re.match("JCP.*", logentry["MessageID"]):
                    if logentry["MessageArgs.Arg.0"] != jobid:
                        continue
                    if logentry["MessageID"] == "JCP027":
                        startlogging = True
                        logs.append(logentry)
                    else:
                        startlogging = False
        except Exception as ex:
            logger.debug("ERROR: " + str(ex))
        tempshare.dispose()
        return logs
