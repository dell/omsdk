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
# Authors: Jagadeesh N V
#

import sys
import ipaddress

from omsdk.sdkproto import PREDFISH, ProtocolEnum,ProtocolOptionsFactory
from omsdk.sdkdevice import iDeviceDiscovery, iDeviceRegistry, iDeviceDriver
from omsdk.sdkdevice import iDeviceTopologyInfo
from omsdk.sdkcenum import EnumWrapper,TypeHelper
from omsdk.http.sdkredfishbase import RedfishOptions

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

NGMTypesMap = {
    'BladeSlot': 2000,
    'StorageModule': 2000,
    'ComputeModule' : 2000
}
NGMTypes = EnumWrapper('Type', NGMTypesMap).enum_type

NGMDeviceTypesMap = {
    'IOModule': 8000,
    'ComputeModule': 1000,
    'StorageModule': 3000,
    'BladeSlot' : 1000
}
NGMDeviceTypes = EnumWrapper('DeviceType', NGMDeviceTypesMap).enum_type

NGMCompEnum = EnumWrapper('NGMCompEnum', {
    "System" : "System",
    "ComputeModule" : "ComputeModule",
    "PowerSupply" : "PowerSupply",
    "Fan" : "Fan",
    "Subsystem" : "Subsystem",
    "BladeSlot" : "BladeSlot",
    "CMC" : "CMC",
    "IOModule" : "IOModule",
    "PerformanceMetrics" : "PerformanceMetrics",
    "StorageModule" : "StorageModule",
    "Slots_Summary" : "Slots_Summary",
    "TemperatureSensors": "TemperatureSensors"
}).enum_type

NGMMiscEnum = EnumWrapper("NGMMiscEnum", {
    "Network" : "Network",
    "Devices" : "Devices",
    "IOMDevice": "IOMDevice",
    "ComputeDevice": "ComputeDevice"
}).enum_type

NGMMetricsEnum = EnumWrapper("NGMMetricsEnum", {
    "PowerConsumption": "PowerConsumption",
    "TemperatureMetrics": "TemperatureMetrics",
    "PowerUsageByDevice": "PowerUsageByDevice"
    }).enum_type

NGMComponentTree = {
    NGMCompEnum.System : {
        NGMCompEnum.PowerSupply,
        NGMCompEnum.Fan,
        NGMCompEnum.BladeSlot,
        NGMCompEnum.CMC,
        NGMCompEnum.ComputeModule,
        NGMCompEnum.StorageModule,
        NGMCompEnum.Slots_Summary,
        NGMCompEnum.TemperatureSensors,
        "IOModule"
    },
    "IOModule" : {
        NGMCompEnum.IOModule
    }
}

NGMRestCmds = {}

NGMClassifier = [ NGMCompEnum.System, NGMMiscEnum.Devices, NGMCompEnum.Subsystem ]

def get_inventory_url(id, comp):
    url_created = "/api/DeviceService/Devices({})/InventoryDetails('{}')".format(id,comp)
    return url_created

def get_system_url(id, comp):
    url_created = "/api/DeviceService/Devices({})/{}".format(id,comp)
    return url_created

def get_network_url(id, comp):
    url_created = "/api/DeviceService/Devices({})/Settings('{}')".format(id,comp)
    return url_created

def filter_func(xcomp, ipaddr, list_param):
    flist = []
    addr = list_param[0]
    for sys in xcomp:
        for xaddr in sys[addr]:
            if ':' in ipaddr and ':' in xaddr:
                if PY2:
                    ipaddr = unicode(ipaddr, "utf-8")
                if (ipaddress.ip_address(ipaddr).exploded) in (ipaddress.ip_address(xaddr).exploded):
                    flist.append(sys)
            elif ipaddr in xaddr:
                flist.append(sys)
    return flist

def device_filter(xcomp, ipaddr, list_param):
    flist = []
    devtype = list_param[0]
    attr = list_param[1]
    for devdict in xcomp:
        if devdict.get(attr,0) == devtype:
            flist.append(devdict)
    return flist

