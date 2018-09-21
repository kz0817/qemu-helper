#!/usr/bin/env python3
import argparse
import subprocess

def disk_image_param(args):
    return (
        '-drive',
        'format=raw,file=%s,if=virtio' % args.disk_image
    )


def net_user_param(args):
    return (
        '-net', 'nic,model=virtio -net user'
    )


def tap_param(args):
    # Todo: add interface to args.bridge_name
    return (
        '-netdev','tap,id=netdev0',
        '-device', 'virtio-net,netdev=netdev0'
    )


def kernel_param(args):
    kernel_opt = args.kernel
    s = ['-kernel', kernel_opt[0]]
    if len(kernel_opt) >= 2:
        s.append('-append')
        s.extend([x for x in kernel_opt[1:]])
    return s


def generate(args):
    cmd = []
    cmd.append(args.qemu)
    cmd.append('--enable-kvm')
    cmd.extend(('-m', str(args.memory)))
    cmd.append('-nographic')

    if args.disk_image:
        cmd.extend(disk_image_param(args))

    if args.net_user:
        cmd.extend(('-net', 'nic,model=virtio', '-net', 'user'))

    if args.tap:
        cmd.extend(tap_param(args))

    if args.cdrom:
        cmd.extend(('-cdrom', args.cdrom))

    if args.kernel:
        cmd.extend(kernel_param(args))

    if args.initrd:
        cmd.extend(('-initrd', args.initrd))

    return cmd


def start():
    parser = argparse.ArgumentParser(
        description='A tool for generating QEMU comand lines.')
    parser.add_argument('--qemu', default='qemu-system-x86_64')
    parser.add_argument('-m', '--memory', default=1024)
    parser.add_argument('-d', '--disk-image')
    parser.add_argument('-u', '--net-user', action='store_true')
    parser.add_argument('-t', '--tap', action='store_true')
    parser.add_argument('-c', '--cdrom')
    parser.add_argument('-k', '--kernel', nargs='+')
    parser.add_argument('-i', '--initrd')

    parser.add_argument('-e', '--execute', action='store_true')

    args = parser.parse_args()
    cmd_arr = generate(args)
    print(' '.join(cmd_arr))
    if args.execute:
        subprocess.run(cmd_arr)


if __name__ == '__main__':
    start()
