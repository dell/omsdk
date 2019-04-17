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
from omsdk.sdkcenum import TypeHelper
from omsdk.typemgr.FieldType import FieldType
from omsdk.typemgr.TypeState import TypeState, TypeBase
from omsdk.sdkcunicode import UnicodeStringWriter
import sys
import re
import io

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


# private
#
# def __init__(self, fname, alias, parent=None, volatile=False)
# def __eq__, __ne__, __lt__, __le__, __gt__, __ge__
# def __getattr__
# def __delattr__
# def __setattr__
# def _copy(self, other)
# def _commit(self)
# def _reject(self)
# @_changed
#
# def __str__, __repr__
#
# def _replicate(self, obj, parent)
# def _set_index(self, index=1)
#
# protected:
#
# def my_accept_value(self, value):
#
# public:
# def is_changed(self)
# def fix_changed(self)
# def copy(self, other, commit= False)
# def commit(self)
# def reject(self)
# def freeze(self)
# def unfreeze(self)
# def Properties(self):
#
# def get_root(self)


class ClassType(TypeBase):

    def __init__(self, fname, alias, parent=None, volatile=False, modifyAllowed=True, deleteAllowed=True):
        if PY2:
            super(ClassType, self).__init__()
        else:
            super().__init__()
        self._alias = alias
        self._fname = fname
        self._volatile = volatile
        self._parent = parent
        self._composite = False
        self._index = 1
        self._modifyAllowed = modifyAllowed
        self._deleteAllowed = deleteAllowed

        self._freeze = False

        self.__dict__['_state'] = TypeState.UnInitialized
        self.__dict__['_attribs'] = {}
        self.__dict__['_ign_attribs'] = ()
        self.__dict__['_ign_fields'] = ()

    # Value APIs
    def __getattr__(self, name):
        if name in self.__dict__ and name not in ['_removed']:
            return self.__dict__[name]
        raise AttributeError('Invalid attribute ' + name)

    # Value APIs
    def __setattr__(self, name, value):
        # Do not allow access to internal variables
        if name in ['_removed', '_state']:
            raise AttributeError('Invalid attribute ' + name)

        # Freeze mode: No sets allowed
        if '_freeze' in self.__dict__ and self._freeze:
            raise ValueError('object in freeze mode')

        # allow updates to other fields except _value
        # should we allow updates to  '_type', '_alias', '_fname'?
        if name in ['_alias', '_fname', '_volatile', '_parent',
                    '_composite', '_index', '_freeze',
                    '_modifyAllowed', '_deleteAllowed', '_attribs']:
            self.__dict__[name] = value
            return

        # Does it make sense to have create-only attribute!
        # Create-only attribute : No updates allowed
        # if not self._modifyAllowed and \
        #   self._state in [TypeState.Committed, TypeState.Changing]:
        #    raise ValueError('updates not allowed to this object')

        # CompositeClass : sets not allowed in composite classes
        if self._composite:
            raise AttributeError('composite objects cannot be modified')

        # value is None, object was committed; ==> no change
        # value is actually a object!!
        if value is None and \
                self._state in [TypeState.Committed, TypeState.Changing]:
            return

        if name not in self.__dict__:
            if not isinstance(value, TypeBase):
                raise AttributeError(name + ' attribute not found')
            self.__dict__[name] = value
        elif isinstance(self.__dict__[name], FieldType):
            self.__dict__[name]._value = value
        elif isinstance(self.__dict__[name], ClassType):
            not_implemented
        else:
            raise ValueError('value does not belong to FieldType')

        if self._state in [TypeState.UnInitialized, TypeState.Precommit, TypeState.Initializing]:
            self.__dict__['_state'] = TypeState.Initializing
        elif self._state in [TypeState.Committed, TypeState.Changing]:
            if self._values_changed(self.__dict__, self.__dict__['_orig_value']):
                self.__dict__['_state'] = TypeState.Committed
            else:
                self.__dict__['_state'] = TypeState.Changing
        else:
            print("Should not come here")

        if self.is_changed() and self._parent:
            self._parent.child_state_changed(self, self._state)

    # Value APIs
    def __delattr__(self, name):
        # Do not allow access to internal variables
        if name in ['_orig_value', '_track', '_freeze', '_type',
                    '_value', '_volatile', '_composite']:
            raise AttributeError('Invalid attribute ' + name)

        # Freeze mode - don't allow any updates
        if '_freeze' in self.__dict__ and self._freeze:
            raise AttributeError('object in freeze mode')

        if name in self.__dict__:
            del self.__dict__[name]

        if self._state in [TypeState.UnInitialized, TypeState.Precommit, TypeState.Initializing]:
            self.__dict__['_state'] = TypeState.Initializing
        elif self._state in [TypeState.Committed, TypeState.Changing]:
            if self._values_changed(self.__dict__, self.__dict__['_orig_value']):
                self.__dict__['_state'] = TypeState.Committed
            else:
                self.__dict__['_state'] = TypeState.Changing
        else:
            print("Should not come here")

    # Value APIs
    def my_accept_value(self, value):
        return True

    def _ignore_attribs(self, *ign_attribs):
        self.__dict__['_ign_attribs'] = ign_attribs

    def _ignore_fields(self, *ign_fields):
        self.__dict__['_ign_fields'] = ign_fields

    # State APIs:
    def is_changed(self):
        return self._state in [TypeState.Initializing, TypeState.Precommit, TypeState.Changing]

    def _copy_state(self, source, dest):
        for i in source:
            if i.startswith('_'): continue
            if i not in dest:
                dest[i] = source[i]

        for i in dest:
            if i.startswith('_'): continue
            if i not in source: del dest[i]

    def _values_changed(self, source, dest):
        for i in source:
            if i.startswith('_'): continue
            if i not in dest: return False
            if source[i].is_changed(): return False

        for i in dest:
            if i.startswith('_'): continue
            if i not in source: return False
            if dest[i].is_changed(): return False

        return True

    # State : to Committed
    # allowed even during freeze
    def commit(self, loading_from_scp=False):
        if self.is_changed():
            if not self._composite:
                if '_orig_value' not in self.__dict__:
                    self.__dict__['_orig_value'] = {}
                self._copy_state(source=self.__dict__,
                                 dest=self.__dict__['_orig_value'])
                for i in self.Properties:
                    self.__dict__[i].commit(loading_from_scp)
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
                    for i in self.Properties:
                        del self.__dict__[i]
                    self.__dict__['_state'] = TypeState.UnInitialized
                else:
                    self._copy_state(source=self.__dict__['_orig_value'],
                                     dest=self.__dict__)
                    self.__dict__['_state'] = TypeState.Committed
                    for i in self.Properties:
                        self.__dict__[i].reject()
        return True

    # Does not have children - so not implemented
    def child_state_changed(self, child, child_state):
        if child_state in [TypeState.Initializing, TypeState.Precommit, TypeState.Changing]:
            if self._state in [TypeState.UnInitialized, TypeState.Precommit]:
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
        for i in other.Properties:
            if i not in self.__dict__:
                self.__dict__[i] = other.__dict__[i].clone(parent=self)
            elif not self.__dict__[i]._volatile:
                self.__dict__[i].copy(other.__dict__[i])
        return True

    def _get_combined_properties(self, obj1, obj2):
        list1 = [i for i in obj1.__dict__ if not i.startswith('_')]
        list1.extend([i for i in obj2.__dict__ if not i.startswith('_')])
        return sorted(set(list1))

    # Compare APIs:
    def __lt__(self, other):
        # uses sorted order of attributes for comparision similar to tuples, list!
        if not isinstance(other, type(self)):
            raise TypeError('unorderable types: ' + type(self).__name__ +
                            ", " + type(other).__name__)
        combined_props = self._get_combined_properties(self, other)
        for i in combined_props:
            if i not in self.__dict__:
                return True
            if i not in other.__dict__:
                return False
            if self.__dict__[i].__lt__(other.__dict__[i]):
                return True
            if self.__dict__[i].__gt__(other.__dict__[i]):
                return False
        return False

    # Compare APIs:
    def __le__(self, other):
        # uses sorted order of attributes for comparision similar to tuples, list!
        if not isinstance(other, type(self)):
            raise TypeError('unorderable types: ' + type(self).__name__ +
                            ", " + type(other).__name__)
        combined_props = self._get_combined_properties(self, other)
        for i in combined_props:
            if i not in self.__dict__:
                return True
            if i not in other.__dict__:
                return False
            if self.__dict__[i].__lt__(other.__dict__[i]):
                return True
            if self.__dict__[i].__gt__(other.__dict__[i]):
                return False
        return True

    # Compare APIs:
    def __gt__(self, other):
        # uses sorted order of attributes for comparision similar to tuples, list!
        if not isinstance(other, type(self)):
            raise TypeError('unorderable types: ' + type(self).__name__ +
                            ", " + type(other).__name__)
        combined_props = self._get_combined_properties(self, other)
        for i in combined_props:
            if i not in self.__dict__:
                return False
            if i not in other.__dict__:
                return True
            if self.__dict__[i].__lt__(other.__dict__[i]):
                return False
            if self.__dict__[i].__gt__(other.__dict__[i]):
                return True
        return False

    # Compare APIs:
    def __ge__(self, other):
        # uses sorted order of attributes for comparision similar to tuples, list!
        if not isinstance(other, type(self)):
            raise TypeError('unorderable types: ' + type(self).__name__ +
                            ", " + type(other).__name__)
        combined_props = self._get_combined_properties(self, other)
        for i in combined_props:
            if i not in self.__dict__:
                return False
            if i not in other.__dict__:
                return True
            if self.__dict__[i].__lt__(other.__dict__[i]):
                return False
            if self.__dict__[i].__gt__(other.__dict__[i]):
                return True
        return True

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
        for i in self.Properties:
            self.__dict__[i].freeze()

    # Freeze APIs
    def unfreeze(self):
        self.__dict__['_freeze'] = False
        for i in self.Properties:
            self.__dict__[i].unfreeze()

    # Freeze APIs
    def is_frozen(self):
        return self.__dict__['_freeze']

    def _set_index(self, index=1):
        self._index = index
        for i in self.Properties:
            self.__dict__[i]._index = index

    def get_root(self):
        if self._parent is None:
            return self
        return self._parent.get_root()

    @property
    def Properties(self):
        return sorted([i for i in self.__dict__ if not i.startswith('_')])

    def _get_fields(self, obj):
        if PY2:
            return {k: v for k, v in obj.iteritems() if not k.startswith('_')}
        if PY3:
            return {k: v for k, v in obj.items() if not k.startswith('_')}

    def _clear_duplicates(self):
        for i in self.Properties:
            self.__dict__[i]._clear_duplicates()

    def add_attribute(self, name, value):
        self.__dict__['_attribs'][name] = value

    def reboot_required(self):
        for i in self.Properties:
            if self.__dict__[i].reboot_required():
                return True
        return False

    @property
    def Json(self):
        output = {}
        for i in self._attribs:
            if i not in self._ign_attribs:
                output[i] = self._attribs[i]
        output['_index'] = self._index
        output['_attributes'] = list(self._attribs.keys())

        for i in self.Properties:
            attr_name = i
            if self.__dict__[i]._alias is not None:
                attr_name = self.__dict__[i]._alias
            if attr_name in self._ign_fields:
                continue
            attr_name = re.sub('_.*', '', attr_name)
            if isinstance(self.__dict__[i], FieldType):
                output[attr_name] = TypeHelper.resolve(self.__dict__[i]._value)
            else:
                output[attr_name] = self.__dict__[i].Json
        return output

    @property
    def XML(self):
        return self._get_xml_string(True)

    @property
    def ModifiedXML(self):
        return self._get_xml_string(False)

    def _get_xml_string(self, everything=True, space='', deleted=False):
        s = UnicodeStringWriter()
        if not self._fname:
            # group object!!
            for i in self.Properties:
                if not self.__dict__[i].is_changed() and not everything:
                    continue
                attr_name = i
                if attr_name in self._ign_fields:
                    continue
                if '_' in attr_name:
                    attr_name = re.sub('_.*', '', attr_name)
                    attr_name = "{0}.{1}#{2}".format(self._alias,
                                                     self._index, attr_name)
                else:
                    attr_name = "{0}".format(attr_name)
                if isinstance(self.__dict__[i], FieldType):
                    if self.__dict__[i]._composite:
                        continue
                    if not self.__dict__[i]._modifyAllowed and deleted:
                        continue
                    value = TypeHelper.resolve(self.__dict__[i]._value)
                    if deleted: value = self.__dict__[i]._default_on_delete
                    s._write_output('  <Attribute Name="{0}">{1}</Attribute>\n'.format(
                        attr_name, value))
                else:
                    s._write_output(self.__dict__[i]._get_xml_string(everything, space + '  ', deleted))
            return s.getvalue()

        s._write_output(space + '<{0}'.format(self._fname))
        for i in self._attribs:
            if i not in self._ign_attribs:
                s._write_output(' {0}="{1}"'.format(i, self._attribs[i]))
        s._write_output('>\n')

        orig_len = len(s.getvalue())
        for i in self.Properties:
            if not self.__dict__[i].is_changed() and not everything:
                continue
            attr_name = i
            if attr_name in self._ign_fields:
                continue
            if isinstance(self.__dict__[i], FieldType):
                if not self.__dict__[i]._composite:
                    if not self.__dict__[i]._modifyAllowed and deleted:
                        continue
                    value = TypeHelper.resolve(self.__dict__[i]._value)
                    if deleted: value = self.__dict__[i]._default_on_delete
                    values = [value]
                    if self.__dict__[i]._list:
                        values = value.split(',')
                    for val in values:
                        s._write_output(space +
                                        '  <Attribute Name="{0}">{1}</Attribute>\n'.format(
                                            attr_name, val))
            else:
                s._write_output(self.__dict__[i]._get_xml_string(everything, space + '  ', deleted))
        new_len = len(s.getvalue())
        if new_len == orig_len:
            return ""

        s._write_output(space + '</{0}>\n'.format(self._fname))
        return s.getvalue()

    def json_encode(self):
        return str(self)
