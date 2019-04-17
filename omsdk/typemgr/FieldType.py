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
from omsdk.sdkcunicode import UnicodeHelper
from omsdk.typemgr.TypeState import TypeState, TypeBase
import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
import logging

logger = logging.getLogger(__name__)

# private
#
# def __init__(self, init_value, typename, fname, alias, parent=None, volatile=False)
# def __eq__, __ne__, __lt__, __le__, __gt__, __ge__
# def __str__, __repr__
# def __getattr__
# def __delattr__
# def __setattr__
#
# protected:
#
# def my_accept_value(self, value):
#
# public:
# def is_changed(self)
# def sanitized_value(self):
# def copy(self, other)
# def commit(self)
# def reject(self)
# def freeze(self)
# def unfreeze(self)
# def is_frozen(self)
# def json_encode(self)
# def child_state_changed(self, child, child_state)
# def parent_state_changed(self, new_state)

class FieldType(TypeBase):

    def __init__(self, init_value, typename, fname, alias, parent=None, volatile=False, modifyAllowed = True, deleteAllowed = True, rebootRequired=False, default_on_delete=''):
        if PY2:
            super(FieldType, self).__init__()
        else:
            super().__init__()
        self._type  = typename
        self._alias = alias
        self._fname = fname
        self._volatile = volatile
        self._parent = parent
        self._composite = False
        self._index = 1
        self._modifyAllowed = modifyAllowed
        self._deleteAllowed = deleteAllowed
        self._rebootRequired = rebootRequired
        self._default_on_delete = default_on_delete
        self._list = False

        self._freeze = False

        self.__dict__['_state'] = TypeState.UnInitialized
        self._value = init_value

    # Value APIs
    def __getattr__(self, name):
        if name in self.__dict__ and name not in ['_orig_value']:
            return self.__dict__[name]
        elif name == '_optimal' and self._composite:
            return tuple(sorted([i for i in self.__dict__['_value'] \
                                 if i._value is not None]))
        raise AttributeError('Invalid attribute ' + name)

    @property
    def Value(self):
        return self._value

    @property
    def OptimalValue(self):
        return (self._optimal if self._composite else self._value)

    #deprecate this. replace with Property
    def get_value(self):
        return self._value

    # Value APIs
    def __setattr__(self, name, value):
        # Do not allow access to internal variables
        if name in ['_orig_value', '_state']:
            raise AttributeError('Invalid attribute ' + name)

        # Freeze mode: No sets allowed
        if '_freeze' in self.__dict__ and self._freeze:
            raise ValueError('object in freeze mode')

        # allow updates to other fields except _value
        # should we allow updates to  '_type', '_alias', '_fname'?
        if name not in ['_value']:
            self.__dict__[name] = value
            return

        # Create-only attribute : No updates allowed
        if not self._modifyAllowed and \
           self._state in [TypeState.Committed, TypeState.Changing]:
            raise ValueError('updates not allowed to this object')

        # CompositeField : sets not allowed in composite fields
        if self._composite:
            raise AttributeError('composite objects cannot be modified')

        # value is None, object was committed; ==> no change
        if value is None and \
            self._state in [TypeState.Committed, TypeState.Precommit, TypeState.Changing]:
            return 

        # Validate value and convert it if needed
        valid = False
        msg = None
        if value is None or TypeHelper.belongs_to(self._type, value):
            valid = True
        elif type(self) == type(value):
            value = value._value
            valid = True
        elif UnicodeHelper.is_string(value):
            value = UnicodeHelper.stringize(value)
            # expected value is int
            if self._type == int:
                value = int(value)
                valid = True
            # expected value is bool
            elif self._type == bool:
                value = bool(value)
                valid = True
            # expected value is str
            elif self._type == str:
                valid = True
            # expected value is enumeration
            elif TypeHelper.is_enum(self._type):
                newvalue = TypeHelper.convert_to_enum(value, self._type)
                if newvalue is not None:
                    value = newvalue
                    valid = True
                else:
                    msg = str(value) + " is not " + str(self._type)
            else:
                msg = str(value) + " cannot be converted to " + str(self._type)
        else:
            msg = "No type conversion found for '" + str(value) + "'. "\
                  "Expected " + str(self._type.__name__) + ". Got " +\
                  type(value).__name__

        if valid and not self.my_accept_value(value):
            msg = type(self).__name__ +" returned failure for " + str(value)
            valid = False

        # if invalid, raise ValueError exception
        if not valid:
            raise ValueError(msg)

        # same value - no change
        if name in self.__dict__ and self._value == value:
            return

        # List fields, simply append the new entry!
        if self._list and name in self.__dict__ and self.__dict__[name]:
            value = self.__dict__[name] + "," + value

        # modify the value
        self.__dict__[name] = value

        if self._state in [TypeState.UnInitialized, TypeState.Precommit, TypeState.Initializing]:
            self.__dict__['_state'] = TypeState.Initializing
        elif self._state in [TypeState.Committed, TypeState.Changing]:
            if self._orig_value == self._value:
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
        if name in ['_orig_value', '_track', '_freeze', '_type', '_default_on_delete',
                    '_value', '_volatile', '_composite']:
            raise AttributeError('Invalid attribute ' + name)

        # Freeze mode - don't allow any updates
        if '_freeze' in self.__dict__ and self._freeze:
            raise AttributeError('object in freeze mode')

        if name in self.__dict__:
            del self.__dict__[name]

    def set_value(self, value):
        self._value = value

    # nulls the value
    def nullify_value(self):
        if '_value' in self.__dict__:
            self.__dict__['_value'] = None

        if self._state in [TypeState.UnInitialized, TypeState.Precommit, TypeState.Initializing]:
            self.__dict__['_state'] = TypeState.Initializing
        elif self._state in [TypeState.Committed, TypeState.Changing]:
            if self._orig_value == self._value:
                self.__dict__['_state'] = TypeState.Committed
            else:
                self.__dict__['_state'] = TypeState.Changing
        else:
            print("Should not come here")

        if self.is_changed() and self._parent:
            self._parent.child_state_changed(self, self._state)

    # Value APIs
    def my_accept_value(self, value):
        return True

    # Representation APIs
    def __str__(self):
        return str(self._value)

    # Representation APIs
    def sanitized_value(self):
        if '_value' not in self.__dict__ or self._value is None:
            return None
        return TypeHelper.resolve(self._value)

    # State APIs:
    def is_changed(self):
        return self._state in [TypeState.Initializing, TypeState.Changing]

    def reboot_required(self):
        return self.is_changed() and self._rebootRequired

    # State : to Committed
    # allowed even during freeze
    def commit(self, loading_from_scp = False):
        if self.is_changed() or self._state == TypeState.Precommit:
            if not self._composite:
                self.__dict__['_orig_value'] = self._value
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
                    del self.__dict__['_value']
                    self.__dict__['_state'] = TypeState.UnInitialized
                else:
                    self.__dict__['_value'] = self._orig_value
                    self.__dict__['_state'] = TypeState.Committed
        return True

    # Does not have children - so not implemented
    def child_state_changed(self, child, child_state):
        not_implemented

    # what to do?
    def parent_state_changed(self, new_state):
        not_implemented

    # Object APIs
    def copy(self, other):
        if isinstance(other, type(self)):
            self._value = other._value
            return True
        return False

    def print_commit(self):
        print(self._state)

    # Compare APIs:
    def __lt__(self, other):
        if self._state is TypeState.UnInitialized:
            return False
        if other is None:
            return False
        myvalue = self._value
        if isinstance(other, type(self)):
            othervalue = other._value
        elif isinstance(other, self._type):
            othervalue = other
        else:
            raise TypeError('cannot compare with ' + type(other).__name__)
        if myvalue is None and othervalue is not None:
            return True
        if myvalue is None and othervalue is None:
            return False
        return myvalue < othervalue

    # Compare APIs:
    def __le__(self, other):
        if self._state is TypeState.UnInitialized:
            return False
        if self._value is None and other is None:
            return True
        if self._value is not None and other is None:
            return False
        myvalue = self._value
        if isinstance(other, type(self)):
            othervalue = other._value
        elif isinstance(other, self._type):
            othervalue = other
        else:
            raise TypeError('cannot compare with ' + type(other).__name__)
        if myvalue is not None and othervalue is None:
            return False
        if myvalue is None and othervalue is not None:
            return True
        return myvalue <= othervalue

    # Compare APIs:
    def __gt__(self, other):
        if self._state is TypeState.UnInitialized:
            return False
        if self._value is None:
            return False
        if self._value is not None and other is None:
            return True
        myvalue = self._value
        if isinstance(other, type(self)):
            othervalue = other._value
        elif isinstance(other, self._type):
            othervalue = other
        else:
            raise TypeError('cannot compare with ' + type(other).__name__)
        if myvalue is not None and othervalue is None:
            return True
        return myvalue > othervalue

    # Compare APIs:
    def __ge__(self, other):
        if self._state is TypeState.UnInitialized:
            return False
        if self._value is None and other is None:
            return True
        if self._value is not None and other is None:
            return True
        myvalue = self._value
        if isinstance(other, type(self)):
            othervalue = other._value
        elif isinstance(other, self._type):
            othervalue = other
        else:
            raise TypeError('cannot compare with ' + type(other).__name__)
        if myvalue is None and othervalue is None:
            return True
        if myvalue is None and othervalue is not None:
            return False
        return myvalue >= othervalue

    # Don't allow comparision with string ==> becomes too generic
    # Compare APIs:
    def __eq__(self, other):
        if self._state is TypeState.UnInitialized:
            return False
        if self._value is None and other is None:
            return True
        if self._value is not None and other is None:
            return False
        myvalue = self._value
        if isinstance(other, type(self)):
            othervalue = other._value
        elif isinstance(other, self._type):
            othervalue = other
        else:
            raise TypeError('cannot compare with ' + type(other).__name__)
        if myvalue is None and othervalue is None:
            return True
        if myvalue is None and othervalue is not None:
            return True
        return myvalue == othervalue

    # Compare APIs:
    def __ne__(self, other):
        return not self.__eq__(other)

    # Freeze APIs
    def freeze(self):
        self._freeze = True

    # Freeze APIs
    def unfreeze(self):
        self.__dict__['_freeze'] = False

    # Freeze APIs
    def is_frozen(self):
        return self.__dict__['_freeze']

    def json_encode(self):
        return self._value

    def _clear_duplicates(self):
        pass

    def printx(self):
        print(str(type(self._value))+"<>"+str(self._type)+"::"+str(self._value))
