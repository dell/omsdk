Prerequisites
=============

Liason Share for Configuration Tasks
------------------------------------

If you are going to perform configuration tasks with SDK (like configuring
NIC, BIOS, etc.), you need to create a Liason Share. SDK will save the
configuration tasks into a temporary Server Configuration Profile in the
Liason share and initiate an import request to iDRAC to import the temporary
file. Once the task is complete, the SDK will remove the temporary file.
iDRAC can only import the Server Configuration Profile from a NFS folder or
a Windows Network Share.  Hence, the Liason Share must be an exported share
folder accessible to iDRAC whereas it must be mounted locally on the host
where SDK is being used.  

If you export /LinShare_Ansible from host 192.168.1.21, and mounting it 
onto /mnt path on the machine where SDK is hosted, then create a share object
as follows:

.. code-block:: rest

        # Credentials to access the LinShare_Ansible share on 192.168.1.21
        creds = UserCredentials(<user>, <password>)
    
        FileOnShare(remote = '192.168.1.21:/LinShare_Ansible',
                    mount_point = '/mnt/LinShare_Ansible'
                    isFolder = True, creds)

and register it with idrac as follows:

.. code-block:: rest

    idrac.config_mgr.set_liason_share(myshare)

On Windows, you can create the folder, by specifying a unassiged drive
as the mount_point

.. code-block:: rest

        # Credentials to access the WinShare_Ansible share on 192.168.1.21
        creds = UserCredentials('<domain>\\<user>', <password>)
    
        FileOnShare(remote = '\\\\192.168.1.21\\WinShare_Ansible',
                    mount_point = 'Z:\\'
                    isFolder = True, creds)

Note: Since python uses '\' character as an escape character, windows folders
will take an extra '\' character.
 

Update Share for Update Tasks
-----------------------------

When iDRAC does not have access to internet, Firmware Updates Tasks requires
firmware to be downloaded from ftp.dell.com or downloads.dell.com to a local share.
Also for performance reasons, it would be better to have the firmware downloaded
to iDRAC from a local share rather than from an internet site. However, the
this would require large storage areas to download the firmware updates.

SDK provides an optimal solution for this through an UpdateManager API. The
Update Manager requires a share accessible to iDRACs in the network, which is
also locally mounted onto the machine where SDK will run.

Here are the sequence of steps to perform update tasks:

1. Create a share similar to Liason share and configure it with Update Manager

.. code-block:: rest

    updshare = FileOnShare(remote ='\\\\192.168.0.120\\NFS',
        mount_point='Z:\\', isFolder=True,
        creds = UserCredentials("<user>", "<password>"))

    UpdateManager.configure(updshare)

2. Download the catalog 'ftp://ftp.dell.com/Catalog.xml.gz' to the Update Share
and extract it. This master catalog, released at a periodic cadence contains
the location of the latest firmware, drivers and application updates for all
components of all supported PowerEdge systems.

.. code-block:: rest

    UpdateManager.get_instance().update_catalog()

3. Now we want to create a cache of the firmware updates from ftp.dell.com.
We need this to perform firmware updates locally.  While the downloaded Catalog
contains the latest firmware, drivers and application updates for all components
of all supported PowerEdge systems, the deployed environments may not necessarily
cover the entire PowerEdge portfolio.  Hence, it would be optimal to create
a local cache more representative of the deployed environment. 

To create a local cache, prepare a list of representative systems.  You can use
one of the following methods to create the cache:

a. Create a cache of all firmware belonging to PowerEdge model

.. code-block:: rest

    # Add all components belonging to a Model to Cache.
    catscope = UpdateManager.get_instance().get_cache_catalog()
    for ipaddr in [list of representative iDRACs]:
        idrac = sd.get_driver(sd.driver_enum.iDRAC, ipaddr, creds_for_ipaddr)
        catscope.add_model_to_scope(idrac.SystemIDInHex)
    catscope.save()

