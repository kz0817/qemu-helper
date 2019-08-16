# Brief

This program generates lines to read debug symbol files of Linux kernel
modules to GDB -- i.e. add-symbol-files command line.
Because a loaded address of a kernel module varies, the command line
has to include the address, which can be obtained from /sys/


# Example to use (for Ubuntu)

First generate GDB's commands on the target machine like

    lsmod | sudo ./add-debug-sym-line.py > add.cmd

or from remote machine via SSH.

    ssh target sh -c "lsmod | sudo qemu-helper/kernel-debug-utils/add-debug-sym-line.py" > add.cmd


Then execute the command generated above on GDB.

    (gdb) source add.cmd

