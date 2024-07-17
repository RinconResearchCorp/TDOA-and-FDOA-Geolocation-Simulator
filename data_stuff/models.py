from sqlalchemy import Column, Integer, String, Boolean
from data_stuff.database_utils import Base

class Flight(Base):
	__tablename__ = 'flights'
	icao24 = Column(String, primary_key=True)
	latitude = Column(String)
	longitude = Column(String)
	time_position = Column(Integer)
	on_ground = Column(Boolean)
	


	