#!/usr/bin/env bash
# Usage: bash build_deb.sh [version]   -> lanchat_<version>_all.deb
set -euo pipefail
VER="${1:-1.0.0}"
MAINT="${MAINTAINER:-YOURNAME <you@example.com>}"
ROOT=$(mktemp -d)
mkdir -p "$ROOT/DEBIAN" "$ROOT/usr/bin"
install -m 755 lanchat.py "$ROOT/usr/bin/lanchat"
cat > "$ROOT/DEBIAN/control" << CTL
Package: lanchat
Version: $VER
Section: net
Priority: optional
Architecture: all
Depends: python3
Maintainer: $MAINT
Description: Minimal terminal chat for two machines on the same network
 Run "lanchat" to host or connect to another machine by IP and port.
CTL
dpkg-deb --build --root-owner-group "$ROOT" "lanchat_${VER}_all.deb"