b. Create a cache of the firmware of the components present in the
representative systems

.. code-block:: rest

    # Add firmware for only those components present in representative systems
    catscope = UpdateManager.get_instance().get_cache_catalog()
    for ipaddr in [list of representative iDRACs]:
        idrac = sd.get_driver(sd.driver_enum.iDRAC, ipaddr, creds_for_ipaddr)
        catscope.add_to_scope(idrac.SystemIDInHex, idrac.update_mgr.get_swidentity())
    catscope.save()

c. Optionally, if you want to create a cache of only certain component
updates (like BIOS and iDRAC updates), then you can follow this steps:

.. code-block:: rest

    # Add firmware for only those components present in representative systems
    catscope = UpdateManager.get_instance().get_cache_catalog()
    for ipaddr in [list of representative iDRACs]:
        idrac = sd.get_driver(sd.driver_enum.iDRAC, ipaddr, creds_for_ipaddr)
        catscope.add_to_scope(idrac.SystemIDInHex, idrac.update_mgr.get_swidentity(), 'iDRAC', 'BIOS')
    catscope.save()

After saving the catalog with requisite firmware records, we need to now
download the firmware updates as follows:

.. code-block:: rest

    UpdateManager.get_instance().update_cache()

Now we are ready to perform firmware updates on the devices.

iDRAC Connection
================


How to connect to iDRAC
-----------------------

You have to first initialize the SDK Infrastructure as follows:

.. code-block:: rest

    from omsdk.sdkinfra import sdkinfra
    sd = sdkinfra()
    sd.importPath()

The above two lines initializes the SDK Infrastructure and loads
the drivers present in the path <python_lib>\omdrivers

You can instantiate the iDRAC as follows:

.. code-block:: rest

    idrac = sd.find_driver(ipaddr, creds)

.. code-block:: rest

    idrac = sd.get_driver(sd.driver_enum.iDRAC, ipaddr, creds)

if the ipaddress is resolved to an iDRAC, then an object instance
of iDRACEntity object is returned.  Otherwise None object is returned.

How to disconnect from iDRAC
----------------------------

You need to disconnect the connection to iDRAC. While iDRAC would
salvage connections, if you don't disconnect it can potentially
cause the iDRAC to slow down.

.. code-block:: rest

    idrac.disconnect()


How to reconnect to iDRAC
-------------------------

Reconnect is an convenience function to reconnect to the device
Tears down the connection and recreates one.

.. code-block:: rest

    idrac.reconnect(pOptions)


How to setup a liason share
---------------------------

You can setup the liason share as follows:

.. code-block:: rest

    FileOnShare(remote = '192.168.1.120:/Share', mount_point = '/mnt/Share',
                isFolder = True, creds)
    idrac.config_mgr.set_liason_share(myshare)

iDRAC Details
=============

Attributes returning select information
---------------------------------------

.. attribute:: idrac.AssetTag

    Asset Tag of the system.

.. attribute:: idrac.CMCIPAddress

    If the server is a blade, then the IP Address of 
    Chassis Management Controller containing the blade

.. attribute:: idrac.Model

    Model of the server

.. attribute:: idrac.PowerCap

    Power Cap configured for the server

.. attribute:: idrac.PowerState

    Powered state of the server

.. attribute:: idrac.ServerGeneration

    Generation of the server

.. attribute:: idrac.ServiceTag

    Service Tag of the server

.. attribute:: idrac.SystemID

    System ID of the Server. This ID is used internally to identify
    model of the server.

.. attribute:: idrac.SystemIDInHex

    System ID of the server in Hexadecimal Number. This ID is used in
    querying the firmware updates for a given server model.
    

.. attribute:: idrac.config_mgr.DriverPackInfo

    Driver Packs available on the server.

.. attribute:: idrac.config_mgr.HostMacInfo

    Host MAC Info required for OS Deployment