NGMRestViews = {
    NGMCompEnum.System: {'url' : '/api/ManagementDomainService/Domains',
                          'attribute' : 'value',
                          'filter' : filter_func,
                          'filter_param' : ['PublicAddress']},
    NGMMiscEnum.ComputeDevice: {'url' : '/api/DeviceService/Devices',
                          'attribute' : 'value',
                          'filter' : device_filter,
                          'filter_param' : [1000,'Type']},
    # NGMMiscEnum.Devices: {'url' : '/api/DeviceService/Devices',
    #                       'attribute' : 'value',
    #                       'filter' : device_filter,
    #                       'filter_param' : [2000,'Type']},
    # NGMMiscEnum.Devices: ["DeviceService/Devices", "value"],#There is difference between this call and Above one as Some extra attributes like Expressservicecode is not fetched in the above
    NGMCompEnum.PowerSupply: {'comp' : 'chassisPowerSupplies',
                              'device' : 'System',
                              'key' : 'DeviceId',
                              'gen_func' : get_inventory_url,
                              # 'condition' : ('Type', 2000),
                              'attribute' : 'InventoryInfo'},
    NGMCompEnum.Fan: {'comp' : 'chassisFansList',
                              'device' : 'System',
                              'key' : 'DeviceId',
                              'gen_func' : get_inventory_url,
                              # 'condition' : ('Type', 2000),
                              'attribute' : 'InventoryInfo'},
    NGMCompEnum.TemperatureSensors: {'comp': 'chassisTemperatureList',
                                     'device': 'System',
                                     'key': 'DeviceId',
                                     'gen_func': get_inventory_url,
                                     'attribute': 'InventoryInfo'},
    NGMCompEnum.Subsystem: {'comp' : 'SubSystemHealth',
                              'device' : 'System',
                              'key' : 'DeviceId',
                              'gen_func' : get_system_url,
                              # 'condition' : ('Type', 2000),
                              'attribute' : 'value'},
    NGMCompEnum.BladeSlot: {'comp': 'chassisSlotsList',
                              'device': 'System',
                              'key': 'DeviceId',
                              'gen_func': get_inventory_url,
                              # 'condition': ('Type', 2000),
                              'attribute': 'InventoryInfo'},
    NGMCompEnum.CMC: {'comp': 'chassisControllerList',
                              'device': 'System',
                              'key': 'DeviceId',
                              'gen_func': get_inventory_url,
                              # 'condition': ('Type', 2000),
                              'attribute': 'InventoryInfo'},
    NGMMiscEnum.Network: {'comp': 'Network',
                              'device': 'System',
                              'key': 'DeviceId',
                              'gen_func': get_network_url,
                              # 'condition': ('Type', 4000)
                          },
    NGMMetricsEnum.TemperatureMetrics: {'comp': 'Temperature',
                              'device': 'System',
                              'key': 'DeviceId',
                              'gen_func': get_system_url,
                              # 'condition': ('Type', 2000)
                            },
    NGMMetricsEnum.PowerConsumption: {'comp': 'Power',
                              'device': 'System',
                              'key': 'DeviceId',
                              'gen_func': get_system_url,
                              # 'condition': ('Type', 2000)
                            },
    NGMMetricsEnum.PowerUsageByDevice: {'comp': 'PowerUsageByDevice',
                               'device': 'System',
                               'key': 'DeviceId',
                               'gen_func': get_system_url,
                               # 'condition': ('Type', 2000),
                               'attribute': 'value'
                            },
    NGMCompEnum.StorageModule: {'comp': 'chassisSlotsList',
                            'device': 'System',
                            'key': 'DeviceId',
                            'gen_func': get_inventory_url,
                            # 'condition': ('Type', 2000),
                            'attribute': 'InventoryInfo'},
    NGMCompEnum.IOModule: {'comp': 'chassisSlotsList',
                      'device': 'System',
                      'key': 'DeviceId',
                      'gen_func': get_inventory_url,
                      'attribute': 'InventoryInfo'
                      },
    NGMMiscEnum.IOMDevice: ["DeviceService/Devices", "value"],
    NGMCompEnum.ComputeModule: {'comp': 'chassisSlotsList',
                      'device': 'System',
                      'key': 'DeviceId',
                      'gen_func': get_inventory_url,
                      'attribute': 'InventoryInfo'
                      }
}

