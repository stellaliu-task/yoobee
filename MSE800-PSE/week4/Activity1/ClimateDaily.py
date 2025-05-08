import pandas as pd

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        if self.file_path.endswith('.csv'):
            self.data = pd.read_csv(self.file_path)
        elif self.file_path.endswith('.parquet'):
            self.data = pd.read_parquet(self.file_path)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Parquet.")
        print(f"Data loaded successfully from {self.file_path}")

    def initial_processing(self):
        if self.data is None:
            raise ValueError("No data loaded.")
        

    def  read_rows(self):
        df = pd.read_csv(self.file_path, nrows=10)

        print("Initial Data Summary:")
        print(self.data.info())
        print("\nDescriptive Statistics:")
        print(self.data.describe())
        print("\nTen rows of the data:")
        print(df)

