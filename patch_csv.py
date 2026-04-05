import pandas as pd
import numpy as np

print("🛠️ Patching the CSV instantly...")

try:
    # 1. Load the original monthly data (which has the correct districts)
    source_df = pd.read_csv('cg_rice_monthly_rain.csv')
    districts = source_df['district'].astype(str).str.upper().values

    # 2. Duplicate each district 5 times to match the virtual farms
    patched_districts = np.repeat(districts, 5)

    # 3. Load the big dataset that is missing the column
    final_df = pd.read_csv('final_research_data.csv')

    # 4. Inject the missing 'district' column right at the front
    final_df.insert(0, 'district', patched_districts)

    # 5. Save it back
    final_df.to_csv('final_research_data.csv', index=False)
    print("✅ Patch successful! The 'district' column has been restored.")

except Exception as e:
    print(f"❌ Error during patching: {e}")