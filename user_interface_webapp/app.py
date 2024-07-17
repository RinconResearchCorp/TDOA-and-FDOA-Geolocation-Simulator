
import logging
import os
import requests
from dotenv import load_dotenv
from io import StringIO

from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np

from data_stuff.crud import read_flights
from data_stuff.database_utils import create_url

from doa_utils.simulator import simulate_doa

load_dotenv()

url = create_url()
engine = create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()

app = Flask(__name__, static_folder='static', template_folder='templates')
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/home', methods=['GET'])
def go_home():
    return render_template('index.html')

@app.route('/what', methods=['GET'])
def what():
    return render_template('what.html')

@app.route('/who', methods=['GET'])
def who():
    return render_template('who.html')

@app.route('/why', methods=['GET'])
def why():
    return render_template('why.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['fileUpload']
        if file:
            content = file.read().decode( 'utf-8' )
            data = StringIO(content)
            df = pd.read_csv(data, names=["ICAO", "LAT", "LON", "TIME"], skipinitialspace=True)
            df.sort_values(by="TIME", inplace=True)
            df.to_csv( 'data.csv', index=False )
            return redirect(url_for('batch'))
    return render_template('upload.html')

@app.route('/batch', methods=['GET'])
def batch():
    df = pd.read_csv('data.csv')
    data = df.to_json(orient='records')
    return render_template('batch_render.html', data=data)

@app.route('/live', methods=['GET'])
def live():
    return render_template('cesium_globe.html')

@app.route('/live-data', methods=['GET', 'POST'])
def live_data():
    data = read_flights()
    return jsonify(data)

@app.route('/2D-curve-rendering', methods=['GET'])
def curve_sim():
    return render_template('2D_rendering.html')

@app.route('/get-elevation', methods=["POST"])
def get_elevation():
    data = request.json
    lat, lon = data['latitude'], data['longitude']
    
    api_key = os.getenv( 'GOOGLE_API_KEY' )
    url = f'https://maps.googleapis.com/maps/api/elevation/json?locations={lat}%2C{lon}&key={api_key}'
    
    response = requests.get(url)
    elevation = response.json()['results'][0]['elevation']

    return jsonify({'elevation' : elevation})

@app.route('/run-simulation', methods=['POST'])
def simulate():
    data = request.get_json()
    emitter_pos = np.array([data['emitter']['latitude'], data['emitter']['longitude'], data['emitter']['altitude']])
    emitter_vel = np.array([data['emitter']['northVelocity'], data['emitter']['eastVelocity'], 0])
    receiver_positions = np.array([ [r['latitude'], r['longitude'], r['altitude']] for r in data['receivers']])

    caf_est_pos, caf_est_vel, true_est_pos, true_est_vel = simulate_doa(emitter_pos, emitter_vel, receiver_positions, cartesian=False)

    result = { 'caf_emitter' : { 'latitude' : caf_est_pos[0], 'longitude' : caf_est_pos[1], 'altitude' : caf_est_pos[2], 'northVelocity' : caf_est_vel[0], 'eastVelocity' : caf_est_vel[1] },
               'true_emitter' : { 'latitude' : true_est_pos[0], 'longitude' : true_est_pos[1], 'altitude' : true_est_pos[2], 'northVelocity' : true_est_vel[0], 'eastVelocity' : true_est_vel[1] }
              }#, 'posError' : pos_error, 'velError' : vel_error }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

