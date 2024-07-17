import csv
import plotly.graph_objects as go

def parse_icao_lat_lon(file_path):
    airport_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row in CSV file
        for row in reader:
            country_code, region_name, iata, icao, airport, latitude, longitude = row
            # append latitude, longitude, ICAO, and IATA to airport_data list
            airport_data.append((float(latitude), float(longitude), icao, iata, airport))
    return airport_data

file_path = "flight_data/iata-icao-lat-lon.csv"
airport_data = parse_icao_lat_lon(file_path)

# Unpack data from airport_data list
latitudes, longitudes, icaos, iatas, airport_names = zip(*airport_data)

# Create text for each data point containing all information
texts = [f"ICAO: {icao}<br>IATA: {iata}<br>Airport Name: {name}<br>Latitude: {lat}<br>Longitude: {lon}" 
         for lat, lon, icao, iata, name in zip(latitudes, longitudes, icaos, iatas, airport_names)]

fig = go.Figure()

# Scattergeo for airport data
fig.add_trace(go.Scattergeo(
    lat=latitudes,
    lon=longitudes,
    text=texts,
    mode='markers',
    marker=dict(
        symbol='hash-open',
        color='maroon',
        size=10
    )
))

fig.update_geos(projection_type="orthographic")
fig.update_layout(width=800, height=800, margin={"r":0,"t":0,"l":0,"b":0})

fig.show()

