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
from argparse import ArgumentParser
from omsdk.sdkfile import LocalFile
from omsdk.sdkcenum import TypeHelper
from omsdk.catalog.sdkupdatemgr import UpdateManager
from omsdk.catalog.sdkhttpsrc import DownloadProtocolEnum
from omdrivers.helpers.iDRAC.UpdateHelper import UpdateHelper
from omsdk.omlogs.Logger import LogManager, LoggerConfigTypeEnum
import sys
import logging

# LogManager.setup_logging()
logger = logging.getLogger(__name__)


def RepoBuilder(arglist):
    parser = ArgumentParser(description='Local Repository Builder')
    parser.add_argument('-C', '--catalog',
                        action="store", dest="catalog", nargs='?',
                        default='Catalog', type=str,
                        help="Name of the Catalog file that contains the info about needed DUPs")
    parser.add_argument('-f', '--folder',
                        action="store", dest="folder", type=str,
                        help="folder from where repository is built")
    parser.add_argument('-c', '--components',
                        action="store", dest="component", nargs='+',
                        help="components for which the DUPs are requested.")
    parser.add_argument('-s', '--site',
                        action="store", dest="site", type=str, nargs='?',
                        default='downloads.dell.com',
                        help="models for which the DUPs are requested.")
    parser.add_argument('-p', '--protocol',
                        action="store", dest="protocol", nargs='?',
                        default='HTTP', choices=['HTTP', 'FTP', 'NoOp', 'HashCheck'],
                        help="models for which the DUPs are requested.")
    parser.add_argument('-v', '--verbose',
                        action="store_true", help="verbose mode")
    parser.add_argument('-D', '--download-dups',
                        action="store_true", dest="dld_dups", help="download DUPs")
    parser.add_argument('-l', '--download-catalog',
                        action="store_true", dest="dld_catalog", help="download catalog")
    parser.add_argument('-b', '--build-catalog',
                        action="store_true", dest="build_catalog", help="build catalog")

    options = parser.parse_args(arglist)
    if not options.component:
        options.component = []

    if options.folder is None:
        print("Folder must be provided")
        return -1

    if options.verbose is None:
        options.verbose = False

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not options.dld_dups and not options.build_catalog and \
            not options.dld_catalog:
        options.dld_catalog = True
        options.build_catalog = True
        options.dld_dups = True

    options.protocol = TypeHelper.convert_to_enum(options.protocol,
                                                  DownloadProtocolEnum)

    updshare = LocalFile(local=options.folder, isFolder=True)
    if not updshare.IsValid:
        print("Folder is not writable!")
        return -2

    if options.protocol != DownloadProtocolEnum.HashCheck:
        print("Configuring Update Share...")
    UpdateManager.configure(updshare, site=options.site,
                            protocol=options.protocol)

    if options.dld_catalog:
        if options.protocol != DownloadProtocolEnum.HashCheck:
            print("Updating Catalog from downloads.dell.com...")
        UpdateManager.update_catalog()
    if options.build_catalog:
        if options.protocol != DownloadProtocolEnum.HashCheck:
            print("Building Repository Catalog ....")
            UpdateHelper.build_repo(options.catalog, True, *options.component)
    if options.dld_dups:
        if options.protocol != DownloadProtocolEnum.HashCheck:
            print("Downloading DUPs ...")
        UpdateManager.update_cache(options.catalog)


if __name__ == "__main__":
    RepoBuilder(sys.argv[1:])
