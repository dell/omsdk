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
# Authors: Sachin Kumar
#
import os
import yaml
import tempfile
import logging.config

from enum import Enum

DEFAULT_LOGGER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "logging.yaml")
DEFAULT_LOGGER_LOG_FILE = os.path.join(tempfile.gettempdir(), "omsdk-logs.log")
LOGGER_LEVEL = None
logger = logging.getLogger(__name__)

# Logger Configuration Types
class LoggerConfigTypeEnum(Enum):
    BASIC = 1  # Basic Configuration
    CONFIG_FILE = 2  # Configuration File based Configuration



class LoggerConfiguration:
    @staticmethod
    def __load_config(path):
        try:
            with open(path, 'rt') as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

    def setup_logging(self, logger_config_file=DEFAULT_LOGGER_CONFIG_FILE,
                      logger_log_file=DEFAULT_LOGGER_LOG_FILE, logger_level=LOGGER_LEVEL):
        logger.info("Setting up Logging")
        # Check if file exists
        if os.path.exists(logger_config_file):
            self.__load_config(logger_config_file)
        logger.info("Setting up Logging -- FINISHED")


LogManager = LoggerConfiguration()
