%include 	/usr/lib/rpm/macros.perl
%define         perlname CGI-SpeedyCGI

Summary:	Speed up perl CGI scripts by running them persistently
Name:		perl-%{perlname}
Version:	2.0.1
Release:	2
License:	GPL
Group:		Networking/Daemons
Group(de):	Netzwerkwesen/Server
Group(pl):	Sieciowe/Serwery
Source0:	http://daemoninc.com/speedycgi/%{perlname}-%{version}.tar.gz
Source1:	apache-mod_speedycgi.conf
BuildRequires:	rpm-perlprov >= 3.0.3-16
BuildRequires:	perl >= 5.6
%requires_eq	perl
Requires:	%{perl_sitearch}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		apache_moddir	%(/usr/sbin/apxs -q LIBEXECDIR)

%description 
SpeedyCGI is a way to run CGI perl scripts persistently, which usually
makes them run much more quickly. After the script is initially run,
instead of exiting, SpeedyCGI keeps the perl interpreter running in
memory. During subsequent runs, this interpreter is used to handle new
requests, instead of starting a new perl interpreter for each
execution.

%package -n apache-mod_speedycgi
Summary:	SpeedyCGI apache module
Group:		Networking/Daemons
Group(de):	Netzwerkwesen/Server
Group(pl):	Sieciowe/Serwery
Requires:	%{name} = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n apache-mod_speedycgi
SpeedyCGI apache module.

%prep
%setup -q -n %{perlname}-%{version}

%build
perl Makefile.PL
( cd mod_speedycgi && perl Makefile.PL )

%{__make} OPTIMIZE="%{?debug:-O -g}%{!?debug:$RPM_OPT_FLAGS}"
%{__make} -C mod_speedycgi \
	OPTIMIZE="%{?debug:-O -g}%{!?debug:$RPM_OPT_FLAGS}" \
	APXS="/usr/sbin/apxs"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/%{perl_archlib} \
	$RPM_BUILD_ROOT{%{apache_moddir},/home/httpd/speedy,%{_sysconfdir}/httpd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT 

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/mod_speedycgi.conf
install mod_speedycgi/mod_speedycgi.so $RPM_BUILD_ROOT%{apache_moddir}

gzip -9nf README docs/*.txt contrib/Mason-SpeedyCGI-HOWTO

%clean
rm -rf $RPM_BUILD_ROOT

%post -n apache-mod_speedycgi
HTTPDCONF=%{_sysconfdir}/httpd/httpd.conf
if [ -f $HTTPDCONF ] && \
   ! grep -q "^Include.*/mod_speedycgi.conf" $HTTPDCONF; then
	echo "Include /etc/httpd/mod_speedycgi.conf" >> $HTTPDCONF
fi
if [ -f /var/lock/subsys/httpd ]; then
        /etc/rc.d/init.d/httpd restart 1>&2
else
        echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache http daemon."
fi

%postun -n apache-mod_speedycgi
HTTPDCONF=%{_sysconfdir}/httpd/httpd.conf
grep -E -v "^Include.*mod_speedycgi.conf" $HTTPDCONF > $HTTPDCONF.tmp$$
mv -f $HTTPDCONF.tmp$$ $HTTPDCONF
if [ -f /var/lock/subsys/httpd ]; then
        /etc/rc.d/init.d/httpd restart 1>&2
fi

%files
%defattr(644,root,root,755)
%doc *.gz docs contrib
%{perl_sitelib}/CGI/*.pm
%attr(755,root,root) %{_bindir}/speedy*

%files -n apache-mod_speedycgi
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/mod_speedycgi.conf
%{apache_moddir}/mod_speedycgi.so
%dir /home/httpd/speedy
