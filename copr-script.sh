#!/bin/bash

# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

set -euxo pipefail

latest_tag=$(curl -fLsS --retry 3 'https://api.github.com/repos/Homebrew/brew/releases/latest' | jq -cr '.tag_name')

curl -fLsS --retry 3 'https://raw.githubusercontent.com/HastD/homebrew/refs/heads/main/homebrew.spec' \
    | sed --sandbox -e "s/@@VERSION@@/${latest_tag}/g" > ./homebrew.spec
