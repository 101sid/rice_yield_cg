import requests
import pandas as pd
import time

def fetch_nasa_monthly(lat, lon, year):
    url = f"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={year}&end={year}&format=JSON"
    try:
        res = requests.get(url, timeout=15).json()
        rain = res['properties']['parameter']['PRECTOTCORR']
        return {
            'jun_rain': rain[f"{year}06"],
            'jul_rain': rain[f"{year}07"],
            'aug_rain': rain[f"{year}08"],
            'sep_rain': rain[f"{year}09"],
            'oct_rain': rain[f"{year}10"]
        }
    except Exception as e:
        return None

cg_coords = {
    'RAIPUR': [21.25, 81.62], 'BASTAR': [19.07, 82.02], 'BILASPUR': [22.07, 82.13],
    'SURGUJA': [23.12, 83.18], 'DURG': [21.19, 81.28], 'KORBA': [22.35, 82.68],
    'RAIGARH': [21.89, 83.39], 'JANJGIR-CHAMPA': [22.01, 82.56], 'RAJNANDGAON': [21.10, 80.37],
    'KABIRDHAM': [22.01, 81.22], 'MAHASAMUND': [21.10, 82.09], 'DHAMTARI': [20.70, 81.54],
    'KORIYA': [23.25, 82.55], 'JASHPUR': [22.88, 83.93], 'KANKER': [20.27, 81.49],
    'DANTEWADA': [18.89, 81.35], 'NARAYANPUR': [19.71, 81.22], 'BIJAPUR': [18.79, 80.81]
}

print("🛰️ Accessing NASA POWER for Month-by-Month Data...")
df = pd.read_csv('cg_rice_base.csv')
df['district'] = df['district'].astype(str).str.upper()

results = []
for index, row in df[['district', 'year']].drop_duplicates().iterrows():
    dist, year = row['district'], int(row['year'])
    mapped_dist = next((key for key in cg_coords.keys() if key in dist), None)
    
    if mapped_dist:
        print(f"Fetching Monthly Rain for {mapped_dist} in {year}...")
        monthly_data = fetch_nasa_monthly(cg_coords[mapped_dist][0], cg_coords[mapped_dist][1], year)
        if monthly_data:
            monthly_data.update({'district': dist, 'year': year})
            results.append(monthly_data)
        time.sleep(0.5)

rain_df = pd.DataFrame(results)
final_df = pd.merge(df, rain_df, on=['district', 'year'], how='left').dropna()
final_df.to_csv('cg_rice_monthly_rain.csv', index=False)
print("✅ Monthly Climate Data Saved!")