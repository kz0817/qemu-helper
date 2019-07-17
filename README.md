# qemu-helper
A helper utilities to use QEMU. This software creates a command line or executes it. Users only give a basic paramters such as memory size, a disk image file, a CD image file and so on. Complicated parameters are automatically generated. 

# Example to run

The following command generates the next QEMU command line.

     $ ./qemu-cmd-gen.py -m 2048 -d disk-min.img -t

    qemu-system-x86_64 --enable-kvm -m 2048 -nographic -drive format=raw,file=disk-min.img,if=virtio -netdev tap,id=netdev0 -device virtio-net,netdev=netdev0


# Example to use user-mode network

    qemu-cmd-gen.py -u -f 8022,22

The above command line forwards host's 8022 port to guest's 22 port.


# Setting qemu-bridge-helper for Ubuntu 18.04

    sudo mkdir /etc/qemu
    echo "allow all" | sudo tee /etc/quemu/bridge.conf
