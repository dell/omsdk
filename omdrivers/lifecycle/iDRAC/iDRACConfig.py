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
import json
import xml.etree.ElementTree as ET
from enum import Enum
from datetime import datetime
from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkproto import PWSMAN, PREDFISH, PSNMP
from omsdk.sdkfile import FileOnShare, Share, LocalFile
from omsdk.sdkcreds import UserCredentials
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdkconfig import ConfigFactory
from omsdk.lifecycle.sdkconfigapi import iBaseConfigApi
from omsdk.lifecycle.sdkentry import ConfigEntries, RowStatus
from omsdk.sdktime import SchTimer, TIME_NOW
from omdrivers.lifecycle.iDRAC.rebootOptions import RebootOptions
from omdrivers.enums.iDRAC.iDRACEnums import *
from omdrivers.enums.iDRAC.iDRAC import *
from omdrivers.enums.iDRAC.RAID import *
from omsdk.simulator.devicesim import Simulator
from omdrivers.lifecycle.iDRAC.SCPParsers import XMLParser
from omdrivers.lifecycle.iDRAC.RAIDHelper import RAIDHelper
from past.builtins import long
import sys
import logging
import tempfile
import traceback

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *

    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False

iDRACConfigCompSpec = {
    "LifecycleController": {
        "pattern": "LifecycleController.Embedded.1",
        "registry": "iDRAC",
        "groups": ["LCAttributes"]
    },
    "System": {
        "pattern": "System.Embedded.1",
        "registry": "iDRAC",
        "groups": [
            "LCD",
            "ThermalConfig",
            "QuickSync",
            "ServerPwr",
            "ServerTopology",
            "ServerOS"
        ]
    },
    "iDRAC": {
        "pattern": "iDRAC.Embedded.1",
        "registry": "iDRAC",
        "firmware_pattern": "(iDRAC|OSCollector|USC)\..*",
        "excl_groups": [
            "LCD",
            "ThermalConfig",
            "QuickSync",
            "ServerPwr",
            "ServerTopology",
            "ServerOS"
        ]
    },
    "FC": {
        "pattern": "FC\.Slot\..*",
        "firmware_pattern": "FC\.Slot\..*",
        "registry": "FCHBA",
        "nogroup": True
    },
    "NIC": {
        "pattern": "NIC\..*",
        "firmware_pattern": "NIC\..*",
        "registry": "NIC",
        "nogroup": True
    },
    "Controller": {
        "pattern": "^(RAID|AHCI)\.*",
        "firmware_pattern": "^(RAID|AHCI)\.*",
        "registry": "RAID",
        "groups": ["Controller"],
        "nogroup": True
    },
    "Enclosure": {
        "pattern": "^[^D].+:RAID[.]",
        "firmware_pattern": "^[^D].+:RAID[.]",
        "registry": "RAID",
        "groups": ["Enclosure"],
        "nogroup": True
    },
    "PhysicalDisk": {
        "pattern": "^Disk[.][^V]",
        "firmware_pattern": "^Disk[.][^V]",
        "registry": "RAID",
        "groups": ["PhysicalDisk"],
        "nogroup": True
    },
    "VirtualDisk": {
        "pattern": "^Disk[.]V",
        "registry": "RAID",
        "groups": ["VirtualDisk"],
        "nogroup": True
    },
    "BIOS": {
        "pattern": "BIOS\..*",
        "firmware_pattern": "BIOS\..*",
        "registry": "BIOS",
        "groups": [],
        "nogroup": True
    },
    "DriverPack": {
        "firmware_pattern": "DriverPack\..*",
        "registry": None,
        "groups": [],
        "nogroup": True
    },
    "PowerSupply": {
        "firmware_pattern": "(PSU)\..*",
        "registry": None,
        "groups": [],
        "nogroup": True
    },
    "Diags": {
        "firmware_pattern": "(Diagnostics)\..*",
        "registry": None,
        "groups": [],
        "nogroup": True
    },
    "CPLD": {
        "firmware_pattern": "CPLD\..*",
        "registry": None,
        "groups": [],
        "nogroup": True
    },
    "CMC": {
        "firmware_pattern": "CMC\..*",
        "registry": None,
        "groups": [],
        "nogroup": True
    },
}

iDRACEnumMaps = {
    ExportFormatEnum.JSON: 1,
    ExportFormatEnum.XML: 0,
    ExportMethodEnum.Default: 0,
    ExportMethodEnum.Clone: 1,
    ExportMethodEnum.Replace: 2,
}


def initialize_enum_maps():
    myenums = list(iDRACEnumMaps.keys())
    for i in myenums:
        iDRACEnumMaps[TypeHelper.resolve(i)] = iDRACEnumMaps[i]


def format_enum_wsman(enval):
    initialize_enum_maps()
    if enval in iDRACEnumMaps:
        return iDRACEnumMaps[enval]
    return 0


