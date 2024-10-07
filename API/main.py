from flask import Flask, request, jsonify
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import csv
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

def load_api_mobile_keys():
    with open("D:\\Documentos\\NASA SPACE APPS 2024\\API\\api_mobile_request_keys.txt", "r") as file: #change to your own directory
        keys = [line.strip() for line in file.readlines()]  # Read each line and remove whitespace
    return set(keys)  # Use a set for faster search and to avoid duplicates

API_KEYS = load_api_mobile_keys()

def verify_api_key(api_key):
    return api_key in API_KEYS

ideal_crops = open("D:\\Documentos\\NASA SPACE APPS 2024\\API\\idealConditionsForCrops.csv", "r", encoding="utf-8")
df_idealcrops = pd.read_csv(ideal_crops)

DB_devices = "devices_information.csv"

usrmeteomatics = "sanchez_fernando"
passmeteomatics = "BF9d8pI27r"
with open("D:\\Documentos\\NASA SPACE APPS 2024\\API\\openWeatherKey.txt", "r") as key:
    openWeatherKey = key.read()

today = datetime.now().strftime("%Y-%m-%d")

def openMeteo_dataset(latitude, longitude):  # Future information
    parameters_openmeteo = "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,evapotranspiration,soil_temperature_0cm,soil_moisture_0_to_1cm,wind_speed_10m,pressure_msl"
    url_openmeteo = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly={parameters_openmeteo}&start={today}"
    response_openmeteo = requests.get(url_openmeteo)
    if response_openmeteo.status_code == 200:
        data_openmeteo = response_openmeteo.json()
    else:
        print("No dataset: Meteo-matics")
    
    df_openmeteo = pd.DataFrame(data_openmeteo['hourly'])
    return df_openmeteo

def meteomatics_dataset(latitude, longitude):  # Special information
    agriculture_parameters_meteomatics = [
        "soil_moisture_index_-15cm:idx",  # Soil moisture index
        "volumetric_soil_water_-15cm:m3m3",  # Volumetric soil water content
        "drought_index:idx",  # Drought index
        "vapor_pressure_deficit_2m:hPa",  # Vapor pressure deficit
        "forest_fire_warning:idx",  # Forest fire warning
        "frost_warning:idx"  # Frost warning
    ]
    parameters_meteomatics = ",".join(agriculture_parameters_meteomatics)

    url_meteomatics = f"https://api.meteomatics.com/{today}T00:00:00ZP5D:PT12H/{parameters_meteomatics}/{latitude},{longitude}/html"

    response_meteomatics = requests.get(url_meteomatics, auth=(usrmeteomatics, passmeteomatics))

    # Meteomatics data
    soup_meteomatics = BeautifulSoup(response_meteomatics.text, 'html.parser')
    csv_content_meteomatics = soup_meteomatics.find('pre', id='csv').text
    csv_buffer = StringIO(csv_content_meteomatics)
    df_meteomatics = pd.read_csv(csv_buffer, sep=';')
    
    return df_meteomatics

def openWeather_dataset(latitude, longitude):  # Real-time information
    url_OpenWeather = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={openWeatherKey}"
    
    response_openWeather = requests.get(url_OpenWeather)
    
    if response_openWeather.status_code == 200:
        data_openWeather = response_openWeather.json()
        main_data = data_openWeather['main']
        weather_data = {
            'location': data_openWeather['name'],
            'temperature': main_data['temp'],
            'feels_like': main_data['feels_like'],
            'humidity': main_data['humidity'],
            'pressure': main_data['pressure'],
            'wind_speed': data_openWeather['wind']['speed'],
            'weather_main': data_openWeather['weather'][0]['main'],
            'weather_description': data_openWeather['weather'][0]['description'],
        }
    else:
        print("No dataset: Open Weather")
    
    df_openWeather = pd.DataFrame([weather_data])
    
    return df_openWeather

