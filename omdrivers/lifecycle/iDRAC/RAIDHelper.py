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
from omsdk.sdkinfra import sdkinfra
from omsdk.sdkcreds import UserCredentials
from omsdk.simulator.devicesim import Simulator
from omsdk.sdkprint import PrettyPrint
from omdrivers.types.iDRAC.RAID import *
from omsdk.typemgr.ArrayType import ArrayType, FQDDHelper
import re
import operator

import logging

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, loading_from_scp=True):
        self.Controller = ArrayType(Controller, parent=None,
                                    index_helper=FQDDHelper(),
                                    loading_from_scp=loading_from_scp)
        self.inited = False

    @property
    def ControllerCount(self):
        return self.Controller.Length

    def Controller_load(self, component, array, ctree, ejson, entity):
        return self.my_load(component, array, ctree, ejson, entity)

    def Enclosure_load(self, component, array, ctree, ejson, entity):
        return self.my_load(component, array, ctree, ejson, entity)

    def PhysicalDisk_load(self, component, array, ctree, ejson, entity):
        d = self.my_load(component, array, ctree, ejson, entity)

    def VirtualDisk_load(self, component, array, ctree, ejson, entity):
        return self.my_load(component, array, ctree, ejson, entity)

    def my_load(self, component, array, ctree, ejson, entity):
        if not component in ctree:
            return False
        count = 0
        for count in range(1, len(ejson[component]) + 1):
            comp = ejson[component][count - 1]
            for field in ['EncryptionMode']:
                if field in comp:
                    del comp[field]
            for field in ['BlockSize', 'FreeSize', 'Size']:
                if field in comp:
                    try:
                        comp[field] = int(float(comp[field]))
                    except Exception as ex:
                        print(str(ex))
            entry = array.flexible_new(index=count, **comp)
            if comp['FQDD'] not in ctree[component]:
                continue
            if isinstance(ctree[component], list):
                # leaf node
                continue
            subctree = ctree[component][comp['FQDD']]
            for subcomp in subctree:
                if subcomp in entry.__dict__:
                    self._load_comp(subcomp, entry, subctree, ejson, entity)
        return True

    def _load_comp(self, comp, entry, ctree, ejson, entity):
        func = getattr(self, comp + '_load')
        return func(comp, entry.__dict__[comp], ctree, ejson, entity)

    def load(self, ctree, entity):
        ejson = entity.get_json_device()
        logger.debug(ejson)
        self._load_comp('Controller', self, ctree, ejson, entity)
        self.Controller.commit()
        self.inited = True


