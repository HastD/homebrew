# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

Name:           homebrew
Version:        @@VERSION@@
Release:        1
Summary:        The Missing Package Manager for macOS (or Linux)

License:        Apache-2.0 AND BSD-2-Clause
URL:            https://github.com/HastD/%{name}
Source0:        %{name}-@@VERSION@@.tar.gz
Source1:        %{name}-install.sh

BuildRequires:  curl >= 7.41.0
BuildRequires:  git >= 2.7.0
BuildRequires:  systemd-rpm-macros
Requires:       curl >= 7.41.0
Requires:       gcc
Requires:       git >= 2.7.0
Requires:       zstd
%{?systemd_requires}

%description
Homebrew installs the stuff you need that Apple (or your Linux system) didn't.

%prep
%setup -C
mv %{_sourcedir}/%{name}-install.sh .
patch -p0 < %{name}-install.patch

%build
mkdir .linuxbrew
env -i HOME=/home/linuxbrew PATH=/usr/bin:/bin:/usr/sbin:/sbin NONINTERACTIVE=1 /bin/bash ./%{name}-install.sh

%install
# main brew installation
mkdir -m 755 -p %{buildroot}%{_datadir}/%{name}
cp -a .linuxbrew %{buildroot}%{_datadir}/%{name}

# systemd units for automatic brew setup and updates
mkdir -m 755 -p %{buildroot}%{_unitdir} %{buildroot}%{_presetdir}
cp -a systemd/brew-*.service systemd/brew-*.timer %{buildroot}%{_unitdir}
cp -a systemd-preset/20-brew.preset %{buildroot}%{_presetdir}

# brew shell environment and completions
mkdir -m 755 -p %{buildroot}%{_sysconfdir}/profile.d %{buildroot}%{_datadir}/fish/vendor_conf.d
cp -a profile.d/brew*.sh %{buildroot}%{_sysconfdir}/profile.d
cp -a fish/brew-fish-completion.fish %{buildroot}%{_datadir}/fish/vendor_conf.d

# systemd-tmpfiles
mkdir -m 755 -p %{buildroot}%{_tmpfilesdir}
cp -a tmpfiles.d/homebrew.conf %{buildroot}%{_tmpfilesdir}

%post
%systemd_post brew-setup.service
%systemd_post brew-update.service
%systemd_post brew-update.timer
%systemd_post brew-upgrade.service
%systemd_post brew-upgrade.timer

%preun
%systemd_preun brew-setup.service
%systemd_preun brew-update.service
%systemd_preun brew-update.timer
%systemd_preun brew-upgrade.service
%systemd_preun brew-upgrade.timer

%postun
%systemd_postun_with_reload brew-setup.service
%systemd_postun_with_reload brew-update.service
%systemd_postun_with_restart brew-update.timer
%systemd_postun_with_reload brew-upgrade.service
%systemd_postun_with_restart brew-upgrade.timer

%files
%{_datadir}/%{name}
%{_unitdir}/brew-setup.service
%{_unitdir}/brew-update.service
%{_unitdir}/brew-update.timer
%{_unitdir}/brew-upgrade.service
%{_unitdir}/brew-upgrade.timer
%{_presetdir}/20-brew.preset
%{_datadir}/fish/vendor_conf.d/brew-fish-completions.fish
%{_tmpfilesdir}/homebrew.conf
%config(noreplace) %{_sysconfdir}/profile.d/brew.sh
%config(noreplace) %{_sysconfdir}/profile.d/brew-bash-completions.sh
%ghost %config(noreplace) %{_sysconfdir}/.linuxbrew

%changelog
* Fri Jan 16 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Initial RPM release
