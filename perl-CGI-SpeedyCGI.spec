#
# Conditional build:
%bcond_without	tests	# do not perform "make test"
%bcond_without	apache1	# don't build apache1 module
%bcond_without	apache2	# don't build apache2 module
#
%define	apxs	/usr/sbin/apxs
%define	apxs1	/usr/sbin/apxs1
%include 	/usr/lib/rpm/macros.perl
%define		pdir	CGI
%define		pnam	SpeedyCGI
Summary:	Speed up perl CGI scripts by running them persistently
Summary(pl):	Modu³ przyspieszaj±cy perlowe skrypty CGI
Name:		perl-CGI-SpeedyCGI
Version:	2.22
Release:	9
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://www.cpan.org/modules/by-module/%{pdir}/%{pdir}-%{pnam}-%{version}.tar.gz
# Source0-md5:	2f80df78874e3efa80f180923c4967a1
Source1:	apache-mod_speedycgi.conf
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-APXS.patch
Patch2:		%{name}-apr.patch
URL:		http://daemoninc.com/SpeedyCGI/
%{?with_apache2:BuildRequires:	apache-devel}
%{?with_apache1:BuildRequires:	apache1-devel}
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 3.0.3-16
Requires:	perl(DynaLoader) = %(%{__perl} -MDynaLoader -e 'print DynaLoader->VERSION')
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if %{with apache2}
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)
%define		httpdir		/home/services/httpd
%endif
%if %{with apache1}
%define		_pkglibdir1	%(%{apxs1} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir1	%(%{apxs1} -q SYSCONFDIR 2>/dev/null)
%define		httpdir1		/home/services/apache
%endif

%description
SpeedyCGI is a way to run CGI perl scripts persistently, which usually
makes them run much more quickly. After the script is initially run,
instead of exiting, SpeedyCGI keeps the perl interpreter running in
memory. During subsequent runs, this interpreter is used to handle new
requests, instead of starting a new perl interpreter for each
execution.

%description -l pl
SpeedyCGI to sposób na ci±g³e dzia³anie perlowych skryptów CGI, co
zazwyczaj powoduje, ¿e uruchamiaj± siê du¿o szybciej. Po pocz±tkowym
uruchomieniu skryptu, SpeedyCGI trzyma interpreter Perla w pamiêci.
Przy kolejnych uruchomieniach ten interpreter jest wykorzystywany do
obs³ugi kolejnych zleceñ, zamiast uruchamiania nowego interpretera
Perla do ka¿dego uruchomienia skryptu.

%package -n apache-mod_speedycgi
Summary:	SpeedyCGI apache module
Summary(pl):	Modu³ apache SpeedyCGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	apache(modules-api) = %apache_modules_api
Requires:	apache >= 2.0.36
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache-mod_speedycgi
SpeedyCGI apache module.

%description -n apache-mod_speedycgi -l pl
Modu³ apache SpeedyCGI.

%package -n apache1-mod_speedycgi
Summary:	SpeedyCGI apache module
Summary(pl):	Modu³ apache SpeedyCGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache1-mod_speedycgi
SpeedyCGI apache module.

%description -n apache1-mod_speedycgi -l pl
Modu³ apache SpeedyCGI.

%prep
%setup -q -n %{pdir}-%{pnam}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__perl} Makefile.PL </dev/null \
	INSTALLDIRS=vendor
%{?with_apache1:cd mod_speedycgi && perl Makefile.PL && cd ..}
%{?with_apache2:cd mod_speedycgi2 && perl Makefile.PL && cd ..}

%{__make} \
	OPTIMIZE="%{rpmcflags}"

%if %{with apache1}
%{__make} -C mod_speedycgi APXS="%{apxs1}" \
	OPTIMIZE="%{rpmcflags}"
%endif
%if %{with apache2}
%{__make} -C mod_speedycgi2 APXS="%{apxs}" \
	OPTIMIZE="%{rpmcflags}"
%endif

%{?with_test:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{perl_archlib}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with apache1}
install -d $RPM_BUILD_ROOT{%{_pkglibdir1},%{httpdir1}/speedy,%{_sysconfdir1}/conf.d}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir1}/conf.d/mod_speedycgi.conf
install mod_speedycgi/mod_speedycgi.so $RPM_BUILD_ROOT%{_pkglibdir1}
%endif
%if %{with apache2}
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{httpdir}/speedy,%{_sysconfdir}/httpd.conf}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/90_mod_speedycgi.conf
install mod_speedycgi2/mod_speedycgi.so $RPM_BUILD_ROOT%{_pkglibdir}
%endif

ln -s speedy $RPM_BUILD_ROOT%{_bindir}/speedycgi

%clean
rm -rf $RPM_BUILD_ROOT

%post -n apache-mod_speedycgi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%post -n apache1-mod_speedycgi
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
fi

%preun -n apache-mod_speedycgi
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%preun -n apache1-mod_speedycgi
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README docs contrib
%{perl_vendorlib}/CGI/*.pm
%attr(755,root,root) %{_bindir}/speedy*

%if %{with apache1}
%files -n apache1-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir1}/conf.d/*mod_speedycgi.conf
%attr(755,root,root) %{_pkglibdir1}/mod_speedycgi.so
%dir %{httpdir1}/*
%endif

%if %{with apache2}
%files -n apache-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf/*mod_speedycgi.conf
%attr(755,root,root) %{_pkglibdir}/mod_speedycgi.so
%dir %{httpdir}/*
%endif
