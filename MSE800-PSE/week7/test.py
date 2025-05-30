class RentalManager:
    _instance = None
 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RentalManager, cls).__new__(cls)
            cls._instance.cars_available = ["Toyota", "Honda", "Ford"]
        return cls._instance
 
    def rent_car(self, car_name):
        if car_name in self.cars_available:
            self.cars_available.remove(car_name)
            print(f"{car_name} has been rented.")
        else:
            print(f"{car_name} is not available.")

        print(id(car_name))
 
    def show_available_cars(self):
        print("Available cars:", self.cars_available)
 
 
manager1 = RentalManager()
manager2 = RentalManager()
text1='Honda'
manager1.rent_car(text1)
manager2.show_available_cars()

print(id(text1))