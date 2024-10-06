from flask import Flask, request, jsonify
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

ideal_crops = open("idealConditionsForCrops.csv", "r", encoding="utf-8")
df_idealcrops = pd.read_csv(ideal_crops)

#miLatitud = 19.510232
#miLongitud = -96.884593

latitud_somalia = 21.414988
longitus_somalia = 48.542602

usrmeteomatics = "sanchez_fernando"
passmeteomatics = "BF9d8pI27r"
with open("openWeatherKey.txt", "r") as key:
    openWeatherKey = key.read()

today = datetime.now().strftime("%Y-%m-%d")

def openMeteo_dataset(): #informacion a futuro 
    parameters_openmeteo = "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,evapotranspiration,soil_temperature_0cm,soil_moisture_0_to_1cm,wind_speed_10m,pressure_msl"
    url_openmeteo = f"https://api.open-meteo.com/v1/forecast?latitude={latitud_somalia}&longitude={longitus_somalia}&hourly={parameters_openmeteo}&start={today}"
    response_openmeteo = requests.get(url_openmeteo)
    if response_openmeteo.status_code == 200:
        data_openmeteo = response_openmeteo.json()
    else:
        print("no dataset: Meteo-matics")
    
    df_openmeteo = pd.DataFrame(data_openmeteo['hourly'])
    return df_openmeteo

def meteomatics_dataset(): #informacion especial
    agriculture_parameters_meteomatics = [
        "soil_moisture_index_-15cm:idx",  # Índice de humedad del suelo
        "volumetric_soil_water_-15cm:m3m3",  # Contenido volumétrico de agua en el suelo
        "drought_index:idx",  # Índice de sequía
        "vapor_pressure_deficit_2m:hPa",  # Déficit de presión de vapor
        "forest_fire_warning:idx",  # Advertencia de incendio forestal
        "frost_warning:idx" # Advertencia de heladas
    ]
    parameters_meteomatics = ",".join(agriculture_parameters_meteomatics)

    url_meteomatics= f"https://api.meteomatics.com/{today}T00:00:00ZP5D:PT12H/{parameters_meteomatics}/{latitud_somalia},{longitus_somalia}/html"

    response_meteomatics = requests.get(url_meteomatics, auth=(usrmeteomatics, passmeteomatics))

    #meteomatics data
    soup_meteomatics = BeautifulSoup(response_meteomatics.text, 'html.parser')
    csv_content_meteomatics = soup_meteomatics.find('pre', id='csv').text
    csv_buffer = StringIO(csv_content_meteomatics)
    df_meteomatics = pd.read_csv(csv_buffer, sep=';')
    
    return df_meteomatics
    
def openWeather_dataset(): #infromacion timepo real
    url_OpenWeather = f"https://api.openweathermap.org/data/2.5/weather?lat={latitud_somalia}&lon={longitus_somalia}&units=metric&appid={openWeatherKey}"
    
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
        alerta_fenomeno = {}
        
        # Variables
        soil_moisture_index = row['soil_moisture_index_-15cm:idx']
        drought_index = row['drought_index:idx']
        vapor_pressure_deficit = row['vapor_pressure_deficit_2m:hPa']
        precipitation = row['precipitation']
        wind_speed = row['wind_speed_10m']
        pressure_msl = row['pressure_msl']
        relative_humidity = row['relative_humidity_2m']
        temperature = row['temperature_2m']
        
        # Evaluar sequía
        if drought_index > 3 and soil_moisture_index < 1:
            alerta_fenomeno['Sequía'] = 'Posible sequía detectada debido a índice de sequía elevado y baja humedad del suelo.'

        # Evaluar inundación
        if precipitation > 50 and soil_moisture_index > 2:
            alerta_fenomeno['Inundación'] = 'Posible inundación debido a precipitaciones intensas y alta humedad del suelo.'

        # Evaluar tormenta
        if wind_speed > 50 and precipitation > 20:
            alerta_fenomeno['Tormenta'] = 'Tormenta detectada con alta velocidad de viento y precipitaciones considerables.'

        # Evaluar huracán
        if wind_speed > 100 and pressure_msl < 950:
            alerta_fenomeno['Huracán'] = 'Posible huracán detectado debido a vientos extremadamente fuertes y baja presión.'

        # Evaluar tornado
        if wind_speed > 90 and pressure_msl < 970:
            alerta_fenomeno['Tornado'] = 'Posible tornado debido a vientos fuertes y baja presión.'

        # Evaluar riesgo de incendio forestal
        if vapor_pressure_deficit > 3 and relative_humidity < 20 and temperature > 35:
            alerta_fenomeno['Incendio Forestal'] = 'Alto riesgo de incendio forestal debido a déficit de presión de vapor, baja humedad relativa y alta temperatura.'

        # Si no hay ningún fenómeno detectado
        if not alerta_fenomeno:
            alerta_fenomeno['Condiciones'] = 'Condiciones climáticas normales.'

        alerta_fenomeno['datetime'] = row['datetime']
        resultados.append(alerta_fenomeno)

    return pd.DataFrame(resultados)

if __name__ == "__main__":
    df_meteomatics = meteomatics_dataset()
    df_meteomatics['validdate'] = df_meteomatics['validdate'].str.replace('Z', '', regex=False)
    #print(df_meteomatics)
    
    df_openMeteo = openMeteo_dataset()
    #print(df_openMeteo)
    
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
    
    df_results_agricolas = evaluar_condiciones_agricultura(combined_df, df_idealcrops)
    
    print(df_results_agricolas)
    
    df_results_meteorological = detectar_fenomenos_meteorologicos(combined_df)
    df_results_meteorological.to_csv('alertas', index=False)
    
    print(df_results_meteorological)