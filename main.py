# coding=utf-8
import numpy as np
from funciones import ordenMJD
import matplotlib.pyplot as pl

file = "ds1024_cont_line_A2_20210127_141526.fil"
data = ordenMJD(file, 1,1,"MJD")

plt.plot( data[:,0] , data[:,3] )
plt.xlabel('MJD')
plt.ylabel('Potencia')
plt.savefig('perfil.png')
plt.show()