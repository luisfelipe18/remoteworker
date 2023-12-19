import matplotlib.pyplot as plt
import numpy as np

# Logistic function
def logistic(x, L, k, x0):
    return L / (1 + np.exp(-k*(x-x0)))

np.random.seed(18)

# Data 
L = 1.
k = 1.65 
x0 = 0
x = np.linspace(-2.5, 2.5, 100)
y = logistic(x, L, k, x0)
y2 = logistic(x, 0.99, 1.61, x0)
y3 = logistic(x, 0.95, 1.67, x0)

# Add random noise
e = 0.01*np.random.randn(len(x))
f = 0.03*np.random.randn(len(x))
g = 0.02*np.random.randn(len(x))

#e
# Add higher noise from x=-1.75 to x=-0.75
for i in range(len(x)):
    if -1.75 <= x[i] <= -0.75:
        e[i] = 0.04*np.random.rand()

# Add higher noise from x=-0.5 to x=1.2
for i in range(len(x)):
    if -0.5 <= x[i] <= 1.2: 
        e[i] = 0.06*np.random.rand()

# f
for i in range(len(x)):
    if -1.25 <= x[i] <= -0.5:
        f[i] = 0.02*np.random.rand()

# Add higher noise from 
for i in range(len(x)):
    if 0.75 <= x[i] <= 1.5: 
        f[i] = 0.03*np.random.rand()

# g
for i in range(len(x)):
    if -1.75 <= x[i] <= -0.75:
        g[i] = 0.05*np.random.rand()

# Add higher noise from 
for i in range(len(x)):
    if -1 <= x[i] <= 2: 
        g[i] = 0.04*np.random.rand()



y_noisy = y3 + 0.5*e
y_noisy_2 = y2 + 0.4*f
y_noisy_3 =  y2 + 0.5*g

# Plot  
fig, ax = plt.subplots(figsize=(15, 8))


ax.plot(x, y, linestyle='-', label='True d.f.') 
ax.plot(x, y_noisy, linestyle='dotted', marker='', label="approximating d.f. 1") 
ax.plot(x, y_noisy_2, linestyle='dashdot', marker='', label="approximating d.f. 2")  
ax.plot(x, y_noisy_3, linestyle='--', marker='', label="approximating d.f. 3")  



ax.set_xlim(-2.5, 2.5)
ax.set_ylim(0, 1.1)
ax.legend()
ax.grid(True)

ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')


plt.show()
