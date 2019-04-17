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
from enum import Enum
from omsdk.sdkcreds import ProtocolCredentialsFactory, CredentialsEnum
from datetime import datetime
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkcenum import TypeHelper

import sys
import logging

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

logger = logging.getLogger(__name__)


class ProtocolBase(object):
    def operation(self, protocmds, cmdname, *args):
        pass

    def _build_ops(self, protocmds, cmdname, *args):
        toargs = {}
        if not "Parameters" in protocmds[cmdname]:
            logger.debug(self.proto.ipaddr+": No parameters")
        elif len(protocmds[cmdname]["Parameters"]) != len(args):
            logger.error(self.proto.ipaddr+ ": Too many args")
            return {'Status': 'Failed', 'Message': 'Client Side: Too many arguments'}
        else:
            counter = 0
            for (var, arg, field, val, dest) in protocmds[cmdname]["Parameters"]:
                if (args[counter] is None):
                    myval = ""
                else:
                    args_fixed = args[counter]
                    if PY2 and (val == str and type(args_fixed) == unicode):
                        args_fixed = args_fixed.encode('ascii', 'ignore')
                    if not TypeHelper.belongs_to(val, args_fixed):
                        return {'Status': 'Failed', 'Message': 'Client Side: Argument ' + str(counter) + " got " + str(
                            type(args_fixed)) + "! Must be: " + val.__name__}
                    try:
                        if (val == datetime) and args_fixed.year == 1970:
                            myval = "TIME_NOW"
                        elif (val == datetime):
                            myval = datetime.strftime(args_fixed, "%Y%m%d%H%M%S")
                        else:
                            myval = TypeHelper.resolve(args_fixed.value)
                    except Exception as ex:
                        myval = args_fixed
                toargs[var] = myval
                if dest != None:
                    toargs[var] = dest(toargs[var])
                #logger.debug(self.proto.ipaddr+" : var "+var + "<=>" + str(toargs[var]))
                counter = counter + 1
        return {'Status': 'Success', 'retval': toargs}
