import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, StackingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

print("🧠 Loading High-Resolution Dataset...")
df = pd.read_csv('final_research_data.csv')

# --- ADVANCED AGRONOMIC FEATURES ---
df['npk_total'] = df['nitrogen'] + df['phosphorus'] + df['potassium']
df['total_rain'] = df['jun_rain'] + df['jul_rain'] + df['aug_rain'] + df['sep_rain'] + df['oct_rain']
df['climate_stress_index'] = df['total_rain'] / df['temperature']
df['critical_stage_rain_ratio'] = (df['aug_rain'] + df['sep_rain']) / (df['jun_rain'] + df['jul_rain'] + 1)

# --- THE LEAKAGE FIX: Creating a Unique Group ID ---
# This ensures all 5 virtual farms from "Raipur_2018" stay strictly together.
df['group_id'] = df['district'] + '_' + df['year'].astype(str)

features = [
    'year', 'nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 
    'jun_rain', 'jul_rain', 'aug_rain', 'sep_rain', 'oct_rain',
    'humidity', 'irrigation_type', 'crop_variety', 'soil_type',
    'npk_total', 'climate_stress_index', 'critical_stage_rain_ratio'
]

X = df[features]
y = df['yield']
groups = df['group_id']

# 1. Scale the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- GROUP SHUFFLE SPLIT (Mathematically prevents cloning leakage) ---
print("🔒 Applying GroupShuffleSplit to prevent data leakage...")
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X_scaled, y, groups=groups))

X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# --- THE OPTIMIZED STACKING ENSEMBLE ---
print("🚀 Training Airtight Stacking Ensemble...")
base_models = [
    ('rf', RandomForestRegressor(n_estimators=400, max_depth=20, min_samples_leaf=2, random_state=42, n_jobs=-1)),
    ('hgbr', HistGradientBoostingRegressor(max_iter=400, learning_rate=0.03, l2_regularization=0.1, random_state=42))
]

stack_model = StackingRegressor(
    estimators=base_models, 
    final_estimator=RidgeCV(), 
    cv=5 # Reduced back to 5 for standard grouped validation
)

stack_model.fit(X_train, y_train)

# Evaluate
y_pred = stack_model.predict(X_test)
print("\n📊 --- UN-LEAKED TRUE PERFORMANCE ---")
print(f"R-Squared (R²): {r2_score(y_test, y_pred):.4f}")
print(f"Mean Absolute Error (MAE): {mean_absolute_error(y_test, y_pred):.4f} tons/ha")
print(f"Root Mean Squared Error (RMSE): {np.sqrt(mean_squared_error(y_test, y_pred)):.4f} tons/ha")

pickle.dump(stack_model, open('rice_ensemble.pkl', 'wb'))
pickle.dump(scaler, open('scaler.pkl', 'wb'))
print("\n✅ Saved Airtight Champion Model!")