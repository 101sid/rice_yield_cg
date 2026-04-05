import pandas as pd
import io
import requests

def fetch_official_data():
    # Reliable research mirrors of the official APY (Area, Production, Yield) dataset
    urls = [
        "https://raw.githubusercontent.com/vrushali92/India-Crop-Production-Data-Analysis/main/data/clean/Agriculture_clean.csv",
        "https://raw.githubusercontent.com/nethika/Crop-Yield-Prediction/master/crop_production.csv"
    ]
    
    df = None
    for url in urls:
        print(f"📡 Attempting to connect to: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                print("✅ Connection successful!")
                break
        except Exception as e:
            continue

    if df is None:
        print("❌ All links failed. Please check your internet or the source repositories.")
        return

    # --- DATA ENGINEERING: NORMALIZE COLUMNS ---
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Map common variations to our standard names
    mapping = {
        'state_name': 'state', 'district_name': 'district',
        'crop_year': 'year', 'production': 'prod', 'area': 'area'
    }
    df = df.rename(columns=mapping)

    # --- FILTER FOR CHHATTISGARH RICE ---
    df['state'] = df['state'].astype(str).str.upper()
    df['crop'] = df['crop'].astype(str).str.upper()
    
    # Chhattisgarh is often spelled 'CHHATTISGARH' in Govt records
    cg_rice = df[(df['state'].str.contains('CHHATTISGARH')) & (df['crop'].str.contains('RICE'))].copy()
    
    # --- CALCULATE YIELD ---
    # Formula: Yield = Production / Area
    cg_rice['prod'] = pd.to_numeric(cg_rice['prod'], errors='coerce')
    cg_rice['area'] = pd.to_numeric(cg_rice['area'], errors='coerce')
    
    # Handle the 'yield' column if it doesn't exist
    if 'yield' not in cg_rice.columns:
        cg_rice['yield'] = cg_rice['prod'] / cg_rice['area']
    
    # Clean up outliers and zeros (common in raw Govt data)
    cg_rice = cg_rice.dropna(subset=['yield'])
    cg_rice = cg_rice[(cg_rice['yield'] > 0.1) & (cg_rice['yield'] < 10)] 

    cg_rice.to_csv('cg_rice_base.csv', index=False)
    print(f"📂 Found {len(cg_rice)} official records. Saved to 'cg_rice_base.csv'")

if __name__ == "__main__":
    fetch_official_data()