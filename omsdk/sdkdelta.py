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
import sys
import json
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.sdkenum import Filter

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

DiffStyleMap = {
    "Standard": 1,
    "Formal": 2,
}
DiffStyle = EnumWrapper("DS", DiffStyleMap).enum_type

DiffScopeMap = {
    # added entries
    "Added": 1 << 0,
    # same entries
    "Same": 1 << 1,
    # Modified entries
    "Modified": 1 << 2,
    # Deleted entries
    "Deleted": 1 << 3,
    "Default": 1 << 0 | 1 << 2 | 1 << 3,
}
DiffScope = EnumWrapper("DSp", DiffScopeMap).enum_type


class DiffScopeFilter(Filter):
    def __init__(self, *args):
        if PY2:
            super(DiffScopeFilter, self).__init__(*args)
        else:
            super().__init__(*args)

    def allowedtype(self, scopeType):
        return type(scopeType) == type(DiffScope)

    def check(self, scopeEnum):
        return TypeHelper.belongs_to(DiffScope, scopeEnum)

    def all(self):
        return self._all(DiffScope)


class DiffFilter:
    DiffScopeDefault = DiffScopeFilter(DiffScope.Default)

    def __init__(self, style=DiffStyle.Standard, scope=DiffScopeDefault):
        self.style = style
        self.scope = scope

    def allow_scope(self, refscope):
        return self.scope.isset(refscope)

    def is_style(self, refstyle):
        return self.style == refstyle


