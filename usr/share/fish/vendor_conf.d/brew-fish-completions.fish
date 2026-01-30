#!/usr/bin/env fish

# SPDX-FileCopyrightText: Copyright 2025 Universal Blue
# SPDX-FileCopyrightText: Copyright 2025 The BlueBuild Authors
#
# SPDX-License-Identifier: Apache-2.0

#shellcheck disable=all
if status --is-interactive; and test $(/usr/bin/id -u) -ne 0
    if [ -d /home/linuxbrew/.linuxbrew ]
        /home/linuxbrew/.linuxbrew/bin/brew shellenv fish | source
        if test -d (brew --prefix)/share/fish/completions
            set -p fish_complete_path (brew --prefix)/share/fish/completions
        end
        if test -d (brew --prefix)/share/fish/vendor_completions.d
            set -p fish_complete_path (brew --prefix)/share/fish/vendor_completions.d
        end
    end
end
