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

sys.path.append(os.getcwd())
from ftplib import FTP, error_perm
import socket
from omsdk.sdkprint import PrettyPrint
import time
import gzip
import shutil
import logging

logger = logging.getLogger(__name__)


class FtpCredentials:
    def __init__(self, user='anonymous', password='anonymous@'):
        self.user = user
        self.password = password


class FtpHelper:
    def __init__(self, site, creds):
        try:
            self.ftp = FTP(site, timeout=60)
        except socket.error as e:
            self.ftp = None
            logger.debug("ERROR: Connection failed: " + str(e))
            return
        except socket.gaierror as e:
            self.ftp = None
            logger.debug("ERROR: Connection failed: " + str(e))
            return
        try:
            self.ftp.login(creds.user, creds.password)
        except error_perm:
            logger.debug('ERROR:: cannot login anonymously')
            self.close()
            return
        except socket.timeout:
            logger.debug('ERROR:: socket timedout')
            self.close()
            return
        except Exception as err:
            logger.debug('ERROR:: ' + str(err))
            self.close()
            return

    def close(self):
        try:
            if self.ftp:
                self.ftp.quit()
            self.ftp = None
        except socket.timeout:
            logger.debug('ERROR:: socket timedout')
        except Exception as err:
            logger.debug('ERROR:: ' + str(err))

    # def list_files_to_download(self, lfolder="."):
    #    ldownload =[]
    #    for root, dirs, files in os.walk(lfolder):
    #        tdir = root.replace('\\', '/') + '/'
    #        for f in files:
    #            if self.is_later_than(tdir + f, os.path.join(f)):
    #                ldownload.append(f)
    #    return ldownload

    def list_files_to_download(self, flist, lfolder="."):
        dlist = [fname for fname in flist \
                 if self._is_later_than(fname, lfolder)]
        return dlist

    def _is_later_than(self, fname, lfolder="."):
        lfile = os.path.join(lfolder, *fname.split('/'))
        return self.is_later_than(fname, lfile)

    def is_later_than(self, fname, lfname):
        if not os.path.exists(lfname):
            logger.debug(lfname + " does not exist")
            ltime = time.gmtime(0)
        else:
            ltime = time.gmtime(os.stat(lfname).st_mtime)
        dlist = []
        files = []
        dates = []
        if self.ftp:
            self.ftp.dir(fname, dlist.append)
            for line in dlist:
                fields = line.split()
                if fname.endswith(fields[-1]):
                    files.append(fname)
                else:
                    files.append('notsure')
                stime = None
                if not ':' in fields[7]:
                    stime = fields[5:8]
                    date = time.strptime(' '.join(stime), "%b %d %Y")
                else:
                    stime = [str(time.gmtime().tm_year)] + fields[5:8]
                    date = time.strptime(' '.join(stime), "%Y %b %d %H:%M")
                dates.append(date)
            file_times_ftp = dict(zip(files, dates))
            ftime = file_times_ftp[fname]
            return (ftime > ltime)
        return False

    def download_file(self, fname, lfname):
        try:
            if not self.ftp:
                return False
            # logger.debug('Downloading ' + fname + " to " + lfname)
            f = open(lfname, 'wb')
            self.ftp.retrbinary('RETR ' + fname, f.write)
            f.close()
        except Exception as ex:
            logger.debug("File Download failed:" + str(ex))
            return False
        return True

    def _download_files(self, fname, lfolder):
        rfname = fname.split('/')
        lfile = os.path.join(lfolder, *rfname)
        if len(rfname) > 1:
            nfolder = os.path.join(lfolder, *rfname[0:-1])
            if not os.path.exists(nfolder):
                try:
                    os.makedirs(nfolder)
                except Exception as ex:
                    logger.debug("Cannot create directory : " + str(ex))
                    return False
            elif not os.path.isdir(nfolder):
                logger.debug("cannot create directory, file exists: " + nfolder)
                return False
        return self.download_file(fname, lfile)

    def download_file_to_folder(self, fname, lfolder="."):
        if not os.path.exists(lfolder) or not os.path.isdir(lfolder):
            logger.debug("Need a folder name")
            return False
        return self._download_files(fname, lfolder)

    def download_files(self, flist, lfolder="."):
        counter = {'success': 0, 'failed': 0}
        for fname in flist:
            if self.download_file_to_folder(fname, lfolder):
                counter['success'] += 1
            else:
                counter['failed'] += 1
        return counter

    def download_newerfiles(self, flist, lfolder="."):
        flist = self.list_files_to_download(flist, lfolder)
        return self.download_files(flist, lfolder)

    def download_catalog(self, folder="."):
        c = 'Catalog.xml.gz'
        self.download_file_to_folder(c, folder)
        self.unzip_file(os.path.join(c, folder))

    def unzip_file(self, lfname, tfname=None):
        if not tfname:
            tfname = lfname.rsplit('.gz', 1)[0]
        with gzip.open(lfname, 'rb') as f_in:
            with open(tfname, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return True
