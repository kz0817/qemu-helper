#!/usr/bin/env python3
import argparse
import subprocess
import shlex
import platform

class Command(object):
    def __init__(self):
        self.__exec_arr = []
        self.__show_arr = []


    def __iadd__(self, arg):
        if isinstance(arg, str):
            arg_arr = (arg,)
        else:
            arg_arr = arg

        for param in arg_arr:
            self.__exec_arr.append(param)
            self.__show_arr.append(self.__quote_if_needed(param))

        return self


    def __quote_if_needed(self, arg):
        if ' ' not in arg:
            return arg
        escaped_arg = arg.replace("'", "\\'")
        return "'%s'" % escaped_arg;


    def __str__(self):
        return ' '.join(self.__show_arr)


    def get_arguments(self):
        return self.__exec_arr


def disk_image_param(disk_image):
    return (
        '-drive',
        'format=raw,file=%s,if=virtio' % disk_image
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
        # Kernel option shall be handled as one parameter
        s.append(' '.join([x for x in kernel_opt[1:]]))
    return s


def accel_param(args):
    return {
        'Linux': '--enable-kvm',
        'Darwin': ('-accel', 'hvf')
    }[platform.system()]


def generate(args):
    cmd = Command()
    cmd += args.qemu
    if not args.no_accel:
        cmd += accel_param(args)
    cmd += ('-m', str(args.memory))

    if args.smp is not None:
        cmd += ('-smp', str(args.smp))

    if args.nographic:
        cmd += '-nographic'

    for disk_image in args.disk_images:
        cmd += disk_image_param(disk_image)

    if args.net_user:
        cmd += ('-net', 'nic,model=virtio', '-net', 'user')

    if args.tap:
        cmd += tap_param(args)

    if args.cdrom:
        cmd += ('-cdrom', args.cdrom)

    if args.kernel:
        cmd += kernel_param(args)

    if args.initrd:
        cmd += ('-initrd', args.initrd)

    if args.boot:
        cmd += ('-boot', args.boot)

    if args.monitor:
        cmd += ('-monitor', args.monitor)

    return cmd


def start():
    parser = argparse.ArgumentParser(
        description='A tool for generating QEMU comand lines.')
    parser.add_argument('--qemu', default='qemu-system-x86_64')
    parser.add_argument('-s', '--smp', type=int)
    parser.add_argument('-A', '--no-accel', action='store_true')
    parser.add_argument('-m', '--memory', type=int, default=1024)
    parser.add_argument('-d', '--disk-images', action='append', default=[])
    parser.add_argument('-u', '--net-user', action='store_true')
    parser.add_argument('-t', '--tap', action='store_true')
    parser.add_argument('-c', '--cdrom')
    parser.add_argument('-k', '--kernel', nargs='+')
    parser.add_argument('-i', '--initrd')
    parser.add_argument('-n', '--nographic', action='store_true')
    parser.add_argument('-b', '--boot', help='c: HDD, d: CDROM')
    parser.add_argument('-M', '--monitor', nargs='?', const='stdio')

    parser.add_argument('-e', '--execute', action='store_true')

    args = parser.parse_args()
    cmd = generate(args)
    print(cmd)
    if args.execute:
        subprocess.run(cmd.get_arguments())


if __name__ == '__main__':
    start()
