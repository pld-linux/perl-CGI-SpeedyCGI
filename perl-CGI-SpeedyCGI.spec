#
# Conditional build:
# _without_tests - do not perform "make test"
#
%include 	/usr/lib/rpm/macros.perl
%define		pdir	CGI
%define         pnam	SpeedyCGI
Summary:	Speed up perl CGI scripts by running them persistently
Summary(pl):	Modu³ przyspieszaj±cy perlowe skrypty CGI
Name:		perl-CGI-SpeedyCGI
Version:	2.21
Release:	3
License:	GPL
Group:		Networking/Daemons
URL:		http://daemoninc.com/SpeedyCGI/
Source0:	http://www.cpan.org/modules/by-module/%{pdir}/%{pdir}-%{pnam}-%{version}.tar.gz
Source1:	apache-mod_speedycgi.conf
Patch0:		%{name}-DESTDIR.patch
BuildRequires:	apache(EAPI)-devel
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	perl-devel >= 5.6
Requires(post,preun):	/usr/sbin/apxs
Requires(post,preun):	apache
Requires(post,preun):	grep
Requires(preun):	fileutils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		apxs		/usr/sbin/apxs
%define		apache_moddir	%(/usr/sbin/apxs -q LIBEXECDIR)
%define		httpdir		/home/services/httpd

%description 
SpeedyCGI is a way to run CGI perl scripts persistently, which usually
makes them run much more quickly. After the script is initially run,
instead of exiting, SpeedyCGI keeps the perl interpreter running in
memory. During subsequent runs, this interpreter is used to handle new
requests, instead of starting a new perl interpreter for each
execution.

%description -l pl
SpeedyCGI to sposób na ci±g³e dzia³anie perlowych skryptów CGI, co
zazwyczaj pododuje, ¿e uruchamiaj± siê du¿o szybciej. Po pocz±tkowym
uruchomieniu skryptu, SpeedyCGI trzyma interpreter perla w pamiêci.
Przy kolejnych uruchomieniach ten interpreter jest wykorzystywany do
obs³ugi kolejnych zleceñ, zamiast uruchamiania nowego interpretera
perla do ka¿dego uruchomienia skryptu.

%package -n apache-mod_speedycgi
Summary:	SpeedyCGI apache module
Summary(pl):	Modu³ apache SpeedyCGI
Group:		Networking/Daemons
Requires:	%{name} = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache-mod_speedycgi
SpeedyCGI apache module.

%description -n apache-mod_speedycgi -l pl
Modu³ apache SpeedyCGI.

%prep
%setup -q -n %{pdir}-%{pnam}-%{version}
%patch -p1

%build
%{__perl} Makefile.PL </dev/null
cd mod_speedycgi && perl Makefile.PL
cd ..

%{__make} OPTIMIZE="%{rpmcflags}"
%{__make} -C mod_speedycgi \
	OPTIMIZE="%{rpmcflags}"

%{!?_without_tests:%{__make} test}

APXS="%{apxs}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{perl_archlib} \
	$RPM_BUILD_ROOT{%{apache_moddir},%{httpdir}/speedy,%{_sysconfdir}/httpd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT 

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/mod_speedycgi.conf
install mod_speedycgi/mod_speedycgi.so $RPM_BUILD_ROOT%{apache_moddir}

%clean
rm -rf $RPM_BUILD_ROOT

%post -n apache-mod_speedycgi
%{apxs} -e -a -n speedycgi %{apache_moddir}/mod_speedycgi.so 1>&2
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*mod_speedycgi.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/mod_speedycgi.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache http daemon."
fi

%preun -n apache-mod_speedycgi
if [ "$1" = "0" ]; then
	umask 027
	%{apxs} -e -A -n speedycgi %{apache_moddir}/mod_speedycgi.so 1>&2
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
%{perl_sitelib}/CGI/*.pm
%attr(755,root,root) %{_bindir}/speedy*

%files -n apache-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/mod_speedycgi.conf
%attr(755,root,root) %{apache_moddir}/mod_speedycgi.so
%dir %{httpdir}
