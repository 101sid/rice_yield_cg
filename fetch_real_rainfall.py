import requests
import pandas as pd
import time

def fetch_nasa_rainfall(lat, lon, year):
    url = f"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={year}&end={year}&format=JSON"
    try:
        response = requests.get(url, timeout=15).json()
        monthly_rain = response['properties']['parameter']['PRECTOTCORR']
        monsoon_total = sum([monthly_rain[f"{year}{month:02d}"] for month in range(6, 11)])
        return monsoon_total
    except Exception as e:
        return None

# Expanded CG Coordinates
cg_coords = {
    'RAIPUR': [21.25, 81.62], 'BASTAR': [19.07, 82.02], 'BILASPUR': [22.07, 82.13],
    'SURGUJA': [23.12, 83.18], 'DURG': [21.19, 81.28], 'KORBA': [22.35, 82.68],
    'RAIGARH': [21.89, 83.39], 'JANJGIR-CHAMPA': [22.01, 82.56], 'RAJNANDGAON': [21.10, 80.37],
    'KABIRDHAM': [22.01, 81.22], 'MAHASAMUND': [21.10, 82.09], 'DHAMTARI': [20.70, 81.54],
    'KORIYA': [23.25, 82.55], 'JASHPUR': [22.88, 83.93], 'KANKER': [20.27, 81.49],
    'DANTEWADA': [18.89, 81.35], 'NARAYANPUR': [19.71, 81.22], 'BIJAPUR': [18.79, 80.81]
}

def update_rainfall_database():
    print("📂 Loading base yield data...")
    df = pd.read_csv('cg_rice_base.csv')
    df['district'] = df['district'].astype(str).str.upper()
    
    unique_combinations = df[['district', 'year']].drop_duplicates()
    results = []

    print("🛰️ Accessing NASA POWER for ALL Districts (This may take a few minutes)...")
    for index, row in unique_combinations.iterrows():
        dist = row['district']
        year = int(row['year'])
        
        # Match standard names (handles spelling variations in Govt data)
        mapped_dist = next((key for key in cg_coords.keys() if key in dist), None)
        
        if mapped_dist:
            lat, lon = cg_coords[mapped_dist]
            print(f"Fetching Rain for {mapped_dist} in {year}...")
            rain = fetch_nasa_rainfall(lat, lon, year)
            if rain:
                results.append({'district': dist, 'year': year, 'real_rainfall': rain})
            time.sleep(0.5) # Prevent NASA from blocking us

    rain_df = pd.DataFrame(results)
    final_df = pd.merge(df, rain_df, on=['district', 'year'], how='left')
    final_df.to_csv('cg_rice_with_real_rain.csv', index=False)
    print(f"✅ Integrated NASA Data for {len(rain_df)} district-years!")

if __name__ == "__main__":
    update_rainfall_database()