import cmath
import matplotlib.pyplot as plt

def get_complex_input(prompt):
    """Safely gets complex number input"""
    while True:
        try:
            return complex(input(prompt))
        except ValueError:
            print("Invalid input. Enter like '3+4j'")

def polar_operations(a, b):
    """Performs mathematically correct operations"""
    # Convert to polar
    a_r, a_theta = cmath.polar(a)
    b_r, b_theta = cmath.polar(b)
    
    # Correct operations (convert to Cartesian and back)
    add = cmath.polar(a + b)
    sub = cmath.polar(a - b)
    mul = cmath.polar(a * b)
    try:
        div = cmath.polar(a / b)
    except ZeroDivisionError:
        div = (float('inf'), 0)
    
    return {
        'a': (a_r, a_theta),
        'b': (b_r, b_theta),
        'add': add,
        'sub': sub,
        'mul': mul,
        'div': div
    }

def plot_results(results):
    """Visualizes the results"""
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111, polar=True)
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown']
    
    for i, (label, (r, theta)) in enumerate(results.items()):
        if r != float('inf'):  # Skip infinite magnitudes
            ax.plot([0, theta], [0, r], label=label, 
                    color=colors[i % len(colors)], marker='o')
    
    ax.set_title("Correct Vector Operations in Polar Coordinates")
    ax.legend()
    plt.show()

if __name__ == "__main__":
    a = get_complex_input("Enter first complex number (e.g., 3+4j): ")
    b = get_complex_input("Enter second complex number: ")
    
    results = polar_operations(a, b)
    plot_results(results)