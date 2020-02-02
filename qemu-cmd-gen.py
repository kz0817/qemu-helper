#!/usr/bin/env python3
import argparse
import subprocess
import shlex
import platform

DEFAULT_QEMU = 'qemu-system-x86_64'
DEFAULT_NUM_CPU = 1
DEFAULT_MEM_SIZE = 1024
DEFAULT_GDB_PORT = 'tcp::1234'
DEFAULT_SOUND_DEV = 'ac97'
DEFAULT_MONITOR_DEV = 'stdio'

OPT_QEMU_HELP = 'use QEMU as a command (Default: %s)' % DEFAULT_QEMU
OPT_SMP_HELP = 'The number of CPUs (Default: %d)' % DEFAULT_NUM_CPU
OPT_MEMORY_HELP = 'set memory size to M KiB (Default: %d)' % DEFAULT_MEM_SIZE
OPT_DRIVE_HELP = '''
'add FILE as a drive. Avaliable OPT: scsi (default virtio)')
'''
OPT_NET_USER_HELP='create a NIC connected to user (private) network with NAT'
OPT_HOST_FWD_HELP = '''
forward a host port to guest. PORTS: host_port,guest_port (Ex: -f 8022,22).
use with -u option.
'''
OPT_TAP_HELP = '''
create a NIC connected to the host's standard bridge.
To use this option, a root privilege is required
'''
OPT_BRIDGES_HELP = '''
create NICs connected to host bridges. BR is a list of the bridges
'''
OPT_BRIDGE_HELPER_HELP = '''
A bridge helper program which connects a VM's tap to a host bridge.
(Default: /usr/lib/qemu/qemu-bridge-helper)
Note: a root privilege is typicall required to use this option.
'''
OPT_SOUND_HELP = '''
add a sound card. DEVICE is a sound card (default: %s).
If this option is not given, no sound device is installed in the VM.
''' % DEFAULT_SOUND_DEV
OPT_INITRD_HELP = '''
use the specified FILE as initrd/initramfs.
This option is typically used with -k
'''
OPT_NOGRAPHIC_HELP = '''
disable graphic and add a serial port redirected to the console.
You can switch between monitor and serial console by ctrl-a c
'''
OPT_BOOT_HELP = 'boot from DRIVE. DRIVE be c (Drive) or d (CD-ROM)'
OPT_MENU_HELP = 'show a menu to select a boot device at BIOS screen'
OPT_MONITOR_HELP = '''
set the monitor device to DEV. If DEV is omitted, %s is used.
''' % DEFAULT_MONITOR_DEV
OPT_GDB_HELP = '''
start GDB server with the specified PORT or default: %s
''' % DEFAULT_GDB_PORT
OPT_VNC_HELP = 'open VNC service. port: 5900 + N'
OPT_USB_HELP = '''
add a Host's USB device whose BUS and DEV can be found in output of "lsusb"
'''
OPT_EXEC_HELP = '''
execute the generated command line.
'''
OPT_ADDITIONAL_HELP = '''
additional QEMU options.
Note: '--' is needed before the options when their first character is '-'.
Ex: qemu-cmd-gen.py -d drive.img -- -vnc :0
QEMU options can be seen at https://linux.die.net/man/1/qemu-kvm
'''

class Context:
    def __init__(self):
        self.have_scsi_dev = False
        self.name_count_map = {}

    def get_name(self, name_key):
        count = self.name_count_map.get(name_key)
        if count is None:
            count = 0
        else:
            count += 1
        self.name_count_map[name_key] = count
        return '%s%d' % (name_key, count)

    def create_scsi_device_if_needed(self):
        if self.have_scsi_dev:
            return []
        self.have_scsi_dev = True
        return ('-device', 'virtio-scsi-pci')

    def create_scsi_hd(self, drive_name):
        return ('-device', 'scsi-hd,drive=%s' % drive_name)


ctx = Context()

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


def drive_image_param(drive):

    interface = None
    cmd = []
    drive_id = ctx.get_name('drive')

    drive_img = drive[0]
    for param in drive[1:]:
        if param == 'scsi':
            cmd += ctx.create_scsi_device_if_needed()
            cmd += ctx.create_scsi_hd(drive_id)
            interface = 'none'
        else:
            assert False, 'Unknown parameter: %s' % param

    ext = drive_img.split('.')[-1]
    fmt = {'qcow2': 'qcow2'}.get(ext, 'raw')
    if interface is None:
        interface = {'fd': 'pflash'}.get(ext, 'virtio')

    cmd += [
        '-drive',
        'id=%s,format=%s,file=%s,if=%s' % (drive_id, fmt, drive_img, interface)
    ]
    return cmd


def net_user_param(args):
    fmt = ',hostfwd=tcp::%s-:%s'
    fwd_list = [fmt % tuple(ports.split(',')) for ports in args.host_forward]
    print(fwd_list)
    return (
        '-net', 'nic,model=virtio', '-net', 'user%s' % ''.join(fwd_list)
    )


def tap_param(args):
    return (
        '-netdev','tap,id=netdev0',
        '-device', 'virtio-net,netdev=netdev0'
    )