# noinspection PyInterpreter
iDRACWsManCmds = {
    ###### LC Services
    "_lc_status": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "GetRemoteServicesAPIStatus",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Return": {},
        "Parameters": []
    },

    "_export_tsr": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportTechSupportReport",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "data_selector_array_in": DataSelectorArrayInEnum,
            "share": FileOnShare,
            "creds": UserCredentials,
        },
        "Return": {
            "File": "file"
        },

        "Parameters": [
            ('DataSelectorArrayIn', "data_selector_array_in", None, DataSelectorArrayInEnum, None),
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None)
        ]
    },

    "_export_tsr_nfs": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportTechSupportReport",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "data_selector_array_in": DataSelectorArrayInEnum,
            "share": FileOnShare,
        },
        "Return": {
            "File": "file"
        },

        "Parameters": [
            ('DataSelectorArrayIn', "data_selector_array_in", None, DataSelectorArrayInEnum, None),
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
        ]
    },

    "_support_assist_collection": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "SupportAssistCollection",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "data_selector_array_in": DataSelectorArrayInEnum,
            "share": FileOnShare,
            "creds": UserCredentials,
            "filter": SupportAssistCollectionFilterEnum,
            "transmit": SupportAssistCollectionTransmitEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('DataSelectorArrayIn', "data_selector_array_in", None, DataSelectorArrayInEnum, None),
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Filter", "filter", None, SupportAssistCollectionFilterEnum, None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None),
            ("Transmit", "transmit", None, SupportAssistCollectionTransmitEnum, None)
        ]
    },

    "_support_assist_collection_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "SupportAssistCollection",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
            "data_selector_array_in": DataSelectorArrayInEnum,
            "filter": SupportAssistCollectionFilterEnum,
            "transmit": SupportAssistCollectionTransmitEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None),
            ("DataSelectorArrayInEnum", "data_selector_array_in", None, DataSelectorArrayInEnum, None),
            ("Filter", "filter", None, SupportAssistCollectionFilterEnum, None),
            ("Transmit", "transmit", None, SupportAssistCollectionTransmitEnum, None)
        ]
    },
    #######
    ## Server Profiles
    #######
    "_sp_restore": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "RestoreImage",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "passphrase": str,
            "image": str
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ('Passphrase', "passphrase", None, type("passphrase"), None),
            ("ImageName", "image", None, type("imagename"), None),
            # ("ScheduledStartTime", datetime),
            # ("UntilTime", datetime)
        ]
    },
    "_sp_backup": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "BackupImage",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "passphrase": str,
            "image": str
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ('Passphrase', "passphrase", None, type("passphrase"), None),
            ("ImageName", "image", None, type("imagename"), None),
            # ("ScheduledStartTime", datetime),
            # ("UntilTime", datetime)
        ]
    },
    #   IPAddress, ShareName, ShareType, Passphrase, ImageName, Username, Password, Workgroup, ScheduledStartTime (TIME_NOW or yyyymmddhhmmss), UntilTime
    #   Returns JobID (return value == 4096)
    #   ShareTypeEnum = (0 = NFS, 2 = CIFS, VFLASH= 4 )
    #   ScheduledStartTime (TIME_NOW or yyyymmddhhmmss)
    #   UntilTime  (yyyymmddhhmmss)
    "_factory_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportFactoryConfiguration",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None)
        ]
    },

    "_factory_export_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportFactoryConfiguration",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None)
        ]
    },

    "_inventory_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportHWInventory",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "xml_schema": XMLSchemaEnum,
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None),
            ("XMLSchema", "xml_schema", None, XMLSchemaEnum, None)
        ]
    },

    "_inventory_export_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportHWInventory",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
            "xml_schema": XMLSchemaEnum,
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None),
            ("XMLSchema", "xml_schema", None, XMLSchemaEnum, None)
        ]
    },
    #######
    ##  Server Configuration Profile
    #######
    "_scp_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportSystemConfiguration",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": type(""),
            "export_format": ExportFormatWsmanEnum,
            "export_use": ExportUseWsmanEnum,
            "include_in_export": IncludeInExportWsmanEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None),
            ("Target", "target", None, type(""), None),
            ("ExportFormat", "export_format", None, ExportFormatWsmanEnum, None),
            ("ExportUse", "export_use", None, ExportUseWsmanEnum, None),
            ("IncludeInExport", "include_in_export", None, IncludeInExportWsmanEnum, None)
        ]
    },

    "_scp_export_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportSystemConfiguration",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
            "target": type(""),
            "export_format": ExportFormatWsmanEnum,
            "export_use": ExportUseWsmanEnum,
            "include_in_export": IncludeInExportWsmanEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None),
            ("Target", "target", None, type(""), None),
            ("ExportFormat", "export_format", None, ExportFormatWsmanEnum, None),
            ("ExportUse", "export_use", None, ExportUseWsmanEnum, None),
            ("IncludeInExport", "include_in_export", None, IncludeInExportWsmanEnum, None)
        ]
    },
    "_scp_import": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ImportSystemConfiguration",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": type(""),
            "shutdown_type": ShutdownTypeWsmanEnum,
            "time_to_wait": type(1),
            "end_host_power_state": EndHostPowerStateWsmanEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("Target", "target", None, type(""), None),
            ("ShutdownType", "shutdown_type", None, ShutdownTypeWsmanEnum, None),
            ("TimeToWait", "time_to_wait", None, type(1), None),
            ("EndHostPowerState", "end_host_power_state", None, EndHostPowerStateWsmanEnum, None)
        ]
    },
    "_scp_import_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ImportSystemConfiguration",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
            "target": type(""),
            "shutdown_type": ShutdownTypeWsmanEnum,
            "time_to_wait": type(1),
            "end_host_power_state": EndHostPowerStateWsmanEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None),
            ("Target", "target", None, type(""), None),
            ("ShutdownType", "shutdown_type", None, ShutdownTypeWsmanEnum, None),
            ("TimeToWait", "time_to_wait", None, int, None),
            ("EndHostPowerState", "end_host_power_state", None, EndHostPowerStateWsmanEnum, None)
        ]
    },

    "_scp_preview_import": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ImportSystemConfigurationPreview",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": SCPTargetEnum,
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None),
            ("Target", "target", None, SCPTargetEnum, None)
        ]
    },

    "_scp_preview_import_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ImportSystemConfigurationPreview",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
            "target": SCPTargetEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None),
            ("Target", "target", None, SCPTargetEnum, None)
        ]
    },

    ###### LC Log
    "_log_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportLCLog",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None)
        ]
    },

    "_log_export_nfs": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportLCLog",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
        ]
    },

    "_log_export_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportLCLog",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None)
        ]
    },

    "_complete_log_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportCompleteLCLog",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("WorkGroup", "creds", 'work_group', type("workgroup"), None)
        ]
    },

    "_complete_log_export_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportCompleteLCLog",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None)
        ]
    },

    "_clear_sel_log": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SELRecordLog",
        "Action": "ClearLog",
        "SelectorSet": {
            "w:Selector": [
            ]},
        "Args": {},
        "Parameters": []
        # return 0 - completed with no error; 1 - not supported; 2 - error
    },
    ###### LC Log

    # Manage Power in Server
    "_change_power_state": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_CSPowerManagementService",
        "Action": "RequestPowerStateChange",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_CSPowerManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'pwrmgtsvc:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "state": PowerStateEnum,
        },
        "Return": {
        },
        "Parameters": [
            ('PowerState', "state", None, PowerStateEnum, None)
        ]
    },
    # Set/Apply Attributes; no scp
    "_jobq_setup": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_JobService",
        "Action": "SetupJobQueue",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_JobService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'JobService'},
                {'@Name': 'SystemName', '#text': 'Idrac'}
            ]},
        "Args": {
            "jobs": list,
            "startat": SchTimer
        },
        "Return": {
        },
        "Parameters": [
            ('JobArray', "jobs", None, list, None),
            ('StartTimeInterval', "startat", "time", datetime, None),
            # ('UntilTime', 'startat', 'until', datetime, None)
        ]
    },
    "_jobq_delete": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_JobService",
        "Action": "DeleteJobQueue",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_JobService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'JobService'},
                {'@Name': 'SystemName', '#text': 'Idrac'}
            ]},
        "Args": {
            "jobid": type("JID"),
        },
        "Return": {
        },
        "Parameters": [
            ('JobID', "jobid", None, type("jobid"), None)
        ]
    },
    "_power_boot": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_ComputerSystem",
        "Action": "RequestStateChange",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'srv:system'}
            ]},
        "Args": {
            "state": PowerBootEnum
        },
        "Return": {
        },
        "Parameters": [
            ('RequestedState', "state", None, PowerBootEnum, None)
        ]
    },
    "_reboot_job": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "CreateRebootJob",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]},
        "Args": {
            "reboot": RebootJobType
        },
        "Return": {
        },
        "Parameters": [
            ('RebootJobType', 'reboot', None, RebootJobType, None)
        ]
    },

    ###### ISO
    "_boot_from_flash": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "BootToISOFromVFlash",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_boot_to_disk": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "BootToHD",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_boot_to_pxe": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "BootToPXE",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_boot_to_iso": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "BootToISO",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_boot_to_network_iso": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "BootToNetworkISO",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "expose_duration": str 
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_folder_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('ImageName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            # RackHD("ExposeDiration",  "duration", None, type("0"), None),
            ("ExposeDuration", "expose_duration", None, str, None),  # 0 - report, 1 - apply
        ]
    },

    "_boot_to_network_iso_nfs": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "BootToNetworkISO",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "expose_duration": str
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_folder_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('ImageName', "share", 'remote_file_name', type("filename"), None),
            ("ExposeDuration", "expose_duration", None, str, None),
            # ("Username",  "creds", 'username', type("user"), None),
            # ("Password",  "creds", 'password', type("password"), None),
            # RackHD("ExposeDiration",  "duration", None, type("0"), None),
        ]
    },

    "_detach_drivers": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DetachDrivers",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []

    },
    "_detach_iso_from_vflash": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DetachISOFromVFlash",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_detach_iso": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DetachISOImage",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_delete_iso_from_vflash": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DetachISOFromVFlash",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_get_driver_pack_info": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "GetDriverPackInfo",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_get_host_mac_info": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "GetHostMACInfo",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_disconnect_network_iso": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DisconnectNetworkISOImage",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_connect_network_iso": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "ConnectNetworkISOImage",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('ImageName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            # RackHD("HashType",  "hashType", None, type(""), None),
            # RackHD("HashValue",  "hashValue", None, type(""), None),
        ]
    },
    "_download_iso": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DownloadISOImage",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('ImageName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            # ("ScheduledStartTime", datetime),
            # ("UntilTime", datetime)
        ]
    },
    "_download_iso_flash": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_OSDeploymentService",
        "Action": "DownloadISOToVFlash",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_OSDeploymentService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:OSDeploymentService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('ImageName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            # ("ScheduledStartTime", datetime),
            # ("UntilTime", datetime)
        ]
    },
    ##############
    ##### Update Management
    ##############
    "_install_from_uri": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "InstallFromURI",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]},
        "Args": {
            "uri": str,
            "target": str,
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('URI', "uri", None, type("tftp://share/dup or cifs://user:pass@ipaddr/dup"), None),
            ("Target", "target", None, type("iDRAC.Embedded.1"), None),
        ]
        # Do reboot after install_from_uri
    },
    "_update_get_repolist": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "GetRepoBasedUpdateList",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]},
        "Args": {},
        "Parameters": []
    },
    "_update_repo": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "InstallFromRepository",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "catalog": str,
            "apply": int,
            "reboot": str
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("CatalogFile", "catalog", None, type("Catalog.xml"), None),
            ("ApplyUpdate", "apply", None, type(0), None),  # 0 - report, 1 - apply
            ("RebootNeeded", "reboot", None, type("TRUE"), None),
        ]
    },
    "_update_repo_nfs": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "InstallFromRepository",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "catalog": str,
            "apply": int,
            "reboot": str
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("CatalogFile", "catalog", None, type("Catalog.xml"), None),
            ("ApplyUpdate", "apply", None, type(0), None),  # 0 - report, 1 - apply
            ("RebootNeeded", "reboot", None, type("TRUE"), None),
        ]
    },
    "_update_repo_url": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "InstallFromRepository",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]
        },
        "Args": {
            "ipaddress": str,
            "share_type": int,
            "share_name": str,
            "catalog_file": str,
            "apply_update": int,
            "reboot_needed": str,
            "ignore_cert_warning": int
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "ipaddress", None, type("10.20.40.50"), None),
            ('ShareName', "share_name", None, type("/test"), None),
            ('ShareType', "share_type", None, type(0), None),
            ('FileName', "catalog_file", None, type("filename"), None),
            ("CatalogFile", "catalog_file", None, type("Catalog.xml"), None),
            ("ApplyUpdate", "apply_update", None, type(0), None),  # 0 - report, 1 - apply
            ("RebootNeeded", "reboot_needed", None, type("TRUE"), None),
            ("IgnoreCertWarning", "ignore_cert_warning", None, type(1), None),
        ]
    },
    "_update_dell_repo_url": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService",
        "Action": "InstallFromRepository",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SoftwareInstallationService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'SoftwareUpdate'},
                {'@Name': 'SystemName', '#text': 'IDRAC:ID'}
            ]
        },
        "Args": {
            "ipaddress": str,
            "share_type": int,
            "catalog_file": str,
            "apply_update": int,
            "reboot_needed": str,
            "ignore_cert_warning": int
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "ipaddress", None, type("10.20.40.50"), None),
            ('ShareType', "share_type", None, type(0), None),
            ('FileName', "catalog_file", None, type("filename"), None),
            ("CatalogFile", "catalog_file", None, type("Catalog.xml"), None),
            ("ApplyUpdate", "apply_update", None, type(0), None),  # 0 - report, 1 - apply
            ("RebootNeeded", "reboot_needed", None, type("TRUE"), None),
            ("IgnoreCertWarning", "ignore_cert_warning", None, type(1), None),
        ]
    },
    "_update_from_repo_using_redfish": {
        "ResourceURI": "/redfish/v1/Dell/Systems/System.Embedded.1/DellSoftwareInstallationService/Actions/DellSoftwareInstallationService",
        "Action": "InstallFromRepository",
        "HttpMethod": "post",
        "SuccessCode": [202],
        "ReturnsJobid": True,
        "Args": {
            "ipaddress": str,
            "share_name": str,
            "share_type": IFRShareTypeEnum,
            "username": str,
            "password": str,
            "catalog_file": str,
            "apply_update": ApplyUpdateEnum,
            "reboot_needed": bool,
            "ignore_cert_warning": IgnoreCertWarnEnum
        },
        "Return": { "File": "file" },
        "Parameters": [
            ('IPAddress', 'ipaddress', None, str, None),
            ('ShareName', 'share_name', None, str, None),
            ('ShareType', 'share_type', None, IFRShareTypeEnum, None),
            ('UserName', 'username', None, str, None),
            ('Password', 'password', None, str, None),
            ('RebootNeeded', 'reboot_needed', None, bool, None),
            ('CatalogFile', 'catalog_file', None, type('Catalog.xml'), None),
            ('ApplyUpdate', 'apply_update', None, ApplyUpdateEnum, None),
            ('IgnoreCertWarning', 'ignore_cert_warning', None, IgnoreCertWarnEnum, None)
        ]
    },

    "_get_update_from_repo_list_using_redfish": {
        "ResourceURI": "/redfish/v1/Dell/Systems/System.Embedded.1/DellSoftwareInstallationService/Actions/DellSoftwareInstallationService",
        "Action": "GetRepoBasedUpdateList",
        "HttpMethod": "post",
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {},
        "Parameters": []
    },

    ##############
    ##### End Update Management
    ##############
    # Blink LED
    "_blink_led": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SystemManagementService",
        "Action": "IdentifyChassis",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_SystemManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:SystemManagementService'},
                {'@Name': 'SystemName', '#text': 'srv:system'}
            ]},
        "Args": {
            "state": BlinkLEDEnum,
            "duration": type(0),  # seconds
        },
        "Return": {
        },
        "Parameters": [
            ('IdentifyState', "state", None, BlinkLEDEnum, None),
            ('DurationLimit', "duration", None, type(0), None)
        ]
    },

    "_change_bios_password": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSService",
        "Action": "ChangePassword",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_BIOSService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:BIOSService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "target": type("BIOS.Setup.1-1"),  # name of BIOS
            "password_type": BIOSPasswordTypeEnum,
            "old_password": type("old"),
            "new_password": type("new"),
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "target", None, type(0), None),
            ('PasswordType', "password_type", None, BIOSPasswordTypeEnum, None),
            ('OldPassword', "old_password", None, type(0), None),
            ('NewPassword', "new_password", None, type(0), None),
        ]
    },

    "_lc_wipe": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "LCWipe",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
        },
        "Return": {
        },
        "Parameters": [
        ]
    },
    "_clear_provisioning_server": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ClearProvisioningServer",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {},
        "Return": {},
        "Parameters": []
    },
    "_reinitiate_dhs": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "LCWipe",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "server": type("provserver.host.com"),  # name of PSErver
            "reset": type(True),  # name of PSErver
            "auto_discover": type("1"),  # 1 - Off, 2- Now, 3 - NextBoot
        },
        "Return": {
        },
        "Parameters": [
            ('ProvisioningServer', "server", None, type("s"), None),
            ('ResetToFactoryDefaults', "reset", None, type(True), None),
            ('PerformAutoDiscovery', "auto_discover", None, type("1"), None),
        ]
    },

    ##############
    ##### License Management
    ##############

    "_delete_license": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "DeleteLicense",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "id": type("EntitlementID"),  # name of PSErver
            "fqdd": type("fqdd_of_device"),  # name of PSErver
            "options": LicenseApiOptionsEnum
        },
        "Return": {
        },
        "Parameters": [
            ('EntitlementID', "id", None, type(""), None),
            ('FQDD', "fqdd", None, type(""), None),
            ('DeleteOptions', "options", None, LicenseApiOptionsEnum, None),
        ]
    },
    "_replace_license": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ReplaceLicense",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "id": type("EntitlementID"),  # name of PSErver
            "fqdd": type("fqdd_of_device"),  # name of PSErver
            "options": LicenseApiOptionsEnum,
            "file": type("file"),
        },
        "Return": {
        },
        "Parameters": [
            ('EntitlementID', "id", None, type(""), None),
            ('FQDD', "fqdd", None, type(""), None),
            ('ReplaceOptions', "options", None, LicenseApiOptionsEnum, None),
            ('LicenseFile', "file", None, type(""), None),
        ]
    },
    "_import_license": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ImportLicense",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "fqdd": type("fqdd_of_device"),  # name of PSErver
            "options": LicenseApiOptionsEnum,
            "file": str,
        },
        "Return": {
        },
        "Parameters": [
            ('FQDD', "fqdd", None, type(""), None),
            ('ImportOptions', "options", None, LicenseApiOptionsEnum, None),
            ('LicenseFile', "file", None, str, None),
        ]
    },
    "_export_device_license_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ExportLicenseByDeviceToNetworkShare",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "fqdd": type("iDRAC.Embedded.1")
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("FQDD", "fqdd", None, type("id"), None),
        ]
    },
    "_export_license_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ExportLicenseToNetworkShare",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "id": type("0")
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("EntitlementID", "id", None, type("id"), None),
        ]
    },
    "_export_license": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ExportLicense",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "id": type("0")
        },
        "Return": {
        },
        "Parameters": [
            ("EntitlementID", "id", None, type("id"), None),
        ]
    },
    "_export_device_license": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ExportLicense",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "fqdd": type("0")
        },
        "Return": {
        },
        "Parameters": [
            ("FQDD", "fqdd", None, type("id"), None),
        ]
    },
    "_license_bits": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ShowLicenseBits",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
        },
        "Return": {
        },
        "Parameters": [
        ]
    },
    "_import_license_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LicenseManagementService",
        "Action": "ImportLicenseFromNetworkShare",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LicenseManagementService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_SPComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LicenseManagementService:1'},
                {'@Name': 'SystemName', '#text': 'systemmc'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "name": type("0"),
            "fqdd": type("0"),
            "options": LicenseApiOptionsEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
            ("LicenseName", "name", None, type("name"), None),
            ("FQDD", "fqdd", None, type("name"), None),
            ("ImportOptions", "options", None, LicenseApiOptionsEnum, None),
        ]
    },
    ##############
    ##### End License Management
    ##############

    "_reset_to_factory": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "iDRACResetCfg",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "preserve": ResetToFactoryPreserveEnum,
            "force": ResetForceEnum
        },
        "Return": {
        },
        "Parameters": [
            ("Preserve", "preserve", None, ResetToFactoryPreserveEnum, None),
            ("Force", "force", None, ResetForceEnum, None),
        ]
    },
    "_reset_idrac": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "iDRACReset",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "force": ResetForceEnum
        },
        "Return": {
        },
        "Parameters": [
            ("Force", "force", None, ResetForceEnum, None),
        ]
    },

    ###### Drive Functions
    "_create_raid_config_job": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "CreateTargetedConfigJob",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "virtual_disk": str,
            "reboot": RebootJobType
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "virtual_disk", None, str, None),
            ('RebootJobType', "reboot", None, RebootJobType, None),
            # out RebootRequired
            # out - 0 -NoError, 1-NotSupported, 2-Error
        ]
    },
    "_delete_raid": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "DeleteVirtualDisk",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "virtual_disk": str
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "virtual_disk", None, str, None),
            # out RebootRequired
            # out - 0 -NoError, 1-NotSupported, 2-Error
        ]
    },
    "_lock_raid": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "LockVirtualDisk",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "virtual_disk": str
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "virtual_disk", None, str, None),
            # out RebootRequired [0=No, 1=Yes]
        ]
    },
    "_remove_all_raids": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "ResetConfig",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "controller": str
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "controller", None, str, None),
            # out RebootRequired [0=No, 1=Yes]
        ]
    },
    "_secure_erase_raid": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "SecureErase",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "virtual_disk": str
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "virtual_disk", None, str, None),
            # out RebootRequired [0=No, 1=Yes]
        ]
    },
    "_blink_drive": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "BlinkTarget",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "target": str
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "target", None, str, None),
        ]
    },
    "_unblink_drive": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_RAIDService",
        "Action": "UnBlinkTarget",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_RAIDService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:RAIDService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "target": str
        },
        "Return": {
        },
        "Parameters": [
            ('Target', "target", None, str, None),
        ]
    },
    ###########
    # WSMAN Streaming
    ###########
    "_clear_transfer_session": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "ClearTransferSession",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "file_operation": FileOperationEnum,
            "file_type": FileTypeEnum
        },
        "Return": {
        },
        "Parameters": [
            ("FileOperation", "file_operation", None, FileOperationEnum, None),
            ("FileType", "file_type", None, FileTypeEnum, None)
        ]
    },
    "_import_data": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "ImportData",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "file_type": FileTypeEnum,
            "in_session_id": long,
            "chunk_size": type(1),
            "file_size": long,
            "txfr_descriptor": TxfrDescriptorEnum,
            "payload": type(""),
            "crc": type(""),
            "payload_encoding": PayLoadEncodingEnum
        },
        "Return": {
            "SessionID": long
        },
        "Parameters": [
            ("ChunkSize", "chunk_size", None, int, None),
            ("FileType", "file_type", None, FileTypeEnum, None),
            # ("ImportFileName", "filename", None, ResetForceEnum, None),
            ("InSessionID", "in_session_id", None, long, None),
            ("CRC", "crc", None, str, None),
            ("FileSize", "file_size", None, long, None),
            ("TxfrDescriptor", "txfr_descriptor", None, TxfrDescriptorEnum, None),
            ("PayLoad", "payload", None, str, None),
            ("PayLoadEncoding", "payload_encoding", None, PayLoadEncodingEnum, None)
        ]
    },
    "_export_data": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "ExportData",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "file_type": FileTypeEnum,
            "in_session_id": long,
            "in_chunk_size": type(1),
            "file_offset": long,
            "tx_data_size": long,
            "payload_encoding": PayLoadEncodingEnum
        },
        "Return": {
            "file_size": long,
            "txfr_descriptor": TxfrDescriptorEnum,
            "payload": type(""),
            "crc": type(""),
            "chunk_size": type(1),
            "session_id": type(""),
            "ret_file_offset": long,
            "ret_tx_data_size": long
        },
        "Parameters": [
            ("FileOffset", "file_offset", None, long, None),
            ("TxDataSize", "tx_data_size", None, long, None),
            ("FileType", "file_type", None, FileTypeEnum, None),
            ("InSessionID", "in_session_id", None, long, None),
            ("InChunkSize", "in_chunk_size", None, int, None),
            ("PayLoadEncoding", "payload_encoding", None, PayLoadEncodingEnum, None),
        ]
    },
    ###########
    # SSL Certificate Import and Export
    ###########

    "_import_ssl_certificate": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "ImportSSLCertificate",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "ssl_cert_file": str,
            "ssl_cert_type": SSLCertTypeEnum,
            "pass_phrase": str
        },
        "Return": {
        },
        "Parameters": [
            ("SSLCertificateFile", "ssl_cert_file", None, str, None),
            ("CertificateType", "ssl_cert_type", None, SSLCertTypeEnum, None),
            ("Passphrase", "pass_phrase", None, str, None)
        ]
    },

    "_export_ssl_certificate": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardService",
        "Action": "ExportSSLCertificate",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "ssl_cert_type": SSLCertTypeEnum,
        },
        "Return": {
        },
        "Parameters": [
            ("SSLCertType", "ssl_cert_type", None, SSLCertTypeEnum, None)
        ]
    },

    ###########
    # Export Video Logs
    ###########
    "_video_log_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportVideoLog",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum,
            "video_log_file_type": VideoLogsFileTypeEnum,
        },
        "Return": {
        },
        "Parameters": [
            ('ShareType', "share_type", None, ShareTypeEnum, None),
            ('FileType', "video_log_file_type", None, VideoLogsFileTypeEnum, None)
        ]
    },

    ###########
    # Export Diagnostics
    ###########
    "_epsa_diagnostics_export": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportePSADiagnosticsResult",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('IPAddress', "share", 'remote_ipaddr', type("10.20.40.50"), None),
            ('ShareName', "share", 'remote_share_name', type("\\test"), None),
            ('ShareType', "share", 'remote_share_type', Share.ShareType, None),
            ('FileName', "share", 'remote_file_name', type("filename"), None),
            ("Username", "creds", 'username', type("user"), None),
            ("Password", "creds", 'password', type("password"), None),
        ]
    },
    "_epsa_diagnostics_export_to_local_share": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",
        "Action": "ExportePSADiagnosticsResult",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_LCService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:LCService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "share_type": ShareTypeEnum
        },
        "Return": {
        },
        "Parameters": [
            ("ShareType", "share_type", None, ShareTypeEnum, None)
        ]
    },

    "_apply_attribute": {
        "ResourceURI": "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardService",
        "Action": "ApplyAttribute",
        "SelectorSet": {
            "w:Selector": [
                {'@Name': 'CreationClassName', '#text': 'DCIM_iDRACCardService'},
                {'@Name': 'SystemCreationClassName', '#text': 'DCIM_ComputerSystem'},
                {'@Name': 'Name', '#text': 'DCIM:iDRACCardService'},
                {'@Name': 'SystemName', '#text': 'DCIM:ComputerSystem'}
            ]},
        "Args": {
            "target": str,
            "attribute_name": str,
            "attribute_value": str
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('Target', "target", None, type(""), None),
            ('AttributeName', "attribute_name", None, type(""), None),
            ('AttributeValue', "attribute_value", None, type(""), None)
        ]
    },

    #############Below are Redfish specific commands, need to be moved once testing completed and protocol issue addressed###########
    "_scp_export_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ExportSystemConfiguration",
        "HttpMethod": "post",
        "SuccessCode": [202],
        "ReturnsJobid": True,
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": type(""),
            "export_format": ExportFormatRedfishEnum,
            "export_use": ExportUseRedfishEnum,
            "include_in_export": IncludeInExportRedfishEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ShareParameters/IPAddress', "share", "remote_ipaddr", type("10.20.40.50"), None),
            ('ShareParameters/ShareName', "share", "remote_share_name", type("\\test"), None),
            ('ShareParameters/ShareType', "share", "remote_share_type_redfish", Share.ShareTypeRedfish, None),
            ('ShareParameters/FileName', "share", "remote_file_name", type("filename"), None),
            ('ShareParameters/UserName', "creds", "username", type("user"), None),
            ('ShareParameters/Username', "creds", "username", type("user"), None), # workaround solution(JIT-132580):
            # Need to adhere with REDFish schema, 14G server changes has reflected.
            # For 12G, 13G changes will be reflected september 2019 onwards.
            ('ShareParameters/Password', "creds", "password", type("password"), None),
            ('ShareParameters/Target', "target", None, type(""), None),
            ('ExportFormat', "export_format", None, ExportFormatRedfishEnum, None),
            ('ExportUse', "export_use", None, ExportUseRedfishEnum, None),
            ('IncludeInExport', "include_in_export", None, IncludeInExportRedfishEnum, None)
        ]
    },

    "_scp_import_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ImportSystemConfiguration",
        "HttpMethod": "post",
        "SuccessCode": [202],
        "ReturnsJobid": True,
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": type(""),
            "shutdown_type": ShutdownTypeRedfishEnum,
            "time_to_wait": type(1),
            "end_host_power_state": EndHostPowerStateRedfishEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ShareParameters/IPAddress', "share", "remote_ipaddr", type("10.20.40.50"), None),
            ('ShareParameters/ShareName', "share", "remote_share_name", type("\\test"), None),
            ('ShareParameters/ShareType', "share", "remote_share_type_redfish", Share.ShareTypeRedfish, None),
            ('ShareParameters/FileName', "share", "remote_file_name", type("filename"), None),
            ('ShareParameters/UserName', "creds", "username", type("user"), None),
            ('ShareParameters/Username', "creds", "username", type("user"), None), # workaround solution(JIT-132580):
            # Need to adhere with REDFish schema, 14G server changes has reflected.
            # For 12G, 13G changes will be reflected september 2019 onwards.
            ('ShareParameters/Password', "creds", "password", type("password"), None),
            ('ShareParameters/Target', "target", None, type(""), None),
            ("ShutdownType", "shutdown_type", None, ShutdownTypeRedfishEnum, None),
            ("TimeToWait", "time_to_wait", None, type(1), None),
            ("HostPowerState", "end_host_power_state", None, EndHostPowerStateRedfishEnum, None)
        ]
    },

    "_get_idracjobdeatilbyid_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs",
        "Action": "",
        "HttpMethod": "get",
        "ResourceURIArg": True,
        "DummyParams": 1,
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {"job_id": type('JID_1000000000000')},
        "Return": {
            "File": "file"
        },
        "Parameters": [('JobID', "job_id", None, type('JID_1000000000000'), None)
                       ]
    },

    "_list_all_idracjob_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs",
        "Action": "",
        "HttpMethod": "get",
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {},
        "Return": {
            "File": "file"
        },
        "Parameters": []
    },

    "_list_fw_inventory_redfish": {
        "ResourceURI": "/redfish/v1/UpdateService/FirmwareInventory",
        "Action": "",
        "HttpMethod": "get",
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {},
        "Return": {
            "File": "file"
        },
        "Parameters": []
    },
    "_configure_system_lockdown_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Attributes",
        "Action": "",
        "HttpMethod": "patch",
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {
            "lockdown_mode": SystemLockdown_LockdownTypes
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('Attributes/Lockdown.1.SystemLockdown', "lockdown_mode", None, SystemLockdown_LockdownTypes, None),
        ]
    },
    "_change_power_state_redfish": {
        "ResourceURI": "/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset",
        "Action": "",
        "HttpMethod": "post",
        "SuccessCode": [204],
        "ReturnsJobid": False,
        "Args": {
            "state": ComputerSystemResetTypesEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ResetType', "state", None, ComputerSystemResetTypesEnum, None),
        ]
    },
    "_reset_idrac_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset",
        "Action": "",
        "HttpMethod": "post",
        "SuccessCode": [204],
        "ReturnsJobid": False,
        "Args": {
            "force": ManagerTypesEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ResetType', "force", None, ManagerTypesEnum, None),
        ]
    },
    "_configure_attributes_redfish": {
        "ResourceURI": "/redfish/v1",
        "Action": "",
        "HttpMethod": "patch",
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {
            "rpath": str,
            "parent_attr": str,
            "attr_val": dict
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('r_path', "rpath", None, str, None),
            ('parentattr', "parent_attr", None, str, None),
            ('payload_param', "attr_val", None, dict, None),
        ]

    },
    "_delete_job_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs",
        "Action": "",
        "HttpMethod": "delete",
        "ResourceURIArg": True,
        "DummyParams": 1,
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {"job_id": type('JID_1000000000000')},
        "Return": {
            "File": "file"
        },
        "Parameters": [('JobID', "job_id", None, type('JID_1000000000000'), None)
                       ]
    },
    "_scp_export_to_local_share_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ExportSystemConfiguration",
        "HttpMethod": "post",
        "SuccessCode": [202],
        "ReturnsJobid": True,
        "Args": {
            "target": type(""),
            "export_format": ExportFormatRedfishEnum,
            "export_use": ExportUseRedfishEnum,
            "include_in_export": IncludeInExportRedfishEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ShareParameters/Target', "target", None, type(""), None),
            ('ExportFormat', "export_format", None, ExportFormatRedfishEnum, None),
            ('ExportUse', "export_use", None, ExportUseRedfishEnum, None),
            ('IncludeInExport', "include_in_export", None, IncludeInExportRedfishEnum, None)
        ]
    },

    "_scp_import_from_local_share_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ImportSystemConfiguration",
        "HttpMethod": "post",
        "SuccessCode": [202],
        "ReturnsJobid": True,
        "Args": {
            "target": type(""),
            "import_string": type(""),
            "shutdown_type": ShutdownTypeRedfishEnum,
            "time_to_wait": type(1),
            "end_host_power_state": EndHostPowerStateRedfishEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ShareParameters/Target', "target", None, type(""), None),
            ("ImportBuffer", "import_string", None, type(""), None),
            ("ShutdownType", "shutdown_type", None, ShutdownTypeRedfishEnum, None),
            ("TimeToWait", "time_to_wait", None, type(1), None),
            ("HostPowerState", "end_host_power_state", None, EndHostPowerStateRedfishEnum, None)
        ]
    },

    "_get_resource_redfish": {
        "ResourceURI": "",
        "Action": "",
        "HttpMethod": "get",
        "ResourceURIArg": True,
        "DummyParams": 1,
        "SuccessCode": [200, 202],
        "ReturnsJobid": False,
        "Args": {"resource_uri": type('uri')},
        "Return": {
            "File": "file"
        },
        "Parameters": [('Ruri', "resource_uri", None, type('uri'), None)]
    },
    "_reboot_system_redfish": {
        "ResourceURI": "/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem",
        "Action": "Reset",
        "HttpMethod": "post",
        "SuccessCode": [200, 204, 202],
        "ReturnsJobid": False,
        "Args": {
            "reboot_type": type("")
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ResetType', "reboot_type", None, type(""), None)
        ]
    },

    "_create_bios_config_job_redfish": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs",
        "Action": "",
        "HttpMethod": "post",
        "SuccessCode": [200],
        "ReturnsJobid": True,
        "Args": {
            "target_uri": type("")
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('TargetSettingsURI', "target_uri", None, type(""), None)
        ]
    },

    "_get_acton_redfish": {
        "ResourceURI": "/redfish/v1/Systems/System.Embedded.1",
        "Action": "",
        "HttpMethod": "get",
        "SuccessCode": [200],
        "ReturnsJobid": False,
        "Args": {},
        "Return": {
            "File": "file"
        },
        "Parameters": []
    }

    #############Above are Redfish specific commands, need to be moved once testing completed and protocol issue addressed###########
}

