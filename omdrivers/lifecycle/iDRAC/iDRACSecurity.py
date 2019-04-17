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
import base64

from enum import Enum
from datetime import datetime
from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.http.sdkwsman import WsManProtocol
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkproto import PWSMAN, PREDFISH, PSNMP
from omsdk.sdkfile import FileOnShare, Share
from omsdk.sdkcreds import UserCredentials
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdkconfig import ConfigFactory
from omsdk.lifecycle.sdksecurityapi import iBaseSecurityApi
from omsdk.lifecycle.sdkentry import ConfigEntries, RowStatus
from omsdk.sdktime import SchTimer, TIME_NOW
from omdrivers.enums.iDRAC.iDRACEnums import *

import sys
import tempfile
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


class iDRACSecurity(iBaseSecurityApi):
    def __init__(self, entity):
        if PY2:
            super(iDRACSecurity, self).__init__(entity)
        else:
            super().__init__(entity)
        self._job_mgr = entity.job_mgr
        self._config_mgr = entity.config_mgr

    # SSL Export/Import
    def export_ssl_certificate(self, ssl_cert_type=SSLCertTypeEnum.CA_Cert, export_file=None):
        """
            Export SSL Certificate

            :param ssl_cert_type: SSL Certificate Type. 1 - Web_Server_Cert, 2 - CA_Cert, 3 - Custom_Signing_Cert, 4 - Client_Trust_Cert
            :param export_file: Path to output file.
            :type ssl_cert_type: enum <SSLCertTypeEnum>
            :type export_file: str
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Export SSL Certificate
                sslCert = idrac.security_mgr.export_ssl_certificate(ssl_cert_type=SSLCertTypeEnum.Custom_Signing_Cert)

                # Export SSL Certificate to a file
                sslCert = idrac.security_mgr.export_ssl_certificate(ssl_cert_type=SSLCertTypeEnum.Custom_Signing_Cert,
                                    export_file="path/to/file")
        """
        ssl_cert_data = self.entity._export_ssl_certificate(ssl_cert_type=ssl_cert_type)

        logger.info("Writing SSL Certificate to file : {0} : ".format(export_file))
        if export_file is not None:
            if ssl_cert_data["Status"] == "Success":
                # Write the SSL Certificate Data to file
                try:
                    with open(export_file, 'w+') as f:
                        f.write(ssl_cert_data["Data"]["ExportSSLCertificate_OUTPUT"]["CertificateFile"])
                    logger.info("Successfully Export SSL Certificate to file")
                except IOError as e:
                    logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            else:
                logger.error("Export SSL Certificate to file failed : {0}".format(ssl_cert_data["Message"]))

        return ssl_cert_data

    def import_ssl_certificate(self, ssl_cert_file=None, ssl_cert_type=SSLCertTypeEnum.CA_Cert, passphrase=""):
        """
            Import SSL Certificate

            :param ssl_cert_file: Path to Certificate File.
            :param ssl_cert_type: SSL Certificate type. 1 - Web_Server_Cert, 2 - CA_Cert, 3 - Custom_Signing_Cert, 4 - Client_Trust_Cert
            :param passphrase: Passphrase.
            :type ssl_cert_file: str
            :type ssl_cert_type: enum <SSLCertTypeEnum>
            :type passphrase: str
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Import SSL Certificate
                sslCert = idrac.security_mgr.import_ssl_certificate(ssl_cert_file="path/to/file",
                                    ssl_cert_type=SSLCertTypeEnum.Custom_Signing_Cert, passphrase="passphrase")
        """

        if ssl_cert_file is not None:
            try:
                # Reading SSL Certificate file
                logger.info("Reading SSL Certificate from file : {0} : ".format(ssl_cert_file))
                with open(ssl_cert_file, 'rb') as f:
                    file_data = f.read()

                # Encode data to Base64
                cert_data = bytearray(base64.b64encode(file_data))

                for i in range(0, len(cert_data) + 77, 77):
                    cert_data[i:i] = '\n'.encode()

                ssl_cert_data = self.entity._import_ssl_certificate(ssl_cert_file=cert_data.decode(),
                                                                    ssl_cert_type=ssl_cert_type,
                                                                    pass_phrase=passphrase)
                if ssl_cert_data["Status"] == "Success":
                    logger.info("Successfully Export SSL Certificate to file")
                else:
                    logger.error("Import SSL Certificate from file failed : {0}".format(ssl_cert_data["Message"]))
                    ssl_cert_data = {
                        "Status": "Failed",
                        "Message": ssl_cert_data["Message"]
                    }
            except IOError as e:
                logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        else:
            ssl_cert_data = {"Status": "Failed", "Message": "No certificate file or a bad certificate file" \
                                                            "given for import"}
            logger.error("No Certificate File available to import.")
        return ssl_cert_data
