#!/bin/sh

# SPDX-FileCopyrightText: Copyright 2025 Universal Blue
# SPDX-FileCopyrightText: Copyright 2025 The BlueBuild Authors
# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

# shellcheck shell=sh disable=SC1090,SC1091,SC2039,SC2166,SC3028,SC3054
# Completion is in sh to account for the zsh syntax & when zsh tries to source scripts from /etc/profiles

# Check for interactive bash and that we haven't already been sourced.
if [ -n "${BASH_VERSION-}" ] && [ -n "${PS1-}" ] && [ -z "${BREW_BASH_COMPLETION-}" ] && [ "$(/usr/bin/id -u)" != 0 ]; then

    # Check for recent enough version of bash.
    # shellcheck shell=bash
    if [ "${BASH_VERSINFO[0]}" -gt 4 ] || { [ "${BASH_VERSINFO[0]}" -eq 4 ] && [ "${BASH_VERSINFO[1]}" -ge 2 ]; }; then
        if [ -w /home/linuxbrew/.linuxbrew ]; then
            if ! [ -L /home/linuxbrew/.linuxbrew/etc/bash_completion.d/brew ]; then
                /home/linuxbrew/.linuxbrew/bin/brew completions link > /dev/null
            fi
        fi
        if [ -d /home/linuxbrew/.linuxbrew/etc/bash_completion.d ]; then
            for rc in /home/linuxbrew/.linuxbrew/etc/bash_completion.d/*; do
                if [ -r "$rc" ]; then
                    . "$rc"
                fi
            done
            unset rc
        fi
    fi
    BREW_BASH_COMPLETION=1
    export BREW_BASH_COMPLETION
fi
