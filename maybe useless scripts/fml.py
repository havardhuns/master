import numpy as np
import matplotlib.pyplot as plt
from random import randint
   
Women = [115, 215, 250, 200, 230, 100, 100]
Men = [114, 230, 510, 370, 400, 100, 100]
lol = [100,200,150,300, 250, 100, 100]
lol2 = [300,150,200,250, 200, 100, 100]
lol3 = [300,150,200,250, 200, 100, 100]
  
n=7
r = np.arange(n)
width = 0.15
  
plt.bar(r+width*1.5, [randint(500,700) for i in range(7)], color= '#9dc6e0', width = width*4, edgecolor = 'black', label="H2.1+H2.2")
  
plt.bar(r, Women, color = '#003f5c',
        width = width, edgecolor = 'black',
        label='"6"')

plt.bar(r + width, Men, color = '#7a5195',
        width = width, edgecolor = 'black',
        label='"7"')
plt.bar(r + width*2, lol, color = '#ef5675',
        width = width, edgecolor = 'black',
        label='"8"')
plt.bar(r + width * 3, lol2, color = '#ffa600',
        width = width, edgecolor = 'black',
        label='"9"')
  
plt.xlabel("Block height")
plt.ylabel("Number of transactions with OTC address")

# plt.grid(linestyle='--')
plt.xticks(r + width*1.5,['~100k', '~200k', '~300k', '~400k', '~500k', '~600k', '~700k', ])
plt.legend()
  
plt.show()