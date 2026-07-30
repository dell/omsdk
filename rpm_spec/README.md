# EL8 + Python 3 RPM spec

To build/use, first create a structure for building RPMs:
```
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cp python-omsdk.spec ~/rpmbuild/SPECS
cd ~/rpmbuild/SPECS
```

Download sources:
```
dnf install -y rpmdevtools
spectool -g -R python-omsdk.spec
```

Install build dependencies:
```
dnf install -y dnf-plugins-core epel-release
dnf builddep python-omsdk.spec
```

Build RPMs:
```
dnf install -y rpm-build
rpmbuild -ba python-omsdk.spec
```

Install RPMs:
```
dnf install ~/rpmbuild/RPMS/noarch/python3-{omsdk,omdrivers}*.noarch.rpm
```
