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

def cargar_api_movile_keys():
    with open("api_movile_request_keys.txt", "r") as file:
        keys = [line.strip() for line in file.readlines()]  # Lee cada línea y elimina espacios en blanco
    return set(keys)  # Usar un set para mejorar la búsqueda y evitar duplicados

API_KEYS = cargar_api_movile_keys()

def verificar_api_key(api_key):
    return api_key in API_KEYS

ideal_crops = open("idealConditionsForCrops.csv", "r", encoding="utf-8")
df_idealcrops = pd.read_csv(ideal_crops)

DB_devices = "devices_information.csv"

usrmeteomatics = "sanchez_fernando"
passmeteomatics = "BF9d8pI27r"
with open("openWeatherKey.txt", "r") as key:
    openWeatherKey = key.read()

today = datetime.now().strftime("%Y-%m-%d")

def openMeteo_dataset(latitud, longitud): #informacion a futuro 
    parameters_openmeteo = "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,evapotranspiration,soil_temperature_0cm,soil_moisture_0_to_1cm,wind_speed_10m,pressure_msl"
    url_openmeteo = f"https://api.open-meteo.com/v1/forecast?latitude={latitud}&longitude={longitud}&hourly={parameters_openmeteo}&start={today}"
    response_openmeteo = requests.get(url_openmeteo)
    if response_openmeteo.status_code == 200:
        data_openmeteo = response_openmeteo.json()
    else:
        print("no dataset: Meteo-matics")
    
    df_openmeteo = pd.DataFrame(data_openmeteo['hourly'])
    return df_openmeteo

def meteomatics_dataset(latitud, longitud): #informacion especial
    agriculture_parameters_meteomatics = [
        "soil_moisture_index_-15cm:idx",  # Índice de humedad del suelo
        "volumetric_soil_water_-15cm:m3m3",  # Contenido volumétrico de agua en el suelo
        "drought_index:idx",  # Índice de sequía
        "vapor_pressure_deficit_2m:hPa",  # Déficit de presión de vapor
        "forest_fire_warning:idx",  # Advertencia de incendio forestal
        "frost_warning:idx" # Advertencia de heladas
    ]
    parameters_meteomatics = ",".join(agriculture_parameters_meteomatics)

    url_meteomatics= f"https://api.meteomatics.com/{today}T00:00:00ZP5D:PT12H/{parameters_meteomatics}/{latitud},{longitud}/html"

    response_meteomatics = requests.get(url_meteomatics, auth=(usrmeteomatics, passmeteomatics))

    #meteomatics data
    soup_meteomatics = BeautifulSoup(response_meteomatics.text, 'html.parser')
    csv_content_meteomatics = soup_meteomatics.find('pre', id='csv').text
    csv_buffer = StringIO(csv_content_meteomatics)
    df_meteomatics = pd.read_csv(csv_buffer, sep=';')
    
    return df_meteomatics
    
def openWeather_dataset(latitud, longitud): #infromacion timepo real
    url_OpenWeather = f"https://api.openweathermap.org/data/2.5/weather?lat={latitud}&lon={longitud}&units=metric&appid={openWeatherKey}"
    
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
        print("no dataset: Open Weather")
    
    df_openWeather = pd.DataFrame([weather_data])
    
    return df_openWeather

