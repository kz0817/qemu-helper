# How to use macvtap

## How to create a device

    ip link add link NIC name NAME type macvtap mode bridge

- NIC is a netowrk device name such as eth0 and enp1s0
- NAME is an arbitary vmactap device name (e.g. macvtap0)

## How to bring the device up

    ip link set NAME up

## Add the following option

    -net tap,td=3 3<>/dev/tap`< /sys/class/net/NAME/ifindex`

# References
- https://ahelpme.com/linux/howto-do-qemu-full-virtualization-with-macvtap-networking/
