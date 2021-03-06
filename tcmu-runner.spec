%global _hardened_build 1

# without rbd dependency
# if you wish to exclude rbd handlers in RPM, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without rbd
%{?_without_rbd:%global _without_rbd -Dwith-rbd=false}

# without glusterfs dependency
# if you wish to exclude glfs handlers in RPM, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without glfs
%{?_without_glfs:%global _without_glfs -Dwith-glfs=false}

# without qcow dependency
# if you wish to exclude qcow handlers in RPM, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without qcow
%{?_without_qcow:%global _without_qcow -Dwith-qcow=false}

# without zbc dependency
# if you wish to exclude zbc handlers in RPM, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without zbc
%{?_without_zbc:%global _without_zbc -Dwith-zbc=false}

# without file backed optical dependency
# if you wish to exclude fbo handlers in RPM, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without fbo
%{?_without_fbo:%global _without_fbo -Dwith-fbo=false}



Name:          tcmu-runner
Summary:       A daemon that handles the userspace side of the LIO TCM-User backstore
Group:         System Environment/Daemons
License:       Apache 2.0 or LGPLv2.1
Version:       1.4.0
URL:           https://github.com/open-iscsi/tcmu-runner

#%define _RC
Release:       %{?_RC:%{_RC}}%{dist}
BuildRoot:     %(mktemp -udp %{_tmppath}/%{name}-%{version}%{?_RC:-%{_RC}})
Source:       %{name}-%{version}%{?_RC:-%{_RC}}.tar.gz
ExclusiveOS:   Linux

BuildRequires: cmake make gcc
BuildRequires: libnl3-devel glib2-devel zlib-devel kmod-devel

%if ( 0%{!?_without_rbd:1} )
BuildRequires: librbd1-devel librados2-devel
Requires(pre): librados2, librbd1
%endif

%if ( 0%{!?_without_glfs:1} )
BuildRequires: glusterfs-api-devel
Requires(pre): glusterfs-api
%endif

Requires(pre): kmod, zlib, libnl3, glib2, logrotate, rsyslog
Requires:      libtcmu = %{version}-%{release}

%description
A daemon that handles the userspace side of the LIO TCM-User backstore.

LIO is the SCSI target in the Linux kernel. It is entirely kernel code, and
allows exported SCSI logical units (LUNs) to be backed by regular files or
block devices. But, if we want to get fancier with the capabilities of the
device we're emulating, the kernel is not necessarily the right place. While
there are userspace libraries for compression, encryption, and clustered
storage solutions like Ceph or Gluster, these are not accessible from the
kernel.

The TCMU userspace-passthrough backstore allows a userspace process to handle
requests to a LUN. But since the kernel-user interface that TCMU provides
must be fast and flexible, it is complex enough that we'd like to avoid each
userspace handler having to write boilerplate code.

tcmu-runner handles the messy details of the TCMU interface -- UIO, netlink,
pthreads, and DBus -- and exports a more friendly C plugin module API. Modules
using this API are called "TCMU handlers". Handler authors can write code just
to handle the SCSI commands as desired, and can also link with whatever
userspace libraries they like.

%package -n libtcmu
Summary:       A library supporting LIO TCM-User backstores processing
Group:         Development/Libraries

%description -n libtcmu
libtcmu provides a library for processing SCSI commands exposed by the
LIO kernel target's TCM-User backend.

%package -n libtcmu-devel
Summary:       Development headers for libtcmu
Group:         Development/Libraries
Requires:      %{name} = %{version}-%{release}
Requires:      libtcmu = %{version}-%{release}

%description -n libtcmu-devel
Development header(s) for developing against libtcmu.

%global debug_package %{nil}

%prep
%setup -n %{name}-%{version}%{?_RC:-%{_RC}}

%build
%{__cmake} \
 -DSUPPORT_SYSTEMD=ON -DCMAKE_INSTALL_PREFIX=%{_usr} \
 %{?_without_rbd} \
 %{?_without_zbc} \
 %{?_without_qcow} \
 %{?_without_glfs} \
 %{?_without_fbo} \
 .
%{__make}

%install
%{__make} DESTDIR=%{buildroot} install
%{__rm} -f %{buildroot}/etc/tcmu/tcmu.conf.old
%{__rm} -f %{buildroot}/etc/logrotate.d/tcmu-runner.old

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/tcmu-runner
%dir %{_sysconfdir}/dbus-1/
%dir %{_sysconfdir}/dbus-1/system.d
%config %{_sysconfdir}/dbus-1/system.d/tcmu-runner.conf
%dir %{_datadir}/dbus-1/
%dir %{_datadir}/dbus-1/system-services/
%{_datadir}/dbus-1/system-services/org.kernel.TCMUService1.service
%{_unitdir}/tcmu-runner.service
%dir %{_libdir}/tcmu-runner/
%{_libdir}/tcmu-runner/*.so
%{_mandir}/man8/*
%doc README.md LICENSE.LGPLv2.1 LICENSE.Apache2
%dir %{_sysconfdir}/tcmu/
%config %{_sysconfdir}/tcmu/tcmu.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/tcmu-runner

%files -n libtcmu
%{_libdir}/libtcmu*.so.*

%files -n libtcmu-devel
%{_includedir}/libtcmu.h
%{_includedir}/libtcmu_common.h
%{_libdir}/libtcmu*.so
