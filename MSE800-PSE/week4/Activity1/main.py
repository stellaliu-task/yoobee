import tkinter as tk
from tkinter import filedialog
from ClimateDaily import DataProcessor

def main():
    root = tk.Tk()   #created the main window
    root.withdraw()  #hided the main window
    file_path = filedialog.askopenfilename()
    #file_path = '1026__Screen_Observations__daily.csv'
    processor = DataProcessor(file_path)
    processor.load_data()
    processor.initial_processing()
    processor.read_rows()

if __name__ == "__main__":
    main()
