# How to chagne caps and win keys to ctrl.

On debian based distro, place the following line in /etc/default/keyboard.

    XKBOPTIONS="ctrl:nocaps,altwin:ctrl_win"

Then run

    setupcon -k --force --save
