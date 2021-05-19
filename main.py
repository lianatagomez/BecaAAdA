# coding=utf-8
import numpy as np
from funcionesv2 import ordenMJD
import matplotlib.pyplot as plt

file = "ds1024_cont_line_A2_20210127_141526.fil"

orden = "RA"
data = ordenMJD(file, 1, 1, orden)

plt.ylabel('Potencia')

if orden == "MJD":
    plt.plot(data[1:, 0], data[1:, 3])
    plt.xlabel('MJD')
elif orden == "RA":
    plt.plot(data[:, 1], data[:, 3])
    plt.xlabel('RA')
elif orden == "DEC":
    plt.plot( data[:,2], data[:, 3])
    plt.xlabel('DEC')

#plt.savefig('con_baseline_filtrado_DEC_3.png')
plt.show()