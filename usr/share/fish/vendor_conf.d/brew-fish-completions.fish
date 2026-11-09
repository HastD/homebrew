#!/usr/bin/env fish

# SPDX-FileCopyrightText: Copyright 2025 Universal Blue
# SPDX-FileCopyrightText: Copyright 2025 The BlueBuild Authors
# SPDX-FishCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

#shellcheck disable=all
if status --is-interactive && not fish_is_root_user
    if test -d '/home/linuxbrew/.linuxbrew'
        # Begin output of `brew shellenv fish` (lightly edited for formatting)
        set --global --export HOMEBREW_PREFIX '/home/linuxbrew/.linuxbrew'
        set --global --export HOMEBREW_CELLAR '/home/linuxbrew/.linuxbrew/Cellar'
        set --global --export HOMEBREW_REPOSITORY '/home/linuxbrew/.linuxbrew/Homebrew'
        fish_add_path --global --move --path -a '/home/linuxbrew/.linuxbrew/bin' '/home/linuxbrew/.linuxbrew/sbin'
        if test -n "$MANPATH"
            set --global --export MANPATH (string replace --regex '^:*(.*?):*$' ':$1' -- "$MANPATH")
        end
        if not set --query INFOPATH
            set INFOPATH ''
        end
        set --global --export INFOPATH '/home/linuxbrew/.linuxbrew/share/info' $INFOPATH
        # End output of `brew shellenv fish`

        if test -d '/home/linuxbrew/.linuxbrew/share/fish/completions'
            set -a fish_complete_path '/home/linuxbrew/.linuxbrew/share/fish/completions'
        end
        if test -d '/home/linuxbrew/.linuxbrew/share/fish/vendor_completions.d'
            set -a fish_complete_path '/home/linuxbrew/.linuxbrew/share/fish/vendor_completions.d'
        end
    end
end
