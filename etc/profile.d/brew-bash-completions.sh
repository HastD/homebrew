# shellcheck shell=sh disable=SC1090

# SPDX-FileCopyrightText: Copyright 2025 Universal Blue
# SPDX-FileCopyrightText: Copyright 2025 The BlueBuild Authors
# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

# Check for interactive bash and that we haven't already been sourced
case "$-" in
*i*)
  if [ -n "${BASH_VERSION-}" ] && [ -z "${BREW_BASH_COMPLETION-}" ] && [ "$(/usr/bin/id -u)" != 0 ]; then
    if [ -d /home/linuxbrew/.linuxbrew/etc/bash_completion.d ]; then
      for _brew_completion_file in /home/linuxbrew/.linuxbrew/etc/bash_completion.d/*; do
        if [ -r "${_brew_completion_file}" ]; then
          # Only source completions for non-system commands
          if ! [ -e "/usr/bin/${_brew_completion_file##*/}" ]; then
            . "${_brew_completion_file}"
          fi
        fi
      done
      unset _brew_completion_file
    fi
    BREW_BASH_COMPLETION=1
  fi
  ;;
*) ;;
esac
