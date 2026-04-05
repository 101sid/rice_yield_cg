import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, StackingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

# 1. Load Data
df = pd.read_csv('cg_research_data.csv')
X = df.drop(columns=['yield', 'District', 'Year'])
y = df['yield']

# 2. Scale (Normalize) Data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 4. Stacking Ensemble
print("Training Stacking Ensemble (RF + ET)...")
model = StackingRegressor(
    estimators=[('rf', RandomForestRegressor(n_estimators=100)), ('et', ExtraTreesRegressor(n_estimators=100))],
    final_estimator=RandomForestRegressor(n_estimators=50)
)
model.fit(X_train, y_train)

# 5. Score
print(f"🌟 Research R² Score: {r2_score(y_test, model.predict(X_test)):.4f}")

# 6. Save
pickle.dump(model, open('rice_ensemble.pkl', 'wb'))
pickle.dump(scaler, open('scaler.pkl', 'wb'))
print("✅ Saved 'rice_ensemble.pkl' and 'scaler.pkl'")