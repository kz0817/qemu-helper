# Kernel debug symbol package (Ubuntu)

## Setup the apt repository for debug symbols

Create an APT repository configuration file according to the following article.

https://wiki.ubuntu.com/Debug%20Symbol%20Packages


## Download debug symbol
Example:

    apt install linux-image-4.15.0-54-generic-dbgsym

Then the following file will be located.

    /usr/lib/debug/boot/vmlinux-4.15.0-54-generic


## Disable KASLR

Add the following option to kernel command line and reboot.

   nokaslr

In Ubuntu, edit `GRUB_CMDLINE_LINUX` in /etc/default/grub and run the following command.

   grub-mkconfig > /boot/grub/grub.cfg

## Enable a debug feature of sysrq

   echo 1 > /proc/sys/kernel/sysrq

or set any value containing 0x8.

Editing /etc/sysctl.d/10-magic-sysrq.conf sets the value on boot.


# Attach to the kernel with GDB

Example:

    gdb /usr/lib/debug/boot/vmlinux-4.15.0-54-generic

    (gdb) target remote localhost:1234

