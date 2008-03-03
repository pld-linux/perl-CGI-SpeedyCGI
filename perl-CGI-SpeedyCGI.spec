#
# Conditional build:
%bcond_without	tests	# do not perform "make test"
%bcond_without	apache1	# don't build apache1 module
%bcond_without	apache2	# don't build apache2 module
#
%define	apxs1	/usr/sbin/apxs1
%define	apxs2	/usr/sbin/apxs
%include 	/usr/lib/rpm/macros.perl
%define		pdir	CGI
%define		pnam	SpeedyCGI
Summary:	Speed up perl CGI scripts by running them persistently
Summary(pl.UTF-8):	Moduł przyspieszający perlowe skrypty CGI
Name:		perl-CGI-SpeedyCGI
Version:	2.22
Release:	14
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://www.cpan.org/modules/by-module/%{pdir}/%{pdir}-%{pnam}-%{version}.tar.gz
# Source0-md5:	2f80df78874e3efa80f180923c4967a1
Source1:	apache-mod_speedycgi.conf
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-APXS.patch
Patch2:		%{name}-debian.patch
URL:		http://daemoninc.com/SpeedyCGI/
%{?with_apache2:BuildRequires:	apache-devel}
%{?with_apache1:BuildRequires:	apache1-devel}
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	perl(DynaLoader) = %(%{__perl} -MDynaLoader -e 'print DynaLoader->VERSION')
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if %{with apache1}
%define		apache1confdir	%(%{apxs1} -q SYSCONFDIR 2>/dev/null)/conf.d
%define		apache1libdir	%(%{apxs1} -q LIBEXECDIR 2>/dev/null)
%define		apache1docdir	/home/services/apache
%endif
%if %{with apache2}
%define		apache2confdir	%(%{apxs2} -q SYSCONFDIR 2>/dev/null)/conf.d
%define		apache2libdir	%(%{apxs2} -q LIBEXECDIR 2>/dev/null)
%define		apache2docdir	/home/services/httpd
%endif

%description
SpeedyCGI is a way to run CGI perl scripts persistently, which usually
makes them run much more quickly. After the script is initially run,
instead of exiting, SpeedyCGI keeps the perl interpreter running in
memory. During subsequent runs, this interpreter is used to handle new
requests, instead of starting a new perl interpreter for each
execution.

%description -l pl.UTF-8
SpeedyCGI to sposób na ciągłe działanie perlowych skryptów CGI, co
zazwyczaj powoduje, że uruchamiają się dużo szybciej. Po początkowym
uruchomieniu skryptu, SpeedyCGI trzyma interpreter Perla w pamięci.
Przy kolejnych uruchomieniach ten interpreter jest wykorzystywany do
obsługi kolejnych zleceń, zamiast uruchamiania nowego interpretera
Perla do każdego uruchomienia skryptu.

%package -n apache-mod_speedycgi
Summary:	SpeedyCGI apache module
Summary(pl.UTF-8):	Moduł apache SpeedyCGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache-mod_speedycgi
SpeedyCGI apache module.

%description -n apache-mod_speedycgi -l pl.UTF-8
Moduł apache SpeedyCGI.

%package -n apache1-mod_speedycgi
Summary:	SpeedyCGI apache module
Summary(pl.UTF-8):	Moduł apache SpeedyCGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	apache1 >= 1.3.33-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache1-mod_speedycgi
SpeedyCGI apache module.

%description -n apache1-mod_speedycgi -l pl.UTF-8
Moduł apache SpeedyCGI.

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

%{__make} -j1 \
	CC="%{__cc}" \
	OPTIMIZE="%{rpmcflags}"

%if %{with apache1}
%{__make} -C mod_speedycgi APXS="%{apxs1}" \
	CC="%{__cc}" \
	OPTIMIZE="%{rpmcflags}"
%endif
%if %{with apache2}
%{__make} -C mod_speedycgi2 APXS="%{apxs2}" \
	CC="%{__cc}" \
	OPTIMIZE="%{rpmcflags}"
%endif

%{?with_test:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{perl_archlib}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with apache1}
install -d $RPM_BUILD_ROOT{%{apache1libdir},%{apache1docdir}/speedy,%{apache1confdir}}
install %{SOURCE1} $RPM_BUILD_ROOT%{apache1confdir}/mod_speedycgi.conf
install mod_speedycgi/mod_speedycgi.so $RPM_BUILD_ROOT%{apache1libdir}
%endif
%if %{with apache2}
install -d $RPM_BUILD_ROOT{%{apache2libdir},%{apache2docdir}/speedy,%{apache2confdir}}
install %{SOURCE1} $RPM_BUILD_ROOT%{apache2confdir}/90_mod_speedycgi.conf
install mod_speedycgi2/mod_speedycgi.so $RPM_BUILD_ROOT%{apache2libdir}
%endif

ln -s speedy $RPM_BUILD_ROOT%{_bindir}/speedycgi

%clean
rm -rf $RPM_BUILD_ROOT

%post -n apache-mod_speedycgi
%service -q httpd restart

%post -n apache1-mod_speedycgi
%service -q apache restart

%preun -n apache-mod_speedycgi
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%preun -n apache1-mod_speedycgi
if [ "$1" = "0" ]; then
	%service -q apache restart
fi

%files
%defattr(644,root,root,755)
%doc README docs contrib
%{perl_vendorlib}/CGI/*.pm
%attr(755,root,root) %{_bindir}/speedy*

%if %{with apache1}
%files -n apache1-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{apache1confdir}/*mod_speedycgi.conf
%attr(755,root,root) %{apache1libdir}/mod_speedycgi.so
%dir %{apache1docdir}/*
%endif

%if %{with apache2}
%files -n apache-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{apache2confdir}/*mod_speedycgi.conf
%attr(755,root,root) %{apache2libdir}/mod_speedycgi.so
%dir %{apache2docdir}/*
%endif
