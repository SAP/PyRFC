%global srcname PyRFC

%define debug_package %{nil}

Name:       python-PyRFC
Version:	1.9.6
Release:	1%{?dist}
Summary:    Python bindings for SAP NetWeaver RFC Library

License:	ASL 2.0
URL:		https://github.com/SAP/PyRFC/archive/%{version}/%{srcname}-%{version}.tar.gz
Source0:	%{srcname}-%{version}.tar.gz

%if 0%{?rhel}
# Require Cython 1.9 which is available on RHEL7
Patch0:     PyRFC-Cython-RHEL7.patch
%endif

BuildRequires:  epel-rpm-macros
BuildRequires:  python-devel
BuildRequires:  Cython


%description
The pyrfc Python package provides Python bindings for SAP NetWeaver RFC
Library, for a comfortable way of calling ABAP modules from Python and Python
modules from ABAP, via SAP Remote Function Call (RFC) protocol.


%prep
%autosetup -n %{srcname}-%{version}


%build
# Set PYTHONSOURCE to a dummy value - required for Windows.
export PYTHONSOURCE="/tmp"
%py_build


%install
export PYTHONSOURCE="/tmp"
%py_install


%files
%doc
%{python_sitearch}/*


%changelog
* Wed Apr 05 2017 Jakub Filak <jakub.filak@sap.com> - 1.9.6
- Initial packaging
