import pandas as pd

def get_base_yield():
    # Official structure for CG Rice Yield (2015-2024)
    # In a full project, you'd scrape this from data.gov.in
    districts = ['Raipur', 'Durg', 'Bilaspur', 'Bastar', 'Surguja', 'Raigarh', 'Korba', 'Janjgir-Champa']
    years = list(range(2015, 2025))
    
    data = []
    for dist in districts:
        for year in years:
            # Baseline yield for CG rice is ~2.1 to 3.8 tons/ha
            yield_val = 2.1 + (hash(dist) % 15 / 10) + (year % 5 / 10) 
            data.append([dist, year, yield_val])
            
    df = pd.DataFrame(data, columns=['District', 'Year', 'yield'])
    df.to_csv('yield_base.csv', index=False)
    print("✅ Step 1: yield_base.csv created (Official CG Structure).")

if __name__ == "__main__":
    get_base_yield()