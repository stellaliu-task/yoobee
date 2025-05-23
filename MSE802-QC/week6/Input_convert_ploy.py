import cmath
import matplotlib.pyplot as plt

# Input values
A = input("Enter first number ")
B = input("Enter Second number ")
# Convert the added string to complex number format cuase it required for polar coordinate conversion.
a = complex(A)
b = complex(B)

#...................................................................................................................................
#...................................................................................................................................
#...................................................................................................................................


# convert the input values to polar coordinates.
def polar_coordinates(c):
     r, theta = cmath.polar(c)  # gives the value as a tuple (r, theta) - r is the magnitude (radius) and theta is the phase (angle)  - r and theta here are added as variables
     return r, theta

a_polar = polar_coordinates(a)
b_polar = polar_coordinates(b)


#...................................................................................................................................
#...................................................................................................................................
#...................................................................................................................................

# Perform operations directly in polar coordinates

# Addition (r1 + r2, theta1 + theta2)
add_r = a_polar[0] + b_polar[0]
add_theta = a_polar[1] + b_polar[1]

# Subtraction (r1 - r2, theta1 - theta2)
sub_r = a_polar[0] - b_polar[0]
sub_theta = a_polar[1] - b_polar[1]

# Multiplication (r1 * r2, theta1 + theta2)
mul_r = a_polar[0] * b_polar[0]
mul_theta = a_polar[1] + b_polar[1]

# Division (r1 / r2, theta1 - theta2)
div_r = a_polar[0] / b_polar[0]  # Magnitude division
div_theta = a_polar[1] - b_polar[1]  # Phase subtraction


#...................................................................................................................................
#...................................................................................................................................
#...................................................................................................................................

# Adding results to a graph

results = { #added the values to a dictonary to store them
    'a': a_polar,
    'b': b_polar,
    'add': (add_r, add_theta),
    'sub': (sub_r, sub_theta),
    'mul': (mul_r, mul_theta),
    'div': (div_r, div_theta),
}

plt.figure(figsize=(8, 6)) #creating a figure with 8 inches width, and 6 inches height size 
ax = plt.subplot(111, polar=True) # plt.subplot(nrows, ncols, index) is the function values
colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown'] #providing colors to represent each operation

# Plot each result in polar coordinates
for i, (label, value) in enumerate(results.items()): # enumerate(): This function returns values in results dictonary and assign it to label and value variables. 
 #Value will have the polar coordinates and , dictornary key(add , subscrat etc) for each cordinate will get assigned to the lable
    if value is not None:
        r, theta = value
        ax.plot([0, theta], [0, r], label=label, color=colors[i % len(colors)], marker='o')
        #[0, theta], [0, r] these are x and y cordinates for the starting point.
        # label will the assigned key from the dictory mentioned before
        # same for color as well. I have defined teh colors before 
        # marker symbol is o. as in that is how the cordinates are marked
ax.set_title("Vector Operations in Polar Coordinates") #graph title
ax.legend() #display details as labels colors etc 
plt.show() #display the plot