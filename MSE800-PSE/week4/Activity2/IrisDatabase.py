import pandas as pd
from sklearn.datasets import load_iris

class DataProcessor:
    def __init__(self):
        self.data = None

    def load_data(self):
        iris = load_iris(as_frame=True)     # return the dataset as a pandas.DataFrame
        self.data = iris.frame              # Convert to DataFrame
        #print("Target names:", iris.target_names)

        # maps the number x to its corresponding flower name
        self.data['flower_name'] = self.data['target'].apply(lambda x:iris.target_names[x])

    def print_flowers(self):    
        print("\nUnique names:")  
        print(self.data['flower_name'].unique())
        print("\nAll names:")  
        print(self.data[['flower_name']])