.. attribute:: idrac.config_mgr.LCReady

    Ready state of Lifecycle Controller.  Jobs can be scheduled only if
    Lifecycle Controller is in ready state

.. attribute:: idrac.config_mgr.LCStatus

    Status of the Lifecycle Controller.

.. attribute:: idrac.config_mgr.ServerStatus

    Status of the Server

CSIOR
-----

CSIOR is an option in iDRAC which enables collecting of system inventory
on reboot. This option is required for DellEMC 1xMany Consoles to be able to
perform configuration tasks on the iDRAC.

.. function:: idrac.config_mgr.disable_csior()

    Disables CSIOR

.. function:: idrac.config_mgr.enable_csior()

    Enables CSIOR

AutoDiscovery
-------------

Auto Discovery is method where iDRAC can report its presence to a Provisioning
Server configured in the DNS/DHCP.  The APIs provided will alter the settings
for autodiscovery

.. function:: idrac.config_mgr.reinitiate_dhs()

    iDRAC will reinitate discovery handshare with the provisioning server

.. function:: idrac.config_mgr.clear_provisioning_server()

    This API will clear Provisioning server details from the iDRAC. When 
    rebooted, iDRAC will once again fetch information from DNS/DHCP

Location
--------

Configures the location of the server.

.. function:: idrac.config_mgr.configure_location(datacenter, loc_room, loc_aisle, loc_rack, loc_rack_slot, loc_chassis) 

    :param str datacenter: Datacenter name
    :param str loc_room: Room name
    :param str loc_aisle: Aisle name
    :param str loc_rack: Rack name
    :param str loc_rack_slot: Rack slot
    :param str loc_chassis: Chassis Name

    :return: JSON object providing return status of the operation

    Return Values:
        Success: if location information is configured successfully
        Failed: if the location information could not be configured or 
        there was some internal error


NIC Configuration
-----------------
.. function:: idrac.config_mgr.configure_idrac_dnsname(dnsname)

    Configures DNS Name of iDRAc

.. function:: idrac.config_mgr.configure_idrac_ipv4(enable_ipv4, dhcp_enabled)

    Enables IPv4 Configuration for iDRAC NIC

.. function:: idrac.config_mgr.configure_idrac_ipv4dns(dnsarray, dnsFromDHCP)

    Configures IPv4 DNS Settings for iDRAC NIC

.. function:: idrac.config_mgr.configure_idrac_ipv4static(ipv4_address, ipv4_netmask, ipv4_gateway, dnsarray, dnsFromDHCP)

    Configures IPv4 Static Settings for iDRAC NIC

.. function:: idrac.config_mgr.configure_idrac_ipv6dns(dnsarray, dnsFromDHCP)

    Configures IPv6 DNS Settings for iDRAC NIC

.. function:: idrac.config_mgr.configure_idrac_ipv6static(ipv6_address, ipv6_prefixlen, ipv6_gateway, dnsarray, dnsFromDHCP)

    Configures IPv6 Static Settings for iDRAC NIC

.. function:: idrac.config_mgr.configure_idrac_nic(idrac_nic, failover, auto_negotiate, idrac_nic_speed, auto_dedicated_nic)

    Configures iDRAC NIC Failover and Speed Settings

.. function:: idrac.config_mgr.configure_time_zone(tz, dst_offset, tz_offset)

    Configures Time Zone settings

.. function:: idrac.config_mgr.configure_tls(tls_protocol, ssl_bits)

    Configures TLS Settings

Protocols
---------
.. function:: idrac.config_mgr.disable_snmp()

    Disable SNMP for iDRAC

.. function:: idrac.config_mgr.enable_snmp(community, snmp_port, trap_port, trap_format)

    Configure SNMP Community Name, SNMP Port, SNMP Trap Port and the SNMP Trap Formats

.. function:: idrac.config_mgr.disable_syslog()

    Disable Syslog for iDRAC

