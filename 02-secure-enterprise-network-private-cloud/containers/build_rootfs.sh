#!/usr/bin/env bash

# Stop execution if a command fails or a variable is undefined.
set -euo pipefail

ROOTFS="/opt/enterprise-platform/image-rootfs"
ISO="/mnt/rocky-iso"
REPO="lab-offline"

# Require administrative privileges for RPM installation.
if [[ "$EUID" -ne 0 ]]; then
    echo "Administrative privileges are required."
    exit 1
fi

# Confirm that the offline installation media is mounted.
if ! mountpoint -q "$ISO"; then
    echo "Rocky Linux installation media is not mounted."
    exit 1
fi

# Confirm that the repository and signing key exist.
test -d "$ISO/Minimal/repodata"
test -f "$ISO/RPM-GPG-KEY-Rocky-9"

# Create a separate filesystem for the container runtime.
mkdir -p "$ROOTFS"

# Install Python using only the local signed repository.
dnf \
    --installroot="$ROOTFS" \
    --releasever=9 \
    --disablerepo="*" \
    --repofrompath="$REPO,file://$ISO/Minimal" \
    --enablerepo="$REPO" \
    --setopt="$REPO.gpgcheck=1" \
    --setopt="$REPO.gpgkey=file://$ISO/RPM-GPG-KEY-Rocky-9" \
    --setopt=install_weak_deps=False \
    -y install python3

# Verify that Python works inside the isolated filesystem.
chroot "$ROOTFS" /usr/bin/python3 --version

echo "Offline container filesystem is ready."
