import tensorflow as tf
import matplotlib.pyplot as plt

#class Dataprocessor:

image_path='testimg.jpg'

image_loaded = tf.keras.utils.load_img(image_path)

plt.imshow(image_loaded)
plt.axis('off')
plt.title('Loaded Image')
plt.show()

#import math

#print(math.cos(30))

#print(math.sin(20))