.. function:: idrac.config_mgr.enable_syslog(syslog_port, powerlog_interval, server1, server2, server3)

    Configure SysLog Port, Power Log Port Interval and syslog remote servers


SNMP Trap Destinations
----------------------

Provides APIs for configuring the SNMP Trap Destinations.
When an event occurs in iDRAC, iDRAC generates an SNMP Trap to all these destinations
User can also disable a SNMP Trap Destination, in which case, the entry is still retained in iDRAC,
but traps are not sent to this entry.


.. attribute:: idrac.config_mgr.SNMPTrapDestination

    Returns a JSON containing list of all "SNMP Trap Destinations". Each
    "SNMP Trap Destination" entry contains the IPAddress/Hostname of the
    "SNMP Trap Destination", an optional username for SNMPv3 Traps and
    whether the entry is Enabled/Disabled. The JSON also returns an internal
    slot index in the Trap Destination table, where the entry can be
    found. This corresponds to row in the "SNMP Trap Destination" table
    in iDRAC Console.
    
    A maximum of 16 "SNMP Trap Destination" can be configured with iDRAC.

    A sample return value from the function returning two
    "SNMP Trap Destination" entries is given below.

.. code-block:: rest

        [
            {
                "Destination": "192.168.1.100",
                "SNMPv3Username": null,
                "_slot": 1,
                "State": "Enabled"
            },
            {
                "Destination": "192.168.1.102",
                "SNMPv3Username": null,
                "_slot": 2,
                "State": "Disabled"
            },
        ]


.. function:: idrac.config_mgr.add_trap_destination(trap_dest_host[, username = None])

    Inserts an "SNMP Trap Destination" entry into an empty slot inside
    the "SNMP Trap Destination" Table.

    :param IpAddress trap_dest_host:  "SNMP Trap Destination" host (can be IPv4 or IPv6 address or hostname)
    :param str username: SNMPv3 User Name to which the SNMP Trap is generated.

    :return: JSON reverting status of the call, optional message if the call failed.

    Return Values:

        Success : if the entry was added successfully

        Failed  : if entry was already present or
                  no empty slot was found or
                  if there was some internal errors.

.. function:: idrac.config_mgr.disable_trap_destination(trap_dest_host)

    Disables the "SNMP Trap Destination" entry.  SNMP Traps will not be
    forwarded to this host until the entry is again enabled.

    Arguments:

        trap_dest_host :  SNMP Trap Destination host (can be IPv4 or IPv6 address or hostname)

    Return Values:

        Success : if the entry was enabled successfully

        Failed  : if entry could not be found or,
                  there was some internal errors.

.. function:: idrac.config_mgr.enable_trap_destination(trap_dest_host)

    Enables the "SNMP Trap Destination" entry.  iDRAC will start generating
    SNMP Traps to this host.

    Arguments:

        trap_dest_host :  "SNMP Trap Destination" host (can be IPv4 or IPv6 address or hostname)

    Return Values:

        Success : if the entry was enabled successfully

        Failed  : if entry could not be found or,
                  there was some internal errors.

.. function:: idrac.config_mgr.remove_trap_destination(trap_dest_host)

    Removes the "SNMP Trap Destination" entry.  iDRAC will stop generating
    SNMP Traps to this host. User cannot enable this entry in future.

    Arguments:

        trap_dest_host :  "SNMP Trap Destination" host (can be IPv4 or IPv6 address or hostname)

    Return Values:

        Success : if the entry was enabled successfully

        Failed  : if entry could not be found or,
                  there was some internal errors.


Email Alerts
------------

Provides APIs for configuring the Email Alert Destinations.  When an event
occurs in iDRAC, iDRAC can be configured to generate an Alert to registered
Email Addresses.  User can also disable a Email Alert Destination, in which
case, the entry is still retained in iDRAC, but alerts are not sent to this
entry. User can enable Email Alerts or customize the message to be sent
on events.


