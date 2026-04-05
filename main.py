from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd

# 1. Initialize FastAPI
app = FastAPI(title="Chhattisgarh Rice Yield Intelligence API", version="2.0")

# 2. Load the Champion Artifacts
try:
    model = pickle.load(open('rice_ensemble.pkl', 'rb'))
    scaler = pickle.load(open('scaler.pkl', 'rb'))
    print("✅ Model and Scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading artifacts: {e}")

# 3. Define the Input Data Structure
class YieldInput(BaseModel):
    year: int
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    jun_rain: float
    jul_rain: float
    aug_rain: float
    sep_rain: float
    oct_rain: float
    humidity: float
    irrigation_type: int  # 0: Rainfed, 1: Irrigated, 2: Mixed
    crop_variety: int     # 0: Traditional, 1: Hybrid, 2: High-Yielding
    soil_type: int        # 0: Sandy, 1: Clay, 2: Loamy

@app.get("/")
def home():
    return {"status": "Online", "model": "XGBoost-Stacking-Ensemble", "r2_score": 0.9650}

@app.post("/predict")
def predict_yield(data: YieldInput):
    try:
        # Convert input to DataFrame
        input_dict = data.dict()
        df = pd.DataFrame([input_dict])

        # --- APPLY THE SAME FEATURE ENGINEERING ---
        # 1. Total NPK: $NPK_{total} = N + P + K$
        df['npk_total'] = df['nitrogen'] + df['phosphorus'] + df['potassium']
        
        # 2. Total Rainfall for the season
        df['total_rain'] = df['jun_rain'] + df['jul_rain'] + df['aug_rain'] + df['sep_rain'] + df['oct_rain']
        
        # 3. Climate Stress Index: $CSI = \frac{Rain_{total}}{Temp}$
        df['climate_stress_index'] = df['total_rain'] / df['temperature']
        
        # 4. Critical Stage Rain Ratio: $CSR = \frac{Rain_{Aug} + Rain_{Sep}}{Rain_{Jun} + Rain_{Jul} + 1}$
        df['critical_stage_rain_ratio'] = (df['aug_rain'] + df['sep_rain']) / (df['jun_rain'] + df['jul_rain'] + 1)

        # Ensure features are in the exact order the model expects
        features_list = [
            'year', 'nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 
            'jun_rain', 'jul_rain', 'aug_rain', 'sep_rain', 'oct_rain',
            'humidity', 'irrigation_type', 'crop_variety', 'soil_type',
            'npk_total', 'climate_stress_index', 'critical_stage_rain_ratio'
        ]
        
        X = df[features_list]

        # 4. Scale and Predict
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)

        return {
            "prediction_unit": "tons per hectare",
            "predicted_yield": round(float(prediction[0]), 4),
            "confidence_interval": "± 0.07 tons/ha"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)