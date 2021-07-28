 
# Dell EMC OpenManage Python SDK

DellEMC OpenManage Python SDK (OMSDK) is a python library that helps developers and customers to automate the lifecycle management of PowerEdge Servers. OMSDK module leverages the iDRAC's REST APIs based on [DMTF Redfish standards](https://www.dmtf.org/standards/redfish) as well as [WS-Man](https://www.dmtf.org/standards/ws-man) and SNMP protocols for configuration, deployment, updates and monitoring of PowerEdge Servers.  In addition, OMSDK also supports monitoring and querying inventory information for PowerEdge Modular Infrastructure (M1000e, VRTX and FX2).

## Supported Systems

All Dell EMC PowerEdge 12th and above Generation of PowerEdge Servers, and Chassis Management Controllers of Dell EMC PowerEdge M1000e, Dell EMC PowerEdge VRTX and Dell EMC PowerEdge FX2 Chassis

  * iDRAC 7/8 with Firmware Versions 2.41.40.40 or above
  * iDRAC 9 with Firmware Versions 3.00.00.00 or above

# Prerequisites
Dell EMC OpenManage Python SDK is supported for python 2.7 and above.
  
  * Install the prerequisites using the requirements file on python 2.x as:

    ``` pip install -r requirements-python2x.txt ```

  * Install the prerequisites using the requirements file on python 3.x as:

    ``` pip3 install -r requirements-python3x.txt ```
    
# Installation
  * This branch contains the build version 1.2.478
  * Install the latest development version from github:

	```
	git clone https://github.com/dell/omsdk.git
	cd omsdk
	sh build.sh 1.2 478
	cd dist
	pip install omsdk-1.2.478-py2.py3-none-any.whl
	```
	* If omsdk build creation fails due to `python` command error, configure
	 `python` to launch either `python2` or `python3`. Accordingly configure the `pip` command.
	* Upgrading to latest version of python setuptools and wheel is
	 recommended.
	* omsdk installation may fail with pip version 10.0 and above, follow one of the following steps in such scenario
	
		* Downgrade pip version to lower than 10.0 and then install omsdk
		* Force install omsdk using:
		  ```pip install --ignore-installed omsdk-1.2.478-py2.py3-none-any.whl```
		  
# Uninstallation
  * Uninstall this module as follows:

    ```
	   pip uninstall omsdk
	```

# Documentation
Refer to the [documentation](./docs) for details on how to use this SDK

# Licensing
Licensed under the Apache Software License, version 2.0 (the "License"); you may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# Support
  * Dell EMC OpenManage Python SDK is supported by OpenManage developers team.
  * If you want to report any issue, then please report it by creating a new issue [here](https://github.com/dell/omsdk/issues)
  * If you have any requirements that is not currently addressed, then please let us know by creating a new issue [here](https://github.com/dell/omsdk/issues)
  * If you want to provide any feedback to the development team, then you can do so by sending an email to OpenManageSDK@Dell.com

# Authors
OpenManageSDK (OpenManageSDK@Dell.com)