.. attribute:: idrac.config_mgr.RegisteredEmailAlert

    Returns a JSON containing list of all registered Email Addresses. Each
    Email Address contains the email address of the Email Alert Destination,
    an optional message to be used for Email Alerts and whether the entry is
    Enabled/Disabled. The JSON also returns an internal slot index in the
    Email Alert table, where the entry can be found. This corresponds to row
    in the Email Alert entry table in iDRAC Console.
    
    A maximum of 4 Email addresses can be configured with iDRAC.

.. code-block:: rest

        [
            {
                "Address": "admin.idrac@sample.org",
                "CustomMsg": null,
                "Enable": "Enabled",
                "_slot": 1
            }
        ]

.. function:: idrac.config_mgr.add_email_alert(email_id[, custom_msg = ""])

    Inserts an Email Alert entry into an empty slot inside the Email Address Table.

    Arguments:

        email_id :  Email address to which the Alert need to be sent

        custom_msg : Custom Message

    Return Values:

        Success : if the entry was added successfully

        Failed  : if entry could not be created due to an existing entry, no empty slot or
                  there was some internal errors.

.. function:: idrac.config_mgr.disable_email_alert(email_id)

    Disables the Email Alert entry.  Email Alerts will not be generated to this
    email address until the entry is again enabled.

    Arguments:

        email_id :  Email address to which the Alert need to be sent

    Return Values:

        Success : if the entry was enabled successfully

        Failed  : if entry could not be found, or there was some internal errors.

.. function:: idrac.config_mgr.enable_email_alert(email_id)

    Enables the Email Alert entry.  iDRAC will start generating Email Alerts to this
    email address.

    Arguments:

        email_id :  Email address to which the Alert need to be sent

    Return Values:

        Success : if the entry was enabled successfully

        Failed  : if entry could not be found, or there was some internal errors.

.. function:: idrac.config_mgr.remove_email_alert(email_id)

    Removes the Email Alert entry.  iDRAC will stop generating Email Alert this email address.

    Arguments:

        email_id :  Email address to which the Alert need to be sent

    Return Values:

        Success : if the entry was enabled successfully

        Failed  : if entry could not be found, or there was some internal errors.


.. function:: idrac.config_mgr.change_email_alert(email_id, custom_msg = "")

    Changes the custom_message for this email entry

    Arguments:

        email_id :  Email address to which the Alert need to be sent

        custom_msg : Custom Message

    Return Values:

        Success : if the custom message has been changed properly.

        Failed  : if entry could not be found, or there was some internal errors.

BIOS
----

    bios_reset_to_defaults()
    change_bios_password(passtype, old_password, new_password)


Identifying Chassis
-------------------
    blink_led(ledenum, duration)

Physical Drive
--------------

    blink_drive(target)
    unblink_drive(target)


OS Deployment
=============
.. function:: idrac.config_mgr.boot_to_network_iso(network_iso_image)

    OS Deplpyment task

.. function:: idrac.config_mgr.boot_to_disk()

    OS Deplpyment task

.. function:: idrac.config_mgr.boot_to_pxe()

    OS Deplpyment task

.. function:: idrac.config_mgr.boot_to_iso()

    OS Deplpyment task

.. function:: idrac.config_mgr.detach_iso()

    OS Deplpyment task

.. function:: idrac.config_mgr.detach_iso_from_vflash()

    OS Deplpyment task

.. function:: idrac.config_mgr.disconnect_network_iso()

    OS Deplpyment task

.. function:: idrac.config_mgr.connect_network_iso()

    OS Deplpyment task

.. function:: idrac.config_mgr.download_iso()

    OS Deplpyment task

.. function:: idrac.config_mgr.download_iso_flash()

    OS Deplpyment task



Power Management and Reboot
===========================

.. function:: idrac.config_mgr.change_power(penum)

    Change Power

