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
from datetime import datetime, timedelta, date
import time


class SchTimer:
    def __init__(self, time_str=None, fmt="%Y-%m-%d", untilmin=24 * 60):
        if time_str is None:
            self.time = datetime.now()
        else:
            self.time = datetime.strptime(time_str, fmt)
        self.until = None
        if untilmin is not None:
            self.until = self.time + timedelta(minutes=untilmin)

    def __str__(self):
        mystr = "Time: " + str(self.time)
        if self.until is not None:
            mystr = mystr + "; Until: " + str(self.until)
        return mystr


TIME_NOW = SchTimer(time_str="1970-1-1", untilmin=None)
