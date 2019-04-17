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
from enum import Enum
from omsdk.sdkdevice import iDeviceDiscovery, iDeviceRegistry, iDeviceDriver
from omsdk.sdkcenum import EnumWrapper
from omsdk.sdkfile import FileOnShare, Share
from omsdk.sdkcreds import UserCredentials
from omsdk.sdkproto import PSNMP
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

PrinterCompEnum = EnumWrapper("PrinterCompEnum", {
    "System": "System",
    "PrinterMarker": "PrinterMarker",
    "PrinterMarkerSupplies": "PrinterMarkerSupplies",
    "PrinterGeneral": "PrinterGeneral",
    "Interface": "Interface",
    "PrinterConsoleDisplayBuffer": "PrinterConsoleDisplayBuffer",
    "PrinterCover": "PrinterCover",
    "PrinterInput": "PrinterInput",
    "PrinterMediaPath": "PrinterMediaPath",
    "PrinterOutput": "PrinterOutput",
}).enum_type

if PySnmpPresent:
    PrinterSNMPViews = {
        "System": {
            'hrDeviceIndex': ObjectIdentity('HOST-RESOURCES-MIB', 'hrDeviceIndex'),
            'hrDeviceDescr': ObjectIdentity('HOST-RESOURCES-MIB', 'hrDeviceDescr'),
            'hrDeviceID': ObjectIdentity('HOST-RESOURCES-MIB', 'hrDeviceID'),
            'hrPrinterDetectedErrorState': ObjectIdentity('HOST-RESOURCES-MIB', 'hrPrinterDetectedErrorState'),
            'hrPrinterStatus': ObjectIdentity('HOST-RESOURCES-MIB', 'hrPrinterStatus'),
            "prtGeneralSerialNumber": ObjectIdentity('PRINTER-MIB', 'prtGeneralSerialNumber'),  # hrDeviceIndex
            "prtGeneralPrinterName": ObjectIdentity('PRINTER-MIB', 'prtGeneralPrinterName'),  # hrDeviceIndex
        },
        "PrinterMarker": {
            "prtMarkerIndex": ObjectIdentity('PRINTER-MIB', 'prtMarkerIndex'),
            "prtMarkerLifeCount": ObjectIdentity('PRINTER-MIB', 'prtMarkerLifeCount'),
            "prtMarkerPowerOnCount": ObjectIdentity('PRINTER-MIB', 'prtMarkerPowerOnCount'),
            "prtMarkerStatus": ObjectIdentity('PRINTER-MIB', 'prtMarkerStatus'),
        },
        "PrinterMarkerColorant": {
            "prtMarkerColorantIndex": ObjectIdentity('PRINTER-MIB', 'prtMarkerColorantIndex'),
            "prtMarkerColorantValue": ObjectIdentity('PRINTER-MIB', 'prtMarkerColorantValue'),
        },
        "PrinterMarkerSupplies": {
            "prtMarkerSuppliesIndex": ObjectIdentity('PRINTER-MIB', 'prtMarkerSuppliesIndex'),
            "prtMarkerSuppliesDescription": ObjectIdentity('PRINTER-MIB', 'prtMarkerSuppliesDescription'),
            "prtMarkerSuppliesClass": ObjectIdentity('PRINTER-MIB', 'prtMarkerSuppliesClass'),
            "prtMarkerSuppliesType": ObjectIdentity('PRINTER-MIB', 'prtMarkerSuppliesType'),
            "prtMarkerSuppliesMaxCapacity": ObjectIdentity('PRINTER-MIB', 'prtMarkerSuppliesMaxCapacity'),
            "prtMarkerSuppliesLevel": ObjectIdentity('PRINTER-MIB', 'prtMarkerSuppliesLevel'),
        },
        "Interface": {
            "ifIndex": ObjectIdentity('IF-MIB', 'ifIndex'),
            "ifPhysAddress": ObjectIdentity('IF-MIB', 'ifPhysAddress'),
        },
        "PrinterConsoleDisplayBuffer": {
            "prtConsoleDisplayBufferIndex": ObjectIdentity('PRINTER-MIB', 'prtConsoleDisplayBufferIndex'),
            "prtConsoleDisplayBufferText": ObjectIdentity('PRINTER-MIB', 'prtConsoleDisplayBufferText'),
        },
        "PrinterCover": {
            "prtCoverIndex": ObjectIdentity('PRINTER-MIB', 'prtCoverIndex'),
            "prtCoverDescription": ObjectIdentity('PRINTER-MIB', 'prtCoverDescription'),
            "prtCoverStatus": ObjectIdentity('PRINTER-MIB', 'prtCoverStatus'),
        },
        "PrinterInput": {
            "prtInputIndex": ObjectIdentity('PRINTER-MIB', 'prtInputIndex'),
            "prtInputType": ObjectIdentity('PRINTER-MIB', 'prtInputType'),
            "prtInputDescription": ObjectIdentity('PRINTER-MIB', 'prtInputDescription'),
            "prtInputCapacityUnit": ObjectIdentity('PRINTER-MIB', 'prtInputCapacityUnit'),
            "prtInputMaxCapacity": ObjectIdentity('PRINTER-MIB', 'prtInputMaxCapacity'),
            "prtInputCurrentLevel": ObjectIdentity('PRINTER-MIB', 'prtInputCurrentLevel'),
            "prtInputStatus": ObjectIdentity('PRINTER-MIB', 'prtInputStatus'),
            "prtInputMediaName": ObjectIdentity('PRINTER-MIB', 'prtInputMediaName'),
            "prtInputName": ObjectIdentity('PRINTER-MIB', 'prtInputName'),
            "prtInputVendorName": ObjectIdentity('PRINTER-MIB', 'prtInputVendorName'),
            "prtInputModel": ObjectIdentity('PRINTER-MIB', 'prtInputModel'),
            "prtInputVersion": ObjectIdentity('PRINTER-MIB', 'prtInputVersion'),
            "prtInputSerialNumber": ObjectIdentity('PRINTER-MIB', 'prtInputSerialNumber'),
            "prtInputDescription": ObjectIdentity('PRINTER-MIB', 'prtInputDescription'),
        },
        "PrinterMediaPath": {
            "prtMediaPathIndex": ObjectIdentity('PRINTER-MIB', 'prtMediaPathIndex'),
            "prtMediaPathType": ObjectIdentity('PRINTER-MIB', 'prtMediaPathType'),
            "prtMediaPathMediaSizeUnit": ObjectIdentity('PRINTER-MIB', 'prtMediaPathMediaSizeUnit'),
            "prtMediaPathDescription": ObjectIdentity('PRINTER-MIB', 'prtMediaPathDescription'),
            "prtMediaPathStatus": ObjectIdentity('PRINTER-MIB', 'prtMediaPathStatus'),
        },
        "PrinterOutput": {
            "prtOutputIndex": ObjectIdentity('PRINTER-MIB', 'prtOutputIndex'),
            "prtOutputMaxCapacity": ObjectIdentity('PRINTER-MIB', 'prtOutputMaxCapacity'),
            "prtOutputRemainingCapacity": ObjectIdentity('PRINTER-MIB', 'prtOutputRemainingCapacity'),
            "prtOutputStatus": ObjectIdentity('PRINTER-MIB', 'prtOutputStatus'),
            "prtOutputName": ObjectIdentity('PRINTER-MIB', 'prtOutputName'),
            "prtOutputVendorName": ObjectIdentity('PRINTER-MIB', 'prtOutputVendorName'),
            "prtOutputModel": ObjectIdentity('PRINTER-MIB', 'prtOutputModel'),
            "prtOutputVersion": ObjectIdentity('PRINTER-MIB', 'prtOutputVersion'),
            "prtOutputSerialNumber": ObjectIdentity('PRINTER-MIB', 'prtOutputSerialNumber'),
            "prtOutputDescription": ObjectIdentity('PRINTER-MIB', 'prtOutputDescription'),
        }
    }
    PrinterSNMPClassifier = {
        'SysObjectID': 'SNMPv2-SMI::enterprises\\.674\\.10896'
    }

    PrinterComponentTree = {
        "Full": [
            PrinterCompEnum.System
        ]
    }
else:
    PrinterSNMPClassifier = {}
    PrinterComponentTree = {}
    PrinterSNMPViews = {}


class Printer(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(Printer, self).__init__(iDeviceRegistry("Printer", srcdir, PrinterCompEnum))
        else:
            super().__init__(iDeviceRegistry("Printer", srcdir, PrinterCompEnum))
        if PySnmpPresent:
            self.protofactory.add(PSNMP(
                views=PrinterSNMPViews,
                classifier=PrinterSNMPClassifier
            ))
        self.protofactory.addCTree(PrinterComponentTree)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return iDeviceDriver(self.ref, protofactory, ipaddr, creds)
