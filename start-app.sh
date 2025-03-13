#!/bin/bash
socat PTY,link=${DEVICE:-/dev/ttyUSB0},raw,echo=0 PTY,link=/tmp/virtual_uart2,raw,echo=0 &
python -m app.device.device &
python -m app.main "$@"