def evaluar_condiciones_agricultura(df_combinado, df_ideal):
    resultados = []

    for index, row in df_combinado.iterrows():
        recomendacion = {}

        for _, cultivo in df_ideal.iterrows():
            # Comparar los valores actuales con los ideales
            cultivo_nombre = cultivo['Crop']
            temp_actual = row['temperature_2m']
            temp_ideal = cultivo['temperature_2m (°C)']
            humedad_actual = row['relative_humidity_2m']
            humedad_ideal = cultivo['relative_humidity_2m (%)']
            precipitacion_actual = row['precipitation']
            precipitacion_ideal = cultivo['precipitation (mm)']
            soil_moisutre_actual = row['soil_moisture_0_to_1cm']
            soil_moisutre_ideal = cultivo['soil_moisture_0_to_1cm (m3/m3)']
            soil_temperature_actual = row['soil_temperature_0cm']
            soil_temperature_ideal = cultivo['soil_temperature_0cm (°C)']
            evapotranspiracion_actual = row['evapotranspiration']
            evapotranspiracion_ideal = cultivo['evapotranspiration (mm)'].replace('mm/day', '').strip()
            soil_moisture_index_actual = row['soil_moisture_index_-15cm:idx']
            soil_moisture_index_ideal = cultivo['soil_moisture_index_-15cm (idx)']
            volumetric_soil_water_actual = row['volumetric_soil_water_-15cm:m3m3']
            volumetric_soil_water_ideal = cultivo['volumetric_soil_water_-15cm (m3/m3)']
            drought_index_actual = row['drought_index:idx']
            drought_index_ideal = cultivo['drought_index (idx)']
            pressure_actual = row['pressure_msl']
            pressure_ideal = cultivo['pressure_msl (hPa)']
            vapor_pressure_deficit_actual = row['vapor_pressure_deficit_2m:hPa']
            vapor_pressure_deficit_ideal = cultivo['vapor_pressure_deficit_2m (hPa)']
            
            # Lista para almacenar las condiciones fuera del rango
            fuera_rango = []

            # Evaluar temperatura
            temp_min, temp_max = map(float, temp_ideal.split('-'))
            temp_ok = temp_min <= temp_actual <= temp_max
            if not temp_ok:
                fuera_rango.append(f'Temperatura: {temp_actual} fuera del rango {temp_min}-{temp_max}°C')

            # Evaluar humedad
            humedad_min, humedad_max = map(float, humedad_ideal.split('-'))
            humedad_ok = humedad_min <= humedad_actual <= humedad_max
            if not humedad_ok:
                fuera_rango.append(f'Humedad: {humedad_actual} fuera del rango {humedad_min}-{humedad_max}%')

            # Evaluar precipitación
            precipitacion_ok = False
            if "total" in precipitacion_ideal:
                precipitacion_ok = True
            elif '-' in precipitacion_ideal:
                try:
                    precipitacion_min, precipitacion_max = map(float, precipitacion_ideal.split(' ')[0].split('-'))
                    precipitacion_ok = precipitacion_min <= precipitacion_actual <= precipitacion_max
                except ValueError:
                    precipitacion_ok = False
            else:
                try:
                    precipitacion_valor = float(precipitacion_ideal.split(' ')[0])
                    precipitacion_ok = precipitacion_valor <= precipitacion_actual
                except ValueError:
                    precipitacion_ok = False

            if not precipitacion_ok:
                fuera_rango.append(f'Precipitación: {precipitacion_actual} fuera del rango')

            # Evaluar humedad del suelo
            soilMoisture_min, soilMoisture_max = map(float, soil_moisutre_ideal.split('-'))
            soilMoisture_ok = soilMoisture_min <= soil_moisutre_actual <= soilMoisture_max
            if not soilMoisture_ok:
                fuera_rango.append(f'Humedad del suelo: {soil_moisutre_actual} fuera del rango {soilMoisture_min}-{soilMoisture_max} m3/m3')

            # Evaluar temperatura del suelo
            soilTemp_min, soilTemp_max = map(float, soil_temperature_ideal.split('-'))
            soilTemp_ok = soilTemp_min <= soil_temperature_actual <= soilTemp_max
            if not soilTemp_ok:
                fuera_rango.append(f'Temperatura del suelo: {soil_temperature_actual} fuera del rango {soilTemp_min}-{soilTemp_max}°C')

            # Evaluar evapotranspiración
            evapotranspiration_min, evapotranspiration_max = map(float, evapotranspiracion_ideal.split('-'))
            evapotranspiration_ok = evapotranspiration_min <= evapotranspiracion_actual <= evapotranspiration_max
            if not evapotranspiration_ok:
                fuera_rango.append(f'Evapotranspiración: {evapotranspiracion_actual} fuera del rango {evapotranspiration_min}-{evapotranspiration_max} mm')

            # Evaluar índice de humedad del suelo
            soil_moisture_index_ok = False
            if soil_moisture_index_ideal.lower() == "alto" or soil_moisture_index_ideal.lower() == "moderate-high":
                soil_moisture_index_ok = soil_moisture_index_actual > 1.2
            elif soil_moisture_index_ideal.lower() == "moderado":
                soil_moisture_index_ok = 1.0 <= soil_moisture_index_actual <= 1.2
            elif soil_moisture_index_ideal.lower() == "bajo":
                soil_moisture_index_ok = soil_moisture_index_actual < 1.0

            if not soil_moisture_index_ok:
                fuera_rango.append(f'Índice de humedad del suelo: {soil_moisture_index_actual} fuera del ideal {soil_moisture_index_ideal}')

            # Evaluar agua volumétrica en el suelo
            volumetric_soil_water_min, volumetric_soil_water_max = map(float, volumetric_soil_water_ideal.split('-'))
            volumetric_soil_water_ok = volumetric_soil_water_min <= volumetric_soil_water_actual <= volumetric_soil_water_max
            if not volumetric_soil_water_ok:
                fuera_rango.append(f'Volumen de agua en el suelo: {volumetric_soil_water_actual} fuera del rango {volumetric_soil_water_min}-{volumetric_soil_water_max} m3/m3')

            # Evaluar índice de sequía
            drought_index_min, drought_index_max = map(int, drought_index_ideal.split('-'))
            drought_index_ok = drought_index_min <= drought_index_actual <= drought_index_max
            if not drought_index_ok:
                fuera_rango.append(f'Índice de sequía: {drought_index_actual} fuera del rango {drought_index_min}-{drought_index_max}')

            # Evaluar presión
            pressure_min, pressure_max = map(int, pressure_ideal.split('-'))
            pressure_ok = pressure_min <= pressure_actual <= pressure_max
            if not pressure_ok:
                fuera_rango.append(f'Presión: {pressure_actual} fuera del rango {pressure_min}-{pressure_max} hPa')

            # Evaluar déficit de presión de vapor
            vapor_pressure_deficit_min, vapor_pressure_deficit_max = map(float, vapor_pressure_deficit_ideal.split('-'))
            vapor_pressure_deficit_ok = vapor_pressure_deficit_min <= vapor_pressure_deficit_actual <= vapor_pressure_deficit_max
            if not vapor_pressure_deficit_ok:
                fuera_rango.append(f'Déficit de presión de vapor: {vapor_pressure_deficit_actual} fuera del rango {vapor_pressure_deficit_min}-{vapor_pressure_deficit_max} hPa')

            
            condiciones = [
                temp_ok, humedad_ok, precipitacion_ok, soilMoisture_ok,
                soilTemp_ok, evapotranspiration_ok, soil_moisture_index_ok,
                volumetric_soil_water_ok, drought_index_ok, pressure_ok,
                vapor_pressure_deficit_ok
            ]
            condiciones_optimales = sum(condiciones)
            
             # Generar recomendación
            if condiciones_optimales == len(condiciones):
                recomendacion[cultivo_nombre] = 'Condiciones óptimas para plantar'
            elif condiciones_optimales >= 8:
                recomendacion[cultivo_nombre] = f'Condiciones buenas pero hay que considerar algunos factores ({len(condiciones) - condiciones_optimales} fuera del rango ideal): {", ".join(fuera_rango)}'
            else:
                recomendacion[cultivo_nombre] = f'Condiciones desfavorables ({len(condiciones) - condiciones_optimales} factores fuera del rango ideal): {", ".join(fuera_rango)}'

        recomendacion['datetime'] = row['datetime']
        resultados.append(recomendacion)

    return pd.DataFrame(resultados)

