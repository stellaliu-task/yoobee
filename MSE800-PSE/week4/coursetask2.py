import pandas as pd

file_path = 'Sample_data_2.parquet'
df = pd.read_parquet(file_path)
print(df.head())