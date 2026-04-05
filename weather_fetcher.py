import requests
import pandas as pd
import time

def fetch_nasa_weather(lat, lon, start_year, end_year):
    # NASA POWER API Endpoint
    url = f"https://power.larc.nasa.gov/api/temporal/annual/point?parameters=T2M,PRECTOTCORR,RH2M&community=AG&longitude={lon}&latitude={lat}&start={start_year}&end={end_year}&format=JSON"
    response = requests.get(url).json()
    return response['properties']['parameter']

def build_weather_db():
    # Coordinates for CG Districts
    coords = {
        'Raipur': [21.25, 81.62], 'Bastar': [19.07, 82.02], 
        'Bilaspur': [22.07, 82.13], 'Surguja': [23.12, 83.18]
    }
    
    weather_results = []
    for dist, loc in coords.items():
        print(f"📡 Fetching NASA data for {dist}...")
        data = fetch_nasa_weather(loc[0], loc[1], 2015, 2024)
        for year in range(2015, 2025):
            weather_results.append([
                dist, year, 
                data['T2M'][str(year)], 
                data['PRECTOTCORR'][str(year)], 
                data['RH2M'][str(year)]
            ])
        time.sleep(1) # Be nice to NASA's API
        
    df = pd.DataFrame(weather_results, columns=['District', 'Year', 'temperature', 'rainfall', 'humidity'])
    df.to_csv('weather_data.csv', index=False)
    print("✅ Step 2: weather_data.csv created from NASA API.")

if __name__ == "__main__":
    build_weather_db()