def evaluate_agricultural_conditions(df_combined, df_ideal):
    results = []

    for index, row in df_combined.iterrows():
        recommendation = {}

        for _, crop in df_ideal.iterrows():
            # Compare current values with ideal ones
            crop_name = crop['Crop']
            current_temp = row['temperature_2m']
            ideal_temp = crop['temperature_2m (°C)']
            current_humidity = row['relative_humidity_2m']
            ideal_humidity = crop['relative_humidity_2m (%)']
            current_precipitation = row['precipitation']
            ideal_precipitation = crop['precipitation (mm)']
            current_soil_moisture = row['soil_moisture_0_to_1cm']
            ideal_soil_moisture = crop['soil_moisture_0_to_1cm (m3/m3)']
            current_soil_temperature = row['soil_temperature_0cm']
            ideal_soil_temperature = crop['soil_temperature_0cm (°C)']
            current_evapotranspiration = row['evapotranspiration']
            ideal_evapotranspiration = crop['evapotranspiration (mm)'].replace('mm/day', '').strip()
            current_soil_moisture_index = row['soil_moisture_index_-15cm:idx']
            ideal_soil_moisture_index = crop['soil_moisture_index_-15cm (idx)']
            current_volumetric_soil_water = row['volumetric_soil_water_-15cm:m3m3']
            ideal_volumetric_soil_water = crop['volumetric_soil_water_-15cm (m3/m3)']
            current_drought_index = row['drought_index:idx']
            ideal_drought_index = crop['drought_index (idx)']
            current_pressure = row['pressure_msl']
            ideal_pressure = crop['pressure_msl (hPa)']
            current_vapor_pressure_deficit = row['vapor_pressure_deficit_2m:hPa']
            ideal_vapor_pressure_deficit = crop['vapor_pressure_deficit_2m (hPa)']

            # List to store out-of-range conditions
            out_of_range = []

            # Evaluate temperature
            temp_min, temp_max = map(float, ideal_temp.split('-'))
            temp_ok = temp_min <= current_temp <= temp_max
            if not temp_ok:
                out_of_range.append(f'Temperature: {current_temp} out of range {temp_min}-{temp_max}°C')

            # Evaluate humidity
            humidity_min, humidity_max = map(float, ideal_humidity.split('-'))
            humidity_ok = humidity_min <= current_humidity <= humidity_max
            if not humidity_ok:
                out_of_range.append(f'Humidity: {current_humidity} out of range {humidity_min}-{humidity_max}%')

            # Evaluate precipitation
            precipitation_ok = False
            if "total" in ideal_precipitation:
                precipitation_ok = True
            elif '-' in ideal_precipitation:
                try:
                    precipitation_min, precipitation_max = map(float, ideal_precipitation.split(' ')[0].split('-'))
                    precipitation_ok = precipitation_min <= current_precipitation <= precipitation_max
                except ValueError:
                    precipitation_ok = False
            else:
                try:
                    precipitation_value = float(ideal_precipitation.split(' ')[0])
                    precipitation_ok = precipitation_value <= current_precipitation
                except ValueError:
                    precipitation_ok = False

            if not precipitation_ok:
                out_of_range.append('Precipitation: out of range')

            # Evaluate soil moisture
            soilMoisture_min, soilMoisture_max = map(float, ideal_soil_moisture.split('-'))
            soilMoisture_ok = soilMoisture_min <= current_soil_moisture <= soilMoisture_max
            if not soilMoisture_ok:
                out_of_range.append(f'Soil Moisture: {current_soil_moisture} out of range {soilMoisture_min}-{soilMoisture_max} m3/m3')

            # Evaluate soil temperature
            soilTemp_min, soilTemp_max = map(float, ideal_soil_temperature.split('-'))
            soilTemp_ok = soilTemp_min <= current_soil_temperature <= soilTemp_max
            if not soilTemp_ok:
                out_of_range.append(f'Soil Temperature: {current_soil_temperature} out of range {soilTemp_min}-{soilTemp_max}°C')

            # Evaluate evapotranspiration
            evapotranspiration_min, evapotranspiration_max = map(float, ideal_evapotranspiration.split('-'))
            evapotranspiration_ok = evapotranspiration_min <= current_evapotranspiration <= evapotranspiration_max
            if not evapotranspiration_ok:
                out_of_range.append(f'Evapotranspiration: {current_evapotranspiration} out of range {evapotranspiration_min}-{evapotranspiration_max} mm')

            # Evaluate soil moisture index
            soil_moisture_index_ok = False
            if ideal_soil_moisture_index.lower() == "high" or ideal_soil_moisture_index.lower() == "moderate-high":
                soil_moisture_index_ok = current_soil_moisture_index > 1.2
            elif ideal_soil_moisture_index.lower() == "moderate":
                soil_moisture_index_ok = 1.0 <= current_soil_moisture_index <= 1.2
            elif ideal_soil_moisture_index.lower() == "low":
                soil_moisture_index_ok = current_soil_moisture_index < 1.0

            if not soil_moisture_index_ok:
                out_of_range.append(f'Soil Moisture Index: {current_soil_moisture_index} not within ideal {ideal_soil_moisture_index}')

            # Evaluate volumetric soil water
            volumetric_soil_water_min, volumetric_soil_water_max = map(float, ideal_volumetric_soil_water.split('-'))
            volumetric_soil_water_ok = volumetric_soil_water_min <= current_volumetric_soil_water <= volumetric_soil_water_max
            if not volumetric_soil_water_ok:
                out_of_range.append(f'Volumetric Soil Water: {current_volumetric_soil_water} out of range {volumetric_soil_water_min}-{volumetric_soil_water_max} m3/m3')

            # Evaluate drought index
            drought_index_min, drought_index_max = map(int, ideal_drought_index.split('-'))
            drought_index_ok = drought_index_min <= current_drought_index <= drought_index_max
            if not drought_index_ok:
                out_of_range.append(f'Drought Index: {current_drought_index} out of range {drought_index_min}-{drought_index_max}')

            # Evaluate pressure
            pressure_min, pressure_max = map(int, ideal_pressure.split('-'))
            pressure_ok = pressure_min <= current_pressure <= pressure_max
            if not pressure_ok:
                out_of_range.append(f'Pressure: {current_pressure} out of range {pressure_min}-{pressure_max} hPa')

            # Evaluate vapor pressure deficit
            vapor_pressure_deficit_min, vapor_pressure_deficit_max = map(float, ideal_vapor_pressure_deficit.split('-'))
            vapor_pressure_deficit_ok = vapor_pressure_deficit_min <= current_vapor_pressure_deficit <= vapor_pressure_deficit_max
            if not vapor_pressure_deficit_ok:
                out_of_range.append(f'Vapor Pressure Deficit: {current_vapor_pressure_deficit} out of range {vapor_pressure_deficit_min}-{vapor_pressure_deficit_max} hPa')

            conditions = [
                temp_ok, humidity_ok, precipitation_ok, soilMoisture_ok,
                soilTemp_ok, evapotranspiration_ok, soil_moisture_index_ok,
                volumetric_soil_water_ok, drought_index_ok, pressure_ok,
                vapor_pressure_deficit_ok
            ]
            optimal_conditions = sum(conditions)

            # Generate recommendation
            if optimal_conditions == len(conditions):
                recommendation[crop_name] = 'Optimal conditions for planting'
            elif optimal_conditions >= 8:
                recommendation[crop_name] = f'Good conditions but consider some factors ({len(conditions) - optimal_conditions} out of the ideal range): {", ".join(out_of_range)}'
            else:
                recommendation[crop_name] = f'Unfavorable conditions ({len(conditions) - optimal_conditions} factors out of the ideal range): {", ".join(out_of_range)}'

        recommendation['datetime'] = row['datetime']
        results.append(recommendation)

    return pd.DataFrame(results)

