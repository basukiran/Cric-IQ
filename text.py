import pandas as pd

df = pd.read_csv("odis_deliveries.csv")
df.head(50000).to_csv("odis_deliveries.csv", index=False)