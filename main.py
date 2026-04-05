from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI(title="Chhattisgarh Rice Research API")

# Load the saved model and scaler
model = pickle.load(open('rice_ensemble.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))

class YieldInput(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    rainfall: float
    humidity: float
    irrigation_type: int
    crop_variety: int
    soil_type: int

@app.post("/predict")
def predict_yield(data: YieldInput):
    # 1. Arrange features in the exact order of training
    raw_features = np.array([[
        data.nitrogen, data.phosphorus, data.potassium, data.ph,
        data.temperature, data.rainfall, data.humidity,
        data.irrigation_type, data.crop_variety, data.soil_type
    ]])
    
    # 2. Scale the input using the research scaler
    scaled_features = scaler.transform(raw_features)
    
    # 3. Predict
    prediction = model.predict(scaled_features)
    
    return {
        "predicted_yield": round(float(prediction[0]), 2),
        "unit": "Tons per Hectare",
        "region": "Chhattisgarh Baseline"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)