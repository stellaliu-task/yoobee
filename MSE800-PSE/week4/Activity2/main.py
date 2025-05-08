from IrisDatabase import DataProcessor

def main():
    processor = DataProcessor()
    processor.load_data()
    processor.print_flowers()

if __name__ == "__main__":
    main()