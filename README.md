# Flight Tracker Simulator
Rincon 2024 Intern Project
Kelly Fisher, Elsa Heidrich, Elizabeth Hong & Logan Barnhart

# Installing requirements

* `pip install -r requirements.txt`
* Generate a [Google Elevations API key](https://developers.google.com/maps/documentation/elevation/start) and store it in a file called `.env` in the root directory of the project. The file should contain the following text: `GOOGLE_API_KEY=\<your_api_key_here\>`  -  Google should award $300 in free credits if you're signing up for the first time, so this shouldn't cost money. 

# How to run the application:
* To run the web application, run `python -m user_interface_webapp.app`

# File Descriptions:
```
data_stuff/ # contains database logic for storing live data from opensky api if activated
├── crud.py             # create read update delete functions for database
├── data_collector.py   # collects live data from opensky api
├── database_utils.py   # utilities that are used frequently
├── models.py           # table declaration
├── settings.py         # database connection information
doa_utils/              # contains necessary files for simulating + solving T/FDOA
├── caf.py              # CAF implementations
├── signal_generator.py # signal generator
├── simulator.py        # uses all tools to simulate T/FDOA
├── solver.py           # solver logic to change solution method
sample_recv/            # contains necessary files for receiving and decoding ADS-B signals
├── bladeRF_adsb.c      # C file that receives hex demodulated ads-b signals and either writes to file or sends in socket through port 30001 **requires ADS-B FPGA image to be flashed onto BladeRF
├── Makefile            # Makes the above C file
├── positions.txt       # Test batch file to use on the /upload endpoint 
├── recv_hex.py         # ADS-B decoder that takes in either file input or receives in port 30001
user_interface_webapp/  # contains all frontend, server, and backend logic 
├──static
│   ├── images          # necessary images
│   ├── json            # json files for globe details
│   ├── models          # 3d models for globe
│   ├── scripts         # javascript files for frontent
│   ├── styles          # css stylings
│   ├── video           # video files
├── templates           # html templates
├── app.py              # main file to run the web application  
```


# How to collect data from opensky api for /live-data endpoint

Note that as of now, this is no longer necessary for the webapp to run, but one could connect this to the batch globe rendering with relative ease to visualize live flights around the world

* `pip install -e opensky-api/`
* Follow postgres install instructions in `/flight_data/README.md`
* Update the user and password information in `data_stuff/settings.py` to match your postgres installation
* Run `python -m data_stuff.data_collector &` in the background to begin filling your database with live flight data
* Sending a get request to the /live-data endpoint should yield a json file containing the updated state of the table. 
