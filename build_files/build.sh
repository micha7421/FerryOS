#!/bin/bash

set -ouex pipefail

# Copy the contents of system_files/ of the git repo to /
cp -avf "/ctx/system_files"/. /

### Branding

# Rename the OS but keep ID=fedora, so dnf, bootc and Fedora tooling keep working
OS_RELEASE=/usr/lib/os-release
FEDORA_VERSION="$(. "$OS_RELEASE" && echo "$VERSION_ID")"

set_os_release() {
    local key="$1" value="$2"
    if grep -q "^${key}=" "$OS_RELEASE"; then
        sed -i "s|^${key}=.*|${key}=\"${value}\"|" "$OS_RELEASE"
    else
        echo "${key}=\"${value}\"" >> "$OS_RELEASE"
    fi
}

set_os_release NAME "FerryOS"
set_os_release PRETTY_NAME "FerryOS (based on Fedora ${FEDORA_VERSION})"
set_os_release HOME_URL "https://github.com/micha7421/ferryos"
set_os_release SUPPORT_URL "https://github.com/micha7421/ferryos/issues"
set_os_release BUG_REPORT_URL "https://github.com/micha7421/ferryos/issues"
set_os_release DEFAULT_HOSTNAME "ferryos"

### Packages

# Firefox comes from Flathub instead (see /usr/share/ferryos/flatpaks.list)
if rpm -q firefox; then
    dnf5 -y remove firefox firefox-langpacks
fi

### Services

chmod +x /usr/libexec/ferryos-flatpak-setup
systemctl enable ferryos-flatpak-setup.service
systemctl enable podman.socket
