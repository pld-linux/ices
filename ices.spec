# TODO: check init files 

Summary:	ices2 - Program for feeding MP3 and OGG streams to an Icecast server
Summary(pl):	ices2 - program dostarczaj�cy strumienie MP3 oraz OGG do serwera Icecast
Summary(pt_BR):	Mais um streamer para icecast
Name:		ices
Version:	2.0.1
Release:	1
License:	GPL
Group:		Applications/Sound
Source0:	http://downloads.xiph.org/releases/ices/%{name}-%{version}.tar.bz2
# Source0-md5:	8c7be81b304c4ce588f43b9d02603f6e
Source1:	%{name}.init
Source2:	%{name}.conf.txt
URL:		http://www.icecast.org/ices.php
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	lame-libs-devel
BuildRequires:	libshout-devel
BuildRequires:	python-devel
BuildRequires:	rpmbuild(macros) >= 1.159
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(post,preun):/sbin/chkconfig
Requires:	lame-libs
Provides:	group(icecast)
Provides:	user(icecast)
Obsoletes:	shout
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ices is a part of Icecast server. It submits MP3 and OGG files from a playlist.

%description -l pl
Ices jest cz�ci� serwera Icecast. Odpowiada za dostarczanie plik�w
MP3 i OGG wg playlisty do serwera Icecast.

%prep
%setup -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/icecast,/etc/rc.d/init.d,%{_mandir}/man1}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ices
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/icecast/ices.conf.txt
install debian/ices2.1 $RPM_BUILD_ROOT%{_mandir}/man1

mv -f conf/*.xml $RPM_BUILD_ROOT%{_sysconfdir}/icecast/

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid icecast`" ]; then
	if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Error: group icecast doesn't have gid=57. Correct this before installing ices." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 57 icecast
fi
if [ -n "`/bin/id -u icecast 2>/dev/null`" ]; then
	if [ "`/bin/id -u icecast`" != "57" ]; then
		echo "Error: user icecast doesn't have uid=57. Correct this before installing ices." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 57 -r -d /dev/null -s /bin/false -c "ices" -g icecast icecast 1>&2
fi

%post
/sbin/chkconfig --add ices
if [ -f /var/lock/subsys/ices ]; then
	/etc/rc.d/init.d/ices restart >&2
else
	echo "Run '/etc/rc.d/init.d/ices start' to start ices daemon." >&2
fi

%preun
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/ices ]; then
		/etc/rc.d/init.d/ices stop >&2
	fi
	/sbin/chkconfig --del ices >&2
fi

%postun
if [ "$1" = "0" ]; then
	%userremove icecast
	%groupremove icecast
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README TODO doc/*.html doc/style.css
%attr(754,root,root) /etc/rc.d/init.d/ices
%attr(640,root,icecast) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icecast/*.xml
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
