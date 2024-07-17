import requests
import numpy as np
from plotly import graph_objects as go
import csv

import logging

logger = logging.getLogger(__name__)

def render_live_plot(data):
    """
    Renders globe for given data:

    args:
        data (dict): dictionary with latitude and longitude info and scattergeo kwargs
            each list should contain a list with the lat/long info for one line segment. 
        e.g.: {'lat' : [[1, 2, 3], ...] 'long' : [[1, 2, 3], ...], **kwargs}
    
    returns:
        html for plotly globe with template
    """
    fig = go.Figure()
    
    # fig = plot_airport_data(fig)

    fig = plot_state_data(fig)

    fig = plot_flight_data(data, fig)

    fig = fig_style(fig)
    
    fig_json = fig.to_json()
    return fig_json

def render_tdoa_plot(data):    
    emitter_lat, emitter_lon = data['emitter']
    emitter_alt = data['em_altitude']
    receiver_lats, receiver_lons = data['receivers']
    receiver_altitudes = data['rec_altitudes']

    fig = go.Figure()

    fig = plot_state_data(fig)

    fig = plot_airport_data(fig)

    fig = plot_emitter(fig, emitter_lat, emitter_lon, emitter_alt)

    fig = plot_receivers(fig, receiver_lats, receiver_lons, receiver_altitudes)

    fig = fig_style(fig)

    fig_json = fig.to_json()

    return fig_json

def plot_emitter(fig, lat, lon, alt):    
    marker = dict(
        size = 20,
        color = '#ffc300',
        symbol = 'asterisk-open',
    )
    
    if alt[0][0] != '':
        label = f'Altitude: {int(alt[0][0])} m.'
    

        fig.add_trace(go.Scattergeo(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=marker,
                showlegend=False,
                text=label,
            ))
        
    else:
        fig.add_trace(go.Scattergeo(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=marker,
            showlegend=False,
        ))
    
    return fig

def plot_receivers(fig, lat, lon, alts):
    marker = dict(
        size = 20,
        color = '#ffc300',
        symbol = 'circle-open-dot',
    )

    labels = [f'Altitude: {alt:.0f}' for alt in alts]

    fig.add_trace(go.Scattergeo(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=marker,
            showlegend=False,
            text=labels,
        ))
    
    return fig

def plot_airport_data(fig):
    file_path = "flight_data/iata-icao-lat-lon.csv"
    airport_data = parse_icao_lat_lon(file_path)

    # Unpack data from airport_data list
    latitudes, longitudes, icaos, iatas, airport_names = zip(*airport_data)

    # Create text for each data point containing all information
    texts = [f"ICAO: {icao}<br>IATA: {iata}<br>Airport Name: {name}<br>Latitude: {lat}<br>Longitude: {lon}" 
            for lat, lon, icao, iata, name in zip(latitudes, longitudes, icaos, iatas, airport_names)]

    # Scattergeo for airport data
    fig.add_trace(go.Scattergeo(
        lat=latitudes,
        lon=longitudes,
        text=texts,
        mode='markers',
        marker=dict(
            symbol='hash-open',
            color='#47476c',
            size=10
        )
    ))

    return fig

def plot_state_data(fig):
    states_geojson = requests.get(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_1_states_provinces_lines.geojson"
).json()

    fig = fig.add_trace(go.Scattergeo(
            lat=[
                v
                for sub in [
                    np.array(f["geometry"]["coordinates"])[:, 1].tolist() + [None]
                    for f in states_geojson["features"]
                ]
                for v in sub
            ],
            lon=[
                v
                for sub in [
                    np.array(f["geometry"]["coordinates"])[:, 0].tolist() + [None]
                    for f in states_geojson["features"]
                ]
                for v in sub
            ],
            line=dict(
                width=1,
                color='#cdd6f4',
                ),
            mode="lines",
            showlegend=False,
            hoverinfo="none",
        )
    )

    return fig


def plot_flight_data(data, fig):
    latitude = data['lat']
    longitude = data['lon']

    # fig = go.Figure()

    #Line customization    
    marker = dict(
        size = 10,
        color = '#ffc300',
    )
    line = dict(
        width = 1,
        color = '#ffc300'
    )

    for lat, lon in zip(latitude, longitude):
        # plot lines
        fig.add_trace(go.Scattergeo(
            lat=lat,
            lon=lon,
            mode='lines',
            line=line,
            showlegend=False,
            hoverinfo= 'none',
        ))

        if len(lat) == 1:
            marker['symbol'] = 'triangle-up'
        else:        
            bearing = calculate_bearing(lat, lon)
            direction = triangle_orientation(bearing)
            marker['symbol'] = 'triangle' + direction


        fig.add_trace(go.Scattergeo(
            lat=[lat[-1]],
            lon=[lon[-1]],
            mode='markers',
            marker=marker,
            showlegend=False,
        ))
    
    return fig

def plot_error(fig, lat, lon, r, units='mi'):
    lat_rad, lon_rad = np.radians(lat), np.radians(lon)
    num_pts = 50
    
    if units == 'mi':
        R = 3959
    if units == 'km':
        R=6371

    circle_angles = np.linspace(0, 2*np.pi, num_pts)

    circle_lats = np.arcsin(np.sin(lat_rad) * np.cos(r/R) + np.cos(lat_rad) * np.sin(r/R) * np.cos(circle_angles))
    circle_lons = lon_rad + np.arctan2(np.sin(circle_angles) * np.sin(r/R)* np.cos(lat_rad), np.cos(r/R) - np.sin(lat_rad) * np.sin(circle_lats))
        
    circle_lats = np.degrees(circle_lats)
    circle_lons = np.degrees(circle_lons)

    fig.add_trace( go.Scattergeo(
        lat=circle_lats,
        lon=circle_lons,
        mode='lines',
        fill='toself',
        fillcolor= 'rgba(255, 17, 17, 0.2)',
        line = dict(color='rgba(255, 17, 17, 0.2)')
    ))

    return fig



def calculate_bearing(lat, lon):
    lat1 = lat[-1]
    lat2 = lat[-2]
    lon1 = lon[-1]
    lon2 = lon[-2]

    lat1, lat2, lon1, lon2 = map(np.radians, [lat1, lat2, lon1, lon2])

    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dlon))

    initial_bearing = np.degrees(np.arctan2(x, y))

    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def triangle_orientation(bearing):
    if 335.7 <= bearing < 22.5:
        return '-down'
    elif 22.5 <= bearing < 67.5:
        return '-sw'
    elif 67.5 <= bearing < 112.5:
        return '-left'
    elif 112.5 <= bearing < 157.5:
        return '-nw'
    elif 157.5 <= bearing < 202.5:
        return '-up'
    elif 202.5 <= bearing < 247.5:
        return '-ne'
    elif 247.5 <= bearing < 292.5:
        return '-right'
    elif 292.5 <= bearing < 335.7:
        return '-se'
    else:
        return '-up' # default
    
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

def fig_style(fig):
    fig.update_geos(
        projection_type="orthographic",
        projection_scale=.9,
    )
    fig.update_layout(width=750, 
                      height=750, 
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant',
                      autosize=True,
                      geo=dict(
                          projection_type='orthographic',
                          showland=True,
                          landcolor='#1e1e2e',
                          showocean=True,
                          oceancolor='#cdd6f4',
                          showlakes=True,
                          lakecolor='#cdd6f4',
                          showcountries=True,
                          countrycolor='#cdd6f4',
                          bgcolor='#1e1e2e',
                        #   showstates=True
                        ),
                      showlegend=False
                      )
    
    return fig