def detectar_fenomenos_meteorologicos(df_combinado):
    resultados = []

    for index, row in df_combinado.iterrows():
        alerta_fenomeno = {
            'datetime': row['datetime'],
            'Fenomeno': 'Normal'  # Predeterminado
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
        
        # Evaluar fenómenos meteorológicos
        if drought_index is not None and soil_moisture_index is not None:
            if drought_index > 3 and soil_moisture_index < 1:
                alerta_fenomeno['Fenomeno'] = 'Sequía'

        if precipitation is not None and soil_moisture_index is not None:
            if precipitation > 50 and soil_moisture_index > 2:
                alerta_fenomeno['Fenomeno'] = 'Inundación'

        if wind_speed is not None and precipitation is not None:
            if wind_speed > 50 and precipitation > 20:
                alerta_fenomeno['Fenomeno'] = 'Tormenta'

        if wind_speed is not None and pressure_msl is not None:
            if wind_speed > 100 and pressure_msl < 950:
                alerta_fenomeno['Fenomeno'] = 'Huracán'

            elif wind_speed > 90 and pressure_msl < 970:
                alerta_fenomeno['Fenomeno'] = 'Tornado'

        if vapor_pressure_deficit is not None and relative_humidity is not None and temperature is not None:
            if vapor_pressure_deficit > 3 and relative_humidity < 20 and temperature > 35:
                alerta_fenomeno['Fenomeno'] = 'Incendio Forestal'

        resultados.append(alerta_fenomeno)

    # Retornar los resultados como un DataFrame para facilitar su exportación
    return pd.DataFrame(resultados)

def save_device_info_to_database(ip_fija, numero_serie, fecha_recoleccion, modulos):
    # Verifica si el archivo existe para saber si necesita escribir el encabezado
    archivo_existe = os.path.isfile(DB_devices)

    # Abre el archivo en modo de añadir (append)
    with open(DB_devices, mode='a', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.writer(archivo_csv)

        # Si el archivo no existía, escribe el encabezado
        if not archivo_existe:
            writer.writerow(['IP Fija', 'Número de Serie', 'Fecha de Recolección', 
                             'Módulo', 'Temperatura Ambiental', 'Presión Atmosférica', 'pH', 'Humedad del Suelo'])

        # Escribe los datos de cada módulo en una nueva fila
        for i, modulo in enumerate(modulos, start=1):
            writer.writerow([ip_fija, numero_serie, fecha_recoleccion, 
                             f'Módulo {i}', modulo['temperatura_ambiental'], modulo['presion_atmosferica'], 
                             modulo['ph'], modulo['humedad_suelo']])

# Endpoint crops y recomendaciones agricolas
@app.route('/cropshield/crops', methods=['GET'])
def json_recommendations():
    latitud = request.args.get('latitud')
    longitud = request.args.get('longitud')
    api_key = request.args.get('api_keys')
    
    if not api_key or not verificar_api_key(api_key):
        return jsonify({"error": "Acceso denegado. API Key inválida o no proporcionada."}), 403

    if not latitud or not longitud:
        return jsonify({"error": "Proporcione latitud y longitud"}), 400
    
    # Convertir latitud y longitud a float
    latitud = float(latitud)
    longitud = float(longitud)

    # Obtener datasets
    df_meteomatics = meteomatics_dataset(latitud, longitud)
    df_openMeteo = openMeteo_dataset(latitud, longitud)

    if df_meteomatics is None or df_openMeteo is None:
        return jsonify({"error": "No se pudieron obtener los datos de las APIs"}), 501

    df_meteomatics['validdate'] = df_meteomatics['validdate'].str.replace('Z', '', regex=False)
    
    # Truncar los segundos de la columna 'validdate' de df_meteomatics
    df_meteomatics['validdate'] = pd.to_datetime(df_meteomatics['validdate']).dt.floor('min')

    # Convertir la columna 'time' de df_openMeteo al formato datetime
    df_openMeteo['time'] = pd.to_datetime(df_openMeteo['time']).dt.floor('min')

    # Filtrar las filas de df_openMeteo que coinciden con las fechas y horas de df_meteomatics
    filtered_openMeteo = df_openMeteo[df_openMeteo['time'].isin(df_meteomatics['validdate'])]

    # Asegurarse de que ambos dataframes tienen la columna de fechas con el mismo nombre
    df_meteomatics.rename(columns={'validdate': 'datetime'}, inplace=True)
    filtered_openMeteo = filtered_openMeteo.rename(columns={'time': 'datetime'})

    # Fusionar ambos dataframes usando la columna de datetime
    combined_df = pd.merge(df_meteomatics, filtered_openMeteo, on='datetime', how='inner')

    # Evaluar condiciones agrícolas y fenómenos meteorológicos
    df_results_agricolas = evaluar_condiciones_agricultura(combined_df, df_idealcrops)
    df_results_meteorological = detectar_fenomenos_meteorologicos(combined_df)

    # Convertir DataFrames a JSON
    recomendaciones_agricolas_json= df_results_agricolas.to_dict(orient='records')

    # Devolver JSON con ambas recomendaciones y alertas
    return jsonify({
        "recomendaciones_agricolas": recomendaciones_agricolas_json,
    })

@app.route('/cropshield/alerts', methods=['GET'])
def json_alerts():
    latitud = request.args.get('latitud')
    longitud = request.args.get('longitud')
    api_key = request.args.get('api_keys')
    
    if not api_key or not verificar_api_key(api_key):
        return jsonify({"error": "Acceso denegado. API Key inválida o no proporcionada."}), 403

    if not latitud or not longitud:
        return jsonify({"error": "Proporcione latitud y longitud"}), 400
    
    # Convertir latitud y longitud a float
    latitud = float(latitud)
    longitud = float(longitud)

    # Obtener datasets
    df_meteomatics = meteomatics_dataset(latitud, longitud)
    df_openMeteo = openMeteo_dataset(latitud, longitud)

    if df_meteomatics is None or df_openMeteo is None:
        return jsonify({"error": "No se pudieron obtener los datos de las APIs"}), 501

    df_meteomatics['validdate'] = df_meteomatics['validdate'].str.replace('Z', '', regex=False)
    
    # Truncar los segundos de la columna 'validdate' de df_meteomatics
    df_meteomatics['validdate'] = pd.to_datetime(df_meteomatics['validdate']).dt.floor('min')

    # Convertir la columna 'time' de df_openMeteo al formato datetime
    df_openMeteo['time'] = pd.to_datetime(df_openMeteo['time']).dt.floor('min')

    # Filtrar las filas de df_openMeteo que coinciden con las fechas y horas de df_meteomatics
    filtered_openMeteo = df_openMeteo[df_openMeteo['time'].isin(df_meteomatics['validdate'])]

    # Asegurarse de que ambos dataframes tienen la columna de fechas con el mismo nombre
    df_meteomatics.rename(columns={'validdate': 'datetime'}, inplace=True)
    filtered_openMeteo = filtered_openMeteo.rename(columns={'time': 'datetime'})

    # Fusionar ambos dataframes usando la columna de datetime
    combined_df = pd.merge(df_meteomatics, filtered_openMeteo, on='datetime', how='inner')

    # Evaluar fenómenos meteorológicos
    df_results_meteorological = detectar_fenomenos_meteorologicos(combined_df)

    # Convertir DataFrames a JSON
    alertas_meteorologicas_json = df_results_meteorological.to_dict(orient='records')

    # Devolver JSON con ambas recomendaciones y alertas
    return jsonify({
        "alertas_meteorologicas": alertas_meteorologicas_json
    })

@app.route('/cropshield/weather', methods=['GET'])
def json_weather():
    latitud = request.args.get('latitud')
    longitud = request.args.get('longitud')
    api_key = request.args.get('api_keys')
    
    if not api_key or not verificar_api_key(api_key):
        return jsonify({"error": "Acceso denegado. API Key inválida o no proporcionada."}), 403

    if not latitud or not longitud:
        return jsonify({"error": "Proporcione latitud y longitud"}), 400
    
    # Convertir latitud y longitud a float
    latitud = float(latitud)
    longitud = float(longitud)

    # Obtener datasets
    df_OpenWeather = openWeather_dataset(latitud, longitud)

    if df_OpenWeather is None:
        return jsonify({"error": "No se pudieron obtener los datos de las APIs"}), 501

    # Convertir DataFrames a JSON
    weather_json = df_OpenWeather.to_dict(orient='records')

    # Devolver JSON con ambas recomendaciones y alertas
    return jsonify({
        "alertas_meteorologicas": weather_json
    })

@app.route('/shieldroot/upload', methods=['POST'])
def data_shieldroot_colect():
    # Obtener los datos JSON del cuerpo de la solicitud
    data = request.json

    # Verificar si los datos necesarios están presentes
    ip_fija = data.get('ip_fija')
    numero_serie = data.get('numero_serie')
    fecha_recoleccion = data.get('fecha_recoleccion')
    modulos = data.get('modulos')

    # Validación de datos
    if not ip_fija or not numero_serie or not fecha_recoleccion or not modulos:
        return jsonify({"error": "Faltan datos requeridos. Por favor, proporciona 'ip_fija', 'numero_serie', 'fecha_recoleccion' y 'modulos'."}), 400

    # Verificar que la información de los módulos sea válida
    for modulo in modulos:
        if not all(key in modulo for key in ['temperatura_ambiental', 'presion_atmosferica', 'ph', 'humedad_suelo']):
            return jsonify({"error": "Faltan datos en la información del módulo. Cada módulo debe tener 'temperatura_ambiental', 'presion_atmosferica', 'ph' y 'humedad_suelo'."}), 500
    
    save_device_info_to_database(ip_fija, numero_serie, fecha_recoleccion, modulos)
    
    return jsonify({"mensaje": "Datos recibidos y procesados correctamente.", "exito": True}), 200

@app.route('/shieldroot/data_get', methods=['GET'])
def send_shieldroot_data():
    # Obtener parámetros de filtro opcionales de la solicitud
    ip_fija = request.args.get('ip_fija')
    numero_serie = request.args.get('numero_serie')
    fecha_recoleccion = request.args.get('fecha_recoleccion')

    # Lista para almacenar los datos filtrados
    datos_filtrados = []

    # Verificar si el archivo existe antes de intentar leerlo
    if os.path.isfile(DB_devices):
        with open(DB_devices, mode='r', encoding='utf-8') as archivo_csv:
            reader = csv.DictReader(archivo_csv)

            # Filtrar las filas según los parámetros proporcionados
            for row in reader:
                if ((not ip_fija or row.get('IP Fija') == ip_fija) and
                    (not numero_serie or row.get('Número de Serie') == numero_serie) and
                    (not fecha_recoleccion or row.get('Fecha de Recolección') == fecha_recoleccion)):
                    datos_filtrados.append(row)

    # Devolver los datos filtrados o un mensaje si no se encontraron datos
    if datos_filtrados:
        return jsonify({"datos": datos_filtrados, "exito": True}), 200
    else:
        return jsonify({"mensaje": "No se encontraron datos con los filtros especificados.", "exito": False}), 404

if __name__ == "__main__":
    app.run(debug=True)