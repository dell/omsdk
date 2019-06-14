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
import logging
import base64
import hashlib
import gzip

from omsdk.sdkprint import Prettifyer
from omsdk.sdkcenum import EnumWrapper
from omdrivers.enums.iDRAC.iDRACEnums import *
from past.builtins import long

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    from StringIO import StringIO


class iDRACStreaming():
    def __init__(self, entity):
        # if PY2:
        #   super(iDRACStreaming, self).__init__(entity)
        # else:
        self._job_mgr = entity.job_mgr
        self._config_mgr = entity.config_mgr
        self._log_mgr = entity.log_mgr

    def __recursive_append_char__(self, str_data, position):
        """
        Appends a character recursively after every n characters

        :param str_data: the input string
        :param position: the position
        :type str_data: str
        :type position: int
        :return: the output string
        :rtype: str
        """
        for i in range(0, len(str_data), position):
            yield str_data[i:i + position]

    def __chunkify_data__(self, data, chunk_size):
        """
        Breaks down the data into chunks of equal size

        :param data: the input data
        :param chunk_size: the size of each chunk
        :type data: str
        :type chunk_size: int
        :return: the list of chunked data
        :rtype: list
        """
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def __calculate_crc__(self, data):
        """
        Calculates the CRC for a given data

        :param data: the input data
        :type data: str
        :return: the CRC
        :rtype: int
        """

        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.hexdigest()

    def __export_data_to_local_share(self, export_file_type=None, **kwargs):
        if export_file_type == FileTypeEnum.SystemConfigXML:
            export_data_resp = self._config_mgr.scp_export_to_local_share(
                target=kwargs["target"],
                export_format=kwargs["export_format"],
                export_use=kwargs["export_use"],
                include_in_export=kwargs[
                    "include_in_export"])
        elif export_file_type == FileTypeEnum.LCLogs:
            export_data_resp = self._log_mgr.lclog_export_to_local_share()
        elif export_file_type == FileTypeEnum.Inventory:
            export_data_resp = self._config_mgr.inventory_export_to_local_share(xml_schema=kwargs["xml_schema"])
        elif export_file_type == FileTypeEnum.FactoryConfig:
            export_data_resp = self._config_mgr.factory_export_to_local_share()
        elif export_file_type == FileTypeEnum.TSR:
            export_data_resp = self._config_mgr.support_assist_collection_to_local_share(
                data_selector_array_in=kwargs["data_selector_array_in"],
                filter=kwargs["filter"],
                transmit=kwargs["transmit"])
        elif export_file_type == FileTypeEnum.BootVideoLogs:
            export_data_resp = self._log_mgr.videolog_export_to_local_share(
                video_log_file_type=VideoLogsFileTypeEnum.Boot_Capture)
        elif export_file_type == FileTypeEnum.Diagnostics:
            export_data_resp = self._config_mgr.epsa_diagnostics_export_to_local_share()
        elif export_file_type == FileTypeEnum.LCFullLogs:
            export_data_resp = self._log_mgr.complete_lclog_export_to_local_share()
        elif export_file_type == FileTypeEnum.CrashVideoLogs:
            export_data_resp = self._log_mgr.videolog_export_to_local_share(
                video_log_file_type=VideoLogsFileTypeEnum.Crash_Capture)
        else:
            export_data_resp = {
                "Status": "Failure",
                "Message": "Cannot perform export operation. Please provide a valid export type."
            }

        return export_data_resp

    def __import_data_to_local_share(self, import_file_type=None, **kwargs):
        if import_file_type is FileTypeEnum.SystemConfigXML:
            if "scp_preview" in kwargs and kwargs["scp_preview"] == True:
                import_data_resp = self._config_mgr.scp_preview_import_to_local_share(
                    target=kwargs["target"],
                    job_wait=kwargs["job_wait"])

            else:
                import_data_resp = self._config_mgr.scp_import_to_local_share(
                    target=kwargs["target"],
                    shutdown_type=kwargs[
                        "shutdown_type"],
                    time_to_wait=kwargs["time_to_wait"],
                    end_host_power_state=kwargs[
                        "end_host_power_state"],
                    job_wait=kwargs["job_wait"]
                )

        else:
            import_data_resp = {
                "Status": "Failure",
                "Message": "Cannot perform export operation. Please provide a valid export type."
            }

        return import_data_resp

    # Todo Exported Data should be returned as string or file
    def export_data(self, file_type=FileTypeEnum.SystemConfigXML, export_file="", **kwargs):
        """
        Exports the data

        :param file_type: The Type of File
        :param export_file: The export file
        :param kwargs: Keyword args having the export options
        :type file_type: FileTypeEnum <Enum>
        :type export_file: str
        :type kwargs: list
        :return: the success or failure response
        :rtype: json

        """
        if not self._config_mgr.entity.ServerGeneration.startswith(
                TypeHelper.resolve(ServerGenerationEnum.Generation_14)):
            logger.error("Cannot perform import operation. Importing Data from Local Share is supported only on "
                         "14th Generation of PowerEdge Servers.")
            return {
                "Status": "Failure",
                "Message": "Cannot perform export operation. Exporting Data to Local Share is supported only on "
                           "14th Generation of PowerEdge Servers."
            }

        # Maximum allowed value for chunk size(512KB)
        chunk_size = 122280 if file_type == FileTypeEnum.LCLogs or file_type == FileTypeEnum.LCFullLogs or \
                               file_type == FileTypeEnum.BootVideoLogs or file_type == FileTypeEnum.CrashVideoLogs \
            else 524286

        export_response = ""

        if export_file is None:
            return {
                "Status": "Failure",
                "Message": "Cannot perform export operation. The specified path/file to export doesn't exist."
            }

        # Clear Transfer Session for previous export
        logger.debug("Clearing Transfer Session...")
        clear_transfer_session_resp = self._config_mgr.clear_transfer_session(
            file_operation=FileOperationEnum.Export,
            file_type=file_type)

        clear_transfer_session_status = clear_transfer_session_resp["Status"]
        clear_transfer_session_msg_id = clear_transfer_session_resp["MessageID"]

        if clear_transfer_session_status == "Success" or (
                        clear_transfer_session_status == "Error" and
                        clear_transfer_session_msg_id == "RAC088"):
            logger.debug(clear_transfer_session_msg_id + ":" + clear_transfer_session_resp["Message"] +
                         "Continuing export data operation...")

        else:
            logger.error(clear_transfer_session_resp["MessageID"] + ":" + clear_transfer_session_resp["Message"])
            return {
                "Status": "Failure",
                "Message": "Cannot perform export operation. " + clear_transfer_session_resp["MessageID"] + ":" +
                           clear_transfer_session_resp["Message"]
            }

        # Export data to iDRAC local share
        logger.debug("Exporting Data to iDRAC local share...")
        export_data_to_local_share_resp = self.__export_data_to_local_share(export_file_type=file_type, **kwargs)

        count = 1

        if export_data_to_local_share_resp["Status"] != "Success":
            logger.error(
                export_data_to_local_share_resp["Status"] + ":" + export_data_to_local_share_resp["Message"])
            return {
                "Status": export_data_to_local_share_resp["Status"],
                "Message": "Cannot perform export operation. " +
                           export_data_to_local_share_resp["Message"]
            }

        # Export the first chunk of data
        logger.debug("Exporting the first Chunk...")

        session_id = long(0)
        file_offset = long(0)
        tx_data_size = long(0)

        export_data_resp = self._config_mgr.export_data(
            file_type=file_type,
            in_session_id=session_id, in_chunk_size=chunk_size, file_offset=file_offset, tx_data_size=tx_data_size,
            payload_encoding=PayLoadEncodingEnum.Text)

        logger.debug(export_data_resp)

        if export_data_resp["Status"] != "Success":
            logger.error(export_data_resp["Status"] + ":" + export_data_resp["Message"])

            return {
                "Status": export_data_resp["Status"],
                "Message": "Cannot perform export operation. " +
                           export_data_resp["Message"]
            }

        export_data_output = export_data_resp["Data"]["ExportData_OUTPUT"]

        crc = export_data_output["CRC"]
        payload = export_data_output["PayLoad"]
        ret_file_offset = long(export_data_output["RetFileOffset"])
        ret_tx_Data_size = long(export_data_output["RetTxDataSize"])
        session_id = long(export_data_output["SessionID"])
        txfr_descriptor = export_data_output["TxfrDescriptor"]

        payloads_list = list()

        payloads_list.append(payload)

        # Export the subsequent chunks till EOF
        while int(txfr_descriptor) != 3:
            count += 1
            logger.debug("Exporting chunk {}...".format(count))

            export_data_resp = self._config_mgr.export_data(
                file_type=file_type,
                in_session_id=session_id, in_chunk_size=chunk_size,
                file_offset=ret_file_offset, tx_data_size=ret_tx_Data_size,
                payload_encoding=PayLoadEncodingEnum.Text)

            if export_data_resp["Status"] != "Success":
                logger.error(export_data_resp["Status"] + ":" + export_data_resp["Message"])
                return {
                    "Status": export_data_resp["Status"],
                    "Message": "Cannot perform export operation. " +
                               export_data_resp["Message"]
                }

            export_data_output = export_data_resp["Data"]["ExportData_OUTPUT"]

            # chunk_size = export_data_output["ChunkSize"]
            payload = export_data_output["PayLoad"]
            ret_file_offset = long(export_data_output["RetFileOffset"])
            ret_tx_Data_size = long(export_data_output["RetTxDataSize"])
            session_id = long(export_data_output["SessionID"])
            txfr_descriptor = export_data_output["TxfrDescriptor"]

            payloads_list.append(payload)

        # Generate payload data by merging the payload_list contents and decode the Base64 payload data.
        logger.debug("Generating final payload from exported chunks...")
        export_file_data = base64.b64decode("".join(payloads_list))

        # Calculate CRC from the exported file data
        logger.debug("Calculating CRC from exported file data...")
        export_file_crc = self.__calculate_crc__(export_file_data)

        # Check if CRC obtained from first chunk export matches to the calculated CRC
        if crc == export_file_crc:
            logger.debug("CRC of exported data matched with that in iDRAC local share...")
            try:
                logger.debug("Writing exported content to file...")
                # LC Complete Logs will be exported gzip file
                if file_type == FileTypeEnum.LCFullLogs:
                    with gzip.open(export_file, 'wb+') as f:
                        f.write(gzip.GzipFile(fileobj=StringIO(export_file_data)).read() if PY2
                                else gzip.decompress(export_file_data))
                elif file_type == FileTypeEnum.BootVideoLogs or file_type == FileTypeEnum.CrashVideoLogs:
                    # Todo: Not Implemented
                    with open(export_file, 'w+', encoding='utf-8') as f:
                        f.write(export_file_data.decode("ISO-8859-1"))
                else:
                    with open(export_file, 'w+') as f:
                        f.write(export_file_data.decode("utf-8"))

                export_response = {"Status": "Success", "Message": "File exported successfully!!"}
            except IOError as e:
                logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
                export_response = {"Status": "Failure", "Message": "Unable to export file. " + e.strerror}
        else:
            logger.error("Unable to export file... CRC of exported data doesn't match with that in iDRAC local "
                         "share...")
            export_response = {"Status": "Failure", "Message": "Unable to export file."}

        return export_response

    # TODO: config xml should be passed as file/string
    def import_data(self, import_file_type=FileTypeEnum.SystemConfigXML, import_file=None,
                    **kwargs):
        if not self._config_mgr.entity.ServerGeneration.startswith(
                TypeHelper.resolve(ServerGenerationEnum.Generation_14)):
            logger.error("Cannot perform import operation. Importing Data from Local Share is supported only on "
                         "14th Generation of PowerEdge Servers.")
            return {
                "Status": "Failure",
                "Message": "Cannot perform import operation. Importing Data from Local Share is supported only on "
                           "14th Generation of PowerEdge Servers."
            }

        if import_file is None or not os.path.exists(import_file):
            logger.error("Cannot perform import operation. The specified path/file to import doesn't exist...")
            return {
                "Status": "Failure",
                "Message": "Cannot perform import operation. The specified path/file to import doesn't exist."
            }

        chunk_size = 524288  # Maximum allowed value for chunk size (512KB)

        # Read the file to import
        logger.debug("Reading the contents of the file to import...")

        try:
            with open(import_file, 'r') as f:
                import_file_content = f.read()

            import_data = import_file_content.encode("utf-8")

            file_size = long(len(import_data))

            clear_transfer_session_resp = self._config_mgr.clear_transfer_session(
                file_operation=FileOperationEnum.Import,
                file_type=import_file_type)

            clear_transfer_session_status = clear_transfer_session_resp["Status"]
            clear_transfer_session_msg_id = clear_transfer_session_resp["MessageID"]

            if clear_transfer_session_status == "Success" or (
                            clear_transfer_session_status == "Error" and
                            clear_transfer_session_msg_id == "RAC088"):
                logger.debug(clear_transfer_session_msg_id + ":" + clear_transfer_session_resp["Message"] +
                             "Continuing import data operation...")

            else:
                logger.error(
                    clear_transfer_session_status["MessageID"] + ":" + clear_transfer_session_status["Message"])

                return {
                    "Status": "Failure",
                    "Message": "Cannot perform import operation. " + clear_transfer_session_resp["MessageID"] + ":" +
                               clear_transfer_session_resp["Message"]
                }

            # Calculate the CRC of the config-xml data
            crc = self.__calculate_crc__(import_data)

            # Encode the config-xml to Base64
            encoded_data = bytearray(base64.b64encode(import_data))

            # Divide the Base64 Encoded data into chunks
            payload_chunks = self.__chunkify_data__(encoded_data, chunk_size)

            logger.debug(payload_chunks)

            number_of_chunks = len(payload_chunks)
            session_id = long(0)

            # Import the Base64 Encoded Config XML data chunk-by-chunk
            for count in range(1, number_of_chunks + 1):
                base64_payload = payload_chunks[count - 1]
                payload_size = len(base64_payload)
                logger.debug("Payload Size : {}".format(payload_size))

                # Append \n
                base64_data = "\n".join(self.__recursive_append_char__(base64_payload.decode(), 64))

                payload_data = str(base64_data if count == number_of_chunks and payload_size % 64 is not 0 \
                                       else base64_data + "\n")

                # Import the first chunk
                if count == 1:
                    logger.debug("Importing First Chunk...")
                    import_chunk_resp = self._config_mgr.import_data(
                        file_type=import_file_type,
                        in_session_id=session_id,
                        chunk_size=payload_size, file_size=file_size,
                        txfr_descriptor=TxfrDescriptorEnum.StartOfTransmit,
                        crc=crc,
                        payload=payload_data,
                        payload_encoding=PayLoadEncodingEnum.Base64)

                    logger.debug(import_chunk_resp)

                    if import_chunk_resp["Status"] != "Success":
                        logger.error(import_chunk_resp["Status"] + ":" + import_chunk_resp["Message"])
                        return {
                            "Status": import_chunk_resp["Status"],
                            "Message": "Cannot perform export operation. " +
                                       import_chunk_resp["Message"]
                        }

                    session_id = long(import_chunk_resp["Data"]["ImportData_OUTPUT"]["SessionID"])

                # Import the last chunk
                elif count == number_of_chunks:
                    logger.debug("Importing Chunk {}(Last Chunk)...".format(count))
                    import_chunk_resp = self._config_mgr.import_data(
                        file_type=import_file_type,
                        in_session_id=session_id, chunk_size=payload_size,
                        crc=crc,
                        file_size=file_size,
                        txfr_descriptor=TxfrDescriptorEnum.EndOfPacket,
                        payload=payload_data,
                        payload_encoding=PayLoadEncodingEnum.Base64)

                    logger.debug(import_chunk_resp)

                    if import_chunk_resp["Status"] != "Success":
                        logger.error(import_chunk_resp["Status"] + ":" + import_chunk_resp["Message"])
                        return {
                            "Status": import_chunk_resp["Status"],
                            "Message": "Cannot perform export operation. " +
                                       import_chunk_resp["Message"]
                        }

                # Import subsequent chunks
                else:
                    logger.debug("Importing Chunk {}...".format(count))

                    import_chunk_resp = self._config_mgr.import_data(
                        file_type=import_file_type,
                        in_session_id=session_id, chunk_size=payload_size,
                        crc=crc,
                        file_size=file_size, payload=payload_data,
                        txfr_descriptor=TxfrDescriptorEnum.NormalTransmission,
                        payload_encoding=PayLoadEncodingEnum.Base64)

                    logger.debug(import_chunk_resp)

                    if import_chunk_resp["Status"] != "Success":
                        logger.error(import_chunk_resp["Status"] + ":" + import_chunk_resp["Message"])
                        return {
                            "Status": import_chunk_resp["Status"],
                            "Message": "Cannot perform export operation. " +
                                       import_chunk_resp["Message"]
                        }

            import_data_resp = self.__import_data_to_local_share(import_file_type=import_file_type, **kwargs)

            logger.debug(import_data_resp)

            if import_data_resp["Status"] != "Success":
                logger.error(import_data_resp["Status"] + ":" + import_data_resp["Message"])
                return {
                    "Status": import_data_resp["Status"],
                    "Message": "Cannot perform export operation. " +
                               import_data_resp["Message"]
                }

        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            import_data_resp = {"Status": "Failure", "Message": "Unable to import file. " + e.strerror}

        return import_data_resp
