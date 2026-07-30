Name:           python-omsdk
Version:        1.2.481
Release:        1%{?dist}
Summary:        Dell EMC OpenManage Python SDK inc. drivers
License:        ASL 2.0
URL:            https://github.com/dell/omsdk
Source0:        https://github.com/dell/omsdk/archive/refs/tags/v%{version}.tar.gz
BuildArch:      noarch

%description
DellEMC OpenManage Python SDK (OMSDK) is a python library that helps developers
and customers to automate the lifecycle management of PowerEdge Servers. OMSDK
module leverages the iDRAC's REST APIs based on DMTF Redfish standards as well
as WS-Man and SNMP protocols for configuration, deployment, updates and
monitoring of PowerEdge Servers. In addition, OMSDK also supports monitoring
and querying inventory information for PowerEdge Modular Infrastructure
(M1000e, VRTX and FX2).


%package -n python%{python3_pkgversion}-omsdk
Summary: Dell EMC OpenManage Python SDK
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
#Requires:       python#{python3_pkgversion}-certifi
Requires:       python%{python3_pkgversion}-charset-normalizer
Requires:       python%{python3_pkgversion}-future
Requires:       python%{python3_pkgversion}-idna
Requires:       python%{python3_pkgversion}-ply
Requires:       python%{python3_pkgversion}-pyasn1
Requires:       python%{python3_pkgversion}-pycryptodomex
Requires:       python%{python3_pkgversion}-pysnmp
Requires:       python%{python3_pkgversion}-pysnmp
Requires:       python%{python3_pkgversion}-pyyaml
Requires:       python%{python3_pkgversion}-requests
Requires:       python%{python3_pkgversion}-smi
Requires:       python%{python3_pkgversion}-urllib3

%{?python_provide:%python_provide python%{python3_pkgversion}-omsdk}

%description -n python%{python3_pkgversion}-omsdk
DellEMC OpenManage Python SDK (OMSDK) is a python library that helps developers
and customers to automate the lifecycle management of PowerEdge Servers. OMSDK
module leverages the iDRAC's REST APIs based on DMTF Redfish standards as well
as WS-Man and SNMP protocols for configuration, deployment, updates and
monitoring of PowerEdge Servers. In addition, OMSDK also supports monitoring
and querying inventory information for PowerEdge Modular Infrastructure
(M1000e, VRTX and FX2).

# omdrivers subpackage
%package -n python%{python3_pkgversion}-omdrivers
Summary: Drivers for Dell EMC OpenManage Python SDK
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
#Requires:       python#{python3_pkgversion}-certifi
Requires:       python%{python3_pkgversion}-charset-normalizer
Requires:       python%{python3_pkgversion}-future
Requires:       python%{python3_pkgversion}-idna
Requires:       python%{python3_pkgversion}-ply
Requires:       python%{python3_pkgversion}-pyasn1
Requires:       python%{python3_pkgversion}-pycryptodomex
Requires:       python%{python3_pkgversion}-pysnmp
Requires:       python%{python3_pkgversion}-pysnmp
Requires:       python%{python3_pkgversion}-pyyaml
Requires:       python%{python3_pkgversion}-requests
Requires:       python%{python3_pkgversion}-smi
Requires:       python%{python3_pkgversion}-urllib3
Requires:       python%{python3_pkgversion}-omsdk

%{?python_provide:%python_provide python%{python3_pkgversion}-omdrivers}

%description -n python%{python3_pkgversion}-omdrivers
Drivers for DellEMC OpenManage Python SDK (OMSDK)


%prep
%autosetup -p1 -n omsdk-%{version}

# Set the version more cleanly
sed -i "/with open('\/tmp\/_version.txt', 'r') as v:/d" setup-omdrivers.py setup-omsdk.py
sed -i '/    ver = v.read()/d' setup-omdrivers.py setup-omsdk.py
sed -i '/# Get the version from _version file/d' setup-omdrivers.py setup-omsdk.py
sed -i 's/    version=ver,/    version="%{version}",/' setup-omdrivers.py setup-omsdk.py

%build
%{__python3} setup-omdrivers.py build
%{__python3} setup-omsdk.py build

%install
%{__python3} setup-omdrivers.py install --skip-build --root $RPM_BUILD_ROOT
%{__python3} setup-omsdk.py install --skip-build --root $RPM_BUILD_ROOT


%files -n python%{python3_pkgversion}-omsdk
%license LICENSE
%doc README.rst
%{python3_sitelib}/omsdk/
%{python3_sitelib}/omsdk-*.egg-info/

%files -n python%{python3_pkgversion}-omdrivers
%license LICENSE
%{python3_sitelib}/omdrivers/
%{python3_sitelib}/omdrivers-*.egg-info/


%changelog

* Sat Jan 01 2022 Will Furnass <will@thearete.co.uk> - 1.2.481-1
- Initial package
