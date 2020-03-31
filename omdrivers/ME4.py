#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
# Authors: Venkatesh Desai, Aijaz Shekh


import sys
from omsdk.sdkproto import ProtocolEnum, PREST
from omsdk.sdkdevice import iDeviceDiscovery, iDeviceRegistry, iDeviceDriver
from omsdk.sdkcenum import EnumWrapper
import logging
logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

ME4CompEnum = EnumWrapper('ME4CompEnum', {
    "System" : "System",
    "Fan" : "Fan",
    "Disk": "Disk",
    "Port": "Port",
    "ExpanderPort": "ExpanderPort",
    "Expander": "Expander",
    "Controller": "Controller",
    "PowerSupply": "PowerSupply",
    "Sensor_Temperature": "Sensor_Temperature",
    "Sensor_Voltage": "Sensor_Voltage",
    "Sensor_ChargeCapacity": "Sensor_ChargeCapacity",
    "Sensor_Amperage": "Sensor_Amperage",
    "Enclosure": "Enclosure",
    "StorageEnclosure": "StorageEnclosure",
    "Volume": "Volume",
    "Subsystem" : "Subsystem",
    "IOM": "IOM",
    "StoragePool": "StoragePool",
    "NIC": "NIC",
    "VDisks": "VDisks"
}).enum_type

ME4MiscEnum = EnumWrapper('ME4MiscEnum', {
    "ServiceTag": "ServiceTag",
    "Versions": "Versions"
}).enum_type

ME4SensorEnum = EnumWrapper('ME4SensorEnum', {
    "Sensor": "Sensor"
}).enum_type


ME4RestViews = {
    ME4CompEnum.System: {
                        'url' : '/api/show/system',
                        'attribute' : 'system',
                         },
    ME4CompEnum.Fan: {
                        'url' : '/api/show/fans',
                        'attribute' : 'fan',
                     },
    ME4CompEnum.Disk: {
                        'url': '/api/show/disks',
                        'attribute': 'drives',
                      },
    ME4CompEnum.NIC: {
                    'url': '/api/show/network-parameters',
                    'attribute': 'network-parameters',
                    },
    ME4CompEnum.Port: {
                        'url': '/api/show/ports',
                        'attribute': 'port',
                      },
    ME4CompEnum.ExpanderPort: {
                                'url': '/api/show/sas-link-health',
                                'attribute': 'expander-ports',
                                },
    ME4CompEnum.Controller: {
                            'url': '/api/show/controllers',
                            'attribute': 'controllers',
                            },
    ME4MiscEnum.Versions: {
                            'url': '/api/show/versions',
                            'attribute': 'versions',
                            },
    ME4MiscEnum.ServiceTag: {
                                'url': '/api/show/service-tag-info',
                                'attribute': 'service-tag-info',
                            },
    ME4CompEnum.PowerSupply: {
                            'url': '/api/show/power-supplies',
                            'attribute': 'power-supplies',
                            },
    ME4CompEnum.Expander: {
                            'url': '/api/show/expander',
                            'attribute': 'sas-status-controller-a',
                            },
    ME4SensorEnum.Sensor: {
                            'url': '/api/show/sensor',
                            'attribute': 'sensors',
                          },
    ME4CompEnum.Enclosure: {
                            'url': '/api/show/enclosure',
                            'attribute': 'enclosures',
                            },
    ME4CompEnum.StorageEnclosure: {
                            'url': '/api/show/enclosure',
                            'attribute': 'enclosures',
                            },
    ME4CompEnum.VDisks: {
                            'url': '/api/show/vdisks',
                            'attribute': 'virtual-disks',
                            },
    ME4CompEnum.Volume: {
                            'url': '/api/show/volumes',
                            'attribute': 'volumes',
                            },
    
    
    ME4CompEnum.IOM: {
                        'url': '/api/show/enclosure',
                        'attribute': 'enclosures',
                        },

    ME4CompEnum.StoragePool: {
                        'url': '/api/show/pools',
                        'attribute': 'pools',
                        },
}

ME4ComponentTree = {
    ME4CompEnum.System: [
        ME4CompEnum.Enclosure,
        ME4CompEnum.Volume,
        ME4CompEnum.StorageEnclosure,

    ],
    ME4CompEnum.StorageEnclosure: [
        ME4CompEnum.Disk,
        ME4CompEnum.Controller,
        ME4CompEnum.PowerSupply,
        ME4CompEnum.Fan,
        # "Sensor"
    ],
    ME4CompEnum.Enclosure:[
        ME4CompEnum.Disk,
        ME4CompEnum.Fan,
        ME4CompEnum.IOM,
        ME4CompEnum.PowerSupply,
    ],
    # "Sensor" : [
    #     ME4CompEnum.Sensor_Temperature,
    #     ME4CompEnum.Sensor_Voltage,
    #     ME4CompEnum.Sensor_Amperage,
    #     ME4CompEnum.Sensor_ChargeCapacity
    # ],
    ME4CompEnum.Controller: [
            ME4CompEnum.Port,
            ME4CompEnum.ExpanderPort,
            ME4CompEnum.NIC,
            ME4CompEnum.Expander,

        ]

}

