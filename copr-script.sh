#!/bin/bash

# SPDX-FileCopyrightText: Copyright 2026 Daniel Hast
#
# SPDX-License-Identifier: Apache-2.0

set -euxo pipefail

release_list="$(
    curl -fLsS --retry 3 'https://api.github.com/repos/Homebrew/brew/releases?per_page=50' \
        | jq -c '[.[] | {tag_name, created_at, html_url}]'
)"

latest_tag=$(jq -cr '.[0].tag_name' <<<"${release_list}")

curl -fLsS --retry 3 'https://raw.githubusercontent.com/secureblue/homebrew/refs/heads/main/homebrew-template.spec' \
    | sed --sandbox -e "s/@@VERSION@@/${latest_tag}/g" > ./homebrew.spec

installer_commit=$(awk '/^%define homebrew_installer_commit / { print $3 }' ./homebrew.spec)

# Append changelog entries generated from Homebrew release data
jq -cr '
    .[] | "* \(.created_at | fromdate | strftime("%a %b %d %Y")) secureblue <noreply@secureblue.dev> - \(.tag_name)\n- \(.html_url)"
' <<<"${release_list}" >> ./homebrew.spec

curl -fLsS --retry 3 \
    -o "homebrew-${latest_tag}.tar.gz" 'https://github.com/secureblue/homebrew/tarball/main' \
    -o 'homebrew-install.sh' "https://raw.githubusercontent.com/Homebrew/install/${installer_commit}/install.sh"

git clone https://github.com/Homebrew/brew.git ./brew.git
tar -cf homebrew-brew-git.tar.gz ./brew.git
rm -rf ./brew.git
