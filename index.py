from flask import Flask, render_template, request
import requests
import time

app = Flask(__name__)

# Simple in-memory cache
cache = {}
CACHE_EXPIRY = 300  # Cache results for 5 minutes

@app.route('/')
def home():
    return render_template('index.html')

# Handle form submission and display solar power estimation.
@app.route('/estimate', methods=['POST'])
def estimate():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    declination = request.form['declination']
    azimuth = request.form['azimuth']

    cache_key = f"{latitude}_{longitude}_{declination}_{azimuth}"
    
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_EXPIRY:
        latest_wattage = cache[cache_key]['wattage']
        return render_template('result.html', data=f"{latest_wattage} watts (cached)")

    # Forecast.Solar API 
    API_URL = f"https://api.forecast.solar/estimate/watts/{latitude}/{longitude}/{declination}/{azimuth}/1.0"

    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Prints error if the request fails
        
        data = response.json()

        if 'result' not in data or not data['result']:
            return render_template('result.html', data="No data available")

        power_data = data['result']
        latest_timestamp = max(power_data.keys())  # Find the most recent time
        latest_wattage = power_data[latest_timestamp]  # Get wattage for that time
        
        # Stores in temporary cache
        cache[cache_key] = {'timestamp': time.time(), 'wattage': latest_wattage}

        return render_template('result.html', data=f"{latest_wattage} watts")

    except requests.exceptions.RequestException as e:
        return render_template('result.html', data=f"Error fetching data: {e}")

if __name__ == '__main__':
    app.run(debug=True)