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
from omsdk.sdkdelta import DiffFilter, DiffStyle, DiffScope
from omsdk.sdkdelta import DeltaComputer
from omsdk.sdkstore import EntityStore
import logging

logger = logging.getLogger(__name__)


class TopologyBuilder:
    def __init__(self, entity_store):
        self.ctree = {}
        self.ctree_flags = {}
        self.assoc = {}
        self.entity_store = entity_store
        if self.entity_store is None: entity_store = EntityStore()
        self.builder_lock = threading.Lock()

    def load(self, entity_store=None):
        if entity_store is None: entity_store = self.entity_store
        with self.builder_lock:
            self.ctree = entity_store.load_master("Topology.json")
            self.ctree_flags = entity_store.load_master("Topology_Flags.json")
            self.assoc = entity_store.load_master("Assoc.json")

    def _find_group(self, group, ctree, fpath=''):
        if group in ctree:
            return (ctree[group], fpath + "/" + group)
        for g in ctree:
            if isinstance(ctree[g], dict) and len(ctree[g]) > 0:
                (c, cf) = self._find_group(group, ctree[g], fpath + "/" + g)
                if c is not None:
                    return (c, cf)
        return (None, None)

    def find_group(self, group):
        return self._find_group(group, self.ctree)

    def _do_update(self, parent, name, entry, update=False, static=False):
        (g, gf) = self._find_group(parent, self.ctree, '')
        if (g is not None) and (name not in g):
            if update:
                g[name] = entry
                self.ctree_flags[gf + '/' + name] = static
            return True
        return False

    def add_group(self, gname, parent=None, static=False):
        if parent == None:
            if gname not in self.ctree:
                self.ctree[gname] = {}
                self.ctree_flags['/' + gname] = static
            return True
        retval = False
        if self._do_update(parent, gname, {}, False, static):
            with self.builder_lock:
                retval = self._do_update(parent, gname, {}, True, static)
        return retval

    def add_device(self, entry, parent):
        if parent == None:
            return False
        key = '-'.join(entry)
        retval = False
        if self._do_update(parent, key, entry, False):
            with self.builder_lock:
                retval = self._do_update(parent, key, entry, True)
        return retval

    def _check_assoc(self, srctree, duptree):
        if isinstance(srctree, str) or isinstance(srctree, list):
            return srctree == duptree
        for i in srctree:
            if (i not in duptree) or \
                    not self._check_assoc(srctree[i], duptree[i]):
                return False
        for i in duptree:
            if i not in srctree:
                return False
        return True

    def remove_assoc(self, *args):
        retval = True

        parent, child, assoc = None, None, self.assoc
        for entry in args:
            child = entry
            child_key = '-'.join(child)
            if parent:
                parent_key = '-'.join(parent)
                logger.debug('Deassoc(parent=' + parent_key + ", child=" + child_key + ")")
                with self.builder_lock:
                    assoc = assoc[parent[0]][parent[1]]

            parent, child = child, None
        if parent and parent[0] in assoc and parent[1] in assoc[parent[0]]:
            del assoc[parent[0]][parent[1]]

        return retval

    def add_assoc(self, *args):
        retval = True

        parent, child, assoc = None, None, self.assoc
        for entry in args:
            child = entry
            child_key = '-'.join(child)
            if parent:
                parent_key = '-'.join(parent)
                logger.debug('Assoc(parent=' + parent_key + ", child=" + child_key + ")")
                with self.builder_lock:
                    if parent[0] not in assoc:
                        assoc[parent[0]] = {}
                    if parent[1] not in assoc[parent[0]]:
                        assoc[parent[0]][parent[1]] = {}
                    if child[0] not in assoc[parent[0]][parent[1]]:
                        assoc[parent[0]][parent[1]][child[0]] = {}
                    assoc = assoc[parent[0]][parent[1]]

            parent, child = child, None
        if parent and assoc:
            assoc[parent[0]] = parent[1]

        return retval

    def store(self, entity_store=None):
        if entity_store is None: entity_store = self.entity_store
        diff_filter = DiffFilter()
        with self.builder_lock:
            entity_store.store(self.ctree_flags, diff_filter,
                               "Topology_Flags.json", DeltaComputer.tree_without_instances)
            entity_store.store(self.ctree, diff_filter,
                               "Topology.json", DeltaComputer.tree_without_instances)
            entity_store.store(self.assoc, diff_filter,
                               "Assoc.json", DeltaComputer.tree_with_instances)

    def printx(self):
        logger.debug(self.ctree)
        logger.debug(self.ctree_flags)
        logger.debug(self.assoc)
