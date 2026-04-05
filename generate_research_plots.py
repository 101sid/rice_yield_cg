import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

print("📈 Generating Thesis Visualizations...")
df = pd.read_csv('final_research_data.csv')
features = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 'rainfall', 'humidity', 'irrigation_type', 'crop_variety', 'soil_type']

X = df[features]
y = df['yield']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

lr = LinearRegression().fit(X_train, y_train)
rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
stack = StackingRegressor(
    estimators=[('rf', rf), ('gbr', GradientBoostingRegressor())],
    final_estimator=GradientBoostingRegressor()
).fit(X_train, y_train)

# 1. Feature Importance
plt.figure(figsize=(10, 6))
importances = rf.feature_importances_
indices = np.argsort(importances)
plt.title('Feature Importance Analysis (Stacking Ensemble)')
plt.barh(range(len(indices)), importances[indices], color='skyblue', align='center')
plt.yticks(range(len(indices)), [features[i] for i in indices])
plt.xlabel('Relative Importance Weight')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300)

# 2. Model Comparison
plt.figure(figsize=(10, 6))
models = ['Linear Regression', 'Random Forest', 'Proposed Ensemble']
scores = [r2_score(y_test, lr.predict(X_test)), r2_score(y_test, rf.predict(X_test)), r2_score(y_test, stack.predict(X_test))]
sns.barplot(x=models, y=scores, palette='viridis')
plt.title('Performance Comparison (R² Score)')
plt.ylabel('R-Squared Value')
plt.ylim(0, 1.0)
for i, v in enumerate(scores):
    plt.text(i, v + 0.02, f"{v:.4f}", ha='center', fontweight='bold')
plt.savefig('model_comparison.png', dpi=300)

# 3. Actual vs Predicted
plt.figure(figsize=(8, 8))
y_pred = stack.predict(X_test)
plt.scatter(y_test, y_pred, alpha=0.5, color='green', label='Predictions')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Perfect Fit')
plt.xlabel('Actual Yield (tons/ha)')
plt.ylabel('Predicted Yield (tons/ha)')
plt.title(f'Actual vs. Predicted Rice Yield (R² = {r2_score(y_test, y_pred):.4f})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('actual_vs_predicted.png', dpi=300)

print("✅ All plots saved at 300 DPI!")