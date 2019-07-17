# How to install Ubuntu server with serial console

## Extract Linux kernel and initrd from ISO image


Ex.:

    sudo mount -o loop ubuntu-18.04.2-server-amd64.iso /mnt/tmp
    cp /mnt/tmp/install/vmlinuz .
    cp /mnt/tmp/install/initrd.gz .


## Run qemu with the kernel option

    qemu-cmd-gen.py -k vmlinuz console=ttyS0 -i initrd.gz -n -c ubuntu-18.04.2-server-amd64.iso -d disk.img


## Run the Linux on the installed disk image (option1)

Boot Linux with the above command line, select load installer components from CD, and Execute a shell

    mkdir /mnt/tmp
    mount /dev/vda1 /mnt/tmp
    chroot /mnt/tmp /bin/bash

    mount -t devtmpfs none /dev
    mount -t proc none /proc
    mount -t sysfs none /sys

Edit /etc/default/grub

    $ diff -u grub.orig grub
    --- grub.orig   2019-07-15 18:00:07.888000000 +0900
    +++ grub        2019-07-17 23:11:42.473040995 +0900
    @@ -4,11 +4,11 @@
     #   info -f grub -n 'Simple configuration'
 
     GRUB_DEFAULT=0
    -GRUB_TIMEOUT_STYLE=hidden
    -GRUB_TIMEOUT=0
    +GRUB_TIMEOUT_STYLE=menu
    +GRUB_TIMEOUT=5
     GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
    -GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
    -GRUB_CMDLINE_LINUX=""
    +GRUB_CMDLINE_LINUX_DEFAULT=""
    +GRUB_CMDLINE_LINUX="console=tty1 console=ttyS0,115200"
 
     # Uncomment to enable BadRAM filtering, modify to suit your needs
     # This works with Linux (no patch required) and with any kernel that obtains
    @@ -16,7 +16,7 @@
     #GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"
 
     # Uncomment to disable graphical terminal (grub-pc only)
    -GRUB_TERMINAL=console
    +GRUB_TERMINAL="console serial"

     # The resolution used on graphical terminal
     # note that you can use only modes which your graphic card supports via VBE
    @@ -32,4 +32,4 @@
     # Uncomment to get a beep at grub start
     #GRUB_INIT_TUNE="480 440 1"
     GRUB_TERMINAL=serial
    -GRUB_SERIAL_COMMAND="serial --unit=0 --speed=9600 --stop=1"
    +GRUB_SERIAL_COMMAND="serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1"


Then run the following command

    grub-mkconfig -o /boot/grub/grub.cfg

