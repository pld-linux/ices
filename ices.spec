Summary:	ices - Program for feeding MP3 streams to an Icecast server
Summary(pl):	ices - program dostarczaj±cy strumienie MP3 do serwera Icecast
Name:		ices
Version:	0.2.2
Release:	0.1
License:	GPL v2
Group:		Applications/Sound
Source0:	http://www.icecast.org/releases/%{name}-%{version}.tar.gz
# Source1:	%{name}.init
Patch0:		ices-libtool_fix.patch
URL:		http://www.icecast.org/
BuildRequires:	autoconf
BuildRequires:	automake
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Prereq:		rc-scripts
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ices is a part of Icecast server. It submit mp3's files from a playlist.

%description -l pl
Ices jest czê¶ci± serwera Icecast. Odpowiada za dostarczanie plików mp3
wg playlisty do serwera Icecast.

%prep
%setup -q
%patch0

%build
cp -f %{_datadir}/automake/config.* .
aclocal
autoconf
%configure \
	--enable-fsstd \
	--enable-libwrap \
	--without-readline

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
# install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} DESTDIR=$RPM_BUILD_ROOT install

# install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ices
install iceplay $RPM_BUILD_ROOT%{_bindir}

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/icecast/%{name}.conf.dist $RPM_BUILD_ROOT%{_sysconfdir}/icecast/%{name}.conf

gzip -9nf AUTHORS BUGS CHANGES COPYING FAQ README TESTED

%clean
rm -r $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid icecast`" ]; then
        if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Warning: group icecast haven't gid=57. Correct this before installing ices." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 57 -r -f icecast
fi
if [ -n "`/bin/id -u icecast 2>/dev/null`" ]; then
	if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Warning: user icecast haven't uid=57. Correct this before installing ices." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 57 -r -d /dev/null -s /bin/false -c "ices" -g icecast icecast 1>&2
fi

%post
chkconfig --add ices
if [ -f /var/lock/subsys/ices ]; then
        /etc/rc.d/init.d/ices restart >&2
else
        echo "Run '/etc/rc.d/init.d/ices start' to start ices deamon." >&2
fi

%preun
if [ "$1" = "0" ] ; then
        if [ -f /var/lock/subsys/ices ]; then
                /etc/rc.d/init.d/ices stop >&2
        fi
        /sbin/chkconfig --del ices >&2
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS.gz BUGS.gz CHANGES.gz COPYING.gz FAQ.gz README.gz TESTED.gz
# %attr(754,root,root) /etc/rc.d/init.d/ices
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/ices.conf
%attr(755,root,root) %{_bindir}/*