NGMRestViews_FieldSpec = {
    NGMMiscEnum.Devices : {
        "Status" : { 'Rename' : 'PrimaryStatus',
                     'Lookup': 'True',
                     'Values': {
                         1000: "Healthy",
                         2000: "Unknown",
                         3000: "Warning",
                         4000: "Critical",
                         5000: "Unknown"
                     }
                },
        "PowerState": {'Lookup': 'True',
                         'Values': {
                             1  : "Unknown",
                             17 : "On",
                             18 : "Off",
                             20 : "Powering On",
                             21 : "Powering Off"
                         }
        },
        "DeviceServiceTag" : {'Rename' : "ServiceTag"},
        "DeviceSpecificData" : {'Create' : {
            'ExpressServiceCode' : {'_Attribute' : 'expressservicecode'},
            'Location' : {'_Attribute' : 'location'}
            }
        },
        "DeviceName" : {'Rename' : 'PhysicalLocationChassisName'},
        "DeviceManagement": {
            'CreateNew': {
                'IPAddresses': {'_Attribute': ['NetworkAddress']},
                'MacAddress': {'_Attribute': ['MacAddress']},
                'URLs': {"_Attribute": ["ManagementProfile", "ManagementURL"]}
            }
        }
    },
    NGMCompEnum.ComputeModule : {
        "HealthStatus" : { 'Rename' : 'PrimaryStatus',
                     'Lookup': 'True',
                     'Values': {
                         1000: "Healthy",
                         2000: "Unknown",
                         3000: "Warning",
                         4000: "Critical",
                         5000: "Unknown"
                     }
                },
        "PowerState": {'Lookup': 'True',
                         'Values': {
                             1  : "Unknown",
                             17 : "On",
                             18 : "Off",
                             20 : "Powering On",
                             21 : "Powering Off"
                         }
        },
        "DeviceManagement" : {'Create' : {
            'IPAddress' : {'_Attribute' : 'NetworkAddress'},
            'URL' : {'_Attribute' : {'ManagementProfile':'ManagementURL'}}
            }
        },
        "DeviceServiceTag": {"Rename": "ServiceTag"},
        "SlotConfiguration": {'Create' : {
            'SlotName' : {'_Attribute' : 'SlotName'},
            'MasterSlotNumber' : {'_Attribute' : 'SlotNumber'},
            'SlotNumber' : {'_Attribute' : 'SlotNumber'}
            }
        }
    },
    NGMMiscEnum.ComputeDevice : {
        "DeviceManagement" : {'Create' : {
                                            'IPAddress' : {'_Attribute' : 'NetworkAddress'},
                                            'URL' : {'_Attribute' : {'ManagementProfile':'ManagementURL'}}
                                        }
        },
        "DeviceServiceTag": {"Rename": "ServiceTag"},
		"SlotConfiguration": {'Create' : {
                                            'SlotName' : {'_Attribute' : 'SlotName'},
                                            'MasterSlotNumber' : {'_Attribute' : 'SlotNumber'},
                                            'SlotNumber' : {'_Attribute' : 'SlotNumber'}
                                        }
							}
    },
    NGMCompEnum.Subsystem : {
        "RollupStatus" : { 'Rename' : 'PrimaryStatus',
                     'Lookup': 'True',
                     'Values': {
                         "1000": "Healthy",
                         "2000": "Unknown",
                         "3000": "Warning",
                         "4000": "Critical",
                         "5000": "Unknown"
                     }
                },
        "SubSystem": {
            'Lookup': 'True',
            'Values': {
                "MM": "CMC"
            }
        }
    },
    NGMCompEnum.PowerSupply : {
        "HealthState" : { 'Rename' : 'PrimaryStatus',
                     'Lookup': 'True',
                     'Values': {
                         1000: "Healthy",
                         2000: "Unknown",
                         3000: "Warning",
                         4000: "Critical",
                         5000: "Unknown"
                     }
        },
        "PowerStatus": {'Lookup': 'True',
                         'Values': {
                             "1"  : "Unknown",
                             "17" : "On",
                             "18" : "Off",
                             "20" : "Powering On",
                             "21" : "Powering Off"
                       }
        },
        "CapacityWatts": {'Rename' : 'TotalOutputPower', 'UnitScale': '0', 'UnitAppend': 'Watts'}
    },
    NGMCompEnum.Fan : {
        "Status" : { 'Rename' : 'PrimaryStatus',
                     'Lookup': 'True',
                     'Values': {
                         1000: "Healthy",
                         2000: "Unknown",
                         3000: "Warning",
                         4000: "Critical",
                         5000: "Unknown"
                     }
        },
        "State": {
            'Rename' : 'PowerState',
            'Lookup': 'True',
                         'Values': {
                             "1"  : "Unknown",
                             "17" : "On",
                             "18" : "Off",
                             "20" : "Powering On",
                             "21" : "Powering Off"
                       }
        },
        "Name": {"Rename": "ElementName"},
        "Speed": {"Rename": "RPM"},
    },
    NGMCompEnum.BladeSlot: {
        "HealthStatus": {'Rename': 'PrimaryStatus',
                        'Lookup': 'True',
                        'Values': {
                            1000: "Healthy",
                            2000: "Unknown",
                            3000: "Warning",
                            4000: "Critical",
                            5000: "Unknown"
                        }
         },
        "PowerState": {'Lookup': 'True',
                         'Values': {
                             1  : "Unknown",
                             17 : "On",
                             18 : "Off",
                             20 : "Powering On",
                             21 : "Powering Off"
                         }
        }
    },
    NGMCompEnum.IOModule: {
        "HealthStatus": {'Rename': 'PrimaryStatus',
                         'Lookup': 'True',
                         'Values': {
                             1000 : "Healthy",
                             2000 : "Unknown",
                             3000 : "Warning",
                             4000 : "Critical",
                             5000 : "Unknown"
                         }
        },
        "Number": {"Rename": "Slot"},
        "SlotDeviceName": {"Rename": "SlotName"}

    },
    NGMMiscEnum.IOMDevice: {
        "PowerState": {'Lookup': 'True',
                        'Values': {
                            1: "Unknown",
                            17: "On",
                            18: "Off",
                            20: "Powering On",
                            21: "Powering Off"
                }
        },
        "DeviceSpecificData": {
            'CreateNew': {
                'LinkTechnologies': {'_Attribute': ['fabricType']}
            }
        },
        "DeviceManagement": {
            'CreateNew': {
                'IPAddresses': {'_Attribute': ['NetworkAddress']},
                'MacAddress': {'_Attribute': ['MacAddress']}
            }
        }
    },

    NGMMiscEnum.Network: {
        "IomIPv4Settings": {'Create': {
            'EnableIPv4': {'_Attribute': 'EnableIPv4'},
            'EnableDHCP': {'_Attribute': 'EnableDHCP'}
            }
        },
        "IomIPv6Settings": {'Create': {
            'EnableIPv6': {'_Attribute': 'EnableIPv6'},
            'UseDHCPv6': {'_Attribute': 'UseDHCPv6'}
            }
        },
    },
    NGMCompEnum.CMC: {
        "Health": {'Rename': 'PrimaryStatus',
                   'Lookup': 'True',
                   'Values': {
                       1000: "Healthy",
                       2000: "Unknown",
                       3000: "Warning",
                       4000: "Critical",
                       5000: "Unknown"
                   }
           },
        "FirmwareVersion": {"Rename": "MgmtControllerFirmwareVersion"}
    },
    NGMCompEnum.System : {
        "Version" : {'Rename' : 'MgmtControllerFirmwareVersion'},
        "Identifier" : {'Rename' : "ServiceTag"},
        "Description" : {'Rename' : "Model"}
    },
    NGMCompEnum.StorageModule: {
        "HealthStatus": {'Rename': 'PrimaryStatus',
                   'Lookup': 'True',
                   'Values': {
                       1000: "Healthy",
                       2000: "Unknown",
                       3000: "Warning",
                       4000: "Critical",
                       5000: "Unknown"
                   }
        },
        "PowerState": {'Lookup': 'True',
                       'Values': {
                           1: "Unknown",
                           17: "On",
                           18: "Off",
                           20: "Powering On",
                           21: "Powering Off"
                       }
        },
        "Number": {"Rename": "MasterSlotNumber"},
        "Name": {"Rename": "SlotName"},
        "SlotIdentifier": {"Rename": "ServiceTag"}
    },
    NGMMetricsEnum.PowerUsageByDevice: {
            "MinPower": {'UnitScale': '0', 'UnitAppend': 'Watts'},
            "PeakPower": {'UnitScale': '0', 'UnitAppend': 'Watts'},
            "PowerConsumption": {'UnitScale': '0', 'UnitAppend': 'Watts'}
    },
    NGMCompEnum.TemperatureSensors: {
        "Status": {
            "Rename": "PrimaryStatus",
            'Lookup': 'True',
            'Values': {
                "1000": "Healthy",
                "2000": "Unknown",
                "3000": "Warning",
                "4000": "Critical",
                "5000": "Unknown"
            }
        },
        "LowerThresholdCritical": {'UnitScale': '0', 'UnitAppend': 'Degree Celsius'},
        "LowerThresholdNoncritical": {'UnitScale': '0', 'UnitAppend': 'Degree Celsius'},
        "UpperThresholdCritical": {'UnitScale': '0', 'UnitAppend': 'Degree Celsius'},
        "UpperThresholdNoncritical": {'UnitScale': '0', 'UnitAppend': 'Degree Celsius'},
        "ReadingCelsius" :  {'Rename': 'Reading', 'UnitScale': '0', 'UnitAppend' : 'Degree Celsius'},
    },
    NGMMetricsEnum.PowerConsumption: {
        "instantaneousHeadroom": {'UnitScale': '0', 'UnitAppend': 'W'},
        "minimumPower": {'UnitScale': '0', 'UnitAppend': 'W'},
        "peakHeadroom": {'UnitScale': '0', 'UnitAppend': 'W'},
        "peakPower": {'UnitScale': '0', 'UnitAppend': 'W'},
        "power": {'UnitScale': '0', 'UnitAppend': 'W'},
        "systemEnergyConsumption": {'UnitScale': '0', 'UnitAppend': 'kWh'}
    }
}

