from src.preprocess import load_data, clean_data, save_cleaned
from src.analysis import calculate_kpis, category_analysis
from src.advanced import rfm_analysis

# Load
df = load_data("data/raw/superstore.csv")

# Clean
df = clean_data(df)

# Save
save_cleaned(df, "data/cleaned/cleaned_data.csv")

# KPIs
kpis = calculate_kpis(df)
print(kpis)

# Category
print(category_analysis(df).head())

# RFM
rfm = rfm_analysis(df)
print(rfm.head())