todo_cmds = [
    "BootConfigSettings",
    "BootSourceSettings",
    "ChangeBootOrder",
    "ChangeBootSourceState",  # instanceid, enabledstate
    "CSIOR",  # Enable, Disable
    "ChangeiDRACCredentials",  # Enable, Disable
    "GetNetworkIsoConnectionInfo",
    "SetPowerCapCmd",
    "UnpackAndAttach",
    "DCIM_iDRACCardService.SSLResetCfg"  # SSL to factory defaults
    "DCIM_iDRACCardService.ExportSSLCertificate"  # SSL to factory defaults
    "DCIM_iDRACCardService.ImportSSLCertificate"  #
    "DCIM_iDRACCardService.RemoveSelf"  # GroupName=group
    "DCIM_iDRACCardService.DeleteGroup"  # GroupName=group
    "DCIM_iDRACCardService.JoinGroup"  # GroupName=group,GroupPasscode

    # Get:CIM_ComputerSystem

]

iDRACRedfishCmds = {
    "_scp_export": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ExportSystemConfiguration",
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": SCPTargetEnum,
            "format_file": ExportFormatEnum,
            "method": ExportMethodEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ShareParameters/IPAddress', "share", "remote_ipaddr", type("10.20.40.50"), None),
            ('ShareParameters/ShareName', "share", "remote_share_name", type("\\test"), None),
            ('ShareParameters/ShareType', "share", "remote_share_type", Share.ShareType, None),
            ('ShareParameters/FileName', "share", "remote_file_name", type("filename"), None),
            ('ShareParameters/Username', "creds", "username", type("user"), None),
            ('ShareParameters/Password', "creds", "password", type("password"), None),
            ('ShareParameters/Target', "target", None, SCPTargetEnum, None),
            # ("ScheduledStartTime", datetime),
            # ("UntilTime", datetime),
            ('ExportFormat', "format_file", None, ExportFormatEnum, None),
        ]
    },
    "_scp_import": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ImportSystemConfiguration",
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": SCPTargetEnum,
            "format_file": ExportFormatEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [
            ('ShareParameters/IPAddress', "share", "remote_ipaddr", type("10.20.40.50"), None),
            ('ShareParameters/ShareName', "share", "remote_share_name", type("\\test"), None),
            ('ShareParameters/ShareType', "share", "remote_share_type", Share.ShareType, None),
            ('ShareParameters/FileName', "share", "remote_file_name", type("filename"), None),
            ('ShareParameters/Username', "creds", "username", type("user"), None),
            ('ShareParameters/Password', "creds", "password", type("password"), None),
            ('ShareParameters/Target', "target", None, SCPTargetEnum, None),
            # ("ScheduledStartTime", datetime),
            # ("UntilTime", datetime),
            ('ExportFormat', "format_file", None, ExportFormatEnum, None),
        ]
    },
    "_scp_import_preview": {
        "ResourceURI": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager",
        "Action": "ImportSystemConfigurationPreview",
        "Args": {
            "share": FileOnShare,
            "creds": UserCredentials,
            "target": SCPTargetEnum,
            "format_file": ExportFormatEnum
        },
        "Return": {
            "File": "file"
        },
        "Parameters": [('ShareParameters', 'IPAddress', type("10.20.40.50")),
                       ('ShareParameters/IPAddress', "share", "remote_ipaddr", type("10.20.40.50"), None),
                       ('ShareParameters/ShareName', "share", "remote_share_name", type("\\test"), None),
                       ('ShareParameters/ShareType', "share", "remote_share_type", Share.ShareType, None),
                       ('ShareParameters/FileName', "share", "remote_file_name", type("filename"), None),
                       ('ShareParameters/Username', "creds", "username", type("user"), None),
                       ('ShareParameters/Password', "creds", "password", type("password"), None),
                       ('ShareParameters/Target', "target", None, SCPTargetEnum, None),
                       # ("ScheduledStartTime", datetime),
                       # ("UntilTime", datetime),
                       ('ExportFormat', "format_file", None, ExportFormatEnum, None),
                       ]
    },
}


class iDRACKeyFieldSpec(object):
    @staticmethod
    def vUserName(vmap):
        if not 'UserName' in vmap:
            return RowStatus.Partial
        username = vmap['UserName']
        retval = RowStatus.Row_With_Invalid_Key
        if (username is not None and len(username.strip()) > 0):
            retval = RowStatus.Row_With_Valid_Key
        return retval

    @staticmethod
    def vAlertDestination(vmap):
        if not 'Destination' in vmap:
            return RowStatus.Partial
        destentry = vmap['Destination']
        retval = RowStatus.Row_With_Invalid_Key
        if (destentry is not None and len(destentry.strip()) > 0 and \
                        destentry not in ["::", '0.0.0.0']):
            retval = RowStatus.Row_With_Valid_Key
        return retval

    @staticmethod
    def vEmailAddress(vmap):
        if not 'Address' in vmap:
            return RowStatus.Partial
        destentry = vmap['Address']
        retval = RowStatus.Row_With_Invalid_Key
        if (destentry is not None and len(destentry.strip()) > 0):
            retval = RowStatus.Row_With_Valid_Key
        return retval


iDRACConfigKeyFields = {
    "Users": {
        "Pattern": 'Users.(\d+)#(.+)',
        "Key": 'UserName',
        "Validate": iDRACKeyFieldSpec.vUserName
    },
    "SNMPAlert": {
        "Pattern": 'SNMPAlert.(\d+)#(.+)',
        "Key": 'Destination',
        "Validate": iDRACKeyFieldSpec.vAlertDestination
    },
    "EmailAlert": {
        "Pattern": 'EmailAlert.(\d+)#(.+)',
        "Key": 'Address',
        "Validate": iDRACKeyFieldSpec.vEmailAddress
    },
}


