from sqlalchemy.engine import URL

def create_url():
    url = URL.create(
        drivername="postgresql",
        username="kellyjbelly",
        password="hello",
        host="/var/run/postgresql/",
        database="adsb_data"
    )

    return url