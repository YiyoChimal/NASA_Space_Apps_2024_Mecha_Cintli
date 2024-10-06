🌱 CropShield API

CropShield is an API developed using Flask to monitor and analyze weather data and agricultural conditions through sensor data and external APIs. This API facilitates data collection from devices, offers agricultural recommendations, and sends alerts about potential meteorological phenomena.
🚀 Features

    Data Collection: Gathers information from agricultural sensors.
    Weather Analysis: Integrates with external APIs to provide current weather data.
    Crop Recommendations: Offers tailored suggestions for crop cultivation.
    Alert System: Warns about adverse meteorological conditions.

📚 Available Endpoints
1. /shieldroot/upload (POST)

    Description: Receives and stores data from devices in a CSV file.
    Method: POST
    Request Format:

    json

{
  "ip_fija": "192.168.1.100",
  "numero_serie": "ABC123456789",
  "fecha_recoleccion": "2024-10-06",
  "modulos": [
    {
      "temperatura_ambiental": 25.6,
      "presion_atmosferica": 1012,
      "ph": 6.5,
      "humedad_suelo": 45.7
    }
  ]
}

Success Response:

json

    {
      "message": "Data received and processed successfully.",
      "success": true
    }

2. /shieldroot/data_get (GET)

    Description: Retrieves stored data from the CSV file using optional filters.

    Method: GET

    Request Parameters:
        ip_fija (optional): Device's fixed IP.
        numero_serie (optional): Device's serial number.
        fecha_recoleccion (optional): Date of data collection.

    Example Request:

    bash

/shieldroot/data_get?ip_fija=192.168.1.100&fecha_recoleccion=2024-10-06

Success Response:

json

    {
      "data": [
        {
          "IP Address": "192.168.1.100",
          "Serial Number": "ABC123456789",
          "Date of Collection": "2024-10-06",
          "Module": "Module 1",
          "Ambient Temperature": "25.6",
          "Atmospheric Pressure": "1012",
          "pH": "6.5",
          "Soil Moisture": "45.7"
        }
      ],
      "success": true
    }

3. /cropshield/crops (GET)

    Description: Provides agricultural recommendations based on current weather conditions.
    Method: GET
    Request Parameters:
        latitude: Location's latitude.
        longitude: Location's longitude.
        api_keys: API key for authentication.
    Success Response: Returns a JSON with crop recommendations.

4. /cropshield/alerts (GET)

    Description: Alerts about potential meteorological phenomena based on current conditions.
    Method: GET
    Request Parameters:
        latitude: Location's latitude.
        longitude: Location's longitude.
        api_keys: API key for authentication.
    Success Response: Returns a JSON with detected meteorological alerts.

5. /cropshield/weather (GET)

    Description: Displays current weather conditions for a specific location using the OpenWeather API.
    Method: GET
    Request Parameters:
        latitude: Location's latitude.
        longitude: Location's longitude.
        api_keys: API key for authentication.
    Success Response: Returns a JSON with the current weather information.

🛠️ Possible Improvements and Suggestions

    Integration with a Real Database:
        Current: Data is stored in a CSV file.
        Suggestion: Migrate to a database like MySQL, PostgreSQL, or SQLite for scalability and security.
        Advantages:
            Faster and more efficient queries.
            Enhanced data management.

    Advanced Error Handling:
        Add validation and error handling layers to improve API stability.

    Authentication and Authorization:
        Implement a more robust system using JWT or OAuth for enhanced security.

    Rate Limiting:
        Limit request rates to prevent system abuse.

    Documentation and Testing:
        Add unit tests using frameworks like pytest.
        Create comprehensive documentation with tools like Swagger.

📋 Prerequisites

    Flask: Framework to handle web requests.
    Python 3.x: Required to run the API.
    Additional Modules: requests, pandas, BeautifulSoup, among others.

🚀 How to Run the API

    Install dependencies:

    bash

pip install -r requirements.txt

Run the Flask application:

bash

    python main.py

    Test the endpoints:
        Use tools like curl, Postman, or your browser to test the API.

📞 Contact

For any questions or suggestions regarding the project, feel free to reach out to us.