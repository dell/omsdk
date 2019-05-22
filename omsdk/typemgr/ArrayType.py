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
from omsdk.typemgr.ClassType import ClassType
from omsdk.typemgr.TypeState import TypeState, TypeBase
from omsdk.typemgr.BuiltinTypes import StringField, IntField
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcunicode import UnicodeStringWriter
import sys
import io
import re
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


# private
#
# >>def __init__(self, mode, fname, alias, parent=None, volatile=False)
# def __init__(self, clsname, min_index=1, max_index=2)
#
# def __eq__, __ne__, __lt__, __le__, __gt__, __ge__
# def __str__, __repr__
#
# protected:
#
# def my_accept_value(self, value):
#
# public:
#
# def new(self, **kwargs):
# def find(self, **kwargs):
# def find_first(self, **kwargs):
# def remove(self, **kwargs):
#
# def is_changed(self)
# def copy(self, other, commit= False)
# def commit(self)
# def reject(self)
# def freeze(self)
# def unfreeze(self)
#
# def get_root(self)


class ArrayType(TypeBase):
    def __init__(self, clsname, parent=None, index_helper=None, loading_from_scp=False):
        if PY2:
            super(ArrayType, self).__init__()
        else:
            super().__init__()

        self._alias = None
        self._fname = clsname.__name__
        self._volatile = False
        self._parent = parent
        self._composite = False
        self._index = 1
        self._loading_from_scp = loading_from_scp
        if index_helper is None:
            index_helper = IndexHelper(1, 20)
        self._index_helper = index_helper
        # self._modifyAllowed = True

        self._cls = clsname
        self._entries = []

        self._keys = {}

        self._freeze = False

        # Special case for Array. Empty Array is still valid
        self.__dict__['_orig_value'] = []
        self.__dict__['_state'] = TypeState.Committed

    # Value APIs
    def __getattr__(self, name):
        matches = re.match('^Index_(\d+)$', name)
        if name in self.__dict__:
            return self.__dict__[name]
        elif matches:
            try:
                n = int(matches.group(1))
                if (n >= 0 and n < self.Length):
                    return self._entries[n]
            except Exception as ex:
                print(str(ex))
        raise AttributeError('Invalid attribute ' + name)

    # State APIs:
    def is_changed(self):
        return self._state in [TypeState.Initializing, TypeState.Changing]

    @property
    def Length(self):
        return len(self._entries)

    def _copy_state(self, source, dest):
        # from _entries to _orig_entries
        toadd = []
        for i in source:
            if i not in dest:
                toadd.append(i)

        toremove = []
        for i in dest:
            if i not in source:
                toremove.append(i)

        for i in toremove:
            dest.remove(i)

        for i in toadd:
            dest.append(i)

        return True

    def _get_key(self, entry):
        if hasattr(entry, 'Key'):
            key = entry.Key._value
            if key: key = str(key)
            return key
        else:
            return entry._index

    def _values_changed(self, source, dest):
        source_idx = []
        for entry in source:
            source_idx.append(self._get_key(entry))
        for entry in dest:
            if self._get_key(entry) not in source_idx:
                return False
            source_idx.remove(self._get_key(entry))
        return (len(source_idx) <= 0)

    def values_deleted(self):
        source_idx = []
        dest_entries = []
        for entry in self._entries:
            source_idx.append(self._get_key(entry))
        for entry in self.__dict__['_orig_value']:
            key = self._get_key(entry)
            if key not in source_idx:
                dest_entries.append(entry)
                continue
            source_idx.remove(key)
        return dest_entries

    # State : to Committed
    # allowed even during freeze
    def commit(self, loading_from_scp=False):
        if self.is_changed():
            if not self._composite:
                self._copy_state(source=self._entries,
                                 dest=self.__dict__['_orig_value'])
                self.__dict__['_orig_value'] = \
                    sorted(self.__dict__['_orig_value'], key=lambda entry: entry._index)
                for entry in self._entries:
                    entry.commit(loading_from_scp)
            if loading_from_scp:
                self.__dict__['_state'] = TypeState.Precommit
            else:
                self.__dict__['_state'] = TypeState.Committed
        return True

    # State : to Committed
    # allowed even during freeze
    def reject(self):
        if self.is_changed():
            if not self._composite:
                if '_orig_value' not in self.__dict__:
                    for i in self._entries:
                        del self._entries
                else:
                    self._copy_state(source=self.__dict__['_orig_value'],
                                     dest=self._entries)
                    for entry in self._entries:
                        entry.reject()
                        self._index_helper.restore_index(entry._index)
                    for i in self._entries:
                        self._keys[self._get_key(i)] = i
                self.__dict__['_state'] = TypeState.Committed
        return True

    # Does not have children - so not implemented
    def child_state_changed(self, child, child_state):

        if child_state in [TypeState.Initializing, TypeState.Precommit, TypeState.Changing]:
            if self._state == TypeState.UnInitialized:
                self.__dict__['_state'] = TypeState.Initializing
            elif self._state == TypeState.Committed:
                self.__dict__['_state'] = TypeState.Changing
        if self.is_changed() and self._parent:
            self._parent.child_state_changed(self, self._state)

    # what to do?
    def parent_state_changed(self, new_state):
        not_implemented

    # Object APIs
    def copy(self, other):
        if other is None or not isinstance(other, type(self)):
            return False
        for i in other._entries:
            if i not in self._entries:
                self._entries[i] = other._entries[i].clone(parent=self)
            elif not self._entries[i]._volatile:
                self._entries[i].copy(other._entries[i])
        return True

    def _get_combined_properties(self, obj1, obj2):
        list1 = [i for i in obj1.__dict__ if not i.startswith('_')]
        list1.extend([i for i in obj2.__dict__ if not i.startswith('_')])
        return sorted(set(list1))

    # Compare APIs:
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError('unorderable types: ' + type(self).__name__ +
                            ", " + type(other).__name__)
        combined_props = self._get_combined_properties(self, other)
        for i in combined_props:
            if i not in self.__dict__:
                return False
            if i not in other.__dict__:
                return False
            if self.__dict__[i].__ne__(other.__dict__[i]):
                return False
        return True

    # Compare APIs:
    def __ne__(self, other):
        return self.__eq__(other) != True

    # Freeze APIs
    def freeze(self):
        self._freeze = True
        for i in self._entries:
            self.__dict__[i].freeze()

    # Freeze APIs
    def unfreeze(self):
        self.__dict__['_freeze'] = False
        for i in self._entries:
            self.__dict__[i].unfreeze()

    # Freeze APIs
    def is_frozen(self):
        return self.__dict__['_freeze']

    def get_root(self):
        if self._parent is None:
            return self
        return self._parent.get_root()

    def my_accept_value(self, value):
        return True

    # State APIs:
    def is_changed(self):
        return self._state in [TypeState.Initializing, TypeState.Precommit, TypeState.Changing]

    def reboot_required(self):
        for i in self._entries:
            if i.reboot_required():
                return True
        return False

    def new(self, index=None, **kwargs):
        return self._new(index, False, **kwargs)

    def flexible_new(self, index=None, **kwargs):
        return self._new(index, True, **kwargs)

    def _new(self, index=None, add=False, **kwargs):
        if index is None and not self._index_helper.has_indexes():
            raise AttributeError('no more entries in array')
        entry = self._cls(parent=self, loading_from_scp=self._loading_from_scp)
        for i in kwargs:
            if i not in entry.__dict__ and add:
                if isinstance(kwargs[i], int):
                    entry.__dict__[i] = IntField(0, parent=self)
                else:
                    entry.__dict__[i] = StringField("", parent=self)
            entry.__setattr__(i, kwargs[i])
        if index is None and self._get_key(entry) is None:
            raise ValueError('key not provided')
        key = self._get_key(entry)
        if index is None and (key and key in self._keys):
            raise ValueError(self._cls.__name__ + " key " + str(key) + ' already exists')

        if index is None:
            index = self._index_helper.next_index()
        else:
            index = int(index)
        entry._set_index(index)
        self._entries.append(entry)
        self._keys[key] = entry
        self._sort()

        # set state!
        if self._state in [TypeState.UnInitialized, TypeState.Initializing]:
            self.__dict__['_state'] = TypeState.Initializing
        elif self._state in [TypeState.Committed, TypeState.Changing]:
            if self._values_changed(self._entries, self.__dict__['_orig_value']):
                self.__dict__['_state'] = TypeState.Committed
            else:
                self.__dict__['_state'] = TypeState.Changing
        else:
            print("Should not come here")

        if self.is_changed() and self._parent:
            self._parent.child_state_changed(self, self._state)
        return entry

    def _clear_duplicates(self):
        keys = {}
        toremove = []
        for entry in self._entries:
            strkey = self._get_key(entry)
            if strkey is None:
                toremove.append(entry)
            elif strkey in ["", "()"]:
                toremove.append(entry)
            elif strkey in keys:
                toremove.append(entry)
            keys[strkey] = entry

        for entry in toremove:
            self._entries.remove(entry)
            self._index_helper.restore_index(entry._index)
            strkey = self._get_key(entry)
            if strkey in self._keys:
                del self._keys[strkey]

        for entry in self._entries:
            self._index_helper.remove(entry._index)
        self._sort()

    # returns a list
    def find(self, **kwargs):
        return self._find(True, **kwargs)

    # returns the first entry
    def find_first(self, **kwargs):
        entries = self._find(False, **kwargs)
        if len(entries) > 0:
            return entries[0]
        return None

    def entry_at(self, index):
        for entry in self._entries:
            if entry._index == index:
                return entry
        return None

    def find_or_create(self, index=None):
        if not index:
            index = self._index_helper.next_index()
        else:
            self._index_helper.remove(index)
        for entry in self._entries:
            if entry._index == index:
                return entry
        return self.new(index)

    def remove(self, **kwargs):
        entries = self._find(True, **kwargs)
        return self._remove_selected(entries)

    def remove_matching(self, criteria):
        entries = self.find_matching(criteria)
        return self._remove_selected(entries)

    def _remove_selected(self, entries):
        if len(entries) <= 0:
            return entries

        for i in entries:
            try:
                self._entries.remove(i)
            except Exception as ex:
                logger.error(str(ex))
            self._index_helper.restore_index(i._index)
            key = self._get_key(i)
            if key in self._keys:
                del self._keys[key]
        self._sort()

        if self._state in [TypeState.UnInitialized, TypeState.Precommit, TypeState.Initializing]:
            self.__dict__['_state'] = TypeState.Initializing
        elif self._state in [TypeState.Committed, TypeState.Changing]:
            if self._values_changed(self._entries, self.__dict__['_orig_value']):
                self.__dict__['_state'] = TypeState.Committed
            else:
                self.__dict__['_state'] = TypeState.Changing
        else:
            print("Should not come here")

        if self.is_changed() and self._parent:
            self._parent.child_state_changed(self, self._state)
        return entries

    def _sort(self):
        self._entries = sorted(self._entries, key=lambda entry: entry._index)

    def _find(self, all_entries=True, **kwargs):
        output = []
        for entry in self._entries:
            found = True
            for field in kwargs:
                if field in entry.__dict__ and \
                        entry.__dict__[field]._value != kwargs[field]:
                    found = False
                    break
                if field in entry._attribs and \
                        entry._attribs[field] != kwargs[field]:
                    found = False
                    break
            if found:
                output.append(entry)
                if not all_entries: break
        return output

    def find_matching(self, criteria):
        output = []
        for entry in self._entries:
            if self.select_entry(entry, criteria):
                output.append(entry)
        return output

    def select_entry(self, entry, criteria):
        try:
            if 'self.' in criteria:
                logger.error("criteria cannot have self references!")
                return False
            criteria = criteria.replace('.parent', '._parent._parent')
            criteria = re.sub('([a-zA-Z0-9_.]+)\s+is\s+([^ \t]+)',
                              '(type(\\1).__name__ == "\\2")', criteria)
            logger.debug("Evaluating: " + criteria)
            return eval(criteria)
        except Exception as ex:
            logger.error(str(ex))

    @property
    def Properties(self):
        return self._entries

    @property
    def Json(self):
        output = []
        for entry in self:
            output.append(entry.Json)
        return output

    @property
    def XML(self):
        return self._get_xml_string(True)

    @property
    def ModifiedXML(self):
        return self._get_xml_string(False)

    def _get_xml_string(self, everything=True, space='', deleted=False):
        s = UnicodeStringWriter()
        for entry in self._entries:
            if not entry.is_changed() and not everything:
                continue
            s._write_output(entry._get_xml_string(everything, space, False))
        for entry in self.values_deleted():
            s._write_output(entry._get_xml_string(True, space, True))
        return s.getvalue()

    def __iter__(self):
        return ArrayTypeIterator(self)


