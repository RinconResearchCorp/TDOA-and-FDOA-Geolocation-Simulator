Folder for receiving/demodulating ADS-B signals using a BladeRF

## REQUIREMENTS
"planes" database in Postgres-- update user and pass in ```recv_hex.py```

Appropriate ADS-B FPGA image installed on BladeRF [link to images](https://www.nuand.com/fpga_images/)

# Instructions for file receive/decode
Comment/uncomment appropriate lines in ```bladeRF_adsb.c``` to write to file and not send through port

Make and run bladeRF_adsb to start collecting

Stop collecting by Ctrl-C

Hex should be written to output.txt

Run ```recv_hex.py --file "output.txt"```

```positions.txt``` should now contain data in format ICAO, latitude, longitude, timestamp
