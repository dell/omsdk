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
from omsdk.version.sdkversion import PY2UC
import io

if PY2UC:
    import codecs


class UnicodeHelper(object):
    @staticmethod
    def is_string(ustring):
        return isinstance(ustring, str) or \
               (PY2UC and isinstance(ustring, unicode))

    @staticmethod
    def stringize(ustring):
        if PY2UC and isinstance(ustring, unicode):
            ustring = ustring.encode('ascii', 'ignore')
        return ustring


class UnicodeWriter(object):
    def __init__(self, name):
        self.name = name
        self.output = None
        
    def __enter__(self):
        if PY2UC:
            self.output = open(self.name, "w")
            # self.output = codecs.open(self.name, encoding='utf-8', mode='w')
        else:
            self.output = open(self.name, "w")
        return self

    def _write_output(self, line):
        if PY2UC:
            self.output.write(unicode(line))
        else:
            self.output.write(line)
                
    def __exit__(self, type, value, traceback):
        if self.output:
            self.output.close()
        return isinstance(value, TypeError)


class UnicodeStringWriter(object):
    def __init__(self):
        self.output = io.StringIO()
        
    def __enter__(self):
        return self

    def _write_output(self, line):
        if PY2UC:
            self.output.write(unicode(line))
        else:
            self.output.write(line)

    def getvalue(self):
        return self.output.getvalue()

    def __exit__(self, type, value, traceback):
        return isinstance(value, TypeError)
