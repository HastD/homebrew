# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

# The homebrew repo contains some files with invalid rpaths, but they're just test files
# that aren't used by anything at runtime.
%global __brp_check_rpaths %{nil}

# Skip steps that could modify the contents of the homebrew repo.
%global __brp_add_determinism /usr/bin/true
%global __brp_linkdupes /usr/bin/true
%global __brp_mangle_shebangs %{nil}
%global debug_package %{nil}

%define homebrew_installer_commit 90fa3d5881cedc0d60c4a3cc5babdb867ef42e5a
%define build_timestamp %(date -u '+%%y%%m%%d%%H')

Name:           homebrew
Version:        @@VERSION@@
Release:        %{build_timestamp}
Summary:        The Missing Package Manager for macOS (or Linux)

License:        Apache-2.0 AND BSD-2-Clause
URL:            https://github.com/secureblue/homebrew
Source0:        homebrew-@@VERSION@@.tar.gz
Source1:        homebrew-install.sh
Source2:        homebrew-brew-git.tar.gz

BuildRequires:  curl >= 7.41.0
BuildRequires:  git-core >= 2.7.0
BuildRequires:  systemd-rpm-macros
Requires:       curl >= 7.41.0
Requires:       gcc
Requires:       git-core >= 2.7.0
Requires:       zstd
%{?systemd_requires}

# Filter out unwanted automatic dependencies. For documentation, see:
# https://docs.fedoraproject.org/en-US/packaging-guidelines/AutoProvidesAndRequiresFiltering/
%global __requires_exclude_from ^%{_datadir}/homebrew/.linuxbrew/Homebrew/((.*/)?\\..*|.*\\.swift|Library/Homebrew/test(_bot)?/.*)$

%description
Homebrew installs the stuff you need that Apple (or your Linux system) didn't.

%prep
%setup -C
cp -a %{SOURCE1} .
patch -p0 < homebrew-install.patch
%setup -T -D -a 2

%build
mkdir .linuxbrew
env -i HOME=/home/linuxbrew PATH=/usr/bin:/bin:/usr/sbin:/sbin NONINTERACTIVE=1 \
    HOMEBREW_BREW_LOCAL_GIT_REMOTE="${PWD}/brew.git" /bin/bash ./homebrew-install.sh

%install
# main brew installation
mkdir -m 755 -p %{buildroot}%{_datadir}/homebrew
cp -a .linuxbrew %{buildroot}%{_datadir}/homebrew

# brew environment settings
install -Dp -m 644 -t %{buildroot}%{_sysconfdir}/homebrew etc/homebrew/brew.env

# systemd units for automatic brew updates
install -Dp -m 644 -t %{buildroot}%{_userunitdir} usr/lib/systemd/user/*

# brew shell environment and completions
install -Dp -m 644 -t %{buildroot}%{_sysconfdir}/profile.d etc/profile.d/brew*.sh
install -Dp -m 644 -t %{buildroot}%{_datadir}/fish/vendor_conf.d usr/share/fish/vendor_conf.d/brew-fish-completions.fish

# systemd-tmpfiles
install -Dp -m 644 -t %{buildroot}%{_tmpfilesdir} usr/lib/tmpfiles.d/homebrew.conf

%post
%systemd_user_post brew-update.service
%systemd_user_post brew-update.timer
%systemd_user_post brew-upgrade.service
%systemd_user_post brew-upgrade.timer

%preun
%systemd_user_preun brew-update.service
%systemd_user_preun brew-update.timer
%systemd_user_preun brew-upgrade.service
%systemd_user_preun brew-upgrade.timer

%postun
%systemd_user_postun_with_reload brew-update.service
%systemd_user_postun_with_restart brew-update.timer
%systemd_user_postun_with_reload brew-upgrade.service
%systemd_user_postun_with_restart brew-upgrade.timer

%files
%{_datadir}/homebrew
%{_userunitdir}/brew-update.service
%{_userunitdir}/brew-update.timer
%{_userunitdir}/brew-upgrade.service
%{_userunitdir}/brew-upgrade.timer
%{_datadir}/fish/vendor_conf.d/brew-fish-completions.fish
%{_tmpfilesdir}/homebrew.conf
%config(noreplace) %{_sysconfdir}/homebrew
%config(noreplace) %{_sysconfdir}/profile.d/brew.sh
%config(noreplace) %{_sysconfdir}/profile.d/brew-bash-completions.sh

%changelog
* Fri Feb 27 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Use tmpfiles.d in place of brew-setup.service
* Mon Feb 23 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Make update services/timers into user units
* Wed Jan 28 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Update installer commit
  - Make Homebrew/brew repo part of SRPM
* Thu Jan 22 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Filter out unwanted automatic dependencies
  - Require git-core instead of the full git package
  - Use build timestamp for release number
* Fri Jan 16 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Initial RPM release