def detect_weather_phenomena(df_combined):
    results = []

    for index, row in df_combined.iterrows():
        weather_alert = {
            'datetime': row['datetime'],
            'Phenomenon': 'Normal'  # Default
        }
        
        # Variables
        soil_moisture_index = row.get('soil_moisture_index_-15cm:idx', None)
        drought_index = row.get('drought_index:idx', None)
        vapor_pressure_deficit = row.get('vapor_pressure_deficit_2m:hPa', None)
        precipitation = row.get('precipitation', None)
        wind_speed = row.get('wind_speed_10m', None)
        pressure_msl = row.get('pressure_msl', None)
        relative_humidity = row.get('relative_humidity_2m', None)
        temperature = row.get('temperature_2m', None)
        
        # Evaluate weather phenomena
        if drought_index is not None and soil_moisture_index is not None:
            if drought_index > 3 and soil_moisture_index < 1:
                weather_alert['Phenomenon'] = 'Drought'

        if precipitation is not None and soil_moisture_index is not None:
            if precipitation > 50 and soil_moisture_index > 2:
                weather_alert['Phenomenon'] = 'Flood'

        if wind_speed is not None and precipitation is not None:
            if wind_speed > 50 and precipitation > 20:
                weather_alert['Phenomenon'] = 'Storm'

        if wind_speed is not None and pressure_msl is not None:
            if wind_speed > 100 and pressure_msl < 950:
                weather_alert['Phenomenon'] = 'Hurricane'

            elif wind_speed > 90 and pressure_msl < 970:
                weather_alert['Phenomenon'] = 'Tornado'

        if vapor_pressure_deficit is not None and relative_humidity is not None and temperature is not None:
            if vapor_pressure_deficit > 3 and relative_humidity < 20 and temperature > 35:
                weather_alert['Phenomenon'] = 'Wildfire'

        results.append(weather_alert)

    # Return the results as a DataFrame for easy export
    return pd.DataFrame(results)