def check_classifier(myListoFDict, cls=None):
    # print('IN NGMs Satisfy me')
    # pprint(myListoFDict)
    valid = False
    flist = []
    type_dict = {"System" : 2000,
                 "Devices" : 2000,
                 "ComputeDevice" : 1000,
                 "IOModule" : 4000}
    type_x = type_dict.get(cls, 2000)
    for sys in myListoFDict:
        if sys.get('Type', 0) == type_x:
            flist.append(sys)
    if flist:
        valid = True
    return (valid, flist)

classify_cond = {
    NGMMiscEnum.Devices :
    {
        ProtocolEnum.REDFISH : check_classifier
    }
}

NGMMergeJoinSpec =  {
   "System" : {
        "_components" : [
            ["System", "DeviceId", "Devices", "Id"]
        ],
        "_components_enum": [
            NGMCompEnum.System,
            NGMMiscEnum.Devices
        ],
        "_overwrite" : False
   },
    "IOModule": {
        "_components": [
            ["IOModule", "SlotDeviceId", "IOMDevice", "Id"]
        ],
        "_components_enum": [
            NGMCompEnum.IOModule,
            NGMMiscEnum.IOMDevice
        ]
    },
    "ComputeModule": {
        "_components": [
            ["ComputeModule", "SlotDeviceId", "ComputeDevice", "Id"]
        ],
        "_components_enum": [
            NGMCompEnum.ComputeModule,
            NGMMiscEnum.ComputeDevice
        ],
        "_overwrite": False
    },
}

