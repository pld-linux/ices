Summary:	ices - Program for feeding MP3 streams to an Icecast server
Summary(pl):	ices - program dostarczaj±cy strumienie MP3 do serwera Icecast
Summary(pt_BR):	Mais um streamer para icecast
Name:		ices
Version:	0.3
Release:	3
License:	GPL
Group:		Applications/Sound
Source0:	http://www.icecast.org/files/%{name}/%{name}-%{version}.tar.gz
# Source0-md5:	cb7bae83597945e90094a46a9f15bd91
Source1:	%{name}.init
Source2:	%{name}.conf.txt
URL:		http://www.icecast.org/
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
Ices is a part of Icecast server. It submits MP3 files from a playlist.

%description -l pl
Ices jest czê¶ci± serwera Icecast. Odpowiada za dostarczanie plików
MP3 wg playlisty do serwera Icecast.

%description -l pt_BR
ices, armed with a list of MP3 files, sends a continuous stream of MP3 data to
an icecast server. The server is then responsible for accepting client
connections and feeding the MP3 stream to them.

%prep
%setup -q

%build
cp -f %{_datadir}/automake/config.* .
rm -f missing
%configure \
	--enable-fsstd \
	--enable-libwrap \
	--without-readline \
	--with-python \
	--with-perl \
	--with-lame

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/icecast,/etc/rc.d/init.d,%{_mandir}/man1}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ices
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/icecast/ices.conf.txt
install doc/ices.1 $RPM_BUILD_ROOT%{_mandir}/man1

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/ices.conf.dist $RPM_BUILD_ROOT%{_sysconfdir}/icecast/%{name}.conf.dist

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
%doc AUTHORS BUGS README README.playlist doc/%{name}manual.html
%attr(754,root,root) /etc/rc.d/init.d/ices
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/ices.conf.txt
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/ices.conf.dist
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
