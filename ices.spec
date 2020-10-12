# TODO: check init files
# - roaraudio-devel >= 0.4.0 ?

Summary:	ices2 - Program for feeding MP3 and OGG streams to an Icecast server
Summary(pl.UTF-8):	ices2 - program dostarczający strumienie MP3 oraz OGG do serwera Icecast
Summary(pt_BR.UTF-8):	Mais um streamer para icecast
Name:		ices
Version:	2.0.3
Release:	1
License:	GPL v2
Group:		Applications/Sound
Source0:	http://downloads.xiph.org/releases/ices/%{name}-%{version}.tar.bz2
# Source0-md5:	df201d7c034ca93ff46202a2c1413b72
Source1:	%{name}.init
Source2:	%{name}.conf.txt
URL:		http://www.icecast.org/ices.php
BuildRequires:	alsa-lib-devel
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	gcc-c++
BuildRequires:	libshout-devel
BuildRequires:	libxml2-devel
BuildRequires:	pkgconfig
BuildRequires:	python-devel
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	lame-libs
Requires:	rc-scripts
Provides:	group(icecast)
Provides:	user(icecast)
Obsoletes:	shout
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ices is a part of Icecast server. It submits MP3 and OGG files from a
playlist.

%description -l pl.UTF-8
Ices jest częścią serwera Icecast. Odpowiada za dostarczanie plików
MP3 i OGG wg playlisty do serwera Icecast.

%prep
%setup -q

%build
%configure \
	--disable-roaraudio
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/icecast,/etc/rc.d/init.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ices
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/icecast/ices.conf.txt

cp -p conf/*.xml $RPM_BUILD_ROOT%{_sysconfdir}/icecast

# files *.html, *.css go to doc
# files *.xml go to _sysconfdir
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/{*.html,*.css,*.xml}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 57 icecast
%useradd -u 57 -r -d /usr/share/empty -s /bin/false -c "ices" -g icecast icecast

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
%doc AUTHORS README.md doc/*.html doc/style.css
%attr(754,root,root) /etc/rc.d/init.d/ices
%attr(640,root,icecast) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icecast/ices-alsa.xml
%attr(640,root,icecast) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icecast/ices-oss.xml
%attr(640,root,icecast) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icecast/ices-playlist.xml
%attr(640,root,icecast) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icecast/ices-roar.xml
%attr(640,root,icecast) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icecast/ices.conf.txt
%attr(755,root,root) %{_bindir}/ices
