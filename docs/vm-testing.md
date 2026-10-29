# Testing FerryOS in a VM

This guide sets up a virt-manager VM on a Linux host, installs Fedora Kinoite in it and switches it to FerryOS. Commands marked **host** run on your normal system; commands marked **VM** run inside the virtual machine.

## 1. Prepare the host

### Check that hardware virtualization works (host)

```bash
ls -l /dev/kvm
```

If `/dev/kvm` doesn't exist, enable virtualization in your BIOS/UEFI (Intel VT-x or AMD-V/SVM) and make sure your kernel has `CONFIG_KVM` plus `CONFIG_KVM_INTEL` or `CONFIG_KVM_AMD`.

### Packages (host, Gentoo)

virt-manager pulls in QEMU and libvirt. You also need UEFI firmware and SPICE support for a usable display:

```bash
emerge --search edk2
```

```bash
sudo emerge --ask --noreplace sys-firmware/edk2-bin
```

(Use whichever edk2 package the search shows.) QEMU should have the `spice` and `usbredir` USE flags; check with:

```bash
equery uses app-emulation/qemu | grep -E "spice|usbredir"
```

### Start libvirt (host)

OpenRC:

```bash
sudo rc-update add libvirtd default && sudo rc-service libvirtd start
```

systemd:

```bash
sudo systemctl enable --now libvirtd
```

### Permissions (host)

```bash
sudo usermod -aG libvirt,kvm $USER
```

Log out and back in afterwards.

### Default network (host)

```bash
sudo virsh net-start default
```

```bash
sudo virsh net-autostart default
```

"Network is already active" is fine.

## 2. Download Fedora Kinoite (host)

Download the Kinoite ISO from <https://fedoraproject.org/atomic-desktops/kinoite/>. The Fedora version doesn't matter much: `bootc switch` replaces the whole system with FerryOS anyway.

Move the ISO to libvirt's image folder to avoid permission errors:

```bash
sudo mv ~/Downloads/Fedora-Kinoite-*.iso /var/lib/libvirt/images/
```

## 3. Create the VM in virt-manager

1. **File → New Virtual Machine → Local install media (ISO image)** → Forward.
2. **Browse** → choose the Kinoite ISO. The OS should be detected as Fedora; if not, untick "Automatically detect" and pick the newest Fedora → Forward.
3. **Memory:** 6144 MB (minimum 4096). **CPUs:** 4 → Forward.
4. **Disk:** 60 GB (Steam and the default apps need room; 40 GB is the minimum) → Forward.
5. **Name:** `ferryos-test`. Tick **Customize configuration before install** → Finish.
6. In the configuration window:
   - **Overview → Chipset:** Q35. **Firmware:** UEFI (the entry *without* `secboot`/`secure` for now). Click **Apply**.
   - **CPUs:** "Copy host CPU configuration" should be ticked (best performance).
   - **Video:** model **Virtio**. Leave 3D acceleration off for the first test.
7. **Begin Installation** (top left).

## 4. Install Kinoite (VM)

1. Choose your language and keyboard layout.
2. **Installation destination:** select the virtual disk, automatic partitioning. Disk encryption isn't needed in a test VM.
3. **Create user:** set name and password, and keep **"Make this user administrator"** ticked.
4. **Begin installation**, wait, then **Reboot**.
5. If the VM boots into the installer again, shut it down, open **Show virtual hardware details → SATA CDROM**, click **Disconnect**, and start it again.

Log in to the fresh Kinoite desktop.

## 5. Back up the clean state (host, optional)

Restoring a clean Kinoite is handy when testing goes wrong. Shut down the VM, then on the host:

```bash
sudo cp --reflink=auto /var/lib/libvirt/images/ferryos-test.qcow2 /var/lib/libvirt/images/ferryos-test-clean.qcow2
```

