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
import sys, os
import re
import json
import threading

from omsdk.sdkprint import PrettyPrint
from omsdk.sdkdelta import DiffFilter, DiffStyle, DiffScope, DiffScopeFilter
from omsdk.sdkdelta import DeltaComputer
from omsdk.sdkenum import CreateMonitorScopeFilter, MonitorScope
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class BaseStore(object):
    def __init__(self):
        pass

    def store_file(current_json, diff_filter, fname, func):
        pass

    def load_master(self, fname):
        pass

    def load_delta(self, fname):
        pass

    @staticmethod
    def makedir(*path_args):
        directory = os.path.join(*path_args)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.isdir(directory):
            logger.debug(directory + " is not a file! defaulting to .")
            directory = "."
        return directory


class EntityStore(BaseStore):
    def __init__(self, *path_args):
        if PY2:
            super(EntityStore, self).__init__()
        else:
            super().__init__()
        self.store_dir = self.makedir(*path_args)
        self.master_dir = self.makedir(self.store_dir, 'Master')
        self.save_delta = True
        if self.save_delta:
            self.delta_dir = self.makedir(self.store_dir, 'Delta')

    def clone(self):
        return Saver(self.store_dir)

    def store(self, current_json, diff_filter, fname, func, relpath=[]):
        master_scope_file = self.master_dir
        if relpath and len(relpath) > 0:
            master_scope_file = self.makedir(master_scope_file, *relpath)

        master_scope_file = os.path.join(master_scope_file, fname)
        # Load the original json file
        orig_json = {}
        if self.save_delta:
            # Compute delta and store them!!
            delta_scope_file = self.delta_dir
            if relpath and len(relpath) > 0:
                delta_scope_file = self.makedir(delta_scope_file, *relpath)
            delta_scope_file = os.path.join(delta_scope_file, fname)

            if os.path.exists(master_scope_file):
                with open(master_scope_file, 'r') as f:
                    orig_json = json.load(f)

                diff_json = func(orig_json, current_json, diff_filter)
            else:
                diff_json = current_json

            with open(delta_scope_file, 'w') as f:
                json.dump(diff_json, f, sort_keys=True, indent=4,
                          separators=(',', ': '))
                f.flush()

        # now write to master file
        with open(master_scope_file, 'w') as f:
            json.dump(current_json, f, sort_keys=True, indent=4,
                      separators=(',', ': '))
            f.flush()

    def load_master(self, *relpath):
        master_scope_file = os.path.join(self.master_dir, *relpath)
        orig_json = {}
        if os.path.exists(master_scope_file):
            with open(master_scope_file, 'r') as f:
                orig_json = json.load(f)
        return orig_json

    def load_delta(self, *relpath):
        delta_scope_file = os.path.join(self.delta_dir, *relpath)
        delta_json = {}
        if os.path.exists(delta_scope_file):
            with open(delta_scope_file, 'r') as f:
                delta_json = json.load(f)
        return delta_json


class DeviceStore(EntityStore):
    def __init__(self, *path_args):
        if PY2:
            super(DeviceStore, self).__init__(*path_args)
        else:
            super().__init__(*path_args)

    def has_topology_info_changes(self, entity):
        updateGroupsNeeded = True
        for scope in ["Key+Inventory+ConfigState"]:
            fname = scope.replace('+', '_') + ".json"
            old_json = self.load_master(entity.device_type,
                                        entity._DeviceKey, fname)
            new_json = entity.entityjson
            if ('System' not in old_json) or (len(old_json['System']) <= 0):
                return updateGroupsNeeded
            if ('System' not in new_json) or (len(new_json['System']) <= 0):
                return updateGroupsNeeded
            influencers = entity._get_topology_influencers()
            for comp in influencers:
                # build a hashmap of old keys
                hmap = {}
                for comp_inst in old_json.get(comp, []):
                    hmap[comp_inst['Key']] = comp_inst

                for comp_inst in new_json.get(comp, []):
                    # check if new key is present in old map
                    # if not present, new entry
                    if comp_inst['Key'] not in hmap:
                        return updateGroupsNeeded
                    # ignore already visited nodes
                    if hmap[comp_inst['Key']] == None:
                        continue
                    # check if influencers are modified!

                    for field in influencers[comp]:
                        if field not in comp_inst or \
                                field not in hmap[comp_inst['Key']]:
                            continue
                        if comp_inst[field] != hmap[comp_inst['Key']][field]:
                            return updateGroupsNeeded
                    # visited node
                    hmap[comp_inst['Key']] = None
                for comp_inst in old_json.get(comp, []):
                    if hmap[comp_inst['Key']]:
                        return updateGroupsNeeded
        return False

    def store_entity(self, entity):
        for scope in ["Key+Inventory+ConfigState", "Metrics", "Health"]:
            monitorfilter = CreateMonitorScopeFilter(scope)
            dscope = DiffScopeFilter(DiffScope.Added, DiffScope.Modified)
            if scope == "Metrics":
                dscope.add(DiffScope.Same)
            else:
                dscope.add(DiffScope.Deleted)
            diff_filter = DiffFilter(scope=dscope, style=DiffStyle.Standard)
            fname = scope.replace('+', '_') + ".json"
            self.store(entity.get_json_device(monitorfilter),
                       diff_filter, fname, DeltaComputer.device_json,
                       [entity.device_type, entity._DeviceKey])
        ctree = entity.ContainmentTree
        if 'System' in ctree:
            self.store({'System': ctree['System']},
                       None, 'ContainmentTree.json',
                       DeltaComputer.tree_with_instances,
                       [entity.device_type, entity._DeviceKey])
