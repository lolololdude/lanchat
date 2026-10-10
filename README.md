# lanchat

Minimal terminal chat for two machines on the same network.

    lanchat                     # menu
    lanchat host [port]
    lanchat connect IP[:PORT]

## Install (once published - see PUBLISHING below)

Windows:  winget install lolololdude.LanChat
Linux:
    sudo mkdir -p /etc/apt/keyrings
    sudo curl -fsSL https://lolololdude.github.io/lanchat-apt/lanchat.gpg -o /etc/apt/keyrings/lanchat.gpg
    echo "deb [signed-by=/etc/apt/keyrings/lanchat.gpg] https://lolololdude.github.io/lanchat-apt ./" | sudo tee /etc/apt/sources.list.d/lanchat.list
    sudo apt update && sudo apt install lanchat

## PUBLISHING (one-time setup, ~20 min)

0. Replace lolololdude everywhere (README, LICENSE, build_deb.sh) with your GitHub username.

1. Release builds
   - Create a GitHub repo named `lanchat`, push these files.
   - `git tag v1.0.0 && git push --tags`
   - The workflow builds the .deb, lanchat.exe (zipped) and ready-made winget manifests,
     and attaches them to a GitHub Release.

2. winget
   - Download `winget-manifests.zip` from the release and unzip it.
   - Fork https://github.com/microsoft/winget-pkgs, then copy the 3 YAML files to:
       manifests/y/lolololdude/LanChat/1.0.0/      (lowercase first letter of your username)
   - Open a pull request. Microsoft's bots validate it (usually a few days).
   - Once merged:  winget install lolololdude.LanChat
   - Test locally first (Windows):  winget validate --manifest <folder>
                                    winget install --manifest <folder>
   - Note: unsigned PyInstaller exes are sometimes flagged by antivirus during validation.
     If that happens, re-run the build or sign the exe.

3. apt
   - Download the .deb from the release into this folder.
   - Make a GPG key if you don't have one:  gpg --quick-generate-key "lanchat repo" rsa3072 sign never
   - bash make_apt_repo.sh <KEY_ID>
   - Create a second GitHub repo `lanchat-apt`, push the CONTENTS of apt-repo/, and enable
     GitHub Pages (Settings > Pages > deploy from branch main, root).
   - For each new version: rebuild the repo and push again.