To restore later: shut down the VM and copy the file back the other way. (virt-manager's built-in snapshots may not work with UEFI VMs, depending on your libvirt version. The copy always works.)

You often won't need this: bootc keeps the previous system, so `sudo bootc rollback` gets you back too (see section 8).

## 6. Switch to FerryOS (VM)

Open **Konsole** in the VM:

```bash
sudo bootc switch ghcr.io/micha7421/ferryos:latest
```

This downloads a few GB. If `bootc` is missing, use rpm-ostree instead:

```bash
sudo rpm-ostree rebase ostree-unverified-registry:ghcr.io/micha7421/ferryos:latest
```

Then reboot:

```bash
sudo systemctl reboot
```

## 7. Check that it's FerryOS (VM)

The OS name:

```bash
cat /etc/os-release
```

`NAME="FerryOS"` and `PRETTY_NAME="FerryOS (based on Fedora …)"` should appear.

Which image is running:

```bash
sudo bootc status
```

Default apps installing in the background (takes a few minutes after the first boot):

```bash
journalctl -u ferryos-flatpak-setup -f
```

Exit with `Ctrl+C`. Afterwards:

```bash
flatpak list --app
```

should list Firefox, LibreOffice, VLC, Steam, Bottles and the rest.

**Look and feel:** the accent color is teal (System Settings → Colors & Themes), and files open with a double-click. These are defaults, so a user who already changed them keeps their own choice. To see the defaults exactly as a new user would, create a second user in System Settings → Users and log in as them.

**Hostname:** `ferryos` is only used if the installer didn't set one, so a VM installed from Kinoite may still be called `fedora`. That's expected.

## 8. Daily loop: test changes

1. Change something in the repo and push to `main`.
2. Wait until the build at <https://github.com/micha7421/FerryOS/actions> is through the "Push To GHCR" step (about 10–20 minutes).
3. In the VM:

```bash
sudo bootc upgrade
```

```bash
sudo systemctl reboot
```

`sudo bootc upgrade --apply` does both in one go.

### Going back

Previous FerryOS version:

```bash
sudo bootc rollback
```

```bash
sudo systemctl reboot
```

You can also pick the older entry in the boot menu: hold **Shift** or press **Esc** right after the VM starts.

Back to plain Kinoite: `sudo bootc switch quay.io/fedora/fedora-kinoite:<version>`, or restore the backup from section 5.

## 9. Making the VM comfortable

- **Copy & paste and auto-resize:** work out of the box with SPICE (Kinoite includes `spice-vdagent`). If not, check **View → Scale Display → Auto resize VM with window**.
- **SSH from the host into the VM:**
  - VM: `sudo systemctl enable --now sshd`
  - host: `sudo virsh domifaddr ferryos-test` shows the IP, then `ssh <user>@<ip>`
- **Shared folder:** in the VM's hardware details, **Memory → Enable shared memory**, then **Add Hardware → Filesystem**, driver **virtiofs**, source a host folder, target `share`. In the VM: `sudo mount -t virtiofs share /mnt`.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| "KVM is not available" | `/dev/kvm` missing: enable VT-x/AMD-V in the BIOS, check kernel config, and make sure you're in the `kvm` group |
| "Network 'default' is not active" | `sudo virsh net-start default` |
| "Permission denied" for the ISO | Move the ISO to `/var/lib/libvirt/images/` |
| Black screen after boot | Video → Virtio without 3D, or try QXL; Display Spice → Listen type "None" |
| No UEFI option under Firmware | Install the edk2 firmware package and restart libvirtd |
| `bootc switch`: "denied" or "unauthorized" | The package on GitHub isn't public yet, or the first build hasn't reached "Push To GHCR" |
| `bootc switch`: "manifest unknown" | Typo in the name; it's lowercase `ghcr.io/micha7421/ferryos:latest` |
| Apps don't appear | `journalctl -u ferryos-flatpak-setup` shows why; it retries every 30 seconds while there's no network |
| Very slow VM | Give it more RAM/CPUs and check "Copy host CPU configuration" |