.. function:: idrac.config_mgr.power_boot(power_boot_enum)

    Power boot

.. function:: idrac.config_mgr.reboot_after_config(reboot_type)

    Reboot after configuring a job


RAID
====

.. function:: idrac.config_mgr.create_raid(vd_name, span_depth, span_length, raid_type, n_disks)

    Creates a RAID Disk


Server Configuration Profile and Server Profiles
================================================

.. function:: idrac.config_mgr.scp_import(scp_share_path)

    Import Server Configuration Profile to iDRAC. This API waits for
    iDRAC to complete the import of Server Configuration Profile. Certain
    changes like RAID creation, would require the server to be rebooted
    after importing the Server Configuration Profile.

    :param omsdk.sdkfile.FileOnShare scp_share_path: Location from where the Server Configuration Profile is imported

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server Configuration profile is successful

        Failed: If the Server Configuration Profile could not be imported.

.. function:: idrac.config_mgr.scp_import_async(scp_share_path)

    Import Server Configuration Profile to iDRAC. This API returns immediately
    and returns the job id assocated with the import operation. Until the 
    operation is complete, iDRAC will not be accepting other jobs. Certain
    changes like RAID creation, would require the server to be rebooted
    after iDRAC successfully imported the Server Configuration Profile.

    :param omsdk.sdkfile.FileOnShare scp_share_path: Location where the Server Configuration Profile is stored

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server Configuration profile is successful.  return_value['Job']['JobId'] has the Job ID associated with the import

        Failed: If the Server Configuration Profile could not be imported.

.. function:: idrac.config_mgr.scp_export(scp_share_path)

    Export Server Configuration Profile to share. This API waits for
    iDRAC to complete the export of Server Configuration Profile to a 
    given share. 

    :param omsdk.sdkfile.FileOnShare scp_share_path: Location where the Server Configuration Profile will be exported

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server Configuration profile is successful

        Failed: If the Server Configuration Profile could not be imported.

.. function:: idrac.config_mgr.scp_export_async(scp_share_path)

    Export Server Configuration Profile to share. This API returns immediately
    and returns the job id assocated with the import operation. Until the 
    operation is complete, iDRAC will not be accepting other jobs.

    :param omsdk.sdkfile.FileOnShare scp_share_path: Location where the Server Configuration Profile will be exported

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server Configuration profile is successful.  return_value['Job']['JobId'] has the Job ID associated with the export

        Failed: If the Server Configuration Profile could not be exported.

.. function:: idrac.config_mgr.sp_import(sp_share_path)

    Import Server Profile to iDRAC. This API waits for iDRAC to complete
    the import of Server Profile. Certain changes like RAID
    creation, would require the server to be rebooted after importing the
    Server Profile.

    :param omsdk.sdkfile.FileOnShare sp_share_path: Location from where the Server Profile is imported

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server profile is successful

        Failed: If the Server Profile could not be imported.

.. function:: idrac.config_mgr.sp_import_async(sp_share_path)

    Import Server Profile to iDRAC. This API returns immediately
    and returns the job id assocated with the import operation. Until the 
    operation is complete, iDRAC will not be accepting other jobs. Certain
    changes like RAID creation, would require the server to be rebooted
    after iDRAC successfully imported the Server Profile.

    :param omsdk.sdkfile.FileOnShare sp_share_path: Location where the Server Profile is stored

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server profile is successful.  return_value['Job']['JobId'] has the Job ID associated with the import

        Failed: If the Server Profile could not be imported.

.. function:: idrac.config_mgr.sp_export(sp_share_path)

    Export Server Profile to share. This API waits for
    iDRAC to complete the export of Server Profile to a 
    given share. 

    :param omsdk.sdkfile.FileOnShare sp_share_path: Location where the Server Profile will be exported

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server profile is successful

        Failed: If the Server Profile could not be imported.

