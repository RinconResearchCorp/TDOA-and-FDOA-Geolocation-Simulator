from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_stuff.models import Flight
from data_stuff.settings import create_url

max_count = 100 

url = create_url()
engine = create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()

def create_flight(icao24, latitude, longitude, time_position, on_ground):
	query = db.query(Flight).filter_by(icao24 = icao24).first()

	if on_ground:
		if query:
			delete_flight(icao24)
		return
	
	if latitude == None or longitude == None or time_position == None:
		return

	if query:
		#flight in table already
		update_flight(icao24=icao24, latitude=latitude, longitude=longitude, time_position=time_position)

	else:
		count = db.query(Flight).count()
		if count > max_count:
			return
		new_flight = Flight(icao24=icao24, latitude=latitude, longitude=longitude, time_position=time_position, on_ground=on_ground)
		db.add(new_flight)
		db.commit()

def update_flight(icao24, latitude, longitude, time_position):
	flight = db.query(Flight).filter_by(icao24 = icao24).first()
	if flight:
		curr_lat = flight.latitude.split()
		curr_lon = flight.longitude.split()

		if len(curr_lat) == 10:
			flight.latitude = ','.join(curr_lat[2:] + [latitude])
		else:
			curr_lat.append(latitude)
			flight.latitude = ','.join(curr_lat)

		if len(curr_lon) == 10:
			flight.longitude = ','.join(curr_lon[2:] + [longitude])
		else:
			curr_lon.append(longitude)
			flight.longitude = ','.join(curr_lon)
		
		flight.time_position = time_position
		db.commit()
		

def delete_flight(icao24):
	flight = db.query(Flight).filter_by(icao24 = icao24).first()
	if flight:
		db.delete(flight)
		db.commit()

def read_flights():
	lats = db.query(Flight.latitude).all()
	longs = db.query(Flight.longitude).all()
	data = {'lat': [list(map(float, lat[0].split(','))) for lat in lats], 
		 	'lon': [list(map(float, lon[0].split(','))) for lon in longs]}

	return data