class Factorial:
    pass  # defined an empty class


def factorial(num1):
    result = 1
    for i in range(1, num1 + 1):
        result *= i
    return result

def check_prime(num1):
    if num1 < 2:
        return False
    for i in range(2, int(num1 ** 0.5) + 1):
        if num1 % i == 0:
            return False
    return True

def display(num1):
    print("Factorial of", num1, "is", Factorial.factorial(num1))
    if Factorial.check_prime(num1):
        print(f"{num1} is a prime number.")
    else:
        print(f"{num1} is not a prime number.")

# using setattr added methods to Factorial
setattr(Factorial, 'factorial', staticmethod(factorial))
setattr(Factorial, 'check_prime', staticmethod(check_prime))
setattr(Factorial, 'display', staticmethod(display))



def main():
    Factorial.display(25)    
if __name__ == "__main__":
    main()