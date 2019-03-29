import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('discussion1.csv')

plt.plot(data['degree'], data['x'], c = 'blue')
plt.plot(data['degree'], data['y'], c = 'red')

plt.xlabel('Heading (degree)')
plt.ylabel('Magnetometer Output')
plt.title('Magnetometer Reading (blue:X, red:Y)')

plt.show()