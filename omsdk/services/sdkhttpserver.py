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
# Authors: Karthik Prabhu
#
import ssl
import logging
import posixpath
import os
import socket
import yaml
import json
import re
from urllib.parse import urlparse, unquote
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer
from random import choice
from socketserver import ThreadingMixIn
from omsdk.sdkcenum import EnumWrapper, TypeHelper

logger = logging.getLogger(__name__)

SDKServerProtocolEnum = EnumWrapper('SDKServerProtocolEnum', {
    'HTTP': "http",
    'HTTPS': "https"
}).enum_type

SDKServerStateEnum = EnumWrapper('SDKServerStateEnum', {
    'Running': 1,
    'Stopped': 2
}).enum_type


class SDKHTTPServer(ThreadingMixIn, HTTPServer):
    def __init__(self, base_path, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.RequestHandlerClass.base_path = base_path


class SDKServerRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = posixpath.normpath(unquote(urlparse(path).path))
        words = path.split('/')
        words = filter(None, words)
        path = self.base_path

        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)

        return path

    def do_GET(self):
        try:
            file_path = self.translate_path(self.path)

            with open(file_path) as f:
                file_content = f.read().encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text-plain')
            self.end_headers()
            self.wfile.write(file_content)
            f.close()

            return

        except IOError:
            self.send_error(HTTPStatus.NOT_FOUND, 'File Not Found: %s' % self.path)

    def do_PUT(self):
        logger.debug(self.headers)
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        self.send_response(HTTPStatus.OK)

        file_path = self.translate_path(self.path)

        try:
            with open(file_path, 'w+') as f:
                f.write(content.decode("utf-8"))
            logger.info("Successfully exported data to file...")
        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

        self.send_header('Content-type', 'text-plain')
        self.end_headers()

        return


class SDKHTTPServerRequestHandler(SDKServerRequestHandler):
    pass


class SDKHTTPSServerRequestHandler(SDKServerRequestHandler):
    pass


class SDKServer:
    # SDK Server instance and services data (Singleton)
    __sdk_server_instance = None
    __http_protocol = TypeHelper.resolve(SDKServerProtocolEnum.HTTP)
    __https_protocol = TypeHelper.resolve(SDKServerProtocolEnum.HTTPS)

    __server = {
        "http": {
            "server_instance": None,
            "server_config": {
                "port": None,
                "directory": None,
                "state": SDKServerStateEnum.Stopped,
                "handler": SDKHTTPServerRequestHandler,
            }
        },
        "https": {
            "server_instance": None,
            "server_config": {
                "port": None,
                "directory": None,
                "state": SDKServerStateEnum.Stopped,
                "handler": SDKHTTPSServerRequestHandler,
                "server_certificate": None,
                "private_key": None,
                "ca_chain_certificate": None
            }
        }
    }

    @staticmethod
    def __load_config(path):
        file_type = path.split(os.sep)[-1].split(".")[-1].lower()
        try:
            with open(path, 'rt') as f:
                if file_type == "json":
                    config = json.load(f)
                elif file_type == "yaml" or file_type == "yml":
                    config = yaml.safe_load(f.read())
            return config

        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

        return None

    @staticmethod
    def load_server_configuration(configuration_file=os.path.join(os.path.dirname(__file__), "config",
                                                                  "sdk-server-config.json")):
        configuration = SDKServer.__load_config(configuration_file)

        if configuration is None:
            logger.error("No configuration available...")
        else:
            # Load HTTP Server configuration
            http_port = configuration[SDKServer.__http_protocol]["port"]
            http_directory = configuration[SDKServer.__http_protocol]["directory"]

            sdk_http_server = SDKServer.__server[SDKServer.__http_protocol]

            sdk_http_server["server_config"]["port"] = choice(http_port) if type(
                http_port) == range else http_port
            sdk_http_server["server_config"]["directory"] = http_directory

            # Load HTTPS Server configuration
            https_port = configuration[SDKServer.__https_protocol]["port"]
            https_directory = configuration[SDKServer.__https_protocol]["directory"]

            https_server_certificate = configuration[SDKServer.__https_protocol]["certificate"]
            https_private_key = configuration[SDKServer.__https_protocol]["private_key"]
            https_ca_chain_certificate = configuration[SDKServer.__https_protocol]["ca_chain_certificate"]
            sdk_https_server = SDKServer.__server[SDKServer.__https_protocol]

            sdk_https_server["server_config"]["port"] = choice(https_port) if type(
                https_port) == range else https_port
            sdk_https_server["server_config"]["directory"] = https_directory
            sdk_https_server["server_config"]["server_certificate"] = https_server_certificate
            sdk_https_server["server_config"]["private_key"] = https_private_key
            sdk_https_server["server_config"]["ca_chain_certificate"] = https_ca_chain_certificate

    @staticmethod
    def get_server_instance():
        if SDKServer.__sdk_server_instance is None:
            SDKServer()

        sdk_http_server = SDKServer.__server[SDKServer.__http_protocol]

        print(sdk_http_server["server_config"]["directory"])
        if sdk_http_server["server_instance"] is None:
            sdk_http_server["server_instance"] = SDKHTTPServer(
                sdk_http_server["server_config"]["directory"],
                ("", sdk_http_server["server_config"]["port"]),
                sdk_http_server["server_config"]["handler"])

        sdk_https_server = SDKServer.__server[SDKServer.__https_protocol]

        if sdk_https_server["server_instance"] is None:
            sdk_https_server["server_instance"] = SDKHTTPServer(
                sdk_https_server["server_config"]["directory"],
                ("", sdk_https_server["server_config"]["port"]),
                sdk_https_server["server_config"]["handler"])

            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_NONE
            context.check_hostname = False

            context.load_cert_chain(certfile=sdk_https_server["server_config"]["server_certificate"],
                                    keyfile=sdk_https_server["server_config"]["private_key"],
                                    password="pword")

            if sdk_https_server["server_config"]["ca_chain_certificate"] is not None:
                context.load_verify_locations(cafile=sdk_https_server["server_config"]["ca_chain_certificate"])

            sdk_https_server["server_instance"].socket = context.wrap_socket(
                sdk_https_server["server_instance"].socket, server_side=True)

        return SDKServer.__sdk_server_instance

    def __init__(self):
        if SDKServer.__sdk_server_instance is not None:
            logger.warning("SDK Server already instantiated..")

        SDKServer.__sdk_server_instance = self

    def start_server(self, protocol=SDKServerProtocolEnum.HTTP):
        server_protocol = TypeHelper.resolve(protocol)
        sdk_server = SDKServer.__server[server_protocol]

        if sdk_server["server_instance"] is None:
            logger.error("{} Server is not instantiated...".format(server_protocol))

        elif sdk_server["server_config"]["state"] == SDKServerStateEnum.Running:
            logger.warning("{} Server is already running...".format(server_protocol))

        else:
            server_address = sdk_server["server_instance"].socket.getsockname()
            sdk_server["server_config"]["state"] = SDKServerStateEnum.Running
            logger.debug("Starting {} server on {} at port {} ...".format(server_protocol, server_address[0],
                                                                          server_address[1]))
            sdk_server["server_instance"].serve_forever()

    def stop_server(self, protocol=SDKServerProtocolEnum.HTTP):
        server_protocol = TypeHelper.resolve(protocol)
        sdk_server = SDKServer.__server[server_protocol]

        if sdk_server["server_instance"] is None:
            logger.error("{} Server is not instantiated...".format(server_protocol))

        elif sdk_server["server_config"]["state"] == SDKServerStateEnum.Stopped:
            logger.warning("{} Server is already stopped...".format(server_protocol))

        else:
            server_address = sdk_server["server_instance"].socket.getsockname()

            logger.debug(
                "Stopping {} server on {} at port {} ...".format(server_protocol, server_address[0], server_address[1]))
            sdk_server["server_instance"].shutdown()
            sdk_server["server_config"]["state"] = SDKServerStateEnum.Stopped

    def get_server_status(self, protocol=SDKServerProtocolEnum.HTTP):
        server_details = SDKServer.__server[TypeHelper.resolve(protocol)]

        return {
            "IPAddress": socket.gethostbyname(socket.gethostname()),
            "Port": server_details["server_config"]["port"],
            "State": server_details["server_config"]["state"]
        }


SDKServer.load_server_configuration()

if __name__ == "__main__":
    import threading

    s1 = SDKServer.get_server_instance()

    server_thread = threading.Thread(
        target=s1.start_server(protocol=SDKServerProtocolEnum.HTTPS))
    server_thread.start()

    print(s1.get_server_status(protocol=SDKServerProtocolEnum.HTTPS))
