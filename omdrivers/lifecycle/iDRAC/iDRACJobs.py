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
import logging
from enum import Enum
from datetime import datetime
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkproto import PWSMAN, PREDFISH, PSNMP
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdkjobs import iBaseJobApi

import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3



try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *

    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False

from omdrivers.enums.iDRAC.iDRACEnums import *

logger = logging.getLogger(__name__)
class iDRACJobs(iBaseJobApi):
    def __init__(self, entity):
        if PY2:
            super(iDRACJobs, self).__init__(entity, iDRACJobsEnum)
        else:
            super().__init__(entity, iDRACJobsEnum)

    # joblist = [ 'JID_20123', 'JID_134' ]
    def queue_jobs(self, job_list, schtime):
        if not isinstance(job_list, list):
            job_list = [job_list]
        return self.entity._jobq_setup(jobs=job_list, startat=schtime)

    def delete_job(self, jobid):
        """
            Delete a job

            :param jobid: Job ID
            :type jobid: str
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

            # Delete a job
            job_status = idrac.job_mgr.delete_job(jobid="jid_1234")
        """
        if self.entity.use_redfish:
            rjson = self.entity._delete_job_redfish(job_id=jobid)
            return rjson
        return self.entity._jobq_delete(jobid=jobid)

    def delete_all_jobs(self):
        """
            Delete all jobs

            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

            # Delete all jobs
            job_status = idrac.job_mgr.delete_all_jobs()
        """
        return self.entity._jobq_delete(jobid="JID_CLEARALL")

    def _get_osd_job_details(self):
        self.osd_job_json = {}
        self.entity._get_entries(self.osd_job_json, iDRACOSDJobsEnum)
        if 'OSDJobs' not in self.osd_job_json:
            return {'Status': 'Failed',
                    'Message': 'Cannot fetch OSD Job status'}
        osdjobs = self.osd_job_json['OSDJobs']
        job = {'InstanceID': None}
        if len(osdjobs) >= 1:
            job = osdjobs[len(osdjobs) - 1]
        return {
            'Data': {'Jobs': job},
            'Status': 'Success'
        }

    def get_job_details(self, jobid):
        if self.entity.use_redfish:
            return self.get_job_details_redfish(jobid)
        selector = {"InstanceID": jobid}
        return self.entity.cfactory.opget(iDRACJobsEnum.Jobs, selector)

    def get_job_status(self, jobid):
        """
            Get the job status

            :param jobid: Job ID
            :type jobid: str
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

            # Get Job Status
            job_status = idrac.job_mgr.get_job_status(jobid="jid_1234")
        """
        if self.entity.use_redfish:
            return self.get_job_status_redfish(jobid)
        jobs = {}
        jobret = {"Status": TypeHelper.resolve(JobStatusEnum.InProgress)}
        if jobid.startswith('DCIM_OSD'):
            # Poll for OSD Concrete Job
            jobs = self._get_osd_job_details()
        else:
            jobs = self.get_job_details(jobid)
        logger.debug(self.entity.ipaddr+": job: "+str(jobs))
        if "Status" in jobs and jobs['Status'] != "Success":
            logger.error(self.entity.ipaddr+" : get_job_status failed: jobid: " + jobid + " : Status " + jobs['Status'])
            logger.error(self.entity.ipaddr+" : get_job_status failed: jobid: " + jobid + " : Message " + jobs['Message'])
            return jobs

        jb = jobs['Data']['Jobs']
        if jb['InstanceID'] != jobid:
            logger.error(self.entity.ipaddr + " : get_job_status failed: jobid: " + jobid + " : ERROR: Job instance not found")
            return jobs
        if 'JobStatus' in jb:
            jobstatus = jb['JobStatus']
            if jobstatus == 'Completed':
                jobstaten = JobStatusEnum.Success
            elif jobstatus == 'Failed':
                jobstaten = JobStatusEnum.Failed
            elif jobstatus == 'Pending':
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('In Progress'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Scheduled'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Running'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Invalid'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Success'):
                jobstaten = JobStatusEnum.Success
            elif jobstatus.endswith('Errors'):
                jobstaten = JobStatusEnum.Failed
            elif 'Message' in jb and jb['Message'] and 'completed' in jb['Message'] and 'errors' not in jb['Message']:
                jobstaten = JobStatusEnum.Success
            else:
                jobstaten = JobStatusEnum.InProgress
            jb['Status'] = TypeHelper.resolve(jobstaten)
        return jb

    def _parse_status_obj(self, retval):
        if not 'Status' in retval:
            retval['Status'] = "Invalid"
            retval['Message'] = "<empty result>"
            return (False, 'Invalid', None)
        elif retval['Status'] != 'Success':
            return (False, retval['Status'], None)
        logger.debug(self.entity.ipaddr + ": retval: " + str(retval))
        if retval['Return'] != "JobCreated":
            return (False, retval['Status'], None)
        if not 'Job' in retval or not 'JobId' in retval['Job']:
            logger.error(self.entity.ipaddr + ": Error: Jobid is not found, even though return says jobid")
            return (True, retval['Status'], None)
        jobid = retval['Job']['JobId']
        logger.debug(self.entity.ipaddr +" : Jobid " + jobid)
        if jobid is None:
            return (True, retval['Status'], None)
        return (True, retval['Status'], jobid)

    def _job_wait(self, fname, rjson, track_jobid=True, show_progress=False):
        (is_job_created, job_status, jobid) = self._parse_status_obj(rjson)
        rjson['file'] = fname
        if job_status != 'Success':
            rjson['retval'] = False
            return rjson
        elif not is_job_created:
            rjson['retval'] = True
            return rjson
        elif not jobid:
            rjson['retval'] = False
            return rjson
        rjson = self.job_wait(jobid, track_jobid, show_progress)
        rjson['file'] = fname
        return rjson

    def job_wait(self, jobid, track_jobid=True, show_progress=False,
                 wait_for=2 * 60 * 60):  # wait for a 2 hours (longgg time)
        """Wait for the job to finish(fail/success)

        :param jobid: id of the job.
        :param path: str.         .
        :returns: returns a json/dict containing job details

        """
        logger.info(self.entity.ipaddr + " : Waiting for the job to finish : " + jobid)
        if track_jobid:
            self.last_job = jobid
        ret_json = {}
        job_ret = False
        wait_till = time.time() + wait_for
        while True:
            status = {}
            time.sleep(30)
            if self.entity.use_redfish:
                status = self.get_job_status_redfish(jobid)
            else:
                status = self.get_job_status(jobid)
            if not 'Status' in status:
                logger.debug(self.entity.ipaddr + " : " + jobid + " : Invalid Status")
            else:
                logger.debug(self.entity.ipaddr+" : "+jobid+ ": status: "+str(status))

                pcc = "0"
                msg = ""
                if 'PercentComplete' in status:
                    pcc = status['PercentComplete']
                if 'Message' in status:
                    msg = status['Message']
                if show_progress:
                    logger.debug(self.entity.ipaddr+
                        "{0} : {1} : Percent Complete: {2} | Message = {3}".format(jobid, status['Status'], pcc, msg))
                if status['Status'] == TypeHelper.resolve(JobStatusEnum.Success):
                    if show_progress:
                        logger.debug(self.entity.ipaddr+" : "+jobid+ ":Message:" + status['Message'])
                    job_ret = True
                    ret_json = status
                    break
                elif status['Status'] != TypeHelper.resolve(JobStatusEnum.InProgress):
                    if show_progress:
                        logger.debug(self.entity.ipaddr+" : "+jobid+ ":Message:" + status['Message'])
                    job_ret = False
                    ret_json = status
                    break
                else:
                    logger.debug(self.entity.ipaddr+" : "+jobid+ ": status: "+str(status))
            if time.time() > wait_till:
                ret_json['Status'] = 'Failed'
                ret_json['Message'] = 'Job wait did not return for {0} seconds'.format(wait_for)
                break
        ret_json['retval'] = job_ret
        return ret_json

    # End Job Functions
    def get_job_details_redfish(self, jobid):
        """Gets Details of the job

        :param jobid: id of the job.
        :param path: str.         .
        :returns: returns a json/dict containing job details

        """
        detail = None
        try:
            detail = self.entity._get_idracjobdeatilbyid_redfish(job_id=jobid)
            logger.debug(self.entity.ipaddr+" : "+jobid+ " : Detail : "+str(detail))
        except:
            logger.error(self.entity.ipaddr+" : "+jobid+ ": Exception in getting job details")

        if detail and 'Status' in detail and detail['Status'] == 'Success' and 'Data' in detail and 'body' in detail[
            'Data']:
            jobs = detail['Data']['body']
            detail['Data'] = {}
            detail['Data']['Jobs'] = jobs
            return detail

        retval = {}
        if detail:
            retval['StatusCode'] = detail['StatusCode']
        retval["Status"] = "Failed"
        if detail and detail['StatusCode'] == 501:
            retval["Data"] = {"Status": "Failed",
                              "Message": "Failed to get job detail. Your iDRAC Firmware does not support this operation."}
        else:
            retval["Data"] = {"Status": "Failed",
                              "Message": "Failed to get job detail"}

        return retval

    def get_job_status_by_msgid(self, msg_id):
        print("msg_id=" + msg_id)
        severity = self.entity.eemi_registry[msg_id]["Severity"]
        print("Severity=" + severity)
        if severity is "Informational":
            return JobStatusEnum.Success
        return JobStatusEnum.Failed

    def get_job_status_redfish(self, jobid):
        """Gets status of the job

        :param jobid: id of the job.
        :param path: str.         .
        :returns: returns a json/dict containing job status(key in the dict is Status) along with other details

        """
        jobdetail = self.get_job_details_redfish(jobid)
        if jobdetail['Status'] == 'Failed':
            return jobdetail

        jobdetail_data = jobdetail['Data']['Jobs']
        if (jobdetail_data['PercentComplete'] < 100) or (100 < jobdetail_data['PercentComplete']):
            jobstaten = JobStatusEnum.InProgress
        elif jobdetail_data['JobState'] == 'Completed':
            jobstaten = self.get_job_status_by_msgid(jobdetail_data['MessageId'])
        elif jobdetail_data['JobState'] == 'Failed' or 'Errors' in jobdetail_data['JobState']:
            jobstaten = JobStatusEnum.Failed
        else:
            jobstaten = JobStatusEnum.Invalid

        jobdetail_data['Status'] = TypeHelper.resolve(jobstaten)
        return jobdetail_data

    def list_idrac_jobs(self):
        if self.entity.use_redfish:
            job_list = self.entity._list_all_idracjob_redfish()
            if job_list and job_list['Data'] and job_list['Data']['body']:
                job_list['Data'] = job_list['Data']['body']
            return job_list