class iDRACConfig(iBaseConfigApi):
    def __init__(self, entity):
        if PY2:
            super(iDRACConfig, self).__init__(entity)
        else:
            super().__init__(entity)
        self._job_mgr = entity.job_mgr
        self.entity.configCompSpec = iDRACConfigCompSpec
        self.liason_share = None
        self._raid_helper = None
        self._raid_tree = None
        self.use_redfish = False
        ###
        self.config = ConfigFactory.get_config(entity.config_dir, iDRACConfigCompSpec)
        self._config_entries = ConfigEntries(iDRACConfigKeyFields)
        ###

        self._initialize()

    def set_liason_share(self, myshare):
        if not (isinstance(myshare, FileOnShare) or isinstance(myshare, LocalFile)):
            logger.debug("should be an instance of FileOnShare")
            return {
                "Status": "Failed",
                "Message": "Invalid share. Should be an instance of FileOnShare"
            }
        if isinstance(myshare, FileOnShare) and not myshare.IsValid:
            logger.debug("Share is not valid, please retry!!")
            logger.debug("You can only perform readonly operations!")
            # return False
        try:
            self.liason_share = myshare
            return self._initialize()
        except Exception as ex:
            error_msg = "Exception while setting up liason share : {}".format(str(ex))
            logger.debug(error_msg)
            return {
                "Status": "Failed",
                "Message": str(ex)
            }

    def _initialize(self):
        self._sysconfig = None
        fcspec = os.path.join(self.entity.config_dir, 'iDRAC.comp_spec')
        self.xmlp = XMLParser(fcspec)
        return self._load_scp()

    def apply_changes(self, reboot=False):
        if self._sysconfig and not self._sysconfig.is_changed():
            msg = {'Status': 'Success',
                   'Message': 'No changes found to commit!'}
            return msg
        return self._commit_scp(None, reboot=reboot)

    # Enabling APIs
    def _commit_scp(self, record, reboot=False):
        filename = None
        msg = {'Status': 'Failed',
               'Message': 'Unable to load configuration'}
        tempshare = None
        content = self._sysconfig.ModifiedXML
        if record is not None:
            content = self.config.format_scp(record)
        if Simulator.is_simulating():
            print('======applying')
            print(content)
            print('======end')
            filename = Simulator.record_config(self.entity.ipaddr, content,
                                               'new-scp.xml')
            msg = {'Status': 'Success',
                   'Message': 'Saved successfully'}
        else:
            if not self.liason_share:
                return {'Status': 'Failed',
                        'Message': 'Configuration Liason Share not registered.'}

            tempshare = self.liason_share.mkstemp(prefix='scp', suffix='.xml')
            if tempshare:
                filename = tempshare.local_full_path

            with open(filename, "w") as f:
                f.write(content)

            msg = self.scp_import(tempshare,
                                  shutdown_type=ShutdownTypeEnum.Forced if reboot else ShutdownTypeEnum.Graceful)

        if msg['Status'] == 'Success':
            self._sysconfig.commit()
        else:
            self._sysconfig.reject()

        if tempshare:
            tempshare.dispose()

        return msg

    def _load_scp(self):
        if self._sysconfig:
            return {'Status': 'Success'}

        filename = None
        msg = {'Status': 'Failed',
               'Message': 'Unable to load configuration'}
        tempshare = None
        if Simulator.is_simulating():
            filename = Simulator.simulate_config(self.entity.ipaddr)
            msg = {'Status': 'Success',
                   'Message': 'Loaded successfully'}
        else:
            if not self.liason_share:
                return {'Status': 'Failed',
                        'Message': 'Configuration Liason Share not registered.'}

            tempshare = self.liason_share.mkstemp(prefix='scp', suffix='.xml')
            if tempshare:
                filename = tempshare.local_full_path

            msg = self.scp_export(tempshare)
            logger.debug(msg)

        if msg['Status'] == 'Success':
            if Simulator.is_recording():
                with open(filename, 'r') as f:
                    content = f.read()
                Simulator.record_config(self.entity.ipaddr, content, 'config.xml')

            try:
                self._sysconfig = self.xmlp.parse_scp(filename)
                self._sysconfig.commit()
                # 1 is used for special default user - root
                self._sysconfig.iDRAC.Users._index_helper.unusable(1)
            except Exception as ex:
                self._sysconfig = None
                logger.error(str(ex))
                msg = {"Status": "Failed", "Message": "{}".format(ex)}
                # traceback.print_exc()

        if tempshare:
            tempshare.dispose()

        return msg

    def _comp_to_fqdd(self, fqdd_list, comp, default=None):
        retVal = []
        if not comp in self.entity.configCompSpec:
            return retVal
        for i in fqdd_list:
            if 'firmware_pattern' in self.entity.configCompSpec[comp]:
                fpattern = self.entity.configCompSpec[comp]['firmware_pattern']
                if re.match(fpattern, i):
                    retVal.append(i)
        if len(retVal) <= 0 and default:
            retVal = default
        return retVal

    def _fqdd_to_comp(self, fqdd_list):
        retVal = []
        for i in fqdd_list:
            found = False
            for comp in self.entity.configCompSpec:
                if 'firmware_pattern' in self.entity.configCompSpec[comp]:
                    fpattern = self.entity.configCompSpec[comp]['firmware_pattern']
                    if re.match(fpattern, i):
                        retVal.append(comp)
                        found = True
                        break
            if not found:
                retVal.append(i)
        return set(retVal)

    def _fqdd_to_comp_map(self, fqdd_list):
        retVal = {}
        for i in fqdd_list:
            found = False
            for comp in self.entity.configCompSpec:
                if 'firmware_pattern' in self.entity.configCompSpec[comp]:
                    fpattern = self.entity.configCompSpec[comp]['firmware_pattern']
                    if re.match(fpattern, i):
                        if comp not in retVal:
                            retVal[comp] = []
                        retVal[comp].append(i)
                        found = True
                        break
            if not found:
                if comp not in retVal:
                    retVal[i] = []
                retVal[i].append(i)
        return retVal

    @property
    def LCReady(self):
        """
            This property provides the information regarding whether the LC is Ready

            .. code-block:: python
                :caption: Examples
                :name: Examples

                msg = idrac.config_mgr.LCReady
        """
        rjson = self.entity._lc_status()
        status = self.entity._get_field_from_action(rjson, "Data", "GetRemoteServicesAPIStatus_OUTPUT", "Status")
        return (status and status in ["0"])

    @property
    def ServerStatus(self):
        rjson = self.entity._lc_status()
        status = self.entity._get_field_from_action(rjson, "Data", "GetRemoteServicesAPIStatus_OUTPUT", "ServerStatus")
        return (status and status not in ["6", "7", "8", "9"])

    @property
    def LCStatus(self):
        """
            This property provides the Status of LC

            .. code-block:: python
                :caption: Examples
                :name: Examples

                msg = idrac.config_mgr.LCStatus
        """
        rjson = self.entity._lc_status()
        states = {
            "0": "Ready",
            "1": "Not Initialized",
            "2": "Reloading Data",
            "3": "Disabled",
            "4": "In Recovery",
            "5": "In Use",
            "U": "Unknown",
        }
        status = self.entity._get_field_from_action(rjson, "Data", "GetRemoteServicesAPIStatus_OUTPUT", "LCStatus")

        if not status or (status not in states):
            status = "U"
        return states[status]

    # LC Status
    def lc_status(self):
        return self.entity._lc_status()

    def wait_till_lc_ready(self, timeout=100):
        sleep_time = 10  # seconds
        ncntr = round(interval / sleep_time)
        for i in range(0, ncntr + 1):
            if self.LCReady:
                return True
            time.sleep(sleep_time)
        return False

    # Blink LED
    def blink_led(self, ledenum, duration=None):
        return self.entity._blink_led(state=ledenum, duration=duration)

    # Decommission: Wipe off all data
    def lc_wipe(self):
        return self.entity._lc_wipe()

    # BIOS Change Password
    def change_bios_password(self, passtype, old_password, new_password):
        return self.entity._change_bios_password(target="BIOS.Setup.1-1",
                                                 passtype=passtype, old_password=old_password,
                                                 new_password=new_password)

    # Power Management and Reboot
    def change_power(self, power_state):
        """
            Change the power state of a server.

            :param power_state: Power State option. 2 - PowerOn, 5 - SoftPowerCycle, 8 - SoftPowerOff, 9 - PowerCycle, 10 - HardReset, 11 - DiagnosticInterrupt, 12 - GracefulPowerOff
            :type power_state: enum <PowerStateEnum>
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Reset iDRAC
                msg = idrac.config_mgr.change_power(PowerStateEnum.SoftPowerCycle)
        """
        if self.entity.use_redfish:
            rjson = self.entity._change_power_state_redfish(state=power_state)
            return rjson
        return self.entity._change_power_state(state=power_state)

    def power_boot(self, power_state):
        """
            Power On/Off the Server

            :param power_state: Power State Option. 2 - Enabled, 3 - Disabled, 11 - Reset
            :type power_state: enum <PowerBootEnum>
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Power On/Off Server
                msg = idrac.config_mgr.power_boot(PowerBootEnum.Enabled)
        """
        return self.entity._power_boot(state=power_state)

    def reboot_after_config(self, reboot_type=RebootJobType.GracefulRebootWithForcedShutdown, job_wait=True):
        """
            Reboot Server after Configuration

            :param reboot_type: Reboot Type Option. 1 - PowerCycle, 2 - GracefulRebootWithoutShutdown, 3 - GracefulRebootWithForcedShutdown
            :param job_wait: The flag to wait for job completion. False will return the Job ID
            :type reboot_type: enum <RebootJobType>
            :type job_wait: bool
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Reboot a server after configuration
                msg = idrac.config_mgr.reboot_after_config(reboot_type=RebootJobType.PowerCycle)
        """
        rjson = self.entity._reboot_job(reboot=reboot_type)

        rjson['file'] = '<reboot>'
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    # Reset to Factory Defaults
    def reset_to_factory(self, preserve_config=ResetToFactoryPreserveEnum.ResetExceptNICAndUsers,
                         force=ResetForceEnum.Graceful):
        """
            Reset the iDRAC to factory default configurations

            :param preserve_config: Preserve configuration option. 0 - ResetExceptNICAndUsers, 1 - ResetAll 2 - ResetAllExceptDefaultUser
            :param force: Reset option. 0 - Graceful, 1 - Force
            :type preserve_config: enum <ResetToFactoryPreserveEnum>
            :type force: enum <ResetForceEnum>
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Reset iDRAC to factory defaults
                msg = idrac.config_mgr.reset_to_factory(preserve_config = ResetToFactoryPreserveEnum.ResetExceptNICAndUsers, force=ResetForceEnum.Force)
        """
        if not self.entity.ServerGeneration.startswith(TypeHelper.resolve(ServerGenerationEnum.Generation_14)):
            print(
                "WARNING : Preserving network and user configuration is supported only on 14th and above Generations of "
                "PowerEdge Servers. Resetting all configuration to default including network and user configuration")
        return self.entity._reset_to_factory(preserve=preserve_config, force=force)

    def reset_idrac(self, force=None):
        """
            Reset the iDRAC

            :param force: Reset option. 0 - Graceful, 1 - Force
            :type force: enum <ResetForceEnum>
            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Reset iDRAC
                msg = idrac.config_mgr.reset_idrac(force=ResetForceEnum.Graceful)
            """
        if force is None:
            force = ManagerTypesEnum.GracefulRestart if self.entity.use_redfish else ResetForceEnum.Graceful

        if self.entity.use_redfish:
            rjson = self.entity._reset_idrac_redfish(force=force)
            return rjson
        return self.entity._reset_idrac(force=force)

    # Auto Discovery APIs
    def clear_provisioning_server(self):
        return self.entity._clear_provisioning_server()

    def reinitiate_dhs(self):
        return self.entity._renitiate_dhs()

    # End Auto Discovery APIs

    @property
    def SystemConfiguration(self):
        return self._sysconfig

    #############################################
    ##  BIOS Boot Mode
    #############################################
    @property
    def BootMode(self):
        return self._sysconfig.BIOS.BootMode

    def configure_boot_mode(self, boot_mode=None):
        """
            Configure Boot Mode

            :param boot_mode: Boot Mode. "Bios" - Bios, "Uefi" - Uefi
            :type boot_mode: enum <BootModeTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Boot Mode
                msg = idrac.config_mgr.configure_boot_mode(BootModeTypes.Uefi)

                idrac.config_mgr.apply_changes(reboot = True)
        """
        if boot_mode is None:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        self.BootMode.set_value(boot_mode)
        # return self.apply_changes(reboot=False)

    def configure_boot_sequence(self, boot_mode=None, boot_sequence=None):
        """
            Configure Boot Sequence

            :param boot_mode: Boot Mode. "Bios" - Bios, "Uefi" - Uefi
            :param boot_sequence: Boot Sequence.
            :type boot_mode: enum <BootModeEnum>
            :type boot_sequence: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Boot Sequence
                msg = idrac.config_mgr.configure_boot_sequence(boot_mode = BootModeEnum.Uefi,
                                                   boot_sequence="device-1, device-2, device-3")

                idrac.config_mgr.apply_changes(reboot = True)
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if TypeHelper.resolve(boot_mode) == TypeHelper.resolve(BootModeEnum.Uefi):
            self.SystemConfiguration.BIOS.UefiBootSeq.set_value(boot_sequence)
        elif TypeHelper.resolve(boot_mode) == TypeHelper.resolve(BootModeEnum.Bios):
            self.SystemConfiguration.BIOS.BiosBootSeq.set_value(boot_sequence)
        else:
            return {
                'Status': 'Failed',
                'Message': 'Invalid Boot Mode'
            }

            # return self.apply_changes(reboot=True)

    #############################################
    ##  BIOS NVME Mode
    #############################################
    @property
    def NvmeMode(self):
        return self._sysconfig.BIOS.NvmeMode

    def configure_nvme_mode(self, nvme_mode=None):
        """
            Configure NVME Mode

            :param nvme_mode: NVME Mode. "NonRaid" - NonRaid, "Raid" - Raid
            :type nvme_mode: enum <NvmeModeTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure NVME Mode
                msg = idrac.config_mgr.configure_nvme_mode(NvmeModeTypes.NonRaid)

                idrac.config_mgr.apply_changes(reboot = True)
        """
        if nvme_mode is None:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        self.NvmeMode.set_value(nvme_mode)
        # return self.apply_changes(reboot=True)

    #############################################
    ##  BIOS Secure Boot Mode
    #############################################
    @property
    def SecureBootMode(self):
        return self._sysconfig.BIOS.SecureBootMode

    def configure_secure_boot_mode(self, secure_boot_mode=None):
        """
            Configure Secure Boot Mode

            :param secure_boot_mode: Secure Boot Mode. "AuditMode" - AuditMode, "DeployedMode" - DeployedMode, "SetupMode" - SetupMode, "UserMode" - UserMode
            :type secure_boot_mode: enum <SecureBootModeTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Secure Boot Mode
                msg = idrac.config_mgr.configure_secure_boot_mode(SecureBootModeTypes.UserMode)

                idrac.config_mgr.apply_changes(reboot = True)
        """
        if secure_boot_mode is None:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        self.SecureBootMode.set_value(secure_boot_mode)
        # return self.apply_changes(reboot=True)

    #############################################
    ##  BIOS One-Time Boot Mode
    #############################################
    @property
    def OneTimeBootMode(self):
        return self._sysconfig.BIOS.OneTimeBootMode

    def configure_onetime_boot_mode(self, onetime_boot_mode=None):
        """
            Configure One-Time Boot Mode

            :param onetime_boot_mode: One-Time Boot Mode. "Disabled" - Disabled, "OneTimeBootSeq" - OneTimeBootSeq, "OneTimeCustomBootSeqStr" - OneTimeCustomBootSeqStr, "OneTimeCustomHddSeqStr" - OneTimeCustomHddSeqStr, "OneTimeCustomUefiBootSeqStr" - OneTimeCustomUefiBootSeqStr, "OneTimeHddSeq" - OneTimeHddSeq, "OneTimeUefiBootSeq" - OneTimeUefiBootSeq
            :type onetime_boot_mode: enum <OneTimeBootModeTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure One-Time Boot Mode
                msg = idrac.config_mgr.configure_onetime_boot_mode(OneTimeBootModeTypes.Disabled)

                idrac.config_mgr.apply_changes(reboot = True)
        """
        if onetime_boot_mode is None:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        self.OneTimeBootMode.set_value(onetime_boot_mode)
        # return self.apply_changes(reboot=True)

    def bios_reset_to_defaults(self):
        self._sysconfig.LifecycleController.LCAttributes.BIOSRTDRequested_LCAttributes = BIOSRTDRequested_LCAttributes.T_True
        return self.apply_changes(reboot=True)

    # Configure APIs
    @property
    def CSIOR(self):
        return self._sysconfig.LifecycleController.LCAttributes.CollectSystemInventoryOnRestart_LCAttributes

    def enable_csior(self):
        """
            Enable Collect System Inventory on Restart(CSIOR)

            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Enable CSIOR
                msg = idrac.config_mgr.enable_csior()
        """
        self.CSIOR.set_value(CollectSystemInventoryOnRestart_LCAttributesTypes.Enabled)
        # return self.apply_changes(reboot=True)

    def disable_csior(self):
        """
            Disable Collect System Inventory on Restart(CSIOR)

            :return: success/failure response
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                # Disable CSIOR
                msg = idrac.config_mgr.disable_csior()
        """
        self.CSIOR.set_value(CollectSystemInventoryOnRestart_LCAttributesTypes.Disabled)
        # return self.apply_changes(reboot=True)

    @property
    def Location(self):
        return self._sysconfig.System.ServerTopology

    # System Lockdown mode APIs

    @property
    def SystemLockdown(self):
        return self._sysconfig.iDRAC.Lockdown.SystemLockdown_Lockdown

    def enable_system_lockdown(self):
        """
        Performs Lockdown enable operation. Lockdown is supported only on 14th Generation of PowerEdge Servers.

        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
            :name: Examples

            # Enable System Lockdown
            msg = idrac.config_mgr.enable_system_lockdown()
        """
        if not self.entity.ServerGeneration.startswith(TypeHelper.resolve(ServerGenerationEnum.Generation_14)):
            return {'Status': 'Failure',
                    'Message': 'Cannot perform Lockdown operation. Lockdown is supported only on 14th Generation of PowerEdge Servers.'}
        if self.entity.use_redfish:
            rjson = self.entity._configure_system_lockdown_redfish(lockdown_mode=SystemLockdown_LockdownTypes.Enabled)
            return rjson
        self.SystemLockdown.set_value(SystemLockdown_LockdownTypes.Enabled)
        return self.apply_changes(reboot=True)

    def disable_system_lockdown(self):
        """
        Performs Lockdown disable operation. Lockdown is supported only on 14th Generation of PowerEdge Servers.

        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
            :name: Examples

            # Disable System Lockdown
            msg = idrac.config_mgr.disable_system_lockdown()
        """

        if not self.entity.ServerGeneration.startswith(TypeHelper.resolve(ServerGenerationEnum.Generation_14)):
            return {'Status': 'Failure',
                    'Message': 'Cannot perform Lockdown operation. Lockdown is supported only on 14th Generation of PowerEdge Servers.'}
        if self.entity.use_redfish:
            rjson = self.entity._configure_system_lockdown_redfish(lockdown_mode=SystemLockdown_LockdownTypes.Disabled)
            return rjson
        return self.entity._apply_attribute(target="iDRAC.Embedded.1", attribute_name="Lockdown.1#SystemLockdown",
                                            attribute_value="0")

    # End of System Lockdown mode APIs

    #############################################
    ##  SNMP Trap Destinations
    #############################################
    @property
    def SNMPTrapDestination(self):
        return self._sysconfig.iDRAC.SNMPAlert

    def configure_snmp_trap_destination(self, destination_number=None, enable_snmp_alert=None, destination=None,
                                        snmp_v3_username=None, state=None):
        """
            Configure SNMP Trap Destination Settings

            :param destination_number: Destination Number
            :param enable_snmp_alert: Enable SNMP Alert. "Enabled" - Enabled, "Disabled" - Disabled
            :param destination: Destination Address
            :param snmp_v3_username: SNMPv3 User
            :param state: State. "Enabled" - Enabled, "Disabled" - Disabled
            :type destination_number: number
            :type enable_snmp_alert: enum <Enable_SNMPAlertTypes>
            :type destination: str
            :type snmp_v3_username: str
            :type state: enum <State_SNMPAlertTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure SNMP Trap Destination Settings
                msg = idrac.config_mgr.configure_snmp_trap_destination(destination_number = 1, destination = "1.1.1.1",
                                                snmp_v3_username = None, state = State_SNMPAlertTypes.Disabled)
                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if destination_number is None:
            return {
                'Status': 'Failed',
                'Message': 'Destination Number is not specified.'
            }

        snmp_trap_destination = self.SNMPTrapDestination.find_or_create(index=destination_number)

        if enable_snmp_alert is not None:
            snmp_trap_destination.Enable_SNMPAlert.set_value(enable_snmp_alert)

        if destination is not None:
            snmp_trap_destination.Destination_SNMPAlert.set_value(destination)

        if snmp_v3_username is not None:
            snmp_trap_destination.SNMPv3Username_SNMPAlert.set_value(snmp_v3_username)

        if state is not None:
            snmp_trap_destination.State_SNMPAlert.set_value(state)

            # return self.apply_changes(reboot=False)

    @property
    def SNMPConfiguration(self):
        return self._sysconfig.iDRAC.SNMP

    def configure_snmp(self, snmp_enable=None, community_name=None, snmp_protocol=None, alert_port=None,
                       discovery_port=None, trap_format=None, ipmi_community=None):
        """
            Configure SNMP Settings

            :param snmp_enable: Enable SNMP. "Enabled" - Enabled, "Disabled" - Disabled
            :param community_name:  Community Name
            :param snmp_protocol: SNMP Protocol. "All" - All, "SNMPv3" - SNMPv3
            :param alert_port: Alert Port
            :param discovery_port: Discovery Port
            :param trap_format: Trap Format. "SNMPv1" - SNMPv1, "SNMPv2" - SNMPv2, "SNMPv3" - SNMPv3
            :type snmp_enable: enum <AgentEnable_SNMPTypes>
            :type community_name: str
            :type snmp_protocol: enum <SNMPProtocol_SNMPTypes>
            :type alert_port: number
            :type discovery_port: number
            :type trap_format: enum <TrapFormat_SNMPTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure SNMP Settings
                msg = msg = idrac.config_mgr.configure_snmp(snmp_enable = AgentEnable_SNMPTypes.Disabled, community_name = "test",
                                          snmp_protocol = SNMPProtocol_SNMPTypes.SNMPv3, alert_port = 161,
                                          discovery_port = 162, trap_format = TrapFormat_SNMPTypes.SNMPv3)

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if snmp_enable is not None:
            self.SNMPConfiguration.AgentEnable_SNMP.set_value(snmp_enable)
        if community_name is not None:
            self.SNMPConfiguration.AgentCommunity_SNMP.set_value(community_name)
        if snmp_protocol is not None:
            self.SNMPConfiguration.SNMPProtocol_SNMP.set_value(snmp_protocol)
        if alert_port is not None:
            self.SNMPConfiguration.AlertPort_SNMP.set_value(alert_port)
        if discovery_port is not None:
            self.SNMPConfiguration.DiscoveryPort_SNMP.set_value(discovery_port)
        if trap_format is not None:
            self.SNMPConfiguration.TrapFormat_SNMP.set_value(trap_format)
        if ipmi_community is not None:
            self.SystemConfiguration.iDRAC.IPMILan.CommunityName_IPMILan.set_value(ipmi_community)

            # return self.apply_changes(reboot=False)

    #############################################
    ##  Web Server Configuration
    #############################################
    @property
    def WebServerConfiguration(self):
        return self._sysconfig.iDRAC.WebServer

    def configure_web_server(self, enable_web_server=None, http_port=None, https_port=None, timeout=None,
                             ssl_encryption=None, tls_protocol=None):
        """
            Configure Web Server Settings

            :param enable_web_server: Enable Web Server. "Enabled" - Enabled, "Disabled" - Disabled
            :param http_port:  HTTP Port
            :param https_port: HTTPS Port
            :param timeout: Timeout
            :param ssl_encryption: SSL Encryption. "Auto-Negotiate" - Auto_Negotiate, "128-Bit or higher" - T_128_Bit_or_higher, "168-Bit or higher" - T_168_Bit_or_higher, "256-Bit or higher" - T_256_Bit_or_higher
            :param tls_protocol: TLS Protocol. "TLS 1.0 and Higher" - TLS_1_0_and_Higher, "TLS 1.1 and Higher" - TLS_1_1_and_Higher, "TLS 1.2 Only" - TLS_1_2_Only
            :type enable_web_server: enum <Enable_WebServerTypes>
            :type http_port: number
            :type https_port: number
            :type timeout: number
            :type ssl_encryption: enum <SSLEncryptionBitLength_WebServerTypes>
            :type tls_protocol: enum <TLSProtocol_WebServerTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Web Server Settings
                msg = msg = msg = idrac.config_mgr.configure_web_server(enable_web_server = Enable_WebServerTypes.Enabled,
                                            http_port = 80, https_port = 443, timeout = 1800,
                                            ssl_encryption = SSLEncryptionBitLength_WebServerTypes.T_128_Bit_or_higher,
                                            tls_protocol = TLSProtocol_WebServerTypes.TLS_1_1_and_Higher)

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if enable_web_server is not None:
            self.WebServerConfiguration.Enable_WebServer.set_value(enable_web_server)

        if http_port is not None:
            self.WebServerConfiguration.HttpPort_WebServer.set_value(http_port)

        if https_port is not None:
            self.WebServerConfiguration.HttpsPort_WebServer.set_value(https_port)

        if timeout is not None:
            self.WebServerConfiguration.Timeout_WebServer.set_value(timeout)

        if ssl_encryption is not None:
            self.WebServerConfiguration.SSLEncryptionBitLength_WebServer.set_value(ssl_encryption)

        if tls_protocol is not None:
            self.WebServerConfiguration.TLSProtocol_WebServer.set_value(tls_protocol)

            # return self.apply_changes(reboot=False)

    @property
    def SMTPServerSettings(self):
        return self._sysconfig.iDRAC.RemoteHosts

    def configure_smtp_server_settings(self, smtp_ip_address=None, smtp_port=None, authentication=None,
                                       username=None, password=None):
        """
            Configure SMTP Server Settings

            :param smtp_ip_address: SMTP IP Address
            :param smtp_port: SMTP Port
            :param authentication: SMTP Authentication. "Enabled" - Enabled, "Disabled" - Disabled
            :param username: Username
            :param password: Password
            :type smtp_ip_address: str
            :type smtp_port: number
            :type authentication: enum <SMTPAuthentication_RemoteHostsTypes>
            :type username: str
            :type password: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure SMTP Server Settings
                msg = idrac.config_mgr.configure_smtp_server_settings(smtp_ip_address = "1.1.1.1", smtp_port = 26,
                                                          authentication = SMTPAuthentication_RemoteHostsTypes.Enabled,
                                                          username = "usrname", password = "passwd")

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if smtp_ip_address is not None:
            self.SMTPServerSettings.SMTPServerIPAddress_RemoteHosts.set_value(smtp_ip_address)

        if smtp_port is not None:
            self.SMTPServerSettings.SMTPPort_RemoteHosts.set_value(smtp_port)

        if authentication is not None:
            self.SMTPServerSettings.SMTPAuthentication_RemoteHosts.set_value(authentication)

        if username is not None:
            self.SMTPServerSettings.SMTPUserName_RemoteHosts.set_value(username)

        if password is not None:
            self.SMTPServerSettings.SMTPPassword_RemoteHosts.set_value(password)

            # return self.apply_changes(reboot=False)

    @property
    def SyslogServers(self):
        return self._sysconfig.iDRAC.SysLog.Servers.Value

    @property
    def SyslogConfig(self):
        return self._sysconfig.iDRAC.SysLog

    def enable_syslog(self, apply_changes=True):
        """
            Enable Sys Log Configuration
            :param apply_changes: ApplyCanges
            :type apply_changes: bool
            :return: success/failure response ,when apply_changes is True
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Enable Syslog
                msg = idrac.config_mgr.enable_syslog()
        """
        # if len(self.SyslogServers) > 0:
        self._sysconfig.iDRAC.SysLog.PowerLogEnable_SysLog = PowerLogEnable_SysLogTypes.Enabled
        self._sysconfig.iDRAC.SysLog.SysLogEnable_SysLog = SysLogEnable_SysLogTypes.Enabled
        if apply_changes:
            return self.apply_changes(reboot=False)

    def disable_syslog(self, apply_changes=True):
        """
            Enable Sys Log Configuration
            :param apply_changes: ApplyCanges
            :type apply_changes: bool
            :return: success/failure response ,when apply_changes is True
            :rtype: JSON


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Disable Syslog
                msg = idrac.config_mgr.disable_syslog()
        """
        # if len(self.SyslogServers) > 0:
        self._sysconfig.iDRAC.SysLog.PowerLogEnable_SysLog = PowerLogEnable_SysLogTypes.Disabled
        self._sysconfig.iDRAC.SysLog.SysLogEnable_SysLog = SysLogEnable_SysLogTypes.Disabled
        if apply_changes:
            return self.apply_changes(reboot=False)

    #############################################
    ##  Timezone
    #############################################
    @property
    def TimeZone(self):
        return self._sysconfig.iDRAC.Time.Timezone_Time

    def configure_timezone(self, timezone=None):
        """
            Configure timezone

            :param timezone: Timezone
            :type timezone: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Timezone
                msg = idrac.config_mgr.configure_timezone('US/Pacific')

                idrac.config_mgr.apply_changes()
        """
        if timezone is None:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        self.TimeZone.set_value(timezone)
        # return self.apply_changes(reboot=False)

    @property
    def Time(self):
        return self._sysconfig.iDRAC.Time

    @property
    def NTPConfiguration(self):
        return self._sysconfig.iDRAC.NTPConfigGroup

    @property
    def NTPServers(self):
        return self.NTPConfiguration.NTPServers

    @property
    def NTPEnabled(self):
        return self.NTPConfiguration.NTPEnable_NTPConfigGroup

    @property
    def NTPMaxDist(self):
        return self._sysconfig.iDRAC.NTPConfigGroup.NTPMaxDist_NTPConfigGroup

    def configure_ntp(self, enable_ntp=None, ntp_server_1=None, ntp_server_2=None, ntp_server_3=None):
        """
            Configure NTP Server Settings

            :param enable_ntp: Enable NTP Server. "Enabled" - Enabled, "Disabled" - Disabled
            :param ntp_server_1: NTP Server 1
            :param ntp_server_2: NTP Server 2
            :param ntp_server_3: NTP Server 3
            :type enable_ntp: enum <NTPEnable_NTPConfigGroupTypes>
            :type ntp_server_1: str
            :type ntp_server_2: str
            :type ntp_server_3: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure NTP Server Settings
                msg = idrac.config_mgr.configure_ntp(enable_ntp = NTPEnable_NTPConfigGroupTypes.Enabled,
                                        ntp_server_1 = "", ntp_server_2 = "", ntp_server_3 = "")

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if enable_ntp is not None:
            self.NTPConfiguration.NTPEnable_NTPConfigGroup.set_value(enable_ntp)
        if ntp_server_1 is not None:
            self.NTPConfiguration.NTP1_NTPConfigGroup.set_value(ntp_server_1)
        if ntp_server_2 is not None:
            self.NTPConfiguration.NTP2_NTPConfigGroup.set_value(ntp_server_2)
        if ntp_server_3 is not None:
            self.NTPConfiguration.NTP3_NTPConfigGroup.set_value(ntp_server_3)

            # return self.apply_changes(reboot=False)

    #############################################
    ##  Email Alerts
    #############################################
    @property
    def RegisteredEmailAlert(self):
        return self._sysconfig.iDRAC.EmailAlert

    def configure_email_alerts(self, alert_number=None, state=None, address=None,
                               custom_message=None):
        """
            Configure Email Alerts Settings

            :param alert_number: Alert Number
            :param state: Alert State. "Enabled" - Enabled, "Disabled" - Disabled
            :param address: Destination Email Address
            :param custom_message: Custom Message
            :type alert_number: number
            :type state: enum <Enable_EmailAlertTypes>
            :type address: str
            :type custom_message: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Email Alerts Settings
                msg = idrac.config_mgr.configure_email_alerts(alert_number = 4, state=Enable_EmailAlertTypes.Enabled,
                                                  address = "test@abc.com", custom_message = "test")
                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if alert_number is None:
            return {
                'Status': 'Failed',
                'Message': 'Alert Number is not specified.'
            }

        email_alert = self.RegisteredEmailAlert.find_or_create(index=alert_number)

        if state is not None:
            email_alert.Enable_EmailAlert.set_value(state)

        if address is not None:
            email_alert.Address_EmailAlert.set_value(address)

        if custom_message is not None:
            email_alert.CustomMsg_EmailAlert.set_value(custom_message)

            # return self.apply_changes(reboot=False)

    #############################################
    ##  End Email Alerts
    #############################################

    def configure_idrac_alerts(self, enable_alerts=None):
        """
            Configure iDRAC Alerts Settings

            :param alert_number: Enable Alerts. "Enabled" - Enabled, "Disabled" - Disabled
            :type custom_message: enum <AlertEnable_IPMILanTypes>
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure iDRAC Alerts Settings
                msg = idrac.config_mgr.configure_idrac_alerts(enable_alerts=AlertEnable_IPMILanTypes.Disabled)

                idrac.config_mgr.apply_changes()
        """
        if enable_alerts is None:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        self.SystemConfiguration.iDRAC.IPMILan.AlertEnable_IPMILan.set_value(enable_alerts)

        # return self.apply_changes(reboot=False)

    @property
    def iDRAC_NIC(self):
        return self._sysconfig.iDRAC.NIC

    @property
    def iDRAC_NICStatic(self):
        return self._sysconfig.iDRAC.NICStatic

    def configure_network_settings(self, enable_nic=None, nic_selection=None, failover_network=None, auto_detect=None,
                                   auto_negotiation=None, network_speed=None, duplex_mode=None, nic_mtu=None):
        """
            Configure Network Settings

            :param enable_nic: Enable NIC. "Enabled" - Enabled, "Disabled" - Disabled
            :param nic_selection:  NIC Selection. "Dedicated" - Dedicated, "LOM1" - LOM1, "LOM2" - LOM2, "LOM3" - LOM3, "LOM4" - LOM4
            :param failover_network: Failover Network. "ALL" : ALL, "LOM1" : LOM1, "LOM2" : LOM2, "LOM3" : LOM3, "LOM4" : LOM4, "T_None" : None
            :param auto_detect: Auto-Detect. "Enabled" - Enabled, "Disabled" - Disabled
            :param auto_negotiation: Auto-Negotiation. "Enabled" - Enabled, "Disabled" - Disabled
            :param network_speed: Network Speed. "10" - T_10, "100" - T_100, "1000" - T_1000
            :param duplex_mode: Duplex Mode. "Full" - Full, "Half" - Half
            :param nic_mtu: NIC MTU
            :type enable_nic: enum <Enable_NICTypes>
            :type nic_selection: enum <Selection_NICTypes>
            :type failover_network: enum <Failover_NICTypes>
            :type auto_detect: enum <AutoDetect_NICTypes>
            :type auto_negotiation: enum <Autoneg_NICTypes>
            :type network_speed: enum <Speed_NICTypes>
            :type duplex_mode: enum <Duplex_NICTypes>
            :type nic_mtu: number
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Network Settings
                msg = msg = msg = idrac.config_mgr.configure_network_settings(enable_nic=Enable_NICTypes.Enabled,
                                          nic_selection=Selection_NICTypes.Dedicated, failover_network=Failover_NICTypes.T_None,
                                          auto_detect=AutoDetect_NICTypes.Disabled, auto_negotiation=Autoneg_NICTypes.Enabled,
                                          network_speed=Speed_NICTypes.T_1000, duplex_mode=Duplex_NICTypes.Full, nic_mtu=1500)

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if enable_nic is not None:
            self.iDRAC_NIC.Enable_NIC.set_value(enable_nic)

        if nic_selection is not None:
            self.iDRAC_NIC.Selection_NIC.set_value(nic_selection)

        if failover_network is not None:
            self.iDRAC_NIC.Failover_NIC.set_value(failover_network)

        if auto_detect is not None:
            self.iDRAC_NIC.AutoDetect_NIC.set_value(auto_detect)

        if auto_negotiation is not None:
            self.iDRAC_NIC.Autoneg_NIC.set_value(auto_negotiation)

        if network_speed is not None:
            self.iDRAC_NIC.Speed_NIC.set_value(network_speed)

        if duplex_mode is not None:
            self.iDRAC_NIC.Duplex_NIC.set_value(duplex_mode)

        if nic_mtu is not None:
            self.iDRAC_NIC.MTU_NIC.set_value(nic_mtu)

            # return self.apply_changes(reboot=False)

    def configure_dns(self, register_idrac_on_dns=None, dns_idrac_name=None, auto_config=None, static_dns=None):
        """
            Configure DNS Settings

            :param register_idrac_on_dns: Register iDRAC on DNS. "Enabled" - Enabled, "Disabled" - Disabled
            :param dns_idrac_name: DNS iDRAC Name
            :param auto_config: Auto-Config. "Disabled" - Disabled, "Enable Once" - Enable_Once, "Enable Once After Reset" - Enable_Once_After_Reset
            :param static_dns: Static DNS
            :type register_idrac_on_dns: enum <DNSRegister_NICTypes>
            :type dns_idrac_name: str
            :type auto_config: enum <DNSDomainNameFromDHCP_NICTypes>
            :type static_dns: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure DNS Settings
                msg = idrac.config_mgr.configure_dns(register_idrac_on_dns = DNSRegister_NICTypes.Enabled,
                                            dns_idrac_name = "idrac-st123", auto_config = DNSDomainNameFromDHCP_NICTypes.Enabled,
                                            static_dns = "domain.com")

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if register_idrac_on_dns is not None:
            self.iDRAC_NIC.DNSRegister_NIC.set_value(register_idrac_on_dns)

        if dns_idrac_name is not None:
            self.iDRAC_NIC.DNSRacName_NIC.set_value(dns_idrac_name)

        if auto_config is not None:
            self.iDRAC_NICStatic.DNSDomainFromDHCP_NICStatic.set_value(auto_config)

        if static_dns is not None:
            self.iDRAC_NIC.DNSDomainName_NIC.set_value(static_dns)

            # return self.apply_changes(reboot=False)

    def configure_nic_vlan(self, vlan_enable=None, vlan_id=None, vlan_priority=None):
        """
            Configure NIC VLAN Settings

            :param vlan_enable: Enable VLAN. "Enabled" - Enabled, "Disabled" - Disabled
            :param vlan_id: VLAN ID
            :param vlan_priority: VLAN Priority
            :type vlan_enable: enum <VLanEnable_NICTypes>
            :type vlan_id: number
            :type vlan_priority: number
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure NIC VLAN Settings
                msg = idrac.config_mgr.configure_nic_vlan(vlan_enable=VLanEnable_NICTypes.Enabled,
                                              vlan_id=0, vlan_priority=1)
                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if vlan_enable is not None:
            self.iDRAC_NIC.VLanEnable_NIC.set_value(vlan_enable)

        if vlan_id is not None:
            self.iDRAC_NIC.VLanID_NIC.set_value(vlan_id)

        if vlan_priority is not None:
            self.iDRAC_NIC.VLanPriority_NIC.set_value(vlan_priority)

            # return self.apply_changes(reboot=False)

    @property
    def iDRAC_IPv4Static(self):
        return self._sysconfig.iDRAC.IPv4Static

    def configure_static_ipv4(self, ip_address=None, dns_1=None, dns_2=None, dns_from_dhcp=None, gateway=None,
                              net_mask=None):
        """
            Configure Static IPv4 Settings

            :param ip_address: IP Address
            :param dns_1: Preferred DNS Server
            :param dns_2: Alternate DNS Server
            :param dns_from_dhcp: DNS From DHCP. "Enabled" - Enabled, "Disabled" - Disabled
            :param gateway: Gateway
            :param net_mask: Subnet Mask
            :type ip_address: str
            :type dns_1: str
            :type dns_2: str
            :type dns_from_dhcp: enum <DHCPEnable_IPv4Types>
            :type gateway: str
            :type net_mask: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure Static IPv4 Settings
                msg = idrac.config_mgr.configure_static_ipv4(ip_address = "1.1.1.1", dns_1 = "0.0.0.0", dns_2 = "0.0.0.0",
                                             dns_from_dhcp = DNSFromDHCP_IPv4StaticTypes.Enabled, gateway="1.2.3.4",
                                             net_mask="255.255.255.125")

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if ip_address is not None:
            self.iDRAC_IPv4Static.Address_IPv4Static.set_value(ip_address)

        if dns_1 is not None:
            self.iDRAC_IPv4Static.DNS1_IPv4Static.set_value(dns_1)

        if dns_2 is not None:
            self.iDRAC_IPv4Static.DNS2_IPv4Static.set_value(dns_2)

        if dns_from_dhcp is not None:
            self.iDRAC_IPv4Static.DNSFromDHCP_IPv4Static.set_value(dns_from_dhcp)

        if gateway is not None:
            self.iDRAC_IPv4Static.Gateway_IPv4Static.set_value(gateway)

        if net_mask is not None:
            self.iDRAC_IPv4Static.Netmask_IPv4Static.set_value(net_mask)

            # return self.apply_changes(reboot=False)

    @property
    def iDRAC_IPv4(self):
        return self._sysconfig.iDRAC.IPv4

    def configure_ipv4(self, ip_address=None, enable_dhcp=None, dns_1=None, dns_2=None, dns_from_dhcp=None,
                       enable_ipv4=None, gateway=None, net_mask=None):
        """
            Configure IPv4 Settings

            :param ip_address: IP Address
            :param enable_dhcp: Enable DHCP. "Enabled" - Enabled, "Disabled" - Disabled
            :param dns_1: Preferred DNS Server
            :param dns_2: Alternate DNS Server
            :param dns_from_dhcp: DNS From DHCP. "Enabled" - Enabled, "Disabled" - Disabled
            :param enable_ipv4: Enable IPv4. "Enabled" - Enabled, "Disabled" - Disabled
            :param gateway: Gateway
            :param net_mask: Subnet Mask
            :type ip_address: str
            :type enable_dhcp: enum <DHCPEnable_IPv4Types>
            :type dns_1: str
            :type dns_2: str
            :type dns_from_dhcp: enum <DHCPEnable_IPv4Types>
            :type enable_ipv4: enum <Enable_IPv4Types>
            :type gateway: str
            :type net_mask: str
            :return: None
            :rtype: None


            .. code-block:: python
                :caption: Examples
                :name: Examples

                #Set liason share
                myshare = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                            mount_point='Z:\\', isFolder=False,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

                liason_share_status = idrac.config_mgr.set_liason_share(myshare)

                # Configure IPv4 Settings
                    msg = idrac.config_mgr.configure_ipv4(ip_address = "1.1.1.1", enable_dhcp = DHCPEnable_IPv4Types.Enabled,
                                          dns_1 = "0.0.0.0", dns_2 = "0.0.0.0", dns_from_dhcp = DNSFromDHCP_IPv4Types.Enabled,
                                          enable_ipv4 = Enable_IPv4Types.Enabled, gateway = "1.2.3.4", net_mask = "255.255.255.125" )

                idrac.config_mgr.apply_changes()
        """
        arg_length = len(list(filter(None, locals().values())))

        if arg_length == 0:
            return {
                'Status': 'Failed',
                'Message': 'No Configuration parameter(s) available.'
            }

        if ip_address is not None:
            self.iDRAC_IPv4.Address_IPv4.set_value(ip_address)

        if enable_dhcp is not None:
            self.iDRAC_IPv4.DHCPEnable_IPv4.set_value(enable_dhcp)

        if dns_1 is not None:
            self.iDRAC_IPv4.DNS1_IPv4.set_value(dns_1)

        if dns_2 is not None:
            self.iDRAC_IPv4.DNS2_IPv4.set_value(dns_2)

        if dns_from_dhcp is not None:
            self.iDRAC_IPv4.DNSFromDHCP_IPv4.set_value(dns_from_dhcp)

        if enable_ipv4 is not None:
            self.iDRAC_IPv4.Enable_IPv4.set_value(enable_ipv4)

        if gateway is not None:
            self.iDRAC_IPv4.Gateway_IPv4.set_value(gateway)

        if net_mask is not None:
            self.iDRAC_IPv4.Netmask_IPv4.set_value(net_mask)

            # return self.apply_changes(reboot=False)

    @property
    def iDRAC_IPv6Static(self):
        return self._sysconfig.iDRAC.IPv6Static

    @property
    def iDRAC_IPv6(self):
        return self._sysconfig.iDRAC.IPv6

    @property
    def TLSProtocol(self):
        return self._sysconfig.iDRAC.WebServer.TLSProtocol_WebServer

    @property
    def SSLEncryptionBits(self):
        return self._sysconfig.iDRAC.WebServer.SSLEncryptionBitLength_WebServer

    @property
    def RaidHelper(self):
        if not self._raid_helper:
            self._raid_helper = RAIDHelper(self.entity)
        return self._raid_helper

    # Tech Service Report Export
    def export_tsr(self, tsr_store_path, data_selector_array_in=DataSelectorArrayInEnum.HW_Data, job_wait=True):
        """
        collects the TSR i.e hardware, OS and App data, then compresses and saves the zip file to remote share path

        :param tsr_store_path: the share path where file needs to be exported
        :param data_selector_array_in: DataSelectorArrayIn to select the data. 0 - HW Data 1 - OS, App Data Without PII,
                                        2 - OSApp Data, 3 - TTY Logs
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type tsr_store_path: obj <FileOnShare (NFS and CIFS)>
        :type data_selector_array_in: enum <DataSelectorArrayInEnum>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            #Export TSR - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            tsr_file = nfs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.export_tsr(tsr_file)

            # Export TSR - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            tsr_file = cifs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.export_tsr(tsr_file)
        """
        if isinstance(tsr_store_path, LocalFile):
            return {
                "Status": "Failure",
                "Message": "Cannot perform export operation. TSR export on a a Local Share is not supported."
                           "You must use a Network Share(NFS or CIFS)."
            }

        share = tsr_store_path.format(ip=self.entity.ipaddr)
        if TypeHelper.resolve(share.remote_share_type) == TypeHelper.resolve(ShareTypeEnum.NFS):
            rjson = self.entity._export_tsr_nfs(data_selector_array_in=data_selector_array_in, share=share)
        else:
            rjson = self.entity._export_tsr(data_selector_array_in=data_selector_array_in, share=share,
                                            creds=tsr_store_path.creds)

        rjson['file'] = str(share)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    # Server Configuration Profile Import
    def scp_import(self, share_path, target=SCPTargetEnum.ALL, shutdown_type=ShutdownTypeEnum.Graceful,
                   time_to_wait=300,
                   end_host_power_state=EndHostPowerStateEnum.On, job_wait=True):
        """
        Imports the system configuration of the Lifecycle Controller from a file on local/remote share

        :param share_path: the share path where file needs to be exported
        :param target: Components to Import. Selective list of FQDDs should be given in comma separated format.
                        Default = "All"
        :param shutdown_type: Shutdown type before performing import operation. 0 - Graceful, 1 - Forced, 2 - NoReboot
        :param time_to_wait: Time to wait for host to shut down. Min. Value - 300 sec. Max value - 3600 sec.
        :param end_host_power_state:  Desired host power state after import operation. Type of state:  0 - Off, 1 - On
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type target: enum <SCPTargetEnum>
        :type shutdown_type: enum <ShutdownTypeEnum>
        :type time_to_wait: number
        :type end_host_power_state: enum <EndHostPowerStateEnum>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            # Import System Configuration Profile - NFS Share
            nfs_share = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                                    mount_point='Z:\\', isFolder=False,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            idrac.config_mgr.scp_import(nfs_share, target=SCPTargetEnum.ALL, shutdown_type=ShutdownTypeEnum.Graceful,
                time_to_wait=300, end_host_power_state=EndHostPowerStateEnum.On, job_wait=True)

            # Import System Configuration Profile - CIFS Share
            cifs_share = FileOnShare(remote="\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>\\<FILE-NAME>", isFolder=False,
                                     creds=UserCredentials(<USERNAME>, <PASSWORD>))

            idrac.config_mgr.scp_import(cifs_share, target=SCPTargetEnum.IDRAC, shutdown_type=ShutdownTypeEnum.Graceful,
                time_to_wait=300, end_host_power_state=EndHostPowerStateEnum.On, job_wait=True)

            # Import System configuration Profile - Local Share
            local_share = LocalFile(local=os.path.join("path", "to", <FILE-NAME>))
            import_scp_streaming = idrac.config_mgr.scp_import(share_path=local_share, target=[SCPTargetEnum.IDRAC, SCPTargetEnum.BIOS],
                shutdown_type=ShutdownTypeEnum.Graceful, time_to_wait=300, end_host_power_state=EndHostPowerStateEnum.On, job_wait=True)
        """
        share = share_path.format(ip=self.entity.ipaddr)
        target = ",".join(str(TypeHelper.resolve(component)) if TypeHelper.belongs_to(SCPTargetEnum, component)
                          else str(component) for component in target) if isinstance(target, list) \
            else (TypeHelper.resolve(target) if TypeHelper.belongs_to(SCPTargetEnum, target) else target)
        logger.info(self.entity.ipaddr+" : Triggering scp import")
        if self.entity.use_redfish and isinstance(share, LocalFile):
            return self.scp_import_from_local_share_redfish(file_path=share.local_full_path, target=target,
                                                            shutdown_type=shutdown_type,
                                                            time_to_wait=time_to_wait,
                                                            end_host_power_state=end_host_power_state,
                                                            job_wait=job_wait)

        if self.entity.use_redfish:
            rjson = self.entity._scp_import_redfish(share=share, creds=share_path.creds, target=target,
                                                    shutdown_type=ShutdownTypeRedfishEnum[shutdown_type.value],
                                                    time_to_wait=time_to_wait,
                                                    end_host_power_state=EndHostPowerStateRedfishEnum[
                                                        end_host_power_state.value])
            rjson['file'] = str(share)
            if job_wait and rjson['Status'] == 'Success' and 'jobid' in rjson['Data']:
                logger.info(self.entity.ipaddr + ": Tracking scp import job")
                rjson = self.entity.job_mgr.job_wait(rjson['Data']['jobid'])

            return rjson

        if isinstance(share_path, LocalFile):
            import_file = share.local_full_path
            rjson = self.entity.streaming_mgr.import_data(import_file_type=FileTypeEnum.SystemConfigXML,
                                                          import_file=import_file,
                                                          shutdown_type=shutdown_type,
                                                          target=target, time_to_wait=time_to_wait,
                                                          end_host_power_state=end_host_power_state,
                                                          job_wait=job_wait)
        else:
            rjson = self.entity._scp_import(share=share, creds=share_path.creds, target=target,
                                            shutdown_type=ShutdownTypeWsmanEnum[shutdown_type.value],
                                            time_to_wait=time_to_wait,
                                            end_host_power_state=EndHostPowerStateWsmanEnum[end_host_power_state.value])
            rjson['file'] = str(share)

            if job_wait:
                logger.info(self.entity.ipaddr+ ": Tracking scp import job")
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    def scp_import_to_local_share(self, target=SCPTargetEnum.ALL, shutdown_type=ShutdownTypeEnum.Graceful,
                                  time_to_wait=300, end_host_power_state=EndHostPowerStateEnum.On, job_wait=True):
        rjson = self.entity._scp_import_to_local_share(share_type=ShareTypeEnum.Local, target=target,
                                                       shutdown_type=ShutdownTypeWsmanEnum[shutdown_type.value],
                                                       time_to_wait=time_to_wait,
                                                       end_host_power_state=EndHostPowerStateWsmanEnum[
                                                           end_host_power_state.value])

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    # Server Configuration Profile Preview Import
    def scp_preview_import(self, share_path, target=SCPTargetEnum.ALL, job_wait=True):
        """
        Preview the results of the application of the XML template ahead of the actual application with out any reboot.

        :param share_path: the share path where file needs to be exported
        :param target: Ccomponents for ImportPreview. Default - All . Selective list of FQDD's is not supported
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type target: enum <SCPTargetEnum>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            # Import System Configuration Profile Preview - NFS Share
            nfs_share = FileOnShare(remote="<IP OR HOSTNAME>:/<NFS-SHARE-PATH>/<FILE-NAME>",
                                    mount_point='Z:\\', isFolder=False,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            idrac.config_mgr.scp_preview_import(nfs_share, target=SCPTargetEnum.ALL, job_wait=True)

            # Import System Configuration Profile Preview - CIFS Share
            cifs_share = FileOnShare(remote="\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>\\<FILE-NAME>", isFolder=False,
                                     creds=UserCredentials(<USERNAME>, <PASSWORD>))

            idrac.config_mgr.scp_preview_import(cifs_share, target=SCPTargetEnum.ALL, job_wait=True)

            # Import System configuration Profile Preview - Local Share
            local_share = LocalFile(local=os.path.join("path", "to", <FILE-NAME>))
            idrac.config_mgr.scp_preview_import(share_path=local_share, target=SCPTargetEnum.ALL, job_wait=True)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            import_file = share.local_full_path
            rjson = self.entity.streaming_mgr.import_data(import_file_type=FileTypeEnum.SystemConfigXML,
                                                          import_file=import_file, target=target, scp_preview=True,
                                                          job_wait=job_wait)
        else:
            rjson = self.entity._scp_preview_import(share=share, creds=share_path.creds, target=target)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    def scp_preview_import_to_local_share(self, target=SCPTargetEnum.ALL, job_wait=True):
        rjson = self.entity._scp_preview_import_to_local_share(share_type=ShareTypeEnum.Local, target=target)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    def scp_export(self, share_path, target=SCPTargetEnum.ALL, export_format=ExportFormatEnum.XML,
                   export_use=ExportUseEnum.Default, include_in_export=IncludeInExportEnum.Default, job_wait=True):
        """
        Exports the system configuration from the Lifecycle Controller to a file on local/remote share

        :param share_path: the share path where file needs to be exported
        :param target: the component to export. One or more FQDDs can be given in comma separated format. Default - All
        :param export_format: the file format for export <XML or JSON>
        :param export_use: the type of export intended for use. Default, Clone or Replace
        :param include_in_export: extra information to include in export: Default, Include read only,
                                  Include password hash values, Include read only and password hash values
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type target: enum <SCPTargetEnum>
        :type export_format: enum <ExportFormatEnum>
        :type export_use: enum <ExportUseEnum>
        :type include_in_export: enum <IncludeInExportEnum>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
            :name: Examples

            # Export SCP - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                            mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                            creds=UserCredentials(<USERNAME>, <PASSWORD>))

            scp_file = nfs_share.new_file(<FILE-NAME>)

            msg = idrac.config_mgr.scp_export(scp_file, target=SCPTargetEnum.ALL, export_format=ExportFormatEnum.XML,
                export_use=ExportUseEnum.Default, include_in_export=IncludeInExportEnum.Default)

            # Export SCP - NFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                         creds=UserCredentials(<USERNAME>, <PASSWORD>))

            scp_file = cifs_share.new_file(<FILE-NAME>)

            msg = idrac.config_mgr.scp_export(scp_file, target=SCPTargetEnum.BIOS, export_format=ExportFormatEnum.XML,
                export_use=ExportUseEnum.Default, include_in_export=IncludeInExportEnum.Default)

            # Export SCP - Local Share
            local_share = LocalFile(local=<PATH-TO-FILE>)

            msg = idrac.config_mgr.scp_export(share_path=local_share, target=[SCPTargetEnum.IDRAC, SCPTargetEnum.BIOS],
                export_format=ExportFormatEnum.JSON, export_use=ExportUseEnum.Clone,
                include_in_export=IncludeInExportEnum.Default)
        """
        if share_path:
            share = share_path.format(ip=self.entity.ipaddr)
        else:
            logger.error("Share path or mount point does not exist")
            raise ValueError("Share path or mount point does not exist")

        target = ",".join(
            str(TypeHelper.resolve(component)) if TypeHelper.belongs_to(SCPTargetEnum, component) else str(component)
            for component in target) if isinstance(target, list) \
            else (TypeHelper.resolve(target) if TypeHelper.belongs_to(SCPTargetEnum, target) else target)
        logger.info(self.entity.ipaddr+" : Triggering scp export")
        if self.entity.use_redfish and isinstance(share, LocalFile):
            rjson = self.scp_export_to_local_share_redfish(share.local_full_path, target=target,
                                                          export_format=export_format,
                                                          export_use=export_use,
                                                          include_in_export=include_in_export)
            if job_wait and rjson['Status'] == 'Success' and 'jobid' in rjson['Data']:
                logger.info(self.entity.ipaddr + " : Tracking scp export job")
                rjson = self.entity.job_mgr.job_wait(rjson['Data']['jobid'])
            rjson['file'] = str(share)
            return rjson

        if self.entity.use_redfish:
            rjson = self.entity._scp_export_redfish(share=share, creds=share_path.creds,
                                                    target=target,
                                                    export_format=ExportFormatRedfishEnum[export_format.value],
                                                    export_use=ExportUseRedfishEnum[export_use.value],
                                                    include_in_export=IncludeInExportRedfishEnum[
                                                        include_in_export.value])
            if job_wait and rjson['Status'] == 'Success' and 'jobid' in rjson['Data']:
                logger.info(self.entity.ipaddr + " : Tracking scp export job")
                rjson = self.entity.job_mgr.job_wait(rjson['Data']['jobid'])
            rjson['file'] = str(share)
            return rjson

        if isinstance(share, LocalFile):
            export_file = share.local_full_path

            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.SystemConfigXML,
                                                          export_file=export_file,
                                                          target=target,
                                                          export_format=export_format,
                                                          export_use=export_use,
                                                          include_in_export=include_in_export)
        else:
            rjson = self.entity._scp_export(share=share, creds=share_path.creds, target=target,
                                            export_format=ExportFormatWsmanEnum[export_format.value],
                                            export_use=ExportUseWsmanEnum[export_use.value],
                                            include_in_export=IncludeInExportWsmanEnum[include_in_export.value])

            rjson['file'] = str(share)

            if job_wait:
                logger.info(self.entity.ipaddr + " : Tracking scp export job")
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    def scp_export_to_local_share(self, target=SCPTargetEnum.ALL, export_format=ExportFormatEnum.XML,
                                  export_use=ExportUseEnum.Default, include_in_export=IncludeInExportEnum.Default,
                                  job_wait=True):
        logger.debug(self.entity.ipaddr+" : Triggering scp export to local share")
        rjson = self.entity._scp_export_to_local_share(share_type=ShareTypeEnum.Local, target=target,
                                                       export_format=ExportFormatWsmanEnum[export_format.value],
                                                       export_use=ExportUseWsmanEnum[export_use.value],
                                                       include_in_export=IncludeInExportWsmanEnum[
                                                           include_in_export.value])

        if job_wait:
            logger.info(self.entity.ipaddr + " : Tracking scp export job")
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    # Server Profile Backup/Restore
    def sp_backup(self, sp_share_path, passphrase, sp_image_name, job_wait=True):
        share = sp_share_path.format(ip=self.entity.ipaddr)
        rjson = self.entity._sp_backup(share=share, creds=sp_share_path.creds, passphrase=passphrase,
                                       image=sp_image_name)
        rjson['file'] = str(share)
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        return rjson

    def sp_restore(self, sp_share_path, passphrase, sp_image_name, job_wait=True):
        share = sp_share_path.format(ip=self.entity.ipaddr)
        rjson = self.entity._sp_restore(share=share, creds=sp_share_path.creds, passphrase=passphrase,
                                        image=sp_image_name)
        rjson['file'] = str(share)
        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['file'], rjson)
        return rjson

    # Factory Details Export
    def factory_export(self, share_path, job_wait=True):
        """
        Exports the factory configuration from the Lifecycle Controller to a file on local/remote share.

        :param share_path: the share path where file needs to be exported
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            #Export Factory Configuration - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            factory_config_file = nfs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.factory_export(factory_config_file)

            # Export Factory Configuration - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            factory_config_file = cifs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.factory_export(factory_config_file)

            # Export Factory Configuration - Local Share
            local_share = LocalFile(local=os.path.join("path", "to", <FILE-NAME>))
            idrac.config_mgr.factory_export(share_path=local_share)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.FactoryConfig, export_file=export_file)
        else:
            rjson = self.entity._factory_export(share=share, creds=share_path.creds)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    def factory_export_to_local_share(self, job_wait=True):
        rjson = self.entity._factory_export_to_local_share(share_type=ShareTypeEnum.Local)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    # Hardware Inventory Export
    def inventory_export(self, share_path, xml_schema=XMLSchemaEnum.CIM_XML, job_wait=True):
        """
        Exports the hardware inventory from the Lifecycle Controller to a file on local/remote share

        :param share_path: the share path where file needs to be exported
        :param xml_schema: The schema to be used for the Hardware Inventory XML output:  0 (CIM-XML), 1(Simple)
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type xml_schema: enum <XMLSchemaEnum>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            # Export Hardware Inventory - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            hw_inventory_file = nfs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.inventory_export(hw_inventory_file)

            # Export Hardware Inventory - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            hw_inventory_file = cifs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.inventory_export(hw_inventory_file)

            # Export Hardware Inventory - Local Share
            local_share = LocalFile(local=os.path.join("path", "to", <FILE-NAME>))
            idrac.config_mgr.inventory_export(share_path=local_share, xml_schema=XMLSchemaEnum.CIM_XML)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.Inventory, export_file=export_file,
                                                          xml_schema=xml_schema)
        else:
            rjson = self.entity._inventory_export(share=share, creds=share.creds, xml_schema=xml_schema)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    def inventory_export_to_local_share(self, xml_schema=XMLSchemaEnum.CIM_XML, job_wait=True):
        rjson = self.entity._inventory_export_to_local_share(share_type=ShareTypeEnum.Local, xml_schema=xml_schema)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    # Drive APIs
    # target is FQDD of the drive
    def blink_drive(self, target):
        rjson = self.entity._blink_drive(target)
        rjson['file'] = target
        return self._job_mgr._job_wait(rjson['file'], rjson)

    def unblink_drive(self, target):
        rjson = self.entity._unblink_drive(target)
        rjson['file'] = target
        return self._job_mgr._job_wait(rjson['file'], rjson)

    # OS Deployment APIs
    def detach_iso(self):
        rjson = self.entity._detach_iso()
        return rjson

    def detach_iso_from_vflash(self):
        rjson = self.entity._detach_iso_from_vflash()
        rjson['file'] = 'detach_iso_from_vflash'
        return rjson

    def delete_iso_from_vflash(self):
        rjson = self.entity._delete_iso_from_vflash()
        rjson['file'] = 'delete_iso_from_vflash'
        return rjson

    def boot_to_network_iso(self, network_iso_image, uefi_target, expose_duration, job_wait=True):

        if uefi_target == "":
            try:
                lcstatus = self.lc_status()
                if int(lcstatus['Data']['GetRemoteServicesAPIStatus_OUTPUT']['LCStatus']) != 0:
                    return {"Status": "Failed", "Message": "LC is not ready"}
            except:
                return {"Status": "Failed", "Message": "LC is not ready"}
            if TypeHelper.resolve(network_iso_image.remote_share_type) == TypeHelper.resolve(ShareTypeEnum.NFS):
                rjson = self.entity._boot_to_network_iso_nfs(share=network_iso_image, expose_duration=expose_duration)
            else:
                rjson = self.entity._boot_to_network_iso(share=network_iso_image,
                                                         creds=network_iso_image.creds, expose_duration=expose_duration)
            rjson['file'] = str(network_iso_image)
            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)
            return rjson
        else:
            rjson = self.configure_uefi_boot_target(target_path=uefi_target)
            return rjson

    def boot_to_disk(self):
        rjson = self.entity._boot_to_disk()
        rjson['file'] = 'boot_to_disk'
        return self._job_mgr._job_wait(rjson['file'], rjson)

    def boot_to_iso(self):
        rjson = self.entity._boot_to_iso()
        rjson['file'] = 'boot_to_iso'
        return self._job_mgr._job_wait(rjson['file'], rjson)

    def boot_to_pxe(self):
        rjson = self.entity._boot_to_pxe()
        rjson['file'] = 'boot_to_pxe'
        return self._job_mgr._job_wait(rjson['file'], rjson)

    @property
    def DriverPackInfo(self):
        return self.entity._get_driver_pack_info()

    @property
    def HostMacInfo(self):
        return self.entity._get_host_mac_info()

    def connect_network_iso(self, network_iso_image):
        rjson = self.entity._connect_network_iso(share=network_iso_image, creds=network_iso_image.creds)
        rjson['file'] = str(network_iso_image)
        return self._job_mgr._job_wait(rjson['file'], rjson)

    def download_iso(self, network_iso_image):
        rjson = self.entity._download_iso(share=network_iso_image, creds=network_iso_image.creds)
        rjson['file'] = str(network_iso_image)
        return self._job_mgr._job_wait(rjson['file'], rjson)

    def download_iso_flash(self, network_iso_image):
        share = network_iso_image.format(ip=self.entity.ipaddr)
        rjson = self.entity._download_iso_flash(share=network_iso_image, creds=network_iso_image.creds)
        rjson['file'] = str(network_iso_image)
        return self._job_mgr._job_wait(rjson['file'], rjson)

    def disconnect_network_iso(self):
        return self.entity._disconnect_network_iso()

    def detach_drivers(self):
        return self.entity._detach_drivers()

    def clear_transfer_session(self, file_operation, file_type):
        """
        This method is used to restart any transfer sessions by deleting intermediate files based on the file type and file operation

        :param file_operation: the file operation <Import/Export> for which delete file/folder has to be performed
        :param file_type: the file type for which delete file/folder has to be performed
        :type file_operation: enum <FileOperationEnum>
        :type file_type: enum <FileTypeEnum>
        :return: success/failure Response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
            :name: Examples

            idrac.config_mgr.clear_transfer_session(file_operation=FileOperationEnum.Export,
                                                    file_type=FileTypeEnum.SystemConfigXML)

        """
        return self.entity._clear_transfer_session(file_operation=file_operation, file_type=file_type)

    def export_data(self, file_type, in_session_id, in_chunk_size, file_offset, tx_data_size,
                    payload_encoding=PayLoadEncodingEnum.Base64):
        return self.entity._export_data(file_type=file_type, in_session_id=in_session_id, in_chunk_size=in_chunk_size,
                                        file_offset=file_offset, tx_data_size=tx_data_size,
                                        payload_encoding=payload_encoding)

    def import_data(self, file_type, in_session_id, chunk_size, file_size, txfr_descriptor, crc, payload,
                    payload_encoding=PayLoadEncodingEnum.Base64):
        return self.entity._import_data(file_type=file_type, in_session_id=in_session_id, chunk_size=chunk_size,
                                        file_size=file_size, txfr_descriptor=txfr_descriptor, payload=payload,
                                        crc=crc, payload_encoding=payload_encoding)

    # Export PSA Diagnostics
    def epsa_diagnostics_export(self, share_path, job_wait=True):
        """
        Exports the result file of the last completed diagnostics to a file on local/remote share

        :param share_path: the share path where file needs to be exported
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

            #Export Diagnostics Report - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            diagnostic_report_file = nfs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.epsa_diagnostics_export(diagnostic_report_file)

            # Export Diagnostics Report - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            diagnostic_report_file = cifs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.epsa_diagnostics_export(diagnostic_report_file)

            # Export Diagnostics Report - Local Share
            local_share = LocalFile(local=os.path.join("path", "to", <FILE-NAME>))
            idrac.config_mgr.epsa_diagnostics_export(share_path=local_share)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.Diagnostics, export_file=export_file)
        else:
            rjson = self.entity._epsa_diagnostics_export(share=share, creds=share_path.creds)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson;

    def epsa_diagnostics_export_to_local_share(self, job_wait=True):
        rjson = self.entity._epsa_diagnostics_export_to_local_share(share_type=ShareTypeEnum.Local)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    # Support Assist Collection
    def support_assist_collection(self, share_path, data_selector_array_in=DataSelectorArrayInEnum.HW_Data,
                                  filter=SupportAssistCollectionFilterEnum.No,
                                  transmit=SupportAssistCollectionTransmitEnum.No,
                                  job_wait=True):
        """
        Triggers a SupportAssist collection and optionally send the collection to a file on local/remote share

        :param share_path: the share path where file needs to be exported
        :param data_selector_array_in: DataSelectorArrayIn to select the data", 0 - HW Data, 1 - OSApp Data,
                                        2 - TTY Logs, 3 - Debug Logs
        :param filter: Filter the collection for PII. 0 - No, 1- Yes
        :param transmit: Transmit the collection to Dell: 0 - No, 1 - Yes
        :param job_wait: the flag to wait for job completion. False will return the Job ID
        :type share_path: obj <FileOnShare (NFS and CIFS) or LocalFile(Local Share)>
        :type data_selector_array_in: enum <DataSelectorArrayInEnum>
        :type filter: enum <SupportAssistCollectionFilterEnum>
        :type transmit: enum <SupportAssistCollectionTransmitEnum>
        :type job_wait: bool
        :return: success/failure response
        :rtype: JSON


        .. code-block:: python
            :caption: Examples
			:name: Examples

			#Support Assist Collection - NFS Share
            nfs_share = FileOnShare(remote=<IP OR HOSTNAME>:/<NFS-SHARE-PATH>,
                                    mount_point=<MOUNT-DRIVE>:\\>, isFolder=<True/False>,
                                    creds=UserCredentials(<USERNAME>, <PASSWORD>))

            support_assist_collection = nfs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.support_assist_collection(support_assist_collection)

            # Support Assist Collection - CIFS Share
            cifs_share = FileOnShare(remote=\\\\<IP OR HOSTNAME>\\<CIFS-SHARE-PATH>, isFolder=<True/False>,
                                 creds=UserCredentials(<USERNAME>, <PASSWORD>))

            support_assist_collection = cifs_share.new_file(<FILE-NAME>)

            idrac.config_mgr.support_assist_collection(support_assist_collection)

            # Support Assist Collection - Local Share
            local_share = LocalFile(local=os.path.join("path", "to", <FILE-NAME>))
            idrac.config_mgr.support_assist_collection(share_path=local_share)
        """
        share = share_path.format(ip=self.entity.ipaddr)

        if isinstance(share_path, LocalFile):
            export_file = share.local_full_path
            rjson = self.entity.streaming_mgr.export_data(file_type=FileTypeEnum.TSR, export_file=export_file,
                                                          data_selector_array_in=data_selector_array_in,
                                                          filter=filter, transmit=transmit)
        else:
            rjson = self.entity._support_assist_collection(share=share, creds=share_path.creds,
                                                           data_selector_array_in=data_selector_array_in,
                                                           filter=filter, transmit=transmit)

            rjson['file'] = str(share)

            if job_wait:
                rjson = self._job_mgr._job_wait(rjson['file'], rjson)

        return rjson

    def support_assist_collection_to_local_share(self, data_selector_array_in=DataSelectorArrayInEnum.HW_Data,
                                                 filter=SupportAssistCollectionFilterEnum.No,
                                                 transmit=SupportAssistCollectionTransmitEnum.No, job_wait=True):
        rjson = self.entity._support_assist_collection_to_local_share(share_type=ShareTypeEnum.Local,
                                                                      data_selector_array_in=data_selector_array_in,
                                                                      filter=filter, transmit=transmit)

        if job_wait:
            rjson = self._job_mgr._job_wait(rjson['Message'], rjson)

        return rjson

    def list_fw_inventory(self):
        rjson = self.entity._list_fw_inventory_redfish()
        return rjson

    def apply_attribute(self, target, attribute_name, attribute_value):
        return self.entity._apply_attribute(target=target, attribute_name=attribute_name,
                                            attribute_value=attribute_value)

    def configure_uefi_boot_target(self, target_path):
        ''' Set the target uefi path

        :param target_path: path to uefi device
        :param target_path: str
        :return: json message returned
        '''
        attrval = {"BootSourceOverrideTarget": "UefiTarget"}
        rjson = self.entity._configure_attributes_redfish(rpath="/Systems/System.Embedded.1", parent_attr="Boot",
                                                          attr_val=attrval)
        uefitarget = {"UefiTargetBootSourceOverride": target_path}
        rjsontargetboot = self.entity._configure_attributes_redfish(rpath="/Systems/System.Embedded.1",
                                                                    parent_attr="Boot", attr_val=uefitarget)
        if 'Data' in rjsontargetboot and 'StatusCode' in rjsontargetboot['Data'] and rjsontargetboot['Data'][
            'StatusCode'] == 200:
            rjsontargetboot['Status'] = 'Success'
        else:
            rjsontargetboot['Status'] = 'Failed'
            return rjsontargetboot
        next_ruri = rjsontargetboot['Data']['next_ruri']
        tokens = next_ruri.split("/")
        job_id = ''
        if tokens and tokens.__len__() > 0:
            job_id = tokens[-1]
        self.reboot_system()
        if job_id:
            rjosn = self.entity.job_mgr.job_wait(job_id)
            return rjosn
        return rjsontargetboot

    def scp_export_to_local_share_redfish(self, file_path, target=SCPTargetEnum.ALL,
                                          export_format=ExportFormatEnum.XML,
                                          export_use=ExportUseEnum.Default,
                                          include_in_export=IncludeInExportEnum.Default):
        try:
            logger.debug(self.entity.ipaddr+" : Triggering scp export from local share.")
            rjson = self.entity._scp_export_to_local_share_redfish(target=target, export_format=ExportFormatRedfishEnum[
                export_format.value],
                                                                   export_use=ExportUseRedfishEnum[export_use.value],
                                                                   include_in_export=IncludeInExportRedfishEnum[
                                                                       include_in_export.value])
            if rjson and rjson['Status'] == 'Success' and 'Data' in rjson and 'next_ruri' in rjson['Data']:
                task_uri = rjson['Data']['next_ruri']
            else:
                return rjson
        except:
            logger.error(self.entity.ipaddr+" : Exception while executing scp export to local share")
            return {'Status': 'Failed', 'Message': 'Unable to export scp, exception occurred'}

        # task_uri = "/redfish/v1/TaskService/Tasks/JID_133688612609"
        count = 0
        while True:
            try:
                time.sleep(10)
                scp_stream = self.entity._get_resource_redfish(resource_uri=task_uri)

                if 'body' in scp_stream['Data']:
                    scp_xml_string = scp_stream['Data']['body']

                    if (export_format is ExportFormatEnum.XML and "<SystemConfiguration Model" in str(scp_xml_string)) \
                            or (export_format is ExportFormatEnum.JSON and "SystemConfiguration" in scp_xml_string):
                        break
                elif count >= 20:
                    return {'Status': 'Failed', 'Message': 'Unable to get Export content, timed out'}
                count = count + 1
            except Exception as exp:
                logger.error(self.entity.ipaddr+" : Exception while exporting scp : {}".format(str(exp)))
                return {'Status': 'Failed', 'Message': 'Unable to perform Export'}
        try:
            if scp_xml_string:
                f = open(file_path, "w")
                f.write(scp_xml_string if export_format is ExportFormatEnum.XML
                        else json.dumps(scp_xml_string, indent=4))
        except:
            logger.error(self.entity.ipaddr+" : Failed to write exported content to local file")
            return {'Status': 'Failed', 'Message': 'Unable to write exported content to local file'}

        return rjson

    def _get_xml_string_fromlocalscp(self, file_path):
        try:
            f = open(file_path, "r")
            xml_string = f.read()
            f.close()
            return xml_string
        except:
            return None

    def scp_import_from_local_share_redfish(self, file_path, target=SCPTargetEnum.ALL,
                                            shutdown_type=ShutdownTypeEnum.Graceful,
                                            time_to_wait=300, end_host_power_state=EndHostPowerStateEnum.On,
                                            job_wait=True):
        xml_string = self._get_xml_string_fromlocalscp(file_path)
        if not xml_string:
            return {'Status': 'Failed', 'Message': 'Failed to get xml string'}
        rjson = self.entity._scp_import_from_local_share_redfish(target=target, import_string=xml_string,
                                                                 shutdown_type=ShutdownTypeRedfishEnum[
                                                                     shutdown_type.value],
                                                                 time_to_wait=time_to_wait,
                                                                 end_host_power_state=EndHostPowerStateRedfishEnum[
                                                                     end_host_power_state.value])
        rjson['file'] = str(file_path)

        if job_wait and rjson['Status'] == 'Success' and 'jobid' in rjson['Data']:
            logger.info(self.entity.ipaddr + " : Tracking scp import job")
            rjson = self.entity.job_mgr.job_wait(rjson['Data']['jobid'])
        return rjson

    def reboot_system(self):
        redfish_action_json = self.entity._get_acton_redfish()
        reset_allowable_values = self.entity._get_field_from_action(redfish_action_json, 'Data', 'body', 'Actions', '#ComputerSystem.Reset', 'ResetType@Redfish.AllowableValues')
        if reset_allowable_values and "GracefulRestart" in reset_allowable_values:
            reboot_type = "GracefulRestart"
        else:
            reboot_type = "ForceRestart"
        rjson = self.entity._reboot_system_redfish(reboot_type=reboot_type)
        return rjson

    def is_change_applicable(self):
        """when check_mode is enabled ,checks if changes are applicable or not"""
        try:
            logger.info(self.entity.ipaddr + " : Interface is_change_applicable enter")
            if self._sysconfig and not self._sysconfig.is_changed():
                msg = {'Status': 'Success', 'Message': 'No changes found to commit!', 'changes_applicable': False}
            else:
                msg = {'Status': 'Success', 'Message': 'Changes found to commit!', 'changes_applicable': True}
        except Exception as e:
            logger.error(self.entity.ipaddr + " : Interface is_change_applicable failed to execute")
            msg = {'Status': 'Failed', 'Message': 'Failed to execute the command!', 'changes_applicable': False}
        logger.info(self.entity.ipaddr + " : Interface is_change_applicable exit")
        return msg

    def configure_bios(self, bios_attr_val=None):
        """ set the bios attributes in the systemconfig object for apply

        :param bios_attr_val: attributes and corresponding values as dictionary
        :param bios_attr_val: dict
        :return: status
        """
        try:
            logger.debug(self.entity.ipaddr + " : setting bios attributes.")
            self._get_and_set_scp_attr_object({"BIOS": bios_attr_val}, self._sysconfig)
        except AttributeError as attr_err:
            logger.error(self.entity.ipaddr + " : " + attr_err.args[0])
            msg = {'Status': 'Failed', 'Message': attr_err.args[0]}
            return msg
        except:
            logger.error(self.entity.ipaddr + " : Exception occurred while setting attributes.")
            msg = {'Status': 'Failed', 'Message': 'Failed to set attributes'}
            return msg
        logger.info(self.entity.ipaddr + " : successfully set attributes.")
        return {'Status': 'Success', 'Message': 'Succeessfully set attributes'}

    def _get_and_set_scp_attr_object(self, attr_val, obj):

        for key in attr_val:
            try:
                logger.debug(self.entity.ipaddr + " : getting object for : " + str(key))
                newobj = getattr(obj, key)
                logger.debug(self.entity.ipaddr + " : got the attribute object")
            except AttributeError as attr_err:
                logger.error(self.entity.ipaddr + " : " + attr_err.args[0])
                raise

            if not isinstance(attr_val[key], dict):
                logger.debug(
                    self.entity.ipaddr + " : setting value for attribute : " + str(key) + " : value : " + attr_val[key])
                try:
                    newobj.set_value(attr_val[key])
                except:
                    logger.error(self.entity.ipaddr + " : Failed to set value for attribute " + str(key))
                    raise AttributeError("Failed to set value for attribute " + str(key))
            else:
                logger.debug(self.entity.ipaddr + " : calling method recursively as key is of dict type.")
                self._get_and_set_scp_attr_object(attr_val[key], newobj)

        return

    def _get_curr_boot_seq(self):
        try:
            response = self.entity._get_resource_redfish(resource_uri="/redfish/v1/Systems/System.Embedded.1/Bios")
            if response and response['Status'] == 'Success':
                curr_boot_mode = response['Data']['body']['Attributes']['BootMode']
            else:
                raise Exception("Failed to get  BootMode.")

            logger.info(self.entity.ipaddr + " : BootMode is : "+curr_boot_mode)
            if curr_boot_mode == "Uefi":
                return "UefiBootSeq"

            return "BootSeq"
        except KeyError as keyerror:
            logger.error(self.entity.ipaddr+" : Keyerror:"+str(keyerror.args[0]))
            raise KeyError("Failed to get :"+str(keyerror.args[0])+" from response. ")
        except:
            raise

    def _get_boot_sources(self):
        try:
            response = self.entity._get_resource_redfish(
                resource_uri="/redfish/v1/Systems/System.Embedded.1/BootSources")
            if response and response['Status'] == 'Success':
                boot_sources = response['Data']['body']['Attributes']
            else:
                raise Exception("Failed to get  BootSources.")

            return boot_sources
        except KeyError as keyerror:
            logger.error(self.entity.ipaddr + " : Keyerror:" + str(keyerror.args[0]))
            raise KeyError("Failed to get :" + str(keyerror.args[0]) + " from response. ")
        except:
            raise

    def _get_boot_sources_setting_payload(self, input_boot_devices, boot_devices, boot_seq):
        payload_device_list = []
        index_modified = False
        enable_modified = False
        partial_input = False
        if len(input_boot_devices) == 0:
            return {'Payload' : None, 'Modified' : False}
        for input_boot_device in input_boot_devices:
            device_exists = False
            for boot_device in boot_devices:
                if boot_device['Name'] == input_boot_device['Name']:
                    device_exists = True
                    payload_device = {}
                    payload_device['Name'] = boot_device['Name']
                    payload_device['Id'] = boot_device['Id']
                    if 'Enabled' in input_boot_device  and boot_device['Enabled'] != input_boot_device['Enabled']:
                        payload_device['Enabled'] = input_boot_device['Enabled']
                        enable_modified = True
                    else:
                        payload_device['Enabled'] = boot_device['Enabled']

                    if 'Index' in input_boot_device and boot_device['Index'] != input_boot_device['Index']:
                        payload_device['Index'] = input_boot_device['Index']
                        index_modified = True
                    else:
                        payload_device['Index'] = boot_device['Index']
                        if boot_device['Index'] > (len(input_boot_devices)-1):
                            partial_input = True
                    payload_device_list.append(payload_device)
                    break
            if not device_exists:
                logger.error(self.entity.ipaddr + " : Boot Device with name : " + str(
                    input_boot_device['Name']) + "does not exists")
                raise KeyError('Boot Device with name : ' + str(input_boot_device['Name']) + ' does not exists')
        if not enable_modified and not index_modified:
            return {'Payload' : None, 'Modified' : False}
        if partial_input and not index_modified:
            remaining_device_list = []
            for boot_device in boot_devices:
                flag = False
                for payload_device in payload_device_list:
                    if boot_device['Name'] == payload_device['Name']:
                        flag = True
                        break
                if not flag:
                    remaining_device_list.append(boot_device)
            if len(remaining_device_list) > 0:
                payload_device_list.extend(remaining_device_list)
        return {'Payload' : {boot_seq:payload_device_list}, 'Modified' : True}

    def _prepare_boot_sources_paylaoad(self, input_boot_devices):
        curr_boot_seq = self._get_curr_boot_seq()
        boot_sources = self._get_boot_sources()
        boot_devices = boot_sources[curr_boot_seq]
        boot_source_payload = self._get_boot_sources_setting_payload(input_boot_devices, boot_devices, curr_boot_seq)
        return boot_source_payload

    def configure_boot_sources(self, input_boot_devices):
        if not input_boot_devices or len(input_boot_devices) == 0:
            msg = {'Status': 'Failed', 'Message': 'Invalid input, nothing to be done.'}
            return msg
        try:
            payload = self._prepare_boot_sources_paylaoad(input_boot_devices)
            if not payload['Modified']:
                return {'Status': 'Success', 'Message': 'No changes found to apply.'}
            boot_source_payload = payload['Payload']
            logger.info(self.entity.ipaddr+": boot_source payload:"+str(boot_source_payload))
        except Exception as exception:
            logger.error(self.entity.ipaddr+" : Failed to get payload : "+str(exception.args[0]))
            msg = {'Status': 'Failed', 'Message': str(exception.args[0])}
            return msg


        config_attr_response = self.entity._configure_attributes_redfish(
            rpath="/Systems/System.Embedded.1/BootSources/Settings",
            parent_attr="Attributes",
            attr_val=boot_source_payload)
        if config_attr_response['Status']!='Success':
            logger.error(self.entity.ipaddr + " : Failed to set Boot Sources")
            msg = {'Status': 'Failed', 'Message': config_attr_response['error']['error']['@Message.ExtendedInfo'][0]['Message']}
            return msg

        bios_config_job_response = self.entity._create_bios_config_job_redfish(
            target_uri="/redfish/v1/Systems/System.Embedded.1/Bios/Settings")
        if bios_config_job_response['Status']!='Success':
            logger.error(self.entity.ipaddr + " : Failed to set Boot Sources")
            msg = {'Status': 'Failed', 'Message': bios_config_job_response['error']['error']['@Message.ExtendedInfo'][0]['Message']}
            return msg

        job_id = bios_config_job_response['Job']['JobId']
        job_status = self._job_mgr.get_job_status_redfish(job_id)
        if job_status['JobState'] == 'Scheduled':
            logger.info(
                self.entity.ipaddr + " : bios config job with job id : " + str(job_id) + " successfully scheduled")
        else:
            logger.info(self.entity.ipaddr + " : bios config job with job id : " + str(
                job_id) + " is not scheduled, current state is " + str(job_status['JobState']))

        reboot_status = self.reboot_system()
        if reboot_status['Status'] == 'Success':
           logger.info(self.entity.ipaddr + ": reboot triggered")
           time.sleep(100)
        else:
            logger.error(self.entity.ipaddr + ": failed to trigger reboot.")
            return {'Status': 'Failed', 'Message':'Failed to trigger reboot. Please reboot the system to apply changes.'}

        job_response = self.entity.job_mgr.job_wait(job_id)
        return job_response

    def is_bootsources_modified(self, input_boot_devices):
        """
        when check_mode is enabled ,checks if boot sources settings are modified or not.
        :param input_boot_devices:
        :return:
        """
        try:
            logger.info("{} : checking if boot sources settings changed.".format(self.entity.ipaddr))
            curr_boot_seq = self._get_curr_boot_seq()
            logger.info("{} : current boot sequence: {}".format(self.entity.ipaddr, curr_boot_seq))
            boot_sources = self._get_boot_sources()
            boot_devices = boot_sources[curr_boot_seq]
            logger.debug("{} : current boot sources settings : {}.".format(self.entity.ipaddr, boot_devices))
            is_modified = False
            for input_boot_device in input_boot_devices:
                device_exists = False
                for boot_device in boot_devices:
                    if boot_device['Name'] == input_boot_device['Name']:
                        device_exists = True
                        if boot_device['Index'] != input_boot_device['Index']:
                            is_modified = True
                        if boot_device['Enabled'] != input_boot_device['Enabled']:
                            is_modified = True
                        break
                if not device_exists:
                    logger.error(self.entity.ipaddr + " : Boot Device with name : " + str(
                        input_boot_device['Name']) + "does not exists")
                    raise KeyError('Boot Device with name : ' + str(input_boot_device['Name']) + ' does not exists')
            if is_modified:
                msg = {'Status': 'Success', 'Message': 'Changes found to commit!', 'changes_applicable': True}
            else:
                msg = {'Status': 'Success', 'Message': 'No changes found to commit!', 'changes_applicable': False}
        except KeyError as kerror:
            logger.error("{} : method is_bootsources_modified failed to execute. error : {}".format(self.entity.ipaddr,
                                                                                                    kerror.args[0]))
            msg = {'Status': 'Failed', 'Message': 'error : {}.'.format(kerror.args[0]), 'changes_applicable': False}
        except Exception as ex:
            logger.error("{} : method is_bootsources_modified failed to execute.".format(self.entity.ipaddr))
            msg = {'Status': 'Failed', 'Message': 'Failed to execute the command!', 'changes_applicable': False}
        logger.info("{} : exiting is_bootsources_modified method.".format(self.entity.ipaddr))
        return msg
