#!/bin/bash
# shfmt -w
set -eu

echo '=== setup ==='
tgsql -c ipc:tsurugi --script sql/setup.sql
