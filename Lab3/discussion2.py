import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('discussion2.csv')

plt.plot(data['n'], data['CFx'], c = 'blue')
#plt.plot(data['n'], data['CFy'], c = 'red')
plt.plot(data['n'], data['KMx'], c = 'yellow')
#plt.plot(data['n'], data['KMy'], c = 'green')

plt.xlabel('Iteration')
plt.ylabel('Value')
plt.title('Output Value of X value(blue:CFx, yellow:KMx)')

plt.show()

plt.plot(data['n'], data['CFy'], c = 'red')
plt.plot(data['n'], data['KMy'], c = 'green')

plt.xlabel('Iteration')
plt.ylabel('Value')
plt.title('Output Value of Y value(red:CFy, green:KMy)')

plt.show()