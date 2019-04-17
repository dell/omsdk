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

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class iBaseJobApi(object):

    def __init__(self, entity, jobenum):
        self.entity = entity
        self.jobenum = jobenum
        self.reset()

    def reset(self):
        self.last_job = None
        self.jobs_json = {}

    def get_jobs(self):
        return self.entity._get_entries(self.jobs_json, self.jobenum)

    def delete_all_jobs(self):
        pass

    def get_job_details(self, jobid):
        pass

    def get_job_status(self, jobid):
        pass


class iBaseLogApi(object):

    def __init__(self, entity, logenum, logtypesen):
        self.entity = entity
        self.logenum = logenum
        self.logtypesen = logtypesen

    def get_logs(self):
        return self.entity._get_entries(self.jobs_json, self.jobenum)

    def clear_logs(self):
        return self.entity._get_entries(self.jobs_json, self.jobenum)

