#!/usr/bin/env python3
import argparse
import sys
import subprocess

def get_addr(base_path, file_name):
    try:
        with open(f'{base_path}/{file_name}', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def get_original_module_path(name):
    proc = subprocess.run(['modinfo', name],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in proc.stdout.decode('utf8').splitlines():
        words = line.split()
        if words[0] == 'filename:':
            return words[1]


def get_latter_module_path(name, kernel_version):
    path = get_original_module_path(name)
    words = path.split('/')
    assert words[0:3] == ['', 'lib', 'modules']
    fixed_path = words[0:3]
    if kernel_version is None:
        kernel_version = words[4]
    fixed_path += [kernel_version]
    fixed_path += words[5:]
    return '/'.join(fixed_path)


def generate_line(module_base_dir, name, text_addr, data_addr, bss_addr, kernel_version):
    latter_module_path = get_latter_module_path(name, kernel_version)
    module_path = f'{module_base_dir}{latter_module_path}'
    s = f'add-symbol-file {module_path} {text_addr}'
    if data_addr is not None:
        s += f' -s .data {data_addr}'
    if bss_addr is not None:
        s += f' -s .bss {bss_addr}'
    return s


def generate(args):
    mod_names = map(lambda l: l.split()[0], args.infile.readlines()[1:])
    for name in mod_names:
        base_path = f'/sys/module/{name}/sections'
        kwargs = {
            'text_addr': get_addr(base_path, '.text'),
            'data_addr': get_addr(base_path, '.data'),
            'bss_addr' : get_addr(base_path, '.bss'),
            'module_base_dir': args.module_base_dir,
            'name': name,
            'kernel_version': args.kernel_version,
        }
        if kwargs['text_addr'] is None:
            continue
        yield generate_line(**kwargs)


def main():
    parser = argparse.ArgumentParser(
        description='A tool for generating add-symbol-file line of GDB.')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('-d', '--module-base-dir', default='/usr/lib/debug')
    parser.add_argument('-k', '--kernel-version')
    args = parser.parse_args()
    cmd_array = generate(args)
    for c in cmd_array:
        print(c)

if __name__ == '__main__':
    main()
