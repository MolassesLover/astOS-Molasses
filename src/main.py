#!/usr/bin/python3

import os
import sys
import subprocess

# TODO: the installer needs a proper rewrite
# TODO: Use native functions instead of subprocess.run(shell=True, check=True, args=)
# TODO: Append to package list instead of pacstrapping a gazillion times

args = list(sys.argv)


def clear():
    subprocess.run(shell=True, check=True, args="clear")


def to_uuid(part):
    uuid = str(subprocess.check_output(f"blkid -s UUID -o value {part}", shell=True))
    return uuid.replace("b'", "").replace('"', "").replace("\\n'", "")


def strap(packages):
    excode = int(
        subprocess.run(
            shell=True, check=True, args=f'pacstrap /mnt --needed {" ".join(packages)}'
        )
    )
    if excode != 0:
        print("Failed to download packages!")
    return excode


def main(args):
    while True:
        clear()
        print("Welcome to the astOS installer!")
        print(
            """                oQA#$%UMn
                H       9
                G       #
                6       %
                ?#M#%KW3"
                  // \\
                //     \\
              //         \\
            //             \\
        n%@$DK&ML       .0O3#@&M_
        P       #       8       W
        H       U       G       #
        B       N       O       @
        C&&#%HNAR       'WS3QMHB"
          // \\              \\
        //     \\              \\
      //         \\              \\
    //             \\              \\
uURF$##Bv       nKWB$%ABc       aM@3R@D@b
8       M       @       O       #       %
%       &       G       U       @       @
&       @       #       %       %       #
!HGN@MNCf       t&$9#%HQr       ?@G#6S@QP
"""
        )
        print(
            """Select installation profile:
1. Minimal install - suitable for embedded devices or servers
2. Desktop install (Gnome) - suitable for workstations
3. Desktop install (KDE Plasma)
4. Desktop install (MATE)"""
        )
        InstallProfile = str(input("> "))
        if InstallProfile == "1":
            DesktopInstall = 0
            break
        if InstallProfile == "2":
            DesktopInstall = 1
            break
        if InstallProfile == "3":
            DesktopInstall = 2
            break
        if InstallProfile == "4":
            DesktopInstall = 3
            break

    clear()
    while True:
        print("Select a timezone (type list to list):")
        zone = input("> ")
        if zone == "list":
            subprocess.run(shell=True, check=True, args="ls /usr/share/zoneinfo | less")
        else:
            timezone = str(f"/usr/share/zoneinfo/{zone}")
            break

    clear()
    print("Enter hostname:")
    hostname = input("> ")

    subprocess.run(
        shell=True, check=True, args="pacman -Syy --noconfirm archlinux-keyring"
    )
    subprocess.run(shell=True, check=True, args=f"mkfs.btrfs -f {args[1]}")

    efi = os.path.exists("/sys/firmware/efi")

    subprocess.run(shell=True, check=True, args=f"mount {args[1]} /mnt")
    btrdirs = ["@", "@.snapshots", "@home", "@var", "@etc", "@boot"]
    mntdirs = ["", ".snapshots", "home", "var", "etc", "boot"]

    for btrdir in btrdirs:
        subprocess.run(shell=True, check=True, args=f"btrfs sub create /mnt/{btrdir}")

    subprocess.run(shell=True, check=True, args="umount /mnt")

    for mntdir in mntdirs:
        subprocess.run(shell=True, check=True, args=f"mkdir /mnt/{mntdir}")
        subprocess.run(
            shell=True,
            check=True,
            args=f"mount {args[1]} -o \
            subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime \
            /mnt/{mntdir}",
        )

    for i in ("tmp", "root"):
        subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/.snapshots/{i}")
    for i in ("root", "tmp"):
        subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/.snapshots/ast/{i}")

    if efi:
        subprocess.run(shell=True, check=True, args="mkdir /mnt/boot/efi")
        subprocess.run(shell=True, check=True, args=f"mount {args[3]} /mnt/boot/efi")

    packages = [
        "base",
        "linux",
        "linux-firmware",
        "nano",
        "python3",
        "python-anytree",
        "bash",
        "dhcpcd",
        "arch-install-scripts",
        "btrfs-progs",
        "networkmanager",
        "grub",
    ]

    if efi:
        packages.append("efibootmgr")

    inp = ""
    while True:
        if strap(packages):
            print("Do you wish to retry? (y/n")
            while inp.casefold() not in ["y", "n", "yes", "no"]:
                inp = input("> ")
                print("Do you wish to retry? (y/n")
            if inp.casefold() in ["n", "no"]:
                break
        else:
            break

    with open("/mnt/etc/fstab", "a") as f:
        f.write(
            f'UUID="{to_uuid(args[1])}" / btrfs subvol=@,compress=zstd,noatime,ro 0 0\n'
        )

        for mntdir in mntdirs[1:]:
            f.write(
                f'UUID="{to_uuid(args[1])}" /{mntdir} btrfs subvol=@{mntdir},compress=zstd,noatime 0 0\n'
            )

        if efi:
            f.write(f'UUID="{to_uuid(args[3])}" /boot/efi vfat umask=0077 0 2\n')

        f.write("/.snapshots/ast/root /root none bind 0 0\n")
        f.write("/.snapshots/ast/tmp /tmp none bind 0 0\n")

    astpart = to_uuid(args[1])

    subprocess.run(shell=True, check=True, args="mkdir -p /mnt/usr/share/ast/db")
    subprocess.run(shell=True, check=True, args="echo '0' > /mnt/usr/share/ast/snap")

    with open("/mnt/etc/os-release", "w") as f:
        f.write(
            """NAME="astOS"
PRETTY_NAME="astOS"
ID="astos"
BUILD_ID="rolling"
ANSI_COLOR="38;2;23;147;209"
HOME_URL="https://github.com/CuBeRJAN/astOS"
LOGO="astos-logo"
"""
        )
    subprocess.run(
        shell=True, check=True, args="cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db"
    )
    subprocess.run(
        shell=True,
        check=True,
        args='sed -i s,"#DBPath      = /var/lib/pacman/","DBPath      = /usr/share/ast/db/",g /mnt/etc/pacman.conf',
    )
    subprocess.run(
        shell=True,
        check=True,
        args="echo 'DISTRIB_ID=\"astOS\"' > /mnt/etc/lsb-release",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="echo 'DISTRIB_RELEASE=\"rolling\"' >> /mnt/etc/lsb-release",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="echo 'DISTRIB_DESCRIPTION=astOS' >> /mnt/etc/lsb-release",
    )

    subprocess.run(
        shell=True,
        check=True,
        args=f"arch-chroot /mnt ln -sf {timezone} /etc/localtime",
    )
    subprocess.run(
        shell=True, check=True, args="echo 'en_US UTF-8' >> /mnt/etc/locale.gen"
    )
    #    subprocess.run(shell=True, check=True, args="sed -i s/'^#'// /mnt/etc/locale.gen")
    #    subprocess.run(shell=True, check=True, args="sed -i s/'^ '/'#'/ /mnt/etc/locale.gen")
    subprocess.run(shell=True, check=True, args="arch-chroot /mnt locale-gen")
    subprocess.run(shell=True, check=True, args="arch-chroot /mnt hwclock --systohc")
    subprocess.run(
        shell=True, check=True, args="echo 'LANG=en_US.UTF-8' > /mnt/etc/locale.conf"
    )
    subprocess.run(shell=True, check=True, args=f"echo {hostname} > /mnt/etc/hostname")

    subprocess.run(
        shell=True,
        check=True,
        args="sed -i '0,/@/{s,@,@.snapshots/rootfs/snapshot-tmp,}' \
    /mnt/etc/fstab",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="sed -i '0,/@etc/{s,@etc,@.snapshots/etc/etc-tmp,}' \
    /mnt/etc/fstab",
    )
    #    subprocess.run(shell=True, check=True, args="sed -i '0,/@var/{s,@var,@.snapshots/var/var-tmp,}' \
    #    /mnt/etc/fstab")
    subprocess.run(
        shell=True,
        check=True,
        args="sed -i '0,/@boot/{s,@boot,@.snapshots/boot/boot-tmp,}' \
    /mnt/etc/fstab",
    )
    subprocess.run(
        shell=True, check=True, args="mkdir -p /mnt/.snapshots/ast/snapshots"
    )

    subprocess.run(shell=True, check=True, args="cp ./astpk.py /mnt/.snapshots/ast/ast")
    subprocess.run(
        shell=True, check=True, args="arch-chroot /mnt chmod +x /.snapshots/ast/ast"
    )
    subprocess.run(
        shell=True,
        check=True,
        args="arch-chroot /mnt ln -s /.snapshots/ast /var/lib/ast",
    )
    subprocess.run(
        shell=True, check=True, args="arch-chroot /mnt chmod 700 /.snapshots/ast/root"
    )
    subprocess.run(
        shell=True, check=True, args="arch-chroot /mnt chmod 1777 /.snapshots/ast/tmp"
    )

    clear()
    if (
        not DesktopInstall
    ):  # Don't ask for password if doing a desktop install, since root account will be locked anyway (sudo used instead)
        subprocess.run(shell=True, check=True, args="arch-chroot /mnt passwd")
        while True:
            print("did your password set properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                subprocess.run(shell=True, check=True, args="arch-chroot /mnt passwd")

    subprocess.run(
        shell=True, check=True, args="arch-chroot /mnt systemctl enable NetworkManager"
    )
    subprocess.run(
        shell=True,
        check=True,
        args="echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} > /mnt/.snapshots/ast/fstree",
    )

    if DesktopInstall:
        subprocess.run(
            shell=True,
            check=True,
            args="echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'},{\\'name\\': \\'1\\'}]} > /mnt/.snapshots/ast/fstree",
        )
        subprocess.run(
            shell=True, check=True, args=f"echo '{astpart}' > /mnt/.snapshots/ast/part"
        )

    subprocess.run(
        shell=True,
        check=True,
        args="arch-chroot /mnt sed -i s,Arch,astOS,g /etc/default/grub",
    )
    subprocess.run(
        shell=True, check=True, args=f"arch-chroot /mnt grub-install {args[2]}"
    )
    subprocess.run(
        shell=True,
        check=True,
        args=f"arch-chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="sed -i '0,/subvol=@/{s,subvol=@,subvol=@.snapshots/rootfs/snapshot-tmp,g}' /mnt/boot/grub/grub.cfg",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="arch-chroot /mnt ln -s /.snapshots/ast/ast /usr/local/sbin/ast",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0",
    )
    subprocess.run(
        shell=True, check=True, args="btrfs sub create /mnt/.snapshots/etc/etc-tmp"
    )
    #    subprocess.run(shell=True, check=True, args="btrfs sub create /mnt/.snapshots/var/var-tmp")
    subprocess.run(
        shell=True, check=True, args="btrfs sub create /mnt/.snapshots/boot/boot-tmp"
    )
    #    subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/* /mnt/.snapshots/var/var-tmp")
    #    for i in ("pacman", "systemd"):
    #        subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
    #    subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/pacman/* /mnt/.snapshots/var/var-tmp/lib/pacman/")
    #    subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    subprocess.run(
        shell=True,
        check=True,
        args="cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp",
    )
    #    subprocess.run(shell=True, check=True, args="btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")
    subprocess.run(
        shell=True,
        check=True,
        args="btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0",
    )
    subprocess.run(
        shell=True, check=True, args=f"echo '{astpart}' > /mnt/.snapshots/ast/part"
    )

    if DesktopInstall == 1:
        subprocess.run(
            shell=True, check=True, args="echo '1' > /mnt/usr/share/ast/snap"
        )
        packages.extend(
            [
                "flatpak",
                "gnome",
                "gnome-themes-extra",
                "gdm pipewire",
                "pipewire-pulse",
                "sudo",
            ]
        )
        inp = ""
        while True:
            if strap(packages):
                print("Do you wish to retry? (y/n")
                while inp.casefold() not in ["y", "n", "yes", "no"]:
                    inp = input("> ")
                    print("Do you wish to retry? (y/n")
                if inp.casefold() in ["n", "no"]:
                    break
            else:
                break

        clear()
        print("Enter username (all lowercase, max 8 letters)")
        username = input("> ")
        while True:
            print("did your set username properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                print("Enter username (all lowercase, max 8 letters)")
                username = input("> ")
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt useradd {username}"
        )
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt passwd {username}"
        )
        while True:
            print("did your password set properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                subprocess.run(
                    shell=True, check=True, args=f"arch-chroot /mnt passwd {username}"
                )
        subprocess.run(
            shell=True,
            check=True,
            args=f"arch-chroot /mnt usermod -aG audio,input,video,wheel {username}",
        )
        subprocess.run(shell=True, check=True, args="arch-chroot /mnt passwd -l root")
        subprocess.run(shell=True, check=True, args="chmod +w /mnt/etc/sudoers")
        subprocess.run(
            shell=True,
            check=True,
            args="echo '%wheel ALL=(ALL:ALL) ALL' >> /mnt/etc/sudoers",
        )
        subprocess.run(shell=True, check=True, args="chmod -w /mnt/etc/sudoers")
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt mkdir /home/{username}"
        )
        subprocess.run(
            shell=True,
            check=True,
            args=f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' >> /home/{username}/.bashrc",
        )
        subprocess.run(
            shell=True,
            check=True,
            args=f"arch-chroot /mnt chown -R {username} /home/{username}",
        )
        subprocess.run(
            shell=True, check=True, args="arch-chroot /mnt systemctl enable gdm"
        )
        subprocess.run(
            shell=True,
            check=True,
            args="cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-1",
        )
        subprocess.run(
            shell=True, check=True, args="btrfs sub del /mnt/.snapshots/etc/etc-tmp"
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub del /mnt/.snapshots/var/var-tmp")
        subprocess.run(
            shell=True, check=True, args="btrfs sub del /mnt/.snapshots/boot/boot-tmp"
        )
        subprocess.run(
            shell=True, check=True, args="btrfs sub create /mnt/.snapshots/etc/etc-tmp"
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub create /mnt/.snapshots/var/var-tmp")
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub create /mnt/.snapshots/boot/boot-tmp",
        )
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/* /mnt/.snapshots/var/var-tmp")
        #        for i in ("pacman", "systemd"):
        #            subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/pacman/* /mnt/.snapshots/var/var-tmp/lib/pacman/")
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp",
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-1")
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-1",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-1",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap /mnt/.snapshots/rootfs/snapshot-1 /mnt/.snapshots/rootfs/snapshot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="arch-chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp",
        )

    elif DesktopInstall == 2:
        subprocess.run(
            shell=True, check=True, args="echo '1' > /mnt/usr/share/ast/snap"
        )
        packages.extend(
            [
                "flatpak",
                "plasma",
                "xorg",
                "konsole",
                "dolphin",
                "sddm",
                "pipewire",
                "pipewire-pulse",
                "sudo",
            ]
        )

        inp = ""
        while True:
            if strap(packages):
                print("Do you wish to retry? (y/n")
                while inp.casefold() not in ["y", "n", "yes", "no"]:
                    inp = input("> ")
                    print("Do you wish to retry? (y/n")
                if inp.casefold() in ["n", "no"]:
                    break
            else:
                break

        clear()
        print("Enter username (all lowercase, max 8 letters)")
        username = input("> ")
        while True:
            print("did your set username properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                print("Enter username (all lowercase, max 8 letters)")
                username = input("> ")
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt useradd {username}"
        )
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt passwd {username}"
        )
        while True:
            print("did your password set properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                subprocess.run(
                    shell=True, check=True, args=f"arch-chroot /mnt passwd {username}"
                )
        subprocess.run(
            shell=True,
            check=True,
            args=f"arch-chroot /mnt usermod -aG audio,input,video,wheel {username}",
        )
        subprocess.run(shell=True, check=True, args="arch-chroot /mnt passwd -l root")
        subprocess.run(shell=True, check=True, args="chmod +w /mnt/etc/sudoers")
        subprocess.run(
            shell=True,
            check=True,
            args="echo '%wheel ALL=(ALL:ALL) ALL' >> /mnt/etc/sudoers",
        )
        subprocess.run(
            shell=True, check=True, args="echo '[Theme]' > /mnt/etc/sddm.conf"
        )
        subprocess.run(
            shell=True, check=True, args="echo 'Current=breeze' >> /mnt/etc/sddm.conf"
        )
        subprocess.run(shell=True, check=True, args="chmod -w /mnt/etc/sudoers")
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt mkdir /home/{username}"
        )
        subprocess.run(
            shell=True,
            check=True,
            args=f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' >> /home/{username}/.bashrc",
        )
        subprocess.run(
            shell=True,
            check=True,
            args=f"arch-chroot /mnt chown -R {username} /home/{username}",
        )
        subprocess.run(
            shell=True, check=True, args="arch-chroot /mnt systemctl enable sddm"
        )
        subprocess.run(
            shell=True,
            check=True,
            args="cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-1",
        )
        subprocess.run(
            shell=True, check=True, args="btrfs sub del /mnt/.snapshots/etc/etc-tmp"
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub del /mnt/.snapshots/var/var-tmp")
        subprocess.run(
            shell=True, check=True, args="btrfs sub del /mnt/.snapshots/boot/boot-tmp"
        )
        subprocess.run(
            shell=True, check=True, args="btrfs sub create /mnt/.snapshots/etc/etc-tmp"
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub create /mnt/.snapshots/var/var-tmp")
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub create /mnt/.snapshots/boot/boot-tmp",
        )
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/* \
        #                   /mnt/.snapshots/var/var-tmp")
        #        for i in ("pacman", "systemd"):
        #            subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/pacman/* \
        #                   /mnt/.snapshots/var/var-tmp/lib/pacman/")
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/systemd/* \
        #                   /mnt/.snapshots/var/var-tmp/lib/systemd/")
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/boot/* \
                   /mnt/.snapshots/boot/boot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/etc/* \
                   /mnt/.snapshots/etc/etc-tmp",
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub snap -r /mnt/.snapshots/var/var-tmp \
        #                   /mnt/.snapshots/var/var-1")
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp \
                   /mnt/.snapshots/boot/boot-1",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp \
                   /mnt/.snapshots/etc/etc-1",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap /mnt/.snapshots/rootfs/snapshot-1 \
                   /mnt/.snapshots/rootfs/snapshot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="arch-chroot /mnt btrfs sub set-default \
                   /.snapshots/rootfs/snapshot-tmp",
        )

    elif DesktopInstall == 3:
        subprocess.run(
            shell=True, check=True, args="echo '1' > /mnt/usr/share/ast/snap"
        )
        packages.extend(
            [
                "flatpak",
                "mate",
                "pluma",
                "caja",
                "mate-terminal",
                "gdm",
                "pipewire",
                "pipewire-pulse",
                "sudo",
                "ttf-dejavu",
                "mate-extra",
            ]
        )

        inp = ""
        while True:
            if strap(packages):
                print("Do you wish to retry? (y/n")
                while inp.casefold() not in ["y", "n", "yes", "no"]:
                    inp = input("> ")
                    print("Do you wish to retry? (y/n")
                if inp.casefold() in ["n", "no"]:
                    break
            else:
                break

        clear()
        print("Enter username (all lowercase, max 8 letters)")
        username = input("> ")
        while True:
            print("did your set username properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                print("Enter username (all lowercase, max 8 letters)")
                username = input("> ")
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt useradd {username}"
        )
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt passwd {username}"
        )
        while True:
            print("did your password set properly (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                clear()
                subprocess.run(
                    shell=True, check=True, args=f"arch-chroot /mnt passwd {username}"
                )
        subprocess.run(
            shell=True,
            check=True,
            args=f"arch-chroot /mnt usermod -aG \
                    audio,input,video,wheel {username}",
        )
        subprocess.run(shell=True, check=True, args="arch-chroot /mnt passwd -l root")
        subprocess.run(shell=True, check=True, args="chmod +w /mnt/etc/sudoers")
        subprocess.run(
            shell=True,
            check=True,
            args="echo '%wheel ALL=(ALL:ALL) ALL' >> /mnt/etc/sudoers",
        )
        subprocess.run(shell=True, check=True, args="chmod -w /mnt/etc/sudoers")
        subprocess.run(
            shell=True, check=True, args=f"arch-chroot /mnt mkdir /home/{username}"
        )
        subprocess.run(
            shell=True,
            check=True,
            args=f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' \
                    >> /home/{username}/.bashrc",
        )
        subprocess.run(
            shell=True,
            check=True,
            args=f"arch-chroot /mnt chown -R {username} /home/{username}",
        )
        subprocess.run(
            shell=True, check=True, args="arch-chroot /mnt systemctl enable gdm"
        )
        subprocess.run(
            shell=True,
            check=True,
            args="cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-1",
        )
        subprocess.run(
            shell=True, check=True, args="btrfs sub del /mnt/.snapshots/etc/etc-tmp"
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub del /mnt/.snapshots/var/var-tmp")
        subprocess.run(
            shell=True, check=True, args="btrfs sub del /mnt/.snapshots/boot/boot-tmp"
        )
        subprocess.run(
            shell=True, check=True, args="btrfs sub create /mnt/.snapshots/etc/etc-tmp"
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub create /mnt/.snapshots/var/var-tmp")
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub create /mnt/.snapshots/boot/boot-tmp",
        )
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/* \
        #                   /mnt/.snapshots/var/var-tmp")
        #        for i in ("pacman", "systemd"):
        #            subprocess.run(shell=True, check=True, args=f"mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/pacman/* \
        #        /mnt/.snapshots/var/var-tmp/lib/pacman/")
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/var/lib/systemd/* \
        #        /mnt/.snapshots/var/var-tmp/lib/systemd/")
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/boot/* \
                /mnt/.snapshots/boot/boot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/etc/* \
                /mnt/.snapshots/etc/etc-tmp",
        )
        #        subprocess.run(shell=True, check=True, args="btrfs sub snap -r /mnt/.snapshots/var/var-tmp \
        #            /mnt/.snapshots/var/var-1")
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp \
                /mnt/.snapshots/boot/boot-1",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp \
                /mnt/.snapshots/etc/etc-1",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap /mnt/.snapshots/rootfs/snapshot-1 \
                /mnt/.snapshots/rootfs/snapshot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="arch-chroot /mnt btrfs sub set-default \
                /.snapshots/rootfs/snapshot-tmp",
        )

    else:
        subprocess.run(
            shell=True,
            check=True,
            args="btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp",
        )
        subprocess.run(
            shell=True,
            check=True,
            args="arch-chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp",
        )

    subprocess.run(
        shell=True, check=True, args="cp -r /mnt/root/. /mnt/.snapshots/root/"
    )
    subprocess.run(shell=True, check=True, args="cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    subprocess.run(shell=True, check=True, args="rm -rf /mnt/root/*")
    subprocess.run(shell=True, check=True, args="rm -rf /mnt/tmp/*")
    #    subprocess.run(shell=True, check=True, args="umount /mnt/var")

    if efi:
        subprocess.run(shell=True, check=True, args="umount /mnt/boot/efi")

    subprocess.run(shell=True, check=True, args="umount /mnt/boot")
    #    subprocess.run(shell=True, check=True, args="mkdir /mnt/.snapshots/var/var-tmp")
    #    subprocess.run(shell=True, check=True, args="mkdir /mnt/.snapshots/boot/boot-tmp")
    #    subprocess.run(shell=True, check=True, args=f"mount {args[1]} -o subvol=@var,compress=zstd,noatime \
    #    /mnt/.snapshots/var/var-tmp")
    subprocess.run(
        shell=True,
        check=True,
        args=f"mount {args[1]} -o subvol=@boot,compress=zstd,noatime \
    /mnt/.snapshots/boot/boot-tmp",
    )
    #    subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/.snapshots/var/var-tmp/* /mnt/var")
    subprocess.run(
        shell=True,
        check=True,
        args="cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot",
    )
    subprocess.run(shell=True, check=True, args="umount /mnt/etc")
    #    subprocess.run(shell=True, check=True, args="mkdir /mnt/.snapshots/etc/etc-tmp")
    subprocess.run(
        shell=True,
        check=True,
        args=f"mount {args[1]} -o subvol=@etc,compress=zstd,noatime \
    /mnt/.snapshots/etc/etc-tmp",
    )
    subprocess.run(
        shell=True,
        check=True,
        args="cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc",
    )

    if DesktopInstall:
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/.snapshots/etc/etc-1/* \
        /mnt/.snapshots/rootfs/snapshot-tmp/etc",
        )
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/.snapshots/var/var-1/* \
        #        /mnt/.snapshots/rootfs/snapshot-tmp/var")
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/.snapshots/boot/boot-1/* \
        /mnt/.snapshots/rootfs/snapshot-tmp/boot",
        )
    else:
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* \
        /mnt/.snapshots/rootfs/snapshot-tmp/etc",
        )
        #        subprocess.run(shell=True, check=True, args="cp --reflink=auto -r /mnt/.snapshots/var/var-0/* \
        #        /mnt/.snapshots/rootfs/snapshot-tmp/var")
        subprocess.run(
            shell=True,
            check=True,
            args="cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* \
        /mnt/.snapshots/rootfs/snapshot-tmp/boot",
        )

    subprocess.run(shell=True, check=True, args="umount -R /mnt")
    subprocess.run(shell=True, check=True, args=f"mount {args[1]} -o subvolid=0 /mnt")
    subprocess.run(shell=True, check=True, args="btrfs sub del /mnt/@")
    subprocess.run(shell=True, check=True, args="umount -R /mnt")
    clear()
    print("Installation complete")
    print("You can reboot now :)")


main(args)
