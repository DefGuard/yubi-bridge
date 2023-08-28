#!/bin/bash
/etc/init.d/pcscd restart > /dev/null
python3 -m yubi_bridge.main $@
