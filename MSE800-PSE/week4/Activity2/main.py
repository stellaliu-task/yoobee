from IrisDatabase import DataProcessor

def main():
    processor = DataProcessor()
    processor1 = DataProcessor()
    processor.load_data()
    processor.print_flowers()

    print(id(processor), id(processor1))

if __name__ == "__main__":
    main()