from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base 
from data_stuff.settings import create_url

Base = declarative_base()

def create_table():
	url = create_url()
	engine = create_engine(url)
	
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	
    