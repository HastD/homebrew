<!-- SPDX-FileCopyrightText: Copyright 2026 Daniel Hast -->

<!-- SPDX-License-Identifier: Apache-2.0 -->

# Homebrew

[![homebrew](https://img.shields.io/badge/dynamic/json?color=blue&label=homebrew&query=builds.latest.source_package.version&url=https%3A%2F%2Fcopr.fedorainfracloud.org%2Fapi_3%2Fpackage%3Fownername%3Dsecureblue%26projectname%3Dpackages%26packagename%3Dhomebrew%26with_latest_build%3DTrue)](https://copr.fedorainfracloud.org/coprs/secureblue/packages/package/homebrew/)

This repository packages [Homebrew](https://brew.sh/) for Linux as an RPM
package.

The RPM package sets up a Homebrew installation in `/usr/share/homebrew`. To
minimize deviation from the official install script, this installation is
produced at build-time using a version of the install script that's been patched
to use a different installation prefix and to omit steps that should wait until
after installation (such as setting up the Homebrew cache and running
`brew update`).

If Homebrew has not already been set up on the user's system, a systemd service
then copies this installation to `/home/linuxbrew` and transfers ownership of it
to UID 1000. The package also sets up systemd services to automatically update
Homebrew, as well as shell completions for the bash and fish shells.

## Sandbox

This repository also contains a `homebrew-sandbox` package that provides
sandboxing for the brew command using the [Landlock LSM](https://landlock.io/).
It works by wrapping the brew command in a simple Rust program that sets up the
Landlock sandbox and then passes its arguments on to brew.

Note that only brew itself is sandboxed, not programs intalled using brew.

The sandbox allows brew the follow access:

- Read-write access to `/home/linuxbrew/.linuxbrew`, `/home/linuxbrew/.cache`,
  `/var/tmp/homebrew`, and a limited subset of `/dev`;
- Read-only access to `/usr`, `/etc`, `/home/linuxbrew`, and `/proc/cpuinfo`;
- Network access to port 443 only.

This sandbox can be disabled by setting `_HOMEBREW_SANDBOX=0`, either as an
environment variable or in `/etc/homebrew/brew-sandbox.env`.

(You can also set the environment variable `_HOMEBREW_SANDBOX_DEBUG` to have the
wrapper program print debug info showing whether the sandbox is active.)

## Credit

Various files, including some of the systemd unit files and shell completion
scripts, are adapted from
[Universal Blue's Homebrew packaging](https://github.com/ublue-os/brew) and
[BlueBuild's brew module](https://github.com/blue-build/modules/tree/main/modules/brew)
and are redistributed under the terms of the Apache-2.0 license.

Homebrew itself is available under the terms of the BSD-2-Clause license.

This repository complies with the
[REUSE Specification, Version 3.3](https://reuse.software/spec-3.3/); copyright
and license information for each file is documented using SPDX headers.
