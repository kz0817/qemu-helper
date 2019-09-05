# Brief
QEMU is highly functional and has many flexible and complicated command line paramters. I often forget them and have had to look into the manual. This software creates a command line of QEMU (and optionally executes it) from some basic paramters such as memory size, a disk image file, a CD image file and so on.

# Example to run

The following command generates the next QEMU command line.

     $ ./qemu-cmd-gen.py -m 2048 -d disk-min.img -t

    qemu-system-x86_64 --enable-kvm -m 2048 -nographic -drive format=raw,file=disk-min.img,if=virtio -netdev tap,id=netdev0 -device virtio-net,netdev=netdev0


# Example to use user-mode network

    qemu-cmd-gen.py -u -f 8022,22

The above command line forwards host's 8022 port to guest's 22 port.


# Setting qemu-bridge-helper for Ubuntu 18.04

    sudo mkdir /etc/qemu
    echo "allow all" | sudo tee /etc/qemu/bridge.conf
