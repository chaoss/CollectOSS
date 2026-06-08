#!/bin/bash
#SPDX-License-Identifier: MIT
set -e

exec collectoss backend start --pidfile /tmp/main.pid