class RAIDHelper:
    def __init__(self, entity):
        self.storage_tree = None
        self.entity = entity
        self.storage = Storage()
        self._init_storage()


    def _init_storage(self, reset_config=RAIDresetConfigTypes.T_False):
        reset_config = reset_config.value
        if self.storage.inited and reset_config == 'False':
            return self.storage

        self.entity.get_partial_entityjson(
            self.entity.ComponentEnum.Controller,
            self.entity.ComponentEnum.Enclosure,
            self.entity.ComponentEnum.VirtualDisk,
            self.entity.ComponentEnum.PhysicalDisk
        )
        raid_tree = self.entity.ContainmentTree
        self.storage_tree = raid_tree['Storage']
        logger.debug(raid_tree['Storage'])
        self.storage.load(raid_tree["Storage"], self.entity)
        if self.storage.ControllerCount <= 0:
            logger.debug("No Controllers!")
            return self.storage
        # filtering should not be called in case of reset config True
        self.storage.Controller.remove(PrimaryStatus='0')
        for controller in self.storage.Controller:
            controller.Enclosure.remove(PrimaryStatus='0')
            fqdd = str(controller.FQDD)
            filter_query_to_remove_used_disks = '(entry.RaidStatus != "Ready" or entry.RaidStatus != "Non-RAID") and entry.FreeSize._value == 0'
            filter_query_to_remove_invalid_fqdd = '"' + fqdd + '" not in entry.FQDD._value'
            for encl in controller.Enclosure:
                if reset_config == 'False':
                    encl.PhysicalDisk.remove_matching(filter_query_to_remove_used_disks)
                encl.PhysicalDisk.remove_matching(filter_query_to_remove_invalid_fqdd)
            if reset_config == 'False':
                controller.PhysicalDisk.remove_matching(filter_query_to_remove_used_disks)
            controller.PhysicalDisk.remove_matching(filter_query_to_remove_invalid_fqdd)
        return self.storage

    def compute_disk_count(self, span_depth, span_length, n_dhs):
        return span_length * span_depth + n_dhs

    def get_disks(self, n_disks, restconfig=RAIDresetConfigTypes.T_False):
        self._init_storage(reset_config=restconfig)
        s_disks = []
        if self.storage.ControllerCount <= 0:
            print("No Healthy Controllers found!")
            return s_disks

        for controller in self.storage.Controller:
            direct_pd_count = controller.PhysicalDisk.Length
            if direct_pd_count >= n_disks:
                s_disks = [i for i in controller.PhysicalDisk]
                return s_disks[0:n_disks]
            for enclosure in controller.Enclosure:
                encl_pd_count = enclosure.PhysicalDisk.Length
                if encl_pd_count >= n_disks:
                    s_disks = [i for i in enclosure.PhysicalDisk]
                return s_disks[0:n_disks]
        return s_disks

    def filter_disks(self, n_disks, criteria, dhspare=False, restconfig=RAIDresetConfigTypes.T_False):
        self._init_storage(reset_config=restconfig)
        s_disks = []
        if self.storage.ControllerCount <= 0:
            print("No Healthy Controllers found!")
            return s_disks
        criteria = re.sub('(^|[^0-9a-zA-Z])disk([^0-9a-zA-Z])', '\\1entry\\2', criteria)
        for controller in self.storage.Controller:
            s_disks = controller.PhysicalDisk.find_matching(criteria)
            if len(s_disks) >= n_disks:
                if dhspare:
                    return s_disks
                return s_disks[0:n_disks]
            for enclosure in controller.Enclosure:
                s_disks = enclosure.PhysicalDisk.find_matching(criteria)
                if len(s_disks) >= n_disks:
                    if dhspare:
                        return s_disks
                    return s_disks[0:n_disks]
        return s_disks

    @staticmethod
    def raid_std_validation(raid_value=None):
        logger.info("Interface raid_std_validation enter")
        raid_std = {
            "RAID 0": {'pd_slots': range(1, 2), 'span_length': 1, 'checks': operator.ge, 'span_depth': 1},
            "RAID 1": {'pd_slots': range(1, 3), 'span_length': 2, 'checks': operator.eq, 'span_depth': 1},
            "RAID 5": {'pd_slots': range(1, 4), 'span_length': 3, 'checks': operator.ge, 'span_depth': 1},
            "RAID 6": {'pd_slots': range(1, 5), 'span_length': 4, 'checks': operator.ge, 'span_depth': 1},
            "RAID 10": {'pd_slots': range(1, 5), 'span_length': 2, 'checks': operator.eq, 'span_depth': 2},
            "RAID 50": {'pd_slots': range(1, 7), 'span_length': 3, 'checks': operator.ge, 'span_depth': 2},
            "RAID 60": {'pd_slots': range(1, 9), 'span_length': 4, 'checks': operator.ge, 'span_depth': 2}
        }
        status, message = "Success", "Invalid RAID level."
        if raid_std.get(raid_value['raid_level']) is not None:
            raid = raid_std.get(raid_value['raid_level'])
            if raid_value.get('upd_slots') is not None:
                if operator.ne(len(raid_value.get('upd_slots')), raid_value.get('pd_required')):
                    status = "Failed"
                    message = "Invalid physical disk slots or span length or span depth details."
                    return {'Status': status, 'Message': message}
            if raid_value.get('pd_required') or raid_value.get('span_length') is not None:
                pd_slots = raid_value.get('pd_required')
                span_length = raid_value.get('span_length')
                if operator.ne(raid.get('span_depth'), raid_value.get('span_depth')):
                    return {'Status': 'Failed', 'Message': 'Invalid span depth.'}
                if raid.get('checks')(pd_slots, len(raid.get('pd_slots'))):
                    status = "Success"
                    message = "span length validation is successful."
                elif raid.get('checks')(span_length, raid.get('span_length')):
                    status = "Success"
                    message = "physical disk slots validation is successful."
                else:
                    status = "Failed"
                    message = "Invalid physical disk slots or span length or span depth details."
        logger.info("Interface raid_std_validation exit")
        return {"Status": status, "Message": message}

    def get_dhs_disks(self, av_disks, sel_disks, n_dhs):
        logger.info("{} : {}".format(self.entity.ipaddr, "Enter: Dedicated hot spare!"))
        disks = None
        try:
            av_disks_key = set([i.Key for i in av_disks])
            sel_disks_key = set([i.Key for i in sel_disks])
            av_dhs = av_disks_key.difference(sel_disks_key)
            dhs = list(av_dhs)[0:n_dhs]
            disks = [d for k in dhs for d in av_disks if d.Key == k]
            logger.info("{} : {}".format(self.entity.ipaddr, "Exit: Dedicated hot spare!"))
        except Exception:
            logger.error("{} : {}".format(self.entity.ipaddr, "Exception: Dedicated hot spare!"))
        return disks

    def create_virtual_disk(self, sysconfig, **kwargs):
        logger.info(self.entity.ipaddr + " : Interface create_virtual_disk enter")
        filter_query = ""
        for i in ['SpanLength', 'SpanDepth']:
            if i not in kwargs:
                return {
                    'Status': 'Failed',
                    'Message': 'Parameter ' + i + ' is missing'}

        ndisks = self.compute_disk_count(kwargs['SpanLength'], kwargs['SpanDepth'],
                                         kwargs['NumberDedicatedHotSpare'])
        ndks = self.compute_disk_count(kwargs['SpanLength'], kwargs['SpanDepth'], 0)
        if "RAIDresetConfig" not in kwargs:
            kwargs['RAIDresetConfig'] = RAIDresetConfigTypes.T_False
        if 'PhysicalDiskFilter' in kwargs:
            disks = self.filter_disks(ndks, kwargs['PhysicalDiskFilter'], restconfig=kwargs['RAIDresetConfig'])

            # Time being fix for -JIT-107987 - Ansible(1.0.3) - [RAID Configuration] VD creation is failing
            # on external storage (MD Array) configured to server
            # Ensures that existing senarios are not broken
            if len(disks) == 0:
                if kwargs.get('ControllerFQDD') is not None:
                    filter_query = '((entry is PhysicalDisk and "' + kwargs['ControllerFQDD'] + '" in entry.FQDD._value))'
                if kwargs.get('mediatype') is not None:
                    filter_query += ' and entry.MediaType == "' + kwargs['mediatype'] + '"'
                if kwargs.get('busprotocol') is not None:
                    filter_query += ' and entry.BusProtocol == "' + kwargs['busprotocol'] + '"'
                if kwargs.get('PDSlots'):
                    slots_list = kwargs.get('PDSlots')
                    if isinstance(slots_list, str):
                        slots_list = eval(slots_list)
                    slots_list = list(map(str, slots_list))
                    filter_query += ' and entry.Slot._value in ' + str(slots_list)
                if kwargs.get('FQDD'):
                    id_list = kwargs.get('FQDD')
                    filter_query += ' and entry.FQDD._value in ' + str(id_list)
                disks = self.filter_disks(ndks, filter_query, restconfig=kwargs['RAIDresetConfig'])
        else:
            disks = self.get_disks(ndks, restconfig=kwargs['RAIDresetConfig'])

        if len(disks) <= 0:
            logger.debug(self.entity.ipaddr + " : No sufficient disks found in Controller!")
            con_msg = 'Number of sufficient disks not found in Controller!'
            if kwargs.get('ControllerFQDD') is not None:
                con_msg = 'Number of sufficient disks not found in Controller \'{}\'!'.format(
                        kwargs['ControllerFQDD'])
            return {'Status': 'Failed',
                    'Message': con_msg}
        # Assumption: All disks are part of same enclosure or direct attached!
        controller = None
        enclosure = disks[0]._parent._parent
        if not isinstance(disks[0]._parent._parent, Enclosure):
            enclosure = None
            controller = disks[0]._parent._parent
        else:
            controller = enclosure._parent._parent

        cntrl = sysconfig.Controller.find_first(FQDD=controller.FQDD)
        if cntrl is None:
            logger.debug(self.entity.ipaddr + " :  No such controller found!")
            return {'Status': 'Failed',
                    'Message': 'No such controller found!'}

        # Time being fix for -JIT-107987 - Ansible(1.0.3) - [RAID Configuration] VD creation is failing
        # on external storage (MD Array) configured to server
        # Ensures that existing senarios are not broken
        enclosure_fqdd = ""
        if controller.FQDD != kwargs.get('ControllerFQDD') and len(disks) >= 0:
            ctrlst = sysconfig.Controller.Properties
            if ctrlst:
                for c in ctrlst:
                    if c.Json['FQDD'] == kwargs.get('ControllerFQDD'):
                        controller = c
                        cntrl = controller
                        enclosure_fqdd = c.Enclosure.Json[0]['FQDD']

        # Time being fix for -JIT-107987 - Ansible(1.0.3) - [RAID Configuration] VD creation is failing
        # on external storage (MD Array) configured to server
        # Ensures that existing senarios are not broken
        try:
            derived_ctrl_fqdd = controller.FQDD
        except (AttributeError, TypeError):
            derived_ctrl_fqdd = controller.Json['FQDD']

        vdindex = cntrl.VirtualDisk.Length + 1
        vdfqdd = "Disk.Virtual.{0}:{1}".format(vdindex, derived_ctrl_fqdd)
        for i in kwargs:
            if i in cntrl.__dict__:
                cntrl.__dict__[i]._value = kwargs[i]
        vdisk = cntrl.VirtualDisk.new(index=vdindex)
        # pass virtual disk attributes to vdisk
        for i in kwargs:
            if i in vdisk.__dict__:
                if i == 'StripeSize':
                    kwargs[i] = int(kwargs[i] / 512)
                vdisk.__dict__[i]._value = kwargs[i]
        vdisk._attribs['FQDD'] = vdfqdd
        target = cntrl
        if enclosure:
            tgt_encl = cntrl.Enclosure.find_first(FQDD=enclosure.FQDD)
            if tgt_encl is None:
                tgt_encl = cntrl.Enclosure.new(index=cntrl.Enclosure.Length + 1)

                # Time being fix for -JIT-107987 - Ansible(1.0.3) - [RAID Configuration] VD creation is failing
                # on external storage (MD Array) configured to server
                # Ensures that existing senarios are not broken
                if enclosure_fqdd:
                    tgt_encl._attribs['FQDD'] = enclosure_fqdd
                else:
                    tgt_encl._attribs['FQDD'] = enclosure.FQDD
            target = tgt_encl
        counter = 0
        n_dhs = kwargs['NumberDedicatedHotSpare']
        raid_disks = ndisks - n_dhs

        # Time being fix for -JIT-107987 - Ansible(1.0.3) - [RAID Configuration] VD creation is failing
        # on external storage (MD Array) configured to server
        # Ensures that existing senarios are not broken
        try:
            if n_dhs > 0:
                if filter_query:
                    sp_query = filter_query
                else:
                    sp_query = kwargs['PhysicalDiskFilter']
                pd_query = filter(None, re.compile(r"^(\(.*)\sand (?:disk|entry).Slot._value.*$").split(sp_query))[0]
                av_disks = self.filter_disks(n_dhs, pd_query, dhspare=True, restconfig=kwargs['RAIDresetConfig'])
                dhs_msg = "physical disks are not available for dedicated hot spare!"
                if len(av_disks) < 0:
                    return {"Status": "Failed", "Message": dhs_msg}
                dhs_disks = self.get_dhs_disks(av_disks, disks, n_dhs)
                if dhs_disks is None:
                    return {"Status": "Failed", "Message": dhs_msg}
                disks.extend(dhs_disks)
        except Exception:
            logger.error("{} : {}".format(self.entity.ipaddr, "dedicated hot spare exception."))


        for disk in disks:
            counter += 1
            if n_dhs > 0 and (counter > raid_disks and counter <= (raid_disks + n_dhs)):
                state = RAIDHotSpareStatusTypes.Dedicated
                vdisk.RAIDdedicatedSpare = disk.FQDD._value
            else:
                state = RAIDHotSpareStatusTypes.No
                vdisk.IncludedPhysicalDiskID = disk.FQDD._value
            tgt_disk = target.PhysicalDisk.find_first(FQDD=disk.FQDD)
            if tgt_disk is None:
                tgt_disk = target.PhysicalDisk.new(index=target.PhysicalDisk.Length + 1)
                tgt_disk._attribs['FQDD'] = disk.FQDD
            tgt_disk.RAIDHotSpareStatus.nullify_value()
            tgt_disk.RAIDHotSpareStatus.commit()
            tgt_disk.RAIDHotSpareStatus = RAIDHotSpareStatusTypes.No
        logger.info(self.entity.ipaddr + " : Interface create_virtual_disk exit")

    def new_virtual_disk(self, **kwargs):
        logger.info(self.entity.ipaddr + " : Interface new_virtual_disk enter")
        sysconfig = self.entity.config_mgr._sysconfig
        apply_changes = kwargs.get("apply_changes")
        if kwargs.get("multiple_vd") is None:
            logger.debug(self.entity.ipaddr + " : new_virtual_disk single vd creation")
            # This change is for OMSDK v1.0 and v1.1 compatibility
            self.create_virtual_disk(sysconfig, **kwargs)
        else:
            logger.debug(self.entity.ipaddr + " : new_virtual_disk multiple vd creation")
            for vd_val in kwargs["multiple_vd"]:
                span_depth = vd_val.get("SpanDepth") if vd_val.get("SpanDepth") is not None else 0
                span_length = vd_val.get("SpanLength") if vd_val.get("SpanLength") is not None else 0
                if vd_val.get("PDSlots"):
                    upd_slots = vd_val.get("PDSlots")
                elif vd_val.get("FQDD"):
                    upd_slots = vd_val.get("FQDD")
                else:
                    upd_slots = None
                pd_required = int(span_length) * int(span_depth)
                if pd_required == 0:
                    pd_required = None
                vd_dict = {"raid_level": vd_val.get("RAIDTypes"),
                           "span_length": vd_val.get("SpanLength"),
                           "span_depth": span_depth,
                           "pd_required":  pd_required, "upd_slots": upd_slots}
                standard = RAIDHelper.raid_std_validation(raid_value=vd_dict)
                if standard["Status"] == "Failed":
                    return standard
            for kwargs in kwargs["multiple_vd"]:
                try:
                    virtual_disk = self.create_virtual_disk(sysconfig, **kwargs)
                    if virtual_disk:
                        return virtual_disk
                except Exception as e:
                    logger.debug("{}: {}".format(self.entity.ipaddr, e))
        logger.info(self.entity.ipaddr + " : Interface new_virtual_disk exit")
        if apply_changes is True or apply_changes is None:
            return self.entity.config_mgr.apply_changes(reboot=True)
        else:
            return self.entity.config_mgr.is_change_applicable()

    def delete_virtual_disk(self, **kwargs):
        sysconfig = self.entity.config_mgr._sysconfig
        apply_changes = True
        msg = {"Status": "Failed",
               "Message": "Unable to find the virtual disk."}
        if 'apply_changes' in kwargs:
            apply_changes = kwargs['apply_changes']
            del kwargs['apply_changes']
        vd_select = []
        # This change is for DellEMC Ansible v1.0.2 and below compatibility
        if kwargs.get('Name') is not None:
            kwargs['vd_names'] = kwargs.pop('Name')
            kwargs['vd_names'] = [kwargs.get('vd_names')]
        for controller in sysconfig.Controller:
            for vd_name in kwargs.get("vd_names"):
                vd = controller.VirtualDisk.find_first(Name=vd_name)
                try:
                    if vd:
                        vd.RAIDaction = "Delete"
                        vd_select.append(vd)
                except AttributeError:
                    logger.error("{}: {}".format(self.entity.ipaddr,
                                                 "Unable to find the virtual disk!"))
                    pass
        if apply_changes:
            if vd_select:
                msg = self.entity.config_mgr.apply_changes(reboot=True)
                if msg['Status'] == 'Success':
                    try:
                        controller.VirtualDisk._remove_selected(vd_select)
                        sysconfig.commit()
                    except (ValueError, IndexError):
                        logger.info("{}: {}".format(
                            self.entity.ipaddr,
                            "unable to find the virtual disk index!"))
            return msg
        else:
            if vd_select:
                return self.entity.config_mgr.is_change_applicable()
            return msg

    def find_first_virtual_disk(self, **kwargs):
        vdselect = None
        sysconfig = self.entity.config_mgr._sysconfig
        for controller in sysconfig.Controller:
            vdselect = controller.VirtualDisk.find_first(**kwargs)
            if vdselect:
                break
        return vdselect

    def find_virtual_disk(self, **kwargs):
        vdselect = []
        sysconfig = self.entity.config_mgr._sysconfig
        for controller in sysconfig.Controller:
            vdselect.extend(controller.VirtualDisk.find(**kwargs))
        return vdselect

    def find_matching_virtual_disk(self, criteria):
        vdselect = []
        sysconfig = self.entity.config_mgr._sysconfig
        for controller in sysconfig.Controller:
            vdselect.extend(controller.VirtualDisk.find_matching(criteria))
        return vdselect

    def view_storage(self, controller=None, virtual_disk=None):
        """ view storage hierarchy as a json

        :param controller: contoller id
        :param controller: str
        :param virtual_disk: virtual disk id
        :param virtual_disk: str
        :return: returns json accoring to the parameter provided
        """
        try:
            logger.info(self.entity.ipaddr + " : getting storage tree")

            storage_tree = self.storage_tree
            logger.debug(self.entity.ipaddr + " : storage_tree : " + str(storage_tree))
        except:
            logger.error(self.entity.ipaddr + " : error in getting storage tree")
            return {'Status': 'Failed', 'Message': 'Failed to find storage tree'}

        if not controller and not virtual_disk:
            # In case of no parameters return whole storage json
            logger.info(
                self.entity.ipaddr + " : returning full storage tree as controller and virtual disk parameters are None")
            return {'Status': 'Success', 'Message': storage_tree}

        if not controller:
            logger.error(self.entity.ipaddr + " : controller identifier parameter is missing")
            return {'Status': 'Failed', 'Message': 'Controller identifier parameter is missing'}

        # If controller param does not exist in the storage json
        if not 'Controller' in storage_tree or not controller in storage_tree['Controller']:
            logger.error(self.entity.ipaddr + " : unable to find specified controller : " + str(controller))
            msg = {'Status': 'Failed', 'Message': 'Failed to find the controller ' + controller}
            return msg

        if controller and not virtual_disk:
            # In case of only controller param returns json for that particular controller
            logger.info(self.entity.ipaddr + " : returning controller hierarchy for controller : " + str(controller))
            return {'Status': 'Success', 'Message': {controller: storage_tree['Controller'][controller]}}

        if controller and virtual_disk:
            if not 'VirtualDisk' in storage_tree['Controller'][controller] or not virtual_disk in \
                    storage_tree['Controller'][controller]['VirtualDisk']:
                logger.error(self.entity.ipaddr + " : unable to find specified virtual disk : " + str(
                    virtual_disk) + " in controller : " + str(controller))
                msg = {'Status': 'Failed', 'Message': 'Failed to find the volume : ' + str(virtual_disk) + " in controller : " + str(
                    controller)}
                return msg
            logger.info(
                self.entity.ipaddr + " : returning virtual disk : " + str(virtual_disk) + " in controller : " + str(
                    controller))
            return {'Status': 'Success', 'Message': {controller: {'VirtualDisk': {virtual_disk: storage_tree['Controller'][controller]['VirtualDisk'][virtual_disk]}}}}

        logger.error(self.entity.ipaddr + " : failed to execute method. ")
        return {'Status': 'Failed', 'Message': 'Failed to find storage tree'}
