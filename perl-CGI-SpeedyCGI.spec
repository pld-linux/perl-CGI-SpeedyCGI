#
# TODO:
# - build apache1-mod_* for apache1 and apache-mod_* for apache2
#
# Conditional build:
%bcond_without	tests	# do not perform "make test"
%bcond_without	apache1	# do not use apache1 instead of apache (apxs1 instead apxs)
#
%define	apxs	/usr/sbin/apxs%{?with_apache1:1}
%include 	/usr/lib/rpm/macros.perl
%define		pdir	CGI
%define		pnam	SpeedyCGI
Summary:	Speed up perl CGI scripts by running them persistently
Summary(pl):	Modu� przyspieszaj�cy perlowe skrypty CGI
Name:		perl-CGI-SpeedyCGI
Version:	2.22
Release:	6.1
License:	GPL v2+
Group:		Networking/Daemons
URL:		http://daemoninc.com/SpeedyCGI/
Source0:	http://www.cpan.org/modules/by-module/%{pdir}/%{pdir}-%{pnam}-%{version}.tar.gz
# Source0-md5:	2f80df78874e3efa80f180923c4967a1
Source1:	apache-mod_speedycgi.conf
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-APXS.patch
BuildRequires:	apache%{?with_apache1:1}-devel
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 3.0.3-16
Requires(post,preun):	/usr/sbin/apxs%{?with_apache1:1}
Requires(post,preun):	apache%{?with_apache1:1}
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	perl(DynaLoader) = %(%{__perl} -MDynaLoader -e 'print DynaLoader->VERSION')
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR)
%define		httpdir		/home/services/httpd

%description
SpeedyCGI is a way to run CGI perl scripts persistently, which usually
makes them run much more quickly. After the script is initially run,
instead of exiting, SpeedyCGI keeps the perl interpreter running in
memory. During subsequent runs, this interpreter is used to handle new
requests, instead of starting a new perl interpreter for each
execution.

%description -l pl
SpeedyCGI to spos�b na ci�g�e dzia�anie perlowych skrypt�w CGI, co
zazwyczaj powoduje, �e uruchamiaj� si� du�o szybciej. Po pocz�tkowym
uruchomieniu skryptu, SpeedyCGI trzyma interpreter Perla w pami�ci.
Przy kolejnych uruchomieniach ten interpreter jest wykorzystywany do
obs�ugi kolejnych zlece�, zamiast uruchamiania nowego interpretera
Perla do ka�dego uruchomienia skryptu.

%package -n apache-mod_speedycgi
Summary:	SpeedyCGI apache module
Summary(pl):	Modu� apache SpeedyCGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache-mod_speedycgi
SpeedyCGI apache module.

%description -n apache-mod_speedycgi -l pl
Modu� apache SpeedyCGI.

%prep
%setup -q -n %{pdir}-%{pnam}-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__perl} Makefile.PL </dev/null \
	INSTALLDIRS=vendor
cd mod_speedycgi && perl Makefile.PL
cd ..

%{__make} \
	OPTIMIZE="%{rpmcflags}"
%{__make} -C mod_speedycgi APXS="%{apxs}" \
	OPTIMIZE="%{rpmcflags}"

%{?with_test:%{__make} test}

APXS="%{apxs}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{perl_archlib} \
	$RPM_BUILD_ROOT{%{_pkglibdir},%{httpdir}/speedy,%{_sysconfdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/mod_speedycgi.conf
install mod_speedycgi/mod_speedycgi.so $RPM_BUILD_ROOT%{_pkglibdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post -n apache-mod_speedycgi
%{apxs} -e -a -n speedycgi %{_pkglibdir}/mod_speedycgi.so 1>&2
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*mod_speedycgi.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/mod_speedycgi.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache HTTP daemon."
fi

%preun -n apache-mod_speedycgi
if [ "$1" = "0" ]; then
	umask 027
	%{apxs} -e -A -n speedycgi %{_pkglibdir}/mod_speedycgi.so 1>&2
	grep -v "^Include.*mod_speedycgi.conf" /etc/httpd/httpd.conf > \
		/etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README docs contrib
%{perl_vendorlib}/CGI/*.pm
%attr(755,root,root) %{_bindir}/speedy*

%files -n apache-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mod_speedycgi.conf
%attr(755,root,root) %{_pkglibdir}/mod_speedycgi.so
%dir %{httpdir}