.. function:: idrac.config_mgr.sp_export_async(sp_share_path)

    Export Server Profile to share. This API returns immediately
    and returns the job id assocated with the import operation. Until the 
    operation is complete, iDRAC will not be accepting other jobs.

    :param omsdk.sdkfile.FileOnShare sp_share_path: Location where the Server Profile will be exported

    :return: JSON object returning the status of the command

    Return Values:

        Success : If the Server profile is successful.  return_value['Job']['JobId'] has the Job ID associated with the export

        Failed: If the Server Profile could not be exported.



Jobs, Logs and LC Status
========================

.. function:: idrac.config_mgr.wait_till_lc_ready(timeout)

    Wait for timeout or till LC is ready.

.. function:: idrac.config_mgr.lc_status()

    Retrieve the status of server and Lifecycle Controller

Jobs
----

.. function:: idrac.job_mgr.get_jobs()

    Get Jobs

.. function:: idrac.job_mgr.get_job_details(jobid)

    Get Details of a given job id

.. function:: idrac.job_mgr.get_job_status(jobid)

    Get Job status

.. function:: idrac.job_mgr.queue_jobs(job_list, schtime)

    Queue a list of jobs

.. function:: idrac.job_mgr.job_wait(jobid, track_jobid, show_progress)

    Wait for a job to complete

.. function:: idrac.job_mgr.delete_job(jobid)

   Delete the given job id

.. function:: idrac.job_mgr.delete_all_jobs()

    Delete all jobs

Logs
----

.. function:: idrac.log_mgr.clear_logs()

    Clear LC Logs

.. function:: idrac.log_mgr.clear_sel_logs()

    Clear SEL Logs

.. function:: idrac.log_mgr.get_logs()

    Get LC Logs

.. function:: idrac.log_mgr.get_logs_for_job(jobid)

    Get LC Logs for a given job. Requires Liason Share to be configure.

.. function:: idrac.log_mgr.get_logs_for_last_job()

    Get LC Logs for the last job. Requires Liason Share to be configure.

.. function:: idrac.log_mgr.get_sel_logs()

    Get SEL Logs

.. function:: idrac.log_mgr.lclog_export(myshare)

    Export LC Logs to Share

.. function:: idrac.log_mgr.lclog_export_async(myshare)

    Export LC Logs to Share asynchronously.


License
=======

.. attribute:: idrac.license_mgr.LicensableDevices

.. function:: idrac.license_mgr.import_license(license_file, component, options)

    Import License for a given component from a local share.

.. function:: idrac.license_mgr.import_license_share(license_share_path, component, options)

    Import License from a remote share

.. function:: idrac.license_mgr.export_license(folder)

    Export license to a local folder

.. function:: idrac.license_mgr.export_license_share(license_share_path)

    Export license to a remote share

.. function:: idrac.license_mgr.delete_license(entitlementId, component, options)

    Delete a given license

.. function:: idrac.license_mgr.replace_license(license_file, entitlementId, component, options)

    Replace an existing license with the new one.


Update
======

.. function:: idrac.update_mgr.get_swidentity()

    Get Software/Firmware Inventory

.. function:: idrac.update_mgr.save_invcollector_file(invcol_output_file)

    Save Inventory Collector Output file

.. function:: idrac.update_mgr.update_from_repo(myshare, catalog, apply_update, reboot_needed)

    Update from Repository and wait till the job is complete

.. function:: idrac.update_mgr.update_from_repo_async(myshare, catalog, apply_update, reboot_needed)

    Update from Repository and wait till the job is complete

.. function:: idrac.update_mgr.update_get_repolist()

    Get the Update Repo List

Users
=====

Provides APIs for listing, adding, modifying and removing Users local to iDRAC.

.. attribute::     idrac.user_mgr.Users

    Returns a JSON object containing list of all local users. For more details
    about the properties and values, refer to iDRAC Attribute Registry Guide

    You can create upto 16 local users.

    A sample response from the API is as follows:

