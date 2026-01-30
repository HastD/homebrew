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

BuildRequires:  cargo-rpm-macros
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
%setup -q -C
cp -a %{SOURCE1} .
patch -p0 < homebrew-install.patch
%setup -q -T -D -a 2
%cargo_prep

%generate_buildrequires
%cargo_generate_buildrequires -t

%build
mkdir .linuxbrew
env -i HOME=/home/linuxbrew PATH=/usr/bin:/bin:/usr/sbin:/sbin NONINTERACTIVE=1 \
    HOMEBREW_BREW_LOCAL_GIT_REMOTE="${PWD}/brew.git" /bin/bash ./homebrew-install.sh

%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies

%install
# main brew installation
mkdir -m 755 -p %{buildroot}%{_datadir}/homebrew
cp -a .linuxbrew %{buildroot}%{_datadir}/homebrew

# brew environment settings
install -Dp -m 644 -t %{buildroot}%{_sysconfdir}/homebrew etc/homebrew/brew.env

# systemd units for automatic brew setup and updates
install -Dp -m 644 -t %{buildroot}%{_unitdir} usr/lib/systemd/system/*

# brew shell environment and completions
install -Dp -m 644 -t %{buildroot}%{_sysconfdir}/profile.d etc/profile.d/brew*.sh
install -Dp -m 644 -t %{buildroot}%{_datadir}/fish/vendor_conf.d usr/share/fish/vendor_conf.d/brew-fish-completions.fish

# systemd-tmpfiles
install -Dp -m 644 -t %{buildroot}%{_tmpfilesdir} usr/lib/tmpfiles.d/homebrew.conf

# homebrew-sandbox
install -Dp -m 755 -t %{buildroot}%{_datadir}/homebrew-sandbox/.linuxbrew/bin target/rpm/brew
mkdir -p %{buildroot}%{_datadir}/homebrew-sandbox/.linuxbrew/.sandbox
ln -s ../Homebrew/bin/brew %{buildroot}%{_datadir}/homebrew-sandbox/.linuxbrew/.sandbox/brew
install -Dp -m 644 -t %{buildroot}%{_sysconfdir}/homebrew etc/homebrew/brew-sandbox.env

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
%{_datadir}/homebrew
%{_unitdir}/brew-setup.service
%{_unitdir}/brew-update.service
%{_unitdir}/brew-update.timer
%{_unitdir}/brew-upgrade.service
%{_unitdir}/brew-upgrade.timer
%{_datadir}/fish/vendor_conf.d/brew-fish-completions.fish
%{_tmpfilesdir}/homebrew.conf
%config(noreplace) %{_sysconfdir}/homebrew/brew.env
%config(noreplace) %{_sysconfdir}/profile.d/brew.sh
%config(noreplace) %{_sysconfdir}/profile.d/brew-bash-completions.sh
%ghost %config(noreplace) %{_sysconfdir}/.linuxbrew

%package sandbox
Version: 0.1.0
Summary: Sandboxing for the brew command using Landlock
SourceLicense: Apache-2.0 OR MIT
License: (Apache-2.0 OR MIT) AND MIT
Requires: homebrew

%description sandbox
This package provides sandboxing for the brew command using the Landlock LSM.
It works by wrapping the brew command in a simple Rust program that sets up the
Landlock sandbox and then passes its arguments on to brew.

Note that only brew itself is sandboxed, not programs intalled using brew.

The sandbox allows brew full read-write access to the Homebrew prefix and cache
directories, temporary directories, and /dev, and read-only access to /usr and
/etc. Network access is limited to port 443 only. Brew is not granted any access
to user home directories or /run.

%post sandbox
%systemd_post brew-sandbox-setup.service

%preun sandbox
%systemd_preun brew-sandbox-setup.service

%postun sandbox
%systemd_postun_with_reload brew-sandbox-setup.service

%files sandbox
%license LICENSE.dependencies
%{_datadir}/homebrew-sandbox
%{_unitdir}/brew-sandbox-setup.service
%ghost %config(noreplace) %{_sysconfdir}/homebrew/brew-sandbox.env

%changelog
* Sun Feb 1 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Add homebrew-sandbox subpackage
* Wed Jan 28 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Update installer commit
  - Make Homebrew/brew repo part of SRPM
* Thu Jan 22 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Filter out unwanted automatic dependencies
  - Require git-core instead of the full git package
  - Use build timestamp for release number
* Fri Jan 16 2026 Daniel Hast <hast.daniel@protonmail.com>
  - Initial RPM release
