#!/bin/bash
/etc/init.d/pcscd restart > /dev/null
cd yubi-bridge
python3 main.py $@
