#!/usr/bin/env bash
# Builds a signed "flat" apt repository in ./apt-repo from the .deb files in this folder.
# Usage: bash make_apt_repo.sh <GPG_KEY_ID>
# Needs: apt-utils (apt-ftparchive), gnupg.  Publish the apt-repo/ folder (e.g. GitHub Pages).
set -euo pipefail
KEY="${1:?usage: make_apt_repo.sh <GPG_KEY_ID>}"
rm -rf apt-repo && mkdir apt-repo
cp lanchat_*_all.deb apt-repo/
cd apt-repo
apt-ftparchive packages . > Packages
gzip -k -f Packages
apt-ftparchive release . > Release
gpg --batch --yes --default-key "$KEY" -abs -o Release.gpg Release
gpg --batch --yes --default-key "$KEY" --clearsign -o InRelease Release
gpg --export "$KEY" > lanchat.gpg     # binary keyring apt can use directly
touch .nojekyll
echo "Done. Publish the apt-repo/ folder."