.. code-block:: rest

        [
            {
                "AuthenticationProtocol": "SHA",
                "Enable": "Enabled",
                "IpmiLanPrivilege": "Administrator",
                "IpmiSerialPrivilege": "Administrator",
                "PrivacyProtocol": "AES",
                "Privilege": "511",
                "ProtocolEnable": "Disabled",
                "Slot": 2,
                "SolEnable": "Enabled",
                "UserName": "root"
            },
            {
                "AuthenticationProtocol": "SHA",
                "Enable": "Enabled",
                "IpmiLanPrivilege": "Operator",
                "IpmiSerialPrivilege": "User",
                "PrivacyProtocol": "AES",
                "Privilege": "511",
                "ProtocolEnable": "Enabled",
                "Slot": 5,
                "SolEnable": "Enabled",
                "UserName": "vaidees"
            }
        ]

.. function:: idrac.user_mgr.create_user(username, password, user_privilege, others)

    This function creates a idrac local user.
    :param str username: Name of the local user
    :param str password: Password for the given user
    :param UserPrivilegeEnum: Privileges that need to be assiged to the user. User can be assigned as an Administrator, Operator, ReadOnly privileges or NoPrivilege at all.
    :param JSON others: Provides options for other capabilities (Serial On LAN, Protocol, IPMI LAN Privilege and IPMI over Serial privileges)

    :return: JSON Returns a json indicating whether the user was created successfully or not.

    

.. function:: idrac.user_mgr.change_password(username, old_password, new_password)

    This function creates a idrac local user.
    :param str username: Name of the local user
    :param str old_password: Old password for the given user
    :param str new_password: New password for the given user

    :return: JSON Returns a json indicating whether the password has been modified or not



.. function:: idrac.user_mgr.change_privilege(username, user_privilege, others)

    This function creates a idrac local user.
    :param str username: Name of the local user
    :param str user_privilege: New privileges that should be applied to user
    :param str others: Other privileges

    :return: JSON Returns a json indicating whether the privileges has been modified or not

.. function:: idrac.user_mgr.disable_user(username)

    This function disable a idrac local user.
    :param str username: Name of the local user

    :return: JSON Returns a json indicating whether user is disabled or not

.. function:: idrac.user_mgr.enable_user(username)

    This function enable a idrac local user.
    :param str username: Name of the local user

    :return: JSON Returns a json indicating whether user is enabled or not

.. function:: idrac.user_mgr.delete_user(username)

    This function delete a idrac local user.
    :param str username: Name of the local user

    :return: JSON Returns a json indicating whether user is deleted or not

Miscellaneous
=============

Following are commands to perform miscellaneous tasks

LC Wipe
-------

.. function:: idrac.config_mgr.lc_wipe()

    Wipes out all the configuration and data. Useful command if you want
    to wipe content of physical disks before  decommissioning the server.

Resetting iDRAC
---------------

.. function:: idrac.config_mgr.reset_idrac(force)

    Reset iDRAC

.. function:: idrac.config_mgr.reset_to_factory(preserve_config, force)

    Reset iDRAC to factory defaults

.. function:: idrac.config_mgr.export_tsr(tsr_store_path)

   Export Technical Service Report

.. function:: idrac.config_mgr.export_tsr_async(tsr_store_path)

   Export Technical Service Report

.. function:: idrac.config_mgr.factory_export(factory_details_path)

   Export Factory  Details

.. function:: idrac.config_mgr.factory_export_async(factory_details_path)

   Export Factory Details

.. function:: idrac.config_mgr.inventory_export(inventory_details_path)

   Export iDRAC Inventory

.. function:: idrac.config_mgr.inventory_export_async(inventory_details_path)

   Export iDRAC Inventory Async

.. function:: idrac.config_mgr.configure_part_update(part_fw_update, part_config_update)

    Configure Part Firmware Updates
