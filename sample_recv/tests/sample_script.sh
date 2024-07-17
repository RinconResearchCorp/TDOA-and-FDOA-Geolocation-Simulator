#!/bin/bash

bladeRF-cli -p 1>/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "No bladeRF devices connected." >&2
    exit 1
fi


bladeRF-cli -e 'set samplerate rx1 2MHz; set frequency rx1 1090MHz; rx config file=rx_20s.sc16q11 format=bin n=0; rx start; rx; rx wait 40s'