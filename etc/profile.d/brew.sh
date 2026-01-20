#!/usr/bin/env bash

# SPDX-FileCopyrightText: Copyright 2025 Universal Blue
# SPDX-FileCopyrightText: Copyright 2025 The BlueBuild Authors
#
# SPDX-License-Identifier: Apache-2.0

if [[ -d /home/linuxbrew/.linuxbrew && $- == *i* && "$(/usr/bin/id -u)" != 0 ]]; then
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi
