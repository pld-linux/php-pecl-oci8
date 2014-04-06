#
# Conditional build:
%bcond_without	instantclient	# build Oracle oci8 extension module against oracle-instantclient package
%bcond_without	tests		# build without tests
%bcond_with		run_tests	# run tests.php, needs connection to Oracle Database

%define		php_name	php%{?php_suffix}
%define		modname	oci8
Summary:	Extension to access Oracle database
Name:		%{php_name}-pecl-%{modname}
Version:	2.0.8
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	9de75c4649bb047c6192f13092f9751d
Patch0:		instantclient.patch
URL:		http://pecl.php.net/package/oci8/
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
%{?with_run_tests:BuildRequires:	%{php_name}-pcre}
%{?with_instantclient:BuildRequires:	oracle-instantclient-devel}
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(oci8) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
OCI8 extension to access Oracle Databases. The extension can be linked
with Oracle client libraries from Oracle Database 10.2, 11, or 12.1.

%prep
%setup -qc
mv %{modname}-%{version}/* .
%patch0 -p1

cat <<'EOF' > run-tests.sh
#!/bin/sh
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

%build
phpize
%configure \
	--with-oci8=shared%{?with_instantclient:,instantclient,%{_libdir}}
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

%if %{with run_tests}
./run-tests.sh -w failed.log --show-out
test -f failed.log -a ! -s failed.log
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{php_extensiondir}}

%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README CREDITS LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
