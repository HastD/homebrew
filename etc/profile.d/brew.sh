#!/bin/sh

# SPDX-FileCopyrightText: Copyright 2025 Universal Blue
# SPDX-FileCopyrightText: Copyright 2025 The BlueBuild Authors
# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

if [ -x /home/linuxbrew/.linuxbrew/bin/brew ] && [ "$(/usr/bin/id -u)" != 0 ]; then
  case "$-" in
    *i*)
      # Begin output of `brew shellenv bash` (lightly edited for formatting)
      export HOMEBREW_PREFIX='/home/linuxbrew/.linuxbrew'
      export HOMEBREW_CELLAR='/home/linuxbrew/.linuxbrew/Cellar'
      export HOMEBREW_REPOSITORY='/home/linuxbrew/.linuxbrew/Homebrew'
      export PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin${PATH+:$PATH}";
      [ -z "${MANPATH-}" ] || export MANPATH=":${MANPATH#:}"
      export INFOPATH="/home/linuxbrew/.linuxbrew/share/info:${INFOPATH:-}"
      # End output of `brew shellenv bash`
      ;;
  esac
fi