def save_device_info_to_database(fixed_ip, serial_number, collection_date, modules):
    # Check if the file exists to know if it needs to write the header
    file_exists = os.path.isfile(DB_devices)

    # Open the file in append mode
    with open(DB_devices, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # If the file didn't exist, write the header
        if not file_exists:
            writer.writerow(['Fixed IP', 'Serial Number', 'Collection Date', 
                             'Module', 'Ambient Temperature', 'Atmospheric Pressure', 'pH', 'Soil Moisture'])

        # Write the data of each module in a new row
        for i, module in enumerate(modules, start=1):
            writer.writerow([fixed_ip, serial_number, collection_date, 
                             f'Module {i}', module['ambient_temperature'], module['atmospheric_pressure'], 
                             module['ph'], module['soil_moisture']])

# Endpoint crops and agricultural recommendations
@app.route('/cropshield/crops', methods=['GET'])
def json_recommendations():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    api_key = request.args.get('api_key')
    
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Access denied. Invalid or missing API Key."}), 403

    if not latitude or not longitude:
        return jsonify({"error": "Please provide latitude and longitude"}), 400
    
    # Convert latitude and longitude to float
    latitude = float(latitude)
    longitude = float(longitude)

    # Get datasets
    df_meteomatics = meteomatics_dataset(latitude, longitude)
    df_openMeteo = openMeteo_dataset(latitude, longitude)

    if df_meteomatics is None or df_openMeteo is None:
        return jsonify({"error": "Could not fetch data from the APIs"}), 501

    df_meteomatics['validdate'] = df_meteomatics['validdate'].str.replace('Z', '', regex=False)
    
    # Truncate seconds from 'validdate' column in df_meteomatics
    df_meteomatics['validdate'] = pd.to_datetime(df_meteomatics['validdate']).dt.floor('min')

    # Convert 'time' column in df_openMeteo to datetime format
    df_openMeteo['time'] = pd.to_datetime(df_openMeteo['time']).dt.floor('min')

    # Filter df_openMeteo rows matching dates and times from df_meteomatics
    filtered_openMeteo = df_openMeteo[df_openMeteo['time'].isin(df_meteomatics['validdate'])]

    # Ensure both dataframes have the date column with the same name
    df_meteomatics.rename(columns={'validdate': 'datetime'}, inplace=True)
    filtered_openMeteo = filtered_openMeteo.rename(columns={'time': 'datetime'})

    # Merge both dataframes using the datetime column
    combined_df = pd.merge(df_meteomatics, filtered_openMeteo, on='datetime', how='inner')

    # Evaluate agricultural conditions and weather phenomena
    df_results_agricultural = evaluate_agricultural_conditions(combined_df, df_idealcrops)
    df_results_meteorological = detect_weather_phenomena(combined_df)

    # Convert DataFrames to JSON
    agricultural_recommendations_json = df_results_agricultural.to_dict(orient='records')

    # Return JSON with both recommendations and alerts
    return jsonify({
        "agricultural_recommendations": agricultural_recommendations_json,
    })

@app.route('/cropshield/alerts', methods=['GET'])
def json_alerts():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    api_key = request.args.get('api_key')
    
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Access denied. Invalid or missing API Key."}), 403

    if not latitude or not longitude:
        return jsonify({"error": "Please provide latitude and longitude"}), 400
    
    # Convert latitude and longitude to float
    latitude = float(latitude)
    longitude = float(longitude)

    # Get datasets
    df_meteomatics = meteomatics_dataset(latitude, longitude)
    df_openMeteo = openMeteo_dataset(latitude, longitude)

    if df_meteomatics is None or df_openMeteo is None:
        return jsonify({"error": "Could not fetch data from the APIs"}), 501

    df_meteomatics['validdate'] = df_meteomatics['validdate'].str.replace('Z', '', regex=False)
    
    # Truncate seconds from 'validdate' column in df_meteomatics
    df_meteomatics['validdate'] = pd.to_datetime(df_meteomatics['validdate']).dt.floor('min')

    # Convert 'time' column in df_openMeteo to datetime format
    df_openMeteo['time'] = pd.to_datetime(df_openMeteo['time']).dt.floor('min')

    # Filter df_openMeteo rows matching dates and times from df_meteomatics
    filtered_openMeteo = df_openMeteo[df_openMeteo['time'].isin(df_meteomatics['validdate'])]

    # Ensure both dataframes have the date column with the same name
    df_meteomatics.rename(columns={'validdate': 'datetime'}, inplace=True)
    filtered_openMeteo = filtered_openMeteo.rename(columns={'time': 'datetime'})

    # Merge both dataframes using the datetime column
    combined_df = pd.merge(df_meteomatics, filtered_openMeteo, on='datetime', how='inner')

    # Evaluate weather phenomena
    df_results_meteorological = detect_weather_phenomena(combined_df)

    # Convert DataFrames to JSON
    weather_alerts_json = df_results_meteorological.to_dict(orient='records')

    # Return JSON with both recommendations and alerts
    return jsonify({
        "weather_alerts": weather_alerts_json
    })

@app.route('/cropshield/weather', methods=['GET'])
def json_weather():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    api_key = request.args.get('api_key')
    
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Access denied. Invalid or missing API Key."}), 403

    if not latitude or not longitude:
        return jsonify({"error": "Please provide latitude and longitude"}), 400
    
    # Convert latitude and longitude to float
    latitude = float(latitude)
    longitude = float(longitude)

    # Get datasets
    df_OpenWeather = openWeather_dataset(latitude, longitude)

    if df_OpenWeather is None:
        return jsonify({"error": "Could not fetch data from the APIs"}), 501

    # Convert DataFrames to JSON
    weather_json = df_OpenWeather.to_dict(orient='records')

    # Return JSON with both recommendations and alerts
    return jsonify({
        "weather_alerts": weather_json
    })

@app.route('/shieldroot/upload', methods=['POST'])
def data_shieldroot_collect():
    # Get JSON data from the request body
    data = request.json

    # Check if required data is present
    fixed_ip = data.get('fixed_ip')
    serial_number = data.get('serial_number')
    collection_date = data.get('collection_date')
    modules = data.get('modules')

    # Data validation
    if not fixed_ip or not serial_number or not collection_date or not modules:
        return jsonify({"error": "Missing required data. Please provide 'fixed_ip', 'serial_number', 'collection_date', and 'modules'."}), 400

    # Check that module information is valid
    for module in modules:
        if not all(key in module for key in ['ambient_temperature', 'atmospheric_pressure', 'ph', 'soil_moisture']):
            return jsonify({"error": "Missing data in module information. Each module must have 'ambient_temperature', 'atmospheric_pressure', 'ph', and 'soil_moisture'."}), 500
    
    save_device_info_to_database(fixed_ip, serial_number, collection_date, modules)
    
    return jsonify({"message": "Data received and processed successfully.", "success": True}), 200

@app.route('/shieldroot/data_get', methods=['GET'])
def send_shieldroot_data():
    # Get optional filter parameters from the request
    fixed_ip = request.args.get('fixed_ip')
    serial_number = request.args.get('serial_number')
    collection_date = request.args.get('collection_date')

    # List to store filtered data
    filtered_data = []

    # Check if the file exists before attempting to read it
    if os.path.isfile(DB_devices):
        with open(DB_devices, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            # Filter rows based on provided parameters
            for row in reader:
                if ((not fixed_ip or row.get('Fixed IP') == fixed_ip) and
                    (not serial_number or row.get('Serial Number') == serial_number) and
                    (not collection_date or row.get('Collection Date') == collection_date)):
                    filtered_data.append(row)

    # Return filtered data or a message if no data was found
    if filtered_data:
        return jsonify({"data": filtered_data, "success": True}), 200
    else:
        return jsonify({"message": "No data found with the specified filters.", "success": False}), 404

if __name__ == "__main__":
    app.run(debug=True)
