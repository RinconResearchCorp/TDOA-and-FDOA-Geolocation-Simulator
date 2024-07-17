# How to install opensky api dependencies

* run `pip install -e opensky-api/`

# How to install and set up postgreSQL

* First set up psql in your machines terminal:
* install postgreSQL: sudo dnf install postgresql-server postgresql-contrib
* initialize the psql database cluster: sudo postgresql-setup --initdb
* start psql: sudo systemctl start postgresql
* enable psql: sudo systemctl enable postgresql
* create a database and user: sudo -u postgres psql

* now you're in postgres, do the following:
* CREATE DATABASE adsb_data;
* CREATE USER \<username\> WITH PASSWORD '\<password\>';
* ALTER ROLE \<username\> SET client_encoding TO 'utf8';
* ALTER ROLE \<username\> SET default_transaction_isolation TO 'read committed';
* ALTER ROLE \<username\> SET timezone TO 'UTC';
* GRANT ALL PRIVILEGES ON DATABASE <database_name> TO \<username\>;
* \c adsb_data eheidrich
* \conninfo (gets the info for the url to use with sqlalchemy)
* \q (quits postgres in terminal)

If you get something like peer authentication failed, do the following:

* `sudo vim /var/lib/pgsql/data/pg_hba.conf`
* scroll down and look for uncommented lines with a format like:
* * "local   all             postgres                                peer"
* press i to enter insert mode, and replace all 'peer' with 'md5'
* press escape to exit insert mode, then :wq to save and quit
* `sudo systemctl restart postgresql` to restart the psql server
* psql -d adsb_data -U \<username\> -W

Upon which you'll be prompted by your terminal to enter your postgres password. 
