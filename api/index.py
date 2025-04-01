from flask import Flask, jsonify
from flask_socketio import SocketIO
import threading
import time
import random
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Define disaster types with thresholds for alerts
DISASTER_TYPES = {
    'earthquake': {'unit': 'Richter', 'min': 0, 'max': 10, 'alert_threshold': 6.0},
    'temperature': {'unit': '°C', 'min': -20, 'max': 50, 'alert_threshold': 40},
    'wind_speed': {'unit': 'km/h', 'min': 0, 'max': 200, 'alert_threshold': 120},
    'rainfall': {'unit': 'mm', 'min': 0, 'max': 300, 'alert_threshold': 200},
    'air_pressure': {'unit': 'hPa', 'min': 900, 'max': 1100, 'alert_threshold': 950}
}

LOCATIONS = ['A', 'B', 'C', 'D', 'E']
active_threads = {}
alerts = []  # Store active alerts

# Function to generate random disaster data with occasional spikes
def generate_disaster_data(location):
    while True:
        if location not in active_threads:
            break
            
        data = {
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'readings': {}
        }
        
        # Generate readings with occasional spikes
        for disaster, params in DISASTER_TYPES.items():
            # 5% chance of generating a spike
            if random.random() < 0.05:  # 5% probability
                reading = round(random.uniform(params['alert_threshold'], params['max']), 2)
                # Generate alert when threshold is exceeded
                if reading >= params['alert_threshold']:
                    alert = {
                        'location': location,
                        'disaster_type': disaster,
                        'value': reading,
                        'unit': params['unit'],
                        'timestamp': datetime.now().isoformat()
                    }
                    alerts.append(alert)
            else:
                reading = round(random.uniform(params['min'], params['alert_threshold'] - 0.1), 2)
                
            data['readings'][disaster] = {
                'value': reading,
                'unit': params['unit']
            }
            
        socketio.emit('disaster_data', data)
        time.sleep(1)

# Start threads for each location
def start_location_threads():
    for location in LOCATIONS:
        thread = threading.Thread(target=generate_disaster_data, args=(location,))
        thread.daemon = True
        active_threads[location] = thread
        thread.start()

# API Routes
@app.route('/')
def home():
    return 'Smart Security System API is running!'

@app.route('/about')
def about():
    return 'Smart Security System API - Monitoring natural disasters'

# New API endpoint for alerts
@app.route('/api/alerts')
def get_alerts():
    global alerts
    current_alerts = alerts.copy()
    alerts = []  # Clear alerts after fetching
    return jsonify({
        'status': 'success',
        'alerts': current_alerts
    })

# New API endpoint for current readings
@app.route('/api/readings')
def get_readings():
    # This would typically fetch from a stored state, but for simplicity,
    # we'll generate a single set of readings
    readings = {}
    for location in LOCATIONS:
        readings[location] = {}
        for disaster, params in DISASTER_TYPES.items():
            reading = round(random.uniform(params['min'], params['max']), 2)
            readings[location][disaster] = {
                'value': reading,
                'unit': params['unit']
            }
    return jsonify({
        'status': 'success',
        'readings': readings,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    start_location_threads()
