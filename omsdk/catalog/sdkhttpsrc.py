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
import sys
import glob
import socket
import time
import gzip
import shutil
import logging
import hashlib
import base64
import json
from datetime import datetime
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from ftplib import FTP, error_perm

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    from httplib import HTTPConnection
if PY3:
    from http.client import HTTPConnection

UsePyTz = False

if UsePyTz:
    import pytz

logger = logging.getLogger(__name__)

DownloadProtocolEnum = EnumWrapper('DPE', {
   "HTTP": 'HTTP',
   "FTP": 'FTP',
   "NoOp": 'NoOp',
   'HashCheck': 'HashCheck',
}).enum_type

DownloadedFileStatusEnum = EnumWrapper('DFSE', {
   "NotExists": 'NotExists',
   "Same": 'Same',
   "Present": 'Present',
   "Different": 'Different',
   "RemoteIsNew": 'RemoteIsNew',
   "RemoteIsOld": 'RemoteIsOld',
}).enum_type


class FtpCredentials:
    def __init__(self, user='anonymous', password='anonymous@'):
        self.user = user
        self.password = password


class DownloadHelper:
    def __init__(self, site, protocol=DownloadProtocolEnum.HTTP, creds=None):
        self.protocol = protocol
        self.creds = creds
        self.site = site
        self.conn = None
        self.connect()

    def connect(self):
        try:
            if self.conn:
                return True
            if self.protocol == DownloadProtocolEnum.HTTP:
                self.conn = HTTPConnection(self.site)
            elif self.protocol == DownloadProtocolEnum.FTP:
                if self.creds is None: self.creds = FtpCredentials()
                self.conn = FTP(self.site, timeout=60)
                self.conn.login(self.creds.user, self.creds.password)
            elif self.protocol == DownloadProtocolEnum.NoOp:
                self.conn = 'Connected'
            elif self.protocol == DownloadProtocolEnum.HashCheck:
                self.conn = 'Connected'
            return True
        except socket.error as e:
            self.conn = None
            logger.debug("ERROR: Connection failed: " + str(e))
            return False
        except socket.gaierror as e:
            self.conn = None
            logger.debug("ERROR: Connection failed: " + str(e))
            return False

    def disconnect(self):
        try:
            if not self.conn:
                return True
            if self.protocol == DownloadProtocolEnum.HTTP:
                self.conn.close()
            elif self.protocol == DownloadProtocolEnum.FTP:
                self.conn.quit()
            self.conn = None
            return True
        except socket.timeout:
            logger.debug('ERROR:: socket timedout')
            return False
        except Exception as err:
            logger.debug('ERROR:: ' + str(err))
            return False

    def _normalize_date(self, date):
        if date is None: date = '1971-01-01T01:01:01Z',
        try:
            date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
        except Exception as ex:
            logger.debug(str(ex))
        try:
            if isinstance(date, str):
                date = datetime.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception as ex:
            logger.debug(str(ex))
        if isinstance(date, datetime):
            date = datetime(date.year, date.month, date.day,
                            date.hour, date.minute)
        return date

    def _cdt_to_date(self, date):
        # Special case for FTP Server
        date = datetime(date.year, date.month, date.day, date.hour, date.minute)
        if UsePyTz and self.protocol == DownloadProtocolEnum.FTP:
            central = pytz.timezone('US/Central')
            dt_central = central.localize(date)
            date = dt_central.astimezone(pytz.timezone('GMT'))
        return date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _str_date(self, date):
        return date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _validate_file_metadata(self, rfile, file_metadata, rfile_metadata):
        if 'dateTime' not in rfile:
            rfile['dateTime'] = rfile_metadata['dateTime']
        if 'size' not in rfile:
            rfile['size'] = rfile_metadata['size']
        rtime = self._normalize_date(rfile['dateTime'])
        ltime = self._normalize_date(file_metadata['dateTime'])
        if rfile['size'] == file_metadata['size'] and rtime == ltime:
            return DownloadedFileStatusEnum.Same
        if rfile['size'] != file_metadata['size']:
            return DownloadedFileStatusEnum.Different
        logger.debug('Remote size=' + str(rfile['size']) +
                     ", Local size=" + str(file_metadata['size']))
        logger.debug('Remote time=' + self._str_date(rtime) +
                     ", Local time=" + self._str_date(ltime))
        if rtime > ltime:
            return DownloadedFileStatusEnum.RemoteIsNew
        return DownloadedFileStatusEnum.RemoteIsOld

    def _get_hashMD5(self, filename):
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _validate_file(self, rfile, lfile):
        if not os.path.exists(lfile) or not os.path.isfile(lfile):
            logger.debug(lfile + " does not exist")
            return DownloadedFileStatusEnum.NotExists

        if rfile['hashMD5'] is None:
            logger.debug(lfile + " exists. But no hashMD5 given.")
            return DownloadedFileStatusEnum.Present

        file_md5hash = self._get_hashMD5(lfile)
        if file_md5hash.lower() == rfile['hashMD5'].lower():
            logger.debug("HashMD5 for " + lfile + " matches with catalog")
            return DownloadedFileStatusEnum.Same
        logger.debug("HashMD5 for " + lfile + " is different")
        logger.debug("File HashMD5={0}, expected HashMD5={1}".\
                             format(file_md5hash, rfile['hashMD5']))
        return DownloadedFileStatusEnum.Different

    def _get_file_metadata(self, fname, response):
        metadata = {}
        metadata['path'] = fname
        if self.protocol == DownloadProtocolEnum.FTP:
            dlist = []
            self.conn.dir(fname, dlist.append)
            for line in dlist:
                fields = line.split()
                if not fname.endswith(fields[-1]):
                    continue
    
                stime = None
                if not ':' in fields[7]:
                    stime = fields[5:8]
                    date = datetime.strptime(' '.join(stime), "%b %d %Y")
                else:
                    stime = [str(time.gmtime().tm_year)] + fields[5:8]
                    date = datetime.strptime(' '.join(stime), "%Y %b %d %H:%M")
                metadata['dateTime'] = self._cdt_to_date(date)
                metadata['size'] = int(fields[4])
        elif self.protocol == DownloadProtocolEnum.HTTP:
            metadata['size'] = int(response.getheader('Content-Length'))
            metadata['dateTime'] = response.getheader('Last-Modified')
            for header in ['Content-Type', 'Server', 'Date']:
                metadata[header] = response.getheader(header)
        return metadata

    def _download_file(self, rfile, lfile):
        try:
            fstatus = self._validate_file(rfile, lfile)

            if fstatus in [DownloadedFileStatusEnum.Same]:
                # if the file is same, no need to download file
                logger.debug(rfile['path'] + " is as expected!")
                if self.protocol in [DownloadProtocolEnum.HashCheck]:
                    print("{0:16} {1}".format(TypeHelper.resolve(fstatus), lfile))
                return True

            if self.protocol == DownloadProtocolEnum.HashCheck:
                # in case of hashcheck, return the status after printing
                if os.path.exists(lfile) and os.path.isfile(lfile):
                    print("{0:16} {1}".format(TypeHelper.resolve(fstatus), lfile))
                else:
                    print("{0:16} {1}".format('Does not exist', lfile))
                return True
            elif self.protocol == DownloadProtocolEnum.NoOp:
                print('Downloading :' + rfile['path'])
                print('         to :' + lfile)
                return True

            if not self.connect():
                return False
            if not self._create_dir(os.path.dirname(lfile)):
                return False

            file_metadata = {
                    'dateTime':  '1971-01-01T01:01:01Z',
                    'size': 0
            }
            try:
                if os.path.isfile(lfile + ".Metadata"):
                    with open(lfile + ".Metadata", "r") as f1:
                        file_metadata = json.load(f1)
                    logger.debug(json.dumps(file_metadata, sort_keys=True,
                            indent=4, separators=(',', ': ')))
            except Exception as ex:
                logger.debug("Error opening metadata file:" + str(ex))

            logger.debug('Downloading ' + rfile['path'] + " metadata")
            response = None
            if self.protocol == DownloadProtocolEnum.HTTP:
                self.conn.request('GET', '/' + rfile['path'])
                response = self.conn.getresponse()

            rfile_metadata = self._get_file_metadata(rfile['path'], response)
            fstatus = self._validate_file_metadata(rfile,
                                                   file_metadata, rfile_metadata)
            logger.debug("_validate_file_metadata() returned" + str(fstatus))
            if fstatus not in [DownloadedFileStatusEnum.RemoteIsOld,
                               DownloadedFileStatusEnum.RemoteIsNew,
                               DownloadedFileStatusEnum.Different]:
                if response: response.close()
                return True
            logger.debug('Downloading ' + rfile['path'] + " to " + lfile)
            print('Downloading ' + rfile['path'])
            with open(lfile + ".Metadata", "w") as f1:
                f1.write(json.dumps(rfile_metadata, sort_keys=True,
                                    indent=4, separators=(',', ': ')))
            if self.protocol == DownloadProtocolEnum.HTTP:
                with open(lfile, 'wb') as f:
                    f.write(response.read())
            elif self.protocol == DownloadProtocolEnum.FTP:
                f = open(lfile, 'wb')
                self.conn.retrbinary('RETR ' + rfile['path'], f.write)
                f.close()
            fstatus = self._validate_file(rfile, lfile)
            logger.debug("_validate_file() returned" + str(fstatus))
            return (fstatus in [DownloadedFileStatusEnum.Same,
                                DownloadedFileStatusEnum.Present])
        except Exception as ex:
            print(str(ex))
            logger.debug("File Download failed:" + str(ex))
            return False

    def _create_dir(self, lfolder, *rfname):
        nfolder = os.path.join(lfolder, *rfname)
        if not os.path.exists(nfolder):
            try:
                os.makedirs(nfolder)
            except Exception as ex:
                logger.debug("Cannot create directory : " + str(ex))
                return False
        elif not os.path.isdir(nfolder):
            logger.debug("cannot create directory, file exists: " + nfolder)
            return False
        return True

    def download_newerfiles(self, flist, lfolder="."):
        counter = {'success': 0, 'failed': 0}

        if not self._create_dir(lfolder):
            counter['failed'] = len(flist)
            counter['Message'] = 'Local folder not present'
            print("local folder is not present")
            return counter

        for rfile in flist:
            if not isinstance(rfile, dict):
                rfile = {'path': rfile, 'hashMD5': None}
            lfile = os.path.join(lfolder, *rfile['path'].split('/'))
            if self._download_file(rfile, lfile):
                counter['success'] += 1
            else:
                counter['failed'] += 1
        return counter

    def unzip_file(self, lfname, tfname=None):
        if not tfname:
            tfname = lfname.rsplit('.gz', 1)[0]
        retval = False
        if os.path.isfile(lfname):
            f_in = gzip.open(lfname, 'rb')
            try:
                with open(tfname, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    retval = True
            finally:
                f_in.close()
        return retval