class ArrayTypeIterator:

    def __init__(self, array):
        self.array = array
        self.current = -1
        self.high = self.array.Length

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.current >= self.high:
            raise StopIteration
        else:
            self.current += 1
            if self.current >= self.high:
                raise StopIteration
            return self.array._entries[self.current]


class IndexHelper(object):
    def __init__(self, min_value, max_value):
        if PY2:
            super(IndexHelper, self).__init__()
        else:
            super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.indexes_free = [i for i in range(self.min_value, self.max_value + 1)]
        self.reserve = []

    def next_index(self):
        if len(self.indexes_free) > 0:
            index = self.indexes_free[0]
            self.indexes_free.remove(index)
            return index
        raise IndexError('ran out of all entries')

    def unusable(self, index):
        if index in self.indexes_free:
            self.indexes_free.remove(index)
            self.reserve.append(index)

    def remove(self, index):
        if index in self.indexes_free:
            self.indexes_free.remove(index)

    def restore_index(self, index):
        if index not in self.reserve and \
                index not in self.indexes_free:
            self.indexes_free.append(index)
            self.indexes_free = sorted(self.indexes_free)

    def has_indexes(self):
        return len(self.indexes_free) > 0

    def printx(self):
        print(self.__dict__)


class FQDDHelper(IndexHelper):
    def __init__(self):
        if PY2:
            super(FQDDHelper, self).__init__(1, 30)
        else:
            super().__init__(1, 30)
