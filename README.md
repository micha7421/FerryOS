<p align="center"><img src="branding/ferryos-lockup.svg" alt="FerryOS" height="96"></p>

<p align="center"><b>Bring your whole PC with you.</b></p>

FerryOS is a Linux distribution for people moving from Windows. It doesn't just look familiar: it carries over your files, finds the programs you used on Windows and suggests their Linux equivalents, and runs `.exe` files through a compatibility layer when no Linux version exists.

> **Status:** early development. The image builds and boots, but the migration tools (Ferry Welcome) don't exist yet.

## What's inside

| Part | Choice |
|---|---|
| Base | Fedora KDE (Kinoite) via [Universal Blue](https://universal-blue.org/), built with [bootc](https://github.com/bootc-dev/bootc) |
| Desktop | KDE Plasma 6 (Wayland), Windows-like layout, teal accent |
| Updates | Automatic and atomic, with rollback to the previous version |
| Apps | Flatpak from Flathub, installed on first boot (see [`flatpaks.list`](system_files/usr/share/ferryos/flatpaks.list)) |
| Windows programs | Bottles |
| Gaming | Steam with Proton |

## Try it

FerryOS isn't installable from its own ISO yet. To test it, install [Fedora Kinoite](https://fedoraproject.org/atomic-desktops/kinoite/) in a VM, then switch to FerryOS:

```bash
sudo bootc switch ghcr.io/micha7421/ferryos:latest
sudo systemctl reboot
```

Later updates arrive automatically, or by running `sudo bootc upgrade`. The full step-by-step guide is in [docs/vm-testing.md](docs/vm-testing.md).

## Repository layout

| Path | Purpose |
|---|---|
| `Containerfile` | Picks the base image and runs the build script |
| `build_files/build.sh` | Branding, package changes, enabled services |
| `system_files/` | Files copied into the image as-is (`/etc`, `/usr`) |
| `disk_config/` | Configuration for building ISO and VM disk images |
| `.github/workflows/` | Builds, signs and publishes the image on every push to `main` |

## Building locally

Needs Podman and [just](https://github.com/casey/just):

```bash
just build        # build the container image
just build-qcow2  # build a VM disk image
just run-vm       # boot it in QEMU
```

Run `just --list` for all recipes.

## Roadmap

1. ~~Base image, branding, default apps~~
2. Plasma layout and look (taskbar, wallpaper, logo)
3. Ferry Welcome: copy files over from a Windows partition or backup drive
4. Read installed Windows programs from the registry and map them to Linux apps
5. `.exe` handler with Bottles integration and compatibility badges
6. FerryOS ISO and public beta

## Credits

Built on the [Universal Blue image template](https://github.com/ublue-os/image-template).