def bridge_param(args):
    s = []
    helper = '/usr/lib/qemu/qemu-bridge-helper'
    for i, brname in enumerate(args.bridges):
        s.extend((
            '-netdev',
            'bridge,id=brdev%d,br=%s,helper=%s' % (i, brname, helper),
            '-device', 'virtio-net,netdev=brdev%d' % i
        ))
    return s

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


def usb_param(args):
    return (
        '-usb','-device', 'usb-ehci,id=ehci',
        '-device',
        'usb-host,hostbus=%d,hostaddr=%d' % (args.usb[0], args.usb[1])
    )


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

    for drive in args.drive:
        cmd += drive_image_param(drive)

    if args.net_user:
        cmd += net_user_param(args)

    if args.tap:
        cmd += tap_param(args)

    if args.cdrom:
        cmd += ('-cdrom', args.cdrom)

    if args.sound:
        cmd += ('-soundhw', args.sound)

    if args.kernel:
        cmd += kernel_param(args)

    if args.initrd:
        cmd += ('-initrd', args.initrd)

    if args.boot or args.menu:
        param = []
        if args.boot:
            param += [args.boot]
        if args.menu:
            param += ['menu=on']
        cmd += ('-boot', ','.join(param))

    if args.gdb:
        cmd += ('-gdb', args.gdb)

    if args.serial:
        cmd += ('-serial', args.serial)

    if args.monitor:
        cmd += ('-monitor', args.monitor)

    if args.vnc is not None:
        cmd += ('-vnc', ':%s' %args.vnc)

    if args.usb:
        cmd += usb_param(args)

    if args.bridges:
        cmd += bridge_param(args)

    for arg in args.additional:
        cmd += arg

    return cmd


def start():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='A tool for generating QEMU comand lines.')
    parser.add_argument('--qemu', default=DEFAULT_QEMU, help=OPT_QEMU_HELP)
    parser.add_argument('-s', '--smp', type=int, metavar='N', help=OPT_SMP_HELP)
    parser.add_argument('-A', '--no-accel', action='store_true',
                        help='disable accelaration such KVM')
    parser.add_argument('-m', '--memory', type=int, default=DEFAULT_MEM_SIZE,
                        metavar='M', help=OPT_MEMORY_HELP)
    parser.add_argument('-d', '--drive', nargs='+', action='append',
                        default=[],
                        metavar=('FILE', 'OPT'), help=OPT_DRIVE_HELP)
    parser.add_argument('-u', '--net-user', action='store_true',
                        help=OPT_NET_USER_HELP)
    parser.add_argument('-f', '--host-forward', action='append', default=[],
                        metavar='PORTS',
                        help=OPT_HOST_FWD_HELP)
    parser.add_argument('-t', '--tap', action='store_true', help=OPT_TAP_HELP)
    parser.add_argument('-B', '--bridges', action='append', metavar='BR',
                        help=OPT_BRIDGES_HELP)
    # This default path is for Ubuntu
    parser.add_argument('-H', '--bridge-helper',
                        default='/usr/lib/qemu/qemu-bridge-helper',
                        metavar='HELPER', help=OPT_BRIDGE_HELPER_HELP)
    parser.add_argument('-c', '--cdrom', metavar='FILE',
                        help='add a CD-ROM drive with an ISO image file')
    parser.add_argument('-a', '--sound', type=str, nargs='?', default=None,
                        const=DEFAULT_SOUND_DEV, metavar='DEVICE',
                        help=OPT_SOUND_HELP)
    parser.add_argument('-k', '--kernel', nargs='+',
                        metavar=('vmlinuz', 'cmdline'),
                        help='boot Linux kernel directory')
    parser.add_argument('-i', '--initrd', metavar='FILE', help=OPT_INITRD_HELP)
    parser.add_argument('-n', '--nographic', action='store_true',
                        help=OPT_NOGRAPHIC_HELP)
    parser.add_argument('-b', '--boot', metavar='DRIVE', help=OPT_BOOT_HELP)
    parser.add_argument('--menu', action='store_true', help=OPT_MENU_HELP)
    parser.add_argument('-M', '--monitor', nargs='?', metavar='DEV',
                        const=DEFAULT_MONITOR_DEV, help=OPT_MONITOR_HELP)
    parser.add_argument('-g', '--gdb', metavar='PORT',
                        nargs='?', const=DEFAULT_GDB_PORT, help=OPT_GDB_HELP)
    parser.add_argument('-S', '--serial', choices=['mon:stdio', 'pts'],
                        help='add a serial port')
    parser.add_argument('-vnc', type=int, metavar='N', help=OPT_VNC_HELP)
    parser.add_argument('-usb', nargs=2, type=int, metavar=('BUS', 'DEV'),
                        help=OPT_USB_HELP)

    parser.add_argument('-e', '--execute', action='store_true',
                        help=OPT_EXEC_HELP)

    parser.add_argument('additional', nargs='*', help=OPT_ADDITIONAL_HELP)

    args = parser.parse_args()
    cmd = generate(args)
    print(cmd)
    if args.execute:
        subprocess.run(cmd.get_arguments())


if __name__ == '__main__':
    start()