class DeltaComputer:

    def __init__(self):
        pass

    @staticmethod
    def device_json(first, second, diff_filter=None):
        if not diff_filter:
            diff_filter = DiffFilter()
        result = {}
        system = []
        if 'System' in second:
            system = second['System']
        elif 'System' in first:
            system = first['System']

        deleted = result
        if diff_filter.allow_scope(DiffScope.Deleted):
            result["_deleted_instances"] = {}
            result["_deleted_comps"] = {}
            result["_deleted_attribs"] = {}

        added = result
        if diff_filter.allow_scope(DiffScope.Added):
            if diff_filter.is_style(DiffStyle.Formal):
                result["_added_instances"] = {}
                result["_added_comps"] = {}
                result["_added_attribs"] = {}
            else:
                added = {
                    "_added_instances": result,
                    "_added_comps": result,
                    "_added_attribs": result
                }

        modified = result
        if diff_filter.allow_scope(DiffScope.Modified):
            if diff_filter.is_style(DiffStyle.Formal):
                result["_modified_instances"] = {}
                result["_modified_attribs"] = {}
            else:
                modified = {
                    "_modified_instances": result,
                    "_modified_attribs": result
                }

        same = result
        if diff_filter.allow_scope(DiffScope.Same):
            if diff_filter.is_style(DiffStyle.Formal):
                result["_same_instances"] = {}
                result["_same_attribs"] = {}
            else:
                same = {
                    "_same_instances": result,
                    "_same_attribs": result
                }

        for comp in first:
            if comp not in second:
                # comp in first, not in second => deleted
                if diff_filter.allow_scope(DiffScope.Deleted):
                    deleted["_deleted_comps"][comp] = first[comp]
                continue
            # comp in both first and second
            kmap = {}
            # build a hashmap of component instances
            for entries in first[comp]:
                kmap[entries["Key"]] = entries

            for entries in second[comp]:
                # comp instance in second, not in first => added
                if entries["Key"] not in kmap:
                    if diff_filter.allow_scope(DiffScope.Added):
                        if comp not in added["_added_instances"]:
                            added["_added_instances"][comp] = []
                        added["_added_instances"][comp].append(entries)
                    continue

                # comp instance in both, compare attributes
                tomodify, tosame, toadd, todel = {}, {}, {}, {}
                if diff_filter.is_style(DiffStyle.Standard):
                    tosame, toadd = tomodify, tomodify
                first_entries = kmap[entries["Key"]]

                if first_entries is None:
                    if entries is not None:
                        for field in entries:
                            toadd[field] = entries[field]
                    continue

                for field in first_entries:
                    if entries is None or field not in entries:
                        todel[field] = first_entries[field]
                        continue
                    if field == "Key": continue
                    if first_entries[field] != entries[field]:
                        if diff_filter.allow_scope(DiffScope.Modified):
                            tomodify[field] = entries[field]
                    elif diff_filter.allow_scope(DiffScope.Same):
                        tosame[field] = entries[field]

                for field in entries:
                    if field not in first_entries:
                        toadd[field] = entries[field]
                # remove the entry from map - as it is visited
                kmap[entries["Key"]] = None

                if len(tomodify) == 0 and len(todel) == 0 and len(toadd) == 0:
                    # instance is same
                    if diff_filter.allow_scope(DiffScope.Same):
                        tosame["Key"] = entries["Key"]
                        if comp not in same["_same_instances"]:
                            same["_same_instances"][comp] = []
                        same["_same_instances"][comp].append(tosame)
                    continue
                elif len(tosame) == 0 and len(todel) == 0 and len(toadd) == 0:
                    if diff_filter.allow_scope(DiffScope.Modified):
                        tomodify["Key"] = entries["Key"]
                        if comp not in modified["_modified_instances"]:
                            modified["_modified_instances"][comp] = []
                        modified["_modified_instances"][comp].append(tomodify)
                    continue

                if len(tomodify) > 0:
                    tomodify["Key"] = entries["Key"]
                    # insert the tomodify into result array
                    if diff_filter.allow_scope(DiffScope.Modified):
                        if comp not in modified["_modified_attribs"]:
                            modified["_modified_attribs"][comp] = []
                        modified["_modified_attribs"][comp].append(tomodify)
                if diff_filter.is_style(DiffStyle.Formal):
                    if len(tosame) > 0:
                        tosame["Key"] = entries["Key"]
                        # insert the tosame into result array
                        if diff_filter.allow_scope(DiffScope.Same):
                            if comp not in same["_same_attribs"]:
                                same["_same_attribs"][comp] = []
                            same["_same_attribs"][comp].append(tosame)
                    if len(toadd) > 0:
                        toadd["Key"] = entries["Key"]
                        # insert the toadd into result array
                        if diff_filter.allow_scope(DiffScope.Added):
                            if comp not in added["_added_attribs"]:
                                added["_added_attribs"][comp] = []
                            added["_added_attribs"][comp].append(toadd)
                if len(todel) > 0:
                    todel["Key"] = entries["Key"]
                    # insert the tomodify into result array
                    if diff_filter.allow_scope(DiffScope.Deleted):
                        if comp not in deleted["_deleted_attribs"]:
                            deleted["_deleted_attribs"][comp] = []
                        deleted["_deleted_attribs"][comp].append(todel)

            for entkey in kmap:
                if kmap[entkey] == None:
                    continue
                if diff_filter.allow_scope(DiffScope.Deleted):
                    if comp not in deleted["_deleted_instances"]:
                        deleted["_deleted_instances"][comp] = []
                    deleted["_deleted_instances"][comp].append(kmap[entkey])

        for comp in second:
            if comp not in first:
                if diff_filter.allow_scope(DiffScope.Added):
                    added["_added_comps"][comp] = second[comp]

        if 'System' not in result:
            result['System'] = system
        return result

    @staticmethod
    def _recurse_ctree(first, second, result, mod_added, mod_deleted,
                       diff_filter, leaf_has_instances):
        if isinstance(first, list):
            if leaf_has_instances:
                for comp in first:
                    if comp not in second:
                        if diff_filter.allow_scope(DiffScope.Deleted):
                            mod_deleted.append(comp)
                    else:
                        if diff_filter.allow_scope(DiffScope.Same):
                            result.append(comp)
                for comp in second:
                    if comp not in first:
                        if diff_filter.allow_scope(DiffScope.Added):
                            mod_added.append(comp)
            return result

        result["_deleted_tree"] = {}
        result["_deleted_instances"] = {}
        added = result
        if diff_filter.is_style(DiffStyle.Standard):
            added = {}
            added["_added_tree"] = result
            added["_added_instances"] = result
        else:
            result["_added_tree"] = {}
            result["_added_instances"] = {}
        for comp in first:
            # ignore delta special entries
            if comp.startswith("_"): continue
            if isinstance(first[comp], str):
                if comp not in second:
                    if diff_filter.allow_scope(DiffScope.Deleted):
                        result["_deleted_instances"][comp] = [first[comp]]
                elif first[comp] == second[comp]:
                    if diff_filter.allow_scope(DiffScope.Same):
                        result[comp] = first[comp]
                else:
                    if diff_filter.allow_scope(DiffScope.Deleted):
                        result["_deleted_instances"][comp] = [first[comp]]
                    if diff_filter.allow_scope(DiffScope.Added):
                        added["_added_instances"][comp] = [second[comp]]
                continue

            if comp not in second:
                if diff_filter.allow_scope(DiffScope.Deleted):
                    if isinstance(first[comp], list):
                        result["_deleted_instances"][comp] = []
                    else:
                        result["_deleted_tree"][comp] = first[comp]
                continue
            if comp not in result:
                if isinstance(first[comp], list):
                    result[comp] = []
                elif isinstance(first[comp], dict):
                    result[comp] = {}
                else:
                    added["_added_instances"][comp] = first[comp]
                    continue
            if comp not in added["_added_instances"]:
                added["_added_instances"][comp] = []
            if comp not in result["_deleted_instances"]:
                result["_deleted_instances"][comp] = []
            DeltaComputer._recurse_ctree(first[comp], second[comp],
                                         result[comp], added["_added_instances"][comp],
                                         result["_deleted_instances"][comp], diff_filter, leaf_has_instances)
        for comp in second:
            # ignore delta special entries
            if comp.startswith("_"): continue
            if comp not in first:
                if diff_filter.allow_scope(DiffScope.Added):
                    if isinstance(second[comp], list):
                        added["_added_instances"][comp] = second[comp]
                    else:
                        added["_added_tree"][comp] = second[comp]
        return result

    @staticmethod
    def replicate(obj):
        if isinstance(obj, list):
            return [DeltaComputer.replicate(i) for i in obj]
        elif isinstance(obj, dict):
            return dict([(x, DeltaComputer.replicate(obj[x])) for x in obj])
        else:
            return obj

    @staticmethod
    def _clean_tree(todel):
        if isinstance(todel, bool) or isinstance(todel, str):
            return False
        if isinstance(todel, list):
            return len(todel) <= 0
        td = []
        for i in todel:
            if DeltaComputer._clean_tree(todel[i]):
                td.append(i)
        for i in td:
            del todel[i]
        return len(todel) <= 0

    def tree_with_instances(first, second, diff_filter=None):
        if diff_filter is None: diff_filter = DiffFilter()
        first = DeltaComputer.replicate(first)
        second = DeltaComputer.replicate(second)
        result = DeltaComputer._recurse_ctree(first, second, {}, None, None,
                                              diff_filter, True)
        DeltaComputer._clean_tree(result)
        return result

    def tree_without_instances(first, second, diff_filter=None):
        if diff_filter is None: diff_filter = DiffFilter()
        first = DeltaComputer.replicate(first)
        second = DeltaComputer.replicate(second)
        result = DeltaComputer._recurse_ctree(first, second, {}, None, None,
                                              diff_filter, False)
        DeltaComputer._clean_tree(result)
        return result
