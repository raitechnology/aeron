Name:		aeron
Version:	999.999
Release:	99999%{?dist}
Summary:	A reliable messaging system

License:	ASL 2.0
URL:		https://github.com/real-logic/%{name}
Source0:	%{name}-%{version}-99999.tar.gz
BuildRoot:	${_tmppath}
Prefix:	        /usr
BuildRequires:  gcc-c++
BuildRequires:  chrpath
BuildRequires:  libbsd-devel
BuildRequires:  hdrhist
Requires:       zlib
Requires:       libbsd
Requires:       hdrhist
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
Efficient reliable UDP unicast, UDP multicast, and IPC message transport.

%prep
%setup -q


%define _unpackaged_files_terminate_build 0
%define _missing_doc_files_terminate_build 0
%define _missing_build_ids_terminate_build 0
%define _include_gdb_index 1

%build
make build_dir=./usr %{?_smp_mflags} dist_bins
# install include files: cpp client, c client, media driver
install -d ./usr/include
for i in $(find aeron-client/src/main/cpp/ -type d -print) ; do
install -d $i ./usr/include/${i#aeron-client/src/main/cpp/} ;
done
for i in $(find aeron-client/src/main/cpp/ -name '*.h' -print) ; do
install -m 644 $i ./usr/include/${i#aeron-client/src/main/cpp/} ;
done
install -d ./usr/include/aeron
for i in $(find aeron-client/src/main/c/ -type d -print) ; do
install -d $i ./usr/include/aeron/${i#aeron-client/src/main/c/} ;
done
for i in $(find aeron-client/src/main/c/ -name '*.h' -print) ; do
install -m 644 $i ./usr/include/aeron/${i#aeron-client/src/main/c/} ;
done
install -d ./usr/include/aeronmd
for i in $(find aeron-driver/src/main/c/ -type d -print) ; do
install -d $i ./usr/include/aeronmd/${i#aeron-driver/src/main/c/} ;
done
for i in $(find aeron-driver/src/main/c/ -name '*.h' -print) ; do
install -m 644 $i ./usr/include/aeronmd/${i#aeron-driver/src/main/c/} ;
done

install -d ./usr/share/doc/%{name}
install -m 644 README.md LICENSE CONTRIBUTING.md ./usr/share/doc/%{name}/

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/bin/*
/usr/lib64/*
/usr/include/*
/usr/share/doc/*

%post
echo "${RPM_INSTALL_PREFIX}/lib64" > /etc/ld.so.conf.d/%{name}.conf
/sbin/ldconfig

%postun
# if uninstalling
if [ $1 -eq 0 ] ; then
  rm -f /etc/ld.so.conf.d/%{name}.conf
fi
/sbin/ldconfig

%changelog
* __DATE__ <gchrisanderson@gmail.com>
- Hello world