NGMUnionCompSpec = {
   "Slots_Summary":{
        "_components": [
            "BladeSlot",
            "StorageModule",
            "ComputeModule"
        ],
        "_components_enum": [
            NGMCompEnum.BladeSlot,
            NGMCompEnum.StorageModule,
            NGMCompEnum.ComputeModule
        ],
        "_remove_duplicates" : False
   }
}
NGM_more_details_spec = {
    "IOModule": {
        "_components_enum": [
            NGMCompEnum.IOModule,
            NGMMiscEnum.Network
        ]
    },
    "PerformanceMetrics": {
        "_components_enum": [
            NGMMetricsEnum.PowerConsumption,
            NGMMetricsEnum.TemperatureMetrics,
            NGMMetricsEnum.PowerUsageByDevice
        ]
    },
    "System": {
        "_components_enum": [
            NGMCompEnum.System,
            NGMCompEnum.ComputeModule,
            NGMMiscEnum.ComputeDevice,
            NGMCompEnum.StorageModule
        ]
    },
    "Subsystem": {
        "_components_enum": [
            NGMCompEnum.System,
            NGMCompEnum.ComputeModule,
            NGMCompEnum.StorageModule,
            NGMCompEnum.IOModule
        ]
    }

}

class NGM(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(NGM, self).__init__(iDeviceRegistry("NGM", srcdir, NGMCompEnum))
        else:
            super().__init__(iDeviceRegistry("NGM", srcdir, NGMCompEnum))
        self.protofactory.add(PREDFISH(
            views=NGMRestViews,
            cmds=NGMRestCmds,
            view_fieldspec=NGMRestViews_FieldSpec,
            urlbase='api',
            classifier_cond=classify_cond
        ))
        self.protofactory.addCTree(NGMComponentTree)
        self.protofactory.addClassifier(NGMClassifier)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return NGMEntity(self.ref, protofactory, ipaddr, creds)

class NGMEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(NGMEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.more_details_spec = NGM_more_details_spec
        # self.comp_misc_join_spec = NGMDynamicValUnion
        self.comp_merge_join_spec = NGMMergeJoinSpec
        self.comp_union_spec = NGMUnionCompSpec

    def my_fix_obj_index(self, clsName, key, js):
        retval = None
        if clsName == "System":
            if 'ServiceTag' not in js or js['ServiceTag'] is None:
                js['ServiceTag'] = self.ipaddr
            retval = js['ServiceTag']
        if retval is None:
            retval = self.ipaddr + "ngm"
        return retval

    def _isin(self, parentClsName, parent, childClsName, child):
        return True
        # return self._get_obj_index(parentClsName, parent) in \
        #        self._get_obj_index(childClsName, child)

    def get_idrac_ips(self):
        self.get_partial_entityjson(self.ComponentEnum.ComputeModule)
        return self._get_field_device_for_all(self.ComponentEnum.ComputeModule, "IPAddress")

    def _get_topology_info(self):
        self.get_partial_entityjson(self.ComponentEnum.ComputeModule)
        return NGMTopologyInfo(self.get_json_device())

    def _get_topology_influencers(self):
        return {'System': ['Model'],
                'ComputeModule': ['ServiceTag']}

    def _should_i_include(self, component, entry):
        if component == 'System':
            if self.cfactory.work_protocols[0].name == "REDFISH":
                entry['IPAddress'] = self.ipaddr
                port = 443
                if isinstance(self.pOptions, ProtocolOptionsFactory):
                    pOptions = self.pOptions.get(ProtocolEnum.REDFISH)
                    if pOptions:
                        port = pOptions.port
                elif isinstance(self.pOptions, RedfishOptions):
                    port = self.pOptions.port
                if ':' in self.ipaddr:
                    entry['URLString'] = "https://["+str(self.ipaddr) +"]:"+str(port)
                else:
                    entry['URLString'] = "https://" + str(self.ipaddr) + ":" +str(port)
            if "Devices" in self.entityjson:
                attrlist = ['PrimaryStatus', 'ServiceTag']
                sysdict = self.entityjson.get('System', [None])[0]
                devdict = self.entityjson.get('Devices', [None])[0]
                if sysdict and devdict:
                    for attr in attrlist:
                        sysdict[attr] = devdict.get(attr, None)
            if entry.get('ServiceTag', None):
                entry['Key'] = entry.get('ServiceTag')
            if entry.get("IPAddresses"):
                ips = entry.get("IPAddresses").split(",")
                IPv4Address = []
                IPv6Address = []
                for ip in ips:
                    if ':' in ip:
                        IPv6Address.append(ip)
                    else:
                        IPv4Address.append(ip)
                if IPv6Address:
                    entry['IPv6Address'] = ", ".join(str(i) for i in set(IPv6Address))
                if IPv4Address:
                    entry['IPv4Address'] = ", ".join(str(i) for i in set(IPv4Address))
            if entry.get("URLs"):
                ips = entry.get("URLs").split(",")
                IPv4URL = []
                IPv6URL = []
                for ip in ips:
                    if '[' in ip:
                        IPv6URL.append(ip)
                    else:
                        IPv4URL.append(ip)
                if IPv6URL:
                    entry['IPv6URL'] = ", ".join(str(i) for i in set(IPv6URL))
                if IPv4URL:
                    entry['IPv4URL'] = ", ".join(str(i) for i in set(IPv4URL))
        if component == "BladeSlot":
            if entry.get('DeviceType') != TypeHelper.resolve(NGMDeviceTypes.BladeSlot):
                return False
        if component == "ComputeModule":
            model = entry.get('Model', "NA")
            if 'MX740c' in model:
                entry['FormFactor'] = 'Full length Single width'
            if 'MX840c' in model:
                entry['FormFactor'] = 'Full length Double width'
                entry['ExtensionSlot'] = str(int(entry.get('MasterSlotNumber',0))+1)
            if entry.get('DeviceType', "NA") != TypeHelper.resolve(NGMDeviceTypes.ComputeModule) or entry.get("Occupied") != "True" or entry.get("IsPrimarySlot") != "True":
                return False
        if component == "StorageModule":
            if entry.get('DeviceType', "NA") != TypeHelper.resolve(NGMDeviceTypes.StorageModule) or entry.get("Occupied") != "True" or entry.get("IsPrimarySlot") != "True":
                return False
            entry['FormFactor'] = 'Full length Single width'
        if component == "Slots_Summary":
            if entry.get('DeviceType', "NA") != 3000 and entry.get('DeviceType', "NA") != 1000:
                return False
        if component == "PowerUsageByDevice":
            values = ["", None, "NA"]
            if entry.get('MinPower', "NA") in values:
                entry['MinPower'] = "Not Available"
            if entry.get('PeakPower', "NA") in values:
                entry['PeakPower'] = "Not Available"
        if component == 'Subsystem':
            if entry['Key'] not in ['PowerSupply', 'CMC', 'Fan', 'Temperature']:
                return False
        if component == "PowerSupply":
            try:
                values = ['Not Available', None, "", "NA"]
                if entry.get('MemberId', 'NA') in values:
                    entry['Slot'] = 'Not Available'
                else:
                    entry['Slot'] = entry['MemberId'][-1]
            except (IndexError, KeyError, ValueError):
                entry['Slot'] = 'Not Available'
            if entry.get('EnableState', 'NA') == 'Absent':
                entry.pop("PrimaryStatus", None)
        if component == "IOModule":
            if (entry.get("DeviceType") != 4000 and entry.get("DeviceType") != 8000) \
                    or entry.get("Occupied") != "True":
                return False
            if entry.get("IPAddresses"):
                ips = entry.get("IPAddresses").split(",")
                IPv4Address = []
                IPv6Address = []
                for ip in ips:
                    if ':' in ip:
                        IPv6Address.append(ip)
                    else:
                        IPv4Address.append(ip)
                if IPv6Address:
                    entry['IPv6Address'] = ", ".join(str(i) for i in set(IPv6Address))
                if IPv4Address:
                    entry['IPv4Address'] = ", ".join(str(i) for i in set(IPv4Address))
        return True

    def _health_aggregator(self,finalretjson,service):
        calculated_health_numeric = 1
        calculated_health ='Healthy'
        primaryStatusMap = {'Healthy': 1, 'Warning': 2, 'Critical': 3, 'Unknown': 4}
        if finalretjson.get(service, None):
            for entry in finalretjson[service]:

                if (primaryStatusMap[entry['PrimaryStatus']] > calculated_health_numeric):
                    calculated_health_numeric = primaryStatusMap.get(entry['PrimaryStatus'])
                    calculated_health = entry['PrimaryStatus']
        return calculated_health

    def _should_i_modify_component(self, finalretjson, component):
        if component == 'IOModule':
            if "IOModule" and "Network" in finalretjson:
                IOlist = finalretjson['IOModule']
                Nwlist = finalretjson['Network']
                for ntw in Nwlist:
                    for iom in IOlist:
                        if iom.get('Id', "Id") in ntw.get('Key', "Key"):
                            xd = ntw
                            iom.update({k: v for k, v in xd.items() if not k in iom or v=='Not Available'})
        if component == 'Network':
            del finalretjson[component]
        if component == "Subsystem" :
                services = {'StorageModule','ComputeModule','IOModule'}
                for service in services:
                    calculated_health = self._health_aggregator(finalretjson,service)
                    System_entry = {'SubSystem':service,'PrimaryStatus':calculated_health,'Key':service}
                    finalretjson['Subsystem'].append(System_entry)

                calculated_health = self._health_aggregator(finalretjson,component)
                System_entry = {'SubSystem':'System', 'PrimaryStatus': calculated_health, 'Key':'System'}
                finalretjson['Subsystem'].append(System_entry)

        if component == "Slots_Summary":
            bladeslot = finalretjson["Slots_Summary"]
            freeslots = {"1", "2", "3", "4", "5", "6", "7", "8"}
            occupiedSlots = set()
            extensionSlots = set()
            for slot in bladeslot:
                if slot["Occupied"] == "True":
                    if slot["IsPrimarySlot"] == "True" and slot["Number"] != "Not Available":
                        occupiedSlots.add(slot["Number"])
                        if slot["Number"] in freeslots:
                            freeslots.remove(slot["Number"])
                    elif slot["Number"] != "Not Available":
                        extensionSlots.add(slot["Number"])
                        if slot["Number"] in freeslots:
                            freeslots.remove(slot["Number"])

            Slot_Summary = {}
            Slot_Summary['Key'] = 'SlotSummary'
            Slot_Summary['InstanceID'] = 'SlotSummary'
            if freeslots:
                Slot_Summary['FreeSlots'] = ",".join(str(x) for x in freeslots)
            else:
                Slot_Summary['FreeSlots'] = "Chassis is fully occupied"
            if occupiedSlots:
                Slot_Summary['OccupiedSlots'] = ",".join(str(x) for x in occupiedSlots)
            else:
                Slot_Summary['OccupiedSlots'] = "Chassis is empty"
            if extensionSlots:
                Slot_Summary['ExtensionSlots'] = ",".join(str(x) for x in extensionSlots)
            else:
                if occupiedSlots:
                    Slot_Summary['ExtensionSlots'] = "Chassis does not contain any double width Blade"
                else:
                    Slot_Summary['ExtensionSlots'] = "Chassis is empty"

            del finalretjson["Slots_Summary"]
            finalretjson['Slots_Summary'] = []
            finalretjson['Slots_Summary'].append(Slot_Summary)

        clist = ["BladeSlot", "StorageModule", "ComputeModule", "IOModule"]
        if component in clist:
            cmp = finalretjson[component]
            for a in cmp:
                if a.get("DeviceType"):
                    a["DeviceType"] = component
                if a.get("Type"):
                    a["Type"] = component
class NGMTopologyInfo(iDeviceTopologyInfo):
    def __init__(self, json):
        if PY2:
            super(iDeviceTopologyInfo, self).__init__('NGM', json)
        else:
            super().__init__('NGM', json)

    def my_static_groups(self, tbuild):
        tbuild.add_group('Dell', static=True)
        tbuild.add_group('Dell Chassis', 'Dell', static=True)

    def my_groups(self, tbuild):
        if 'Model' in self.system:
            fmgrp = "Dell " + self.system['Model']
            tbuild.add_group(fmgrp, 'Dell Chassis')
            self._add_myself(tbuild, fmgrp)

    def my_assoc(self, tbuild):
        if 'ComputeModule' not in self.json:
            return
        self._remove_assoc(tbuild, [self.mytype, self.system['Key']])
        for slot in self.json['ComputeModule']:
            self._add_assoc(tbuild,
                            [self.mytype, self.system['Key']],
                            ['ComputeModule', slot['Key']],
                            ['Server', slot['ServiceTag']])