ME4RestViews_FieldSpec = {
    ME4CompEnum.System : {
        "health-numeric": {
                            'Rename': 'PrimaryStatus',
                            'Lookup': 'True',
                            'Values': {
                                         0: "Healthy",
                                         1: "Warning",
                                         2: "Critical",
                                         3: "Unknown",
                                         4: "Unknown"
                                     }
                        },
        "redundancy": {
                        'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                        }
    },
    ME4CompEnum.Fan: {
        "health-numeric": {
                            'Rename': 'PrimaryStatus',
                            'Lookup': 'True',
                            'Values': {
                                 0: "Healthy",
                                 1: "Warning",
                                 2: "Critical",
                                 3: "Unknown",
                                 4: "Unknown"
                             }
                },
        "redundancy": {'Create' : {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
        }
    },
    ME4CompEnum.Disk: {
            "health-numeric": {
                        'Rename' : 'PrimaryStatus',
                        'Lookup': 'True',
                        'Values': {
                             0: "Healthy",
                             1: "Warning",
                             2: "Critical",
                             3: "Unknown",
                             4: "Unknown"
                         }
                    },
            "redundancy": {'Create' : {'redundancy-mode' : {'_Attribute' : 'redundancy-mode'}}
            }
        },
    ME4CompEnum.NIC: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.StoragePool: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.VDisks: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.Port: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.Controller: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.ExpanderPort: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "UP",
                               1: "Degraded",
                               2: "Fault",
                               3: "Unknown",
                               4: "N/A",
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.Expander: {
        "status-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                                0: "Unknown",
                                1: "Healthy",
                                2: "Warning",
                                3: "Unknown",
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.PowerSupply: {
        "status-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4SensorEnum.Sensor: {
        "status-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Unknown",
                               1: "Healthy",
                               2: "Critical",
                               3: "Warning",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.Enclosure: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.StorageEnclosure: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.IOM: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                               0: "Healthy",
                               1: "Warning",
                               2: "Critical",
                               3: "Unknown",
                               4: "Unknown"
                           }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.Volume: {
        "health-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                                       0: "Healthy",
                                       1: "Warning",
                                       2: "Critical",
                                       3: "Unknown",
                                       4: "Unknown"
                                    }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
    ME4CompEnum.Subsystem: {
        "status-numeric": {'Rename': 'PrimaryStatus',
                           'Lookup': 'True',
                           'Values': {
                                       0: "Healthy",
                                       1: "Warning",
                                       2: "Critical",
                                       3: "Unknown",
                                       4: "Unknown"
                                    }
                           },
        "redundancy": {'Create': {'redundancy-mode': {'_Attribute': 'redundancy-mode'}}
                       }
    },
}


def check_classifier(myListoFDict, cls=None):
    return (True, myListoFDict)

classify_cond = {
    ME4CompEnum.System :
    {
        ProtocolEnum.REST : check_classifier
    }
}
# ME4Classifier = [ ME4CompEnum.System, ME4CompEnum.Fan, ME4CompEnum.Disk ]
ME4Classifier = [ME4CompEnum.System]

ME4RestCmds ={}

ME4MoreDetailsSpec = {
    "System":{
        "_components_enum": [
            ME4CompEnum.System,
            ME4MiscEnum.ServiceTag,
            ME4MiscEnum.Versions,
            ME4CompEnum.Controller,
            ME4CompEnum.Enclosure,
            ME4CompEnum.Volume,
            ME4CompEnum.StorageEnclosure,
            ME4CompEnum.StoragePool,
            ME4CompEnum.NIC,
            ME4CompEnum.VDisks,
        ]
    }
}

ME4UnionCompSpec = {
   "Sensor":{
        "_components": [
            "Sensor"
        ],
        "_components_enum": [
            ME4SensorEnum.Sensor,
        ],
        "_remove_duplicates" : True,
        "_pivot" : "sensor-type-numeric",
        "sensor-type-numeric" : {
            0 : "Temperature",
            1 : "Amperage",
            2 : "Voltage",
            3 : "Charge Capacity",
            4 : "Unknown Type",
        }
    }
}


class ME4(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(ME4, self).__init__(iDeviceRegistry("ME4", srcdir, ME4CompEnum))
        else:
            super().__init__(iDeviceRegistry("ME4", srcdir, ME4CompEnum))
        self.protofactory.add(PREST(
            views=ME4RestViews,
            cmds=ME4RestCmds,
            view_fieldspec=ME4RestViews_FieldSpec,
            urlbase='api',
            classifier_cond=classify_cond
        ))
        self.protofactory.addCTree(ME4ComponentTree)
        self.protofactory.addClassifier(ME4Classifier)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return ME4Entity(self.ref, protofactory, ipaddr, creds)


class ME4Entity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(ME4Entity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.more_details_spec = ME4MoreDetailsSpec
        self.comp_union_spec = ME4UnionCompSpec
        self.unhealthy_component = []
        self.unhealthy_component_keys = []
        self.is_scalable = False

    @property
    def ContainmentTree(self):
        """
        Adding StorageEnclosure , Enclosure and Volume to Scalable CompTree
        :return: JSON
        """
        device_json = self.get_json_device()
        ctree = self._build_ctree(self.protofactory.ctree, device_json)
        if self.is_scalable:
            systree = ctree.get("System")
            xlist = ["Volume", "Enclosure"]
            for comp in xlist:
                if systree.get(comp) is not None:
                    systree[comp] = []
            self.is_scalable = False
        return ctree

    def _isin(self, parentClsName, parent, childClsName, child):
        """"""
        if (parentClsName == "StorageEnclosure" or parentClsName == "Enclosure") and childClsName == "Disk":
            if parent.get('enclosure-id', None) == child.get('enclosure-id', None):
                return True
            else:
                return False
        if parentClsName == "StorageEnclosure" and childClsName == "Controller":
            if str(parent.get('enclosure-id', None)) == str(child.get('enclosure-id', None)):
                return True
            else:
                return False
        if parentClsName == "Controller" and childClsName == "Port":
            if parent.get('controller-id', None) == child.get('controller', None):
                return True
            else:
                return False
        if parentClsName == "Controller" and (childClsName == "Expander" or childClsName == "ExpanderPort"):
            if (parent.get('controller-id', None) == child.get('controller', None)) and \
                    (int(child.get('enclosure-id', None)) == 0):
                return True
            else:
                return False

        if (parentClsName == "StorageEnclosure" or parentClsName == "Enclosure") and childClsName == "PowerSupply":
            if parent.get('enclosure-id', None) == child.get('enclosure-id', None):
                return True
            else:
                return False
        if parentClsName == "Controller" and childClsName == "NIC":
            enclosure_id = child.get("durable-id").split('_')[-1]
            if parent.get('controller-id', None).lower() == enclosure_id:
                return True
            else:
                return False
        if (parentClsName == "StorageEnclosure" or parentClsName == "Enclosure") and childClsName == "Fan":
            location = child.get('location', None)
            position = str(location.split(',')[0].split(' ')[-1])
            if str(parent.get('enclosure-id', None)) == position:
                return True
            else:
                return False
        return True

    def _should_i_modify_component(self, finalretjson, component):
        """ This function is to add or modify the json data"""
        try:
            if "ServiceTag" == component and "System" in finalretjson.keys():
                if len(finalretjson[component]) == 1:
                    finalretjson['System'][0]['service-tag'] = finalretjson[component][0]['service-tag']
                    finalretjson['System'][0]['Key'] = finalretjson[component][0]['service-tag']
                else:
                    for each in finalretjson[component]:
                        if 'enclosure-id' in each and str(each['enclosure-id']) == "0":
                            finalretjson['System'][0]['service-tag'] = each['service-tag']
                            finalretjson['System'][0]['Key'] = each['service-tag']
            if 'NIC' == component and "System" in finalretjson.keys():
                for val, each in enumerate(finalretjson[component]):
                    finalretjson['System'][0]['IPAddress_' + str(val)] = each['ip-address']
                finalretjson['System'][0]['URLString'] = "https://" + str(self.ipaddr)
            if 'Versions' == component:
                sysdict = finalretjson['System'][0]  # check for 1 item atleast
                verslist = finalretjson['Versions']
                cntrlist = finalretjson['Controller']
                for vers in verslist:
                    verid = vers.get('object-name', "#-#").split('-')[1]
                    for ctrl in cntrlist:
                        ctrlid = ctrl.get('durable-id', "%_%").split('_')[1]
                        if verid == ctrlid:
                            if (str(self.ipaddr) == str(ctrl.get('ip-address', 'Not Available'))or (str(self.ipaddr) in str(ctrl.get('ip6-auto-address', 'Not Available')))):
                                sysdict['bundle-version'] = vers.get('bundle-version', 'Not Available')
                                break
            if "System" == component:
                finalretjson['Subsystem'] = []
                for key, value in finalretjson.items():
                    if self.unhealthy_component:
                        for each_UH in self.unhealthy_component:
                            if key.lower() != 'subsystem' and key.lower() == each_UH['Key'].lower():
                                finalretjson['Subsystem'].append({'Key': each_UH['Key'],
                                                                  'PrimaryStatus': each_UH['PrimaryStatus']})
                    if key != 'Subsystem':
                        health = self.calculate_health(key, value, component)
                        if key.lower() not in self.unhealthy_component_keys:
                            finalretjson['Subsystem'].append({'Key': key, 'PrimaryStatus': health})
            if self.is_scalable:
                self.remove_componet(finalretjson)
        except Exception as E:
            logger.info(E)

        return True

    def _should_i_include(self, component, entry):
        short_name = {"PSU": "PowerSupply", "disk slot": "Disk", "SAS port": "ExpanderPort"}
        health_mapping = {'OK': 'Healthy', 'Degraded': 'Warning', 'Fault': 'Critical', "N/A": 'Unknown'}
        if "System" == component:
            if self.entityjson.get('System') and self.entityjson.get('ServiceTag'):
                system_dict = self.entityjson['System'][0]
                servicetag_dict = self.entityjson['ServiceTag'][0]
                system_dict['Key'] = servicetag_dict.get('service-tag', servicetag_dict.get('Key', "Not Available"))
            if 'unhealthy-component' in entry and self.unhealthy_component == []:
                for data in entry['unhealthy-component']:
                    if data['component-type']in short_name.keys():
                        self.unhealthy_component.append({'Key': short_name[data['component-type']],
                                                         'PrimaryStatus': health_mapping[data['health']]})
                        self.unhealthy_component_keys.append(short_name[data['component-type']])
                    else:
                        self.unhealthy_component.append({'Key': data['component-type'],
                                                         'PrimaryStatus': health_mapping[data['health']]})
                        self.unhealthy_component_keys.append(data['component-type'])
            # port needs to be added for url
            if ':' in self.ipaddr:
                entry['url'] = "https://[" + str(self.ipaddr) + "]"
            else:
                entry['url'] = "https://" + str(self.ipaddr)
        if "StorageEnclosure" == component:
            if entry.get('enclosure-id') != 0:
                return False
        if "IOM" == component:
            if entry.get('enclosure-id') == 0:
                return False
        if "Enclosure" == component:
            if entry.get('enclosure-id') == 0:
                return False
            else:
                return True
        return True


    def get_basic_entityjson(self):
        self.is_scalable = True
        plist = ['StorageEnclosure', 'Enclosure', 'Volume', 'System', 'Versions']
        if self.get_partial_entityjson(*plist):
            return True
        return False


    def remove_componet(self, finalretjson):
        """this function remove all the unwanted json in case of scalable"""
        try:
            keys_list = []
            for i, j in finalretjson.items():
                keys_list.append(i)
            deep_key_list = keys_list[:]
            temp_comp_list = ['System', 'SubSystem', 'StorageEnclosure', 'Enclosure', 'Volume', 'ServiceTag', 'Versions', 'Controller']
            for each in deep_key_list:
                if each not in temp_comp_list:
                    finalretjson.pop(each)
            return True
        except Exception as e:
            logger.info(e)


    def calculate_health(self, key, value, component):
        """this function calculate rollup health"""
        try:
            health_dict = ME4RestViews_FieldSpec[ME4CompEnum[component]]
            list_value = []
            new_health_dict = {}
            for i, j in health_dict["health-numeric"]['Values'].items():
                new_health_dict[j] = i

            if "health-numeric" in health_dict:
                for each in value:
                    # if each['PrimaryStatus'] != 'N/A' and each['PrimaryStatus'] in new_health_dict.keys():
                    if each['PrimaryStatus'] in new_health_dict.keys():
                        list_value.append(new_health_dict[each['PrimaryStatus']])
                if list_value:
                    health = health_dict["health-numeric"]['Values'][max(list_value)]
                    return health
            if "status-numeric" in health_dict:
                for each in value:
                    # if each['PrimaryStatus'] != 'N/A' and each['PrimaryStatus'] in new_health_dict.keys():
                    if each['PrimaryStatus'] in new_health_dict.keys():
                        list_value.append(new_health_dict[each['PrimaryStatus']])
                if list_value:
                    health = health_dict["health-numeric"]['Values'][max(list_value)]
                    return health
            return "Healthy"
        except Exception as e:
            logger.info(e)
            return "Healthy"
