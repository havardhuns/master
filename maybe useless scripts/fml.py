import numpy as np
import matplotlib.pyplot as plt
   
Women = [115, 215, 250, 200, 230]
Men = [114, 230, 510, 370, 400]
lol = [100,200,150,300, 250]
lol2 = [300,150,200,250, 200]
lol3 = [300,150,200,250, 200]
  
n=5
r = np.arange(n)
width = 0.15
  
  
plt.bar(r, Women, color = 'b',
        width = width, edgecolor = 'black',
        label='Women')
plt.bar(r + width, Men, color = 'g',
        width = width, edgecolor = 'black',
        label='Men')
plt.bar(r + width*2, lol, color = 'y',
        width = width, edgecolor = 'black',
        label='Women')
plt.bar(r + width * 3, lol2, color = 'c',
        width = width, edgecolor = 'black',
        label='Men')
plt.bar(r + width * 4, lol3, color = 'm',
        width = width, edgecolor = 'black',
        label='Men')

  
plt.xlabel("Year")
plt.ylabel("Number of people voted")
plt.title("Number of people voted in each year")
  
# plt.grid(linestyle='--')
plt.xticks(r + width*2,['2018','2019','2020','2021', '2022'])
plt.legend()
  
plt.show()