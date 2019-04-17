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
import os
import inspect

sys.path.append(os.getcwd())
from inspect import signature
from omsdk.sdkcenum import TypeHelper, EnumWrapper
import re
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

_membuiltin = ["__class__", "__delattr__", "__dict__", "__dir__", "__doc__", "__eq__", "__format__", "__ge__",
               "__getattribute__", "__gt__", "__hash__", "__init__", "__le__", "__lt__", "__module__", "__ne__",
               "__new__", "__reduce__", "__reduce_ex__", "__repr__", "__setattr__", "__sizeof__", "__str__",
               "__subclasshook__", "__weakref__"]

MemberType = EnumWrapper("omsdk.reflection.sdkapi.MemberType", {
    'Field': 'Field',
    'Private_Field': 'Private_Field',
    'Public_Field': 'Public_Field',
    'Method': 'Method',
    'Public_Method': 'Public_Method',
    'Private_Method': 'Private_Method'
}).enum_type


class SDKApiVisitor(object):
    def __init__(self):
        pass

    def method_start(self, method):
        pass

    def method_arg(self, arg):
        pass

    def method_arg_with_default(self, arg):
        pass

    def method_finish(self):
        pass

    def property_name(self, name):
        pass


class SDKApiInfo(object):
    def __init__(self):
        pass

    def get_members(self, obj, visitor, memtypeen):
        self.pfjson = {}
        return self._get_members(obj, visitor, memtypeen, "", "")

    def _get_members(self, obj, visitor, memtypeen, objname, c=""):
        to_see_private = []
        to_see_public = []
        for (mem_name, value) in inspect.getmembers(obj):
            mem_fqdn = objname + "." + mem_name
            if mem_fqdn in self.pfjson:
                continue

            if mem_name in _membuiltin:
                continue

            if (mem_name.endswith("mgr")):
                if (mem_name.startswith("_") or mem_name.startswith("my_")):
                    to_see_private.append([mem_fqdn, getattr(obj, mem_name)])
                else:
                    to_see_public.append([mem_fqdn, getattr(obj, mem_name)])

            if inspect.ismethod(value) or inspect.isfunction(value):
                mytype = MemberType.Method
                if (mem_name.startswith("_") or mem_name.startswith("my_")):
                    mytype = MemberType.Private_Method
                else:
                    mytype = MemberType.Public_Method
                if mytype == memtypeen or memtypeen == MemberType.Method:
                    self.pfjson[mem_fqdn] = 'done'
                    visitor.method_start(mem_fqdn)
                    self._get_args_str(visitor, obj, mem_name)
                    visitor.method_finish()
            else:
                mytype = MemberType.Field
                if (mem_name.startswith("_") or mem_name.startswith("my_")):
                    mytype = MemberType.Private_Field
                else:
                    mytype = MemberType.Public_Field
                if mytype == memtypeen or memtypeen == MemberType.Field:
                    self.pfjson[mem_fqdn] = 'done'
                    visitor.property_name(mem_fqdn)
        # printing only methods of public objects!!
        for obj2 in to_see_public:
            self._get_members(obj2[1], visitor, memtypeen, obj2[0], c + "  ")
        return True

    def _get_args_str(self, visitor, obj, method):
        rjson = self._get_args(obj, method)
        for arg in rjson:
            if len(arg) > 1:
                visitor.method_arg_with_default(arg[0], arg[1])
            else:
                visitor.method_arg(arg[0])

    def _get_args(self, obj, method):
        rjson = []
        sig = signature(getattr(obj, method))
        for param in sig.parameters.values():
            if param.default is param.empty:
                rjson.append([param.name])
            else:
                rjson.append([param.name, param.default])
        return rjson


class StringApiVisitor(SDKApiVisitor):
    def __init__(self, objname=""):
        self.objname = objname
        self.reset()

    def reset(self):
        self.mystring = self.objname
        self.comma = ""

    def method_start(self, method):
        self.mystring = self.mystring + method + "("

    def method_arg(self, arg):
        self.mystring = self.mystring + self.comma + arg
        self.comma = ","

    def method_arg_with_default(self, arg, defval):
        self.mystring = self.mystring + self.comma + arg + " = " + str(defval)
        self.comma = ","

    def method_finish(self):
        self.mystring = self.mystring + ")"
        logger.debug(self.mystring)
        self.reset()

    def property_name(self, name):
        self.mystring = name
        logger.debug(self.mystring)
        self.reset()
