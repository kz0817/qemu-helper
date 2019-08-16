# Brief

This program generates lines to read debug symbol files of Linux kernel
modules to GDB -- i.e. add-symbol-files command line.
Because a loaded address of a kernel module varies, the command line
has to include the address, which can be obtained from /sys/


# Example to use (for Ubuntu)

First generate GDB's command list file like.

    lsmod | add-debug-sym-line.py -k 4.15.0-54-generic/kernel > add.cmd

The above command should be executed on the target machine, because it reads
/sys and run lsmod.

Then execute the command generated above on GDB.

    (gdb) source add.cmd

