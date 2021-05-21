# coding=utf-8

def ordenMJD(filename,opcion,base,orden):
    #datos de entrada
    #filename = nombre del .fil
    #opcion = 1 es potencia, 0 es espectro
    #base = 1 es quitar linea de base y 0 es no quitarla
    #orden para ordenar por: RA = ascención recta, DEC = por declinación, MJD = por tiempo.
    import numpy as np
    import os
    from astropy.time import Time
    import struct
    import sigproc
    from BaselineRemoval import BaselineRemoval
    from peakutils import baseline

    header = sigproc.read_header(filename)
    f=open(filename,"rb")
    nchans = int(header[0].get("nchans"))   # numero de canales
    f.seek(header[1])                       # le dice a la estructura f que ubique al puntero en una cierta posicion

    # abrimos el archivo con los valores de tiempo ltf.
    time_name = filename[0:len(filename)-4]+'.ltf'  # nombre del archivo .ltf
    time_file = open(time_name, "r")                 # abre el archivo .ltf

    # abrimos el archivo con las posiciones de apuntamiento
    pos_name = filename[0:len(filename)-4]+'.txt'

    MJD_pos = np.loadtxt(pos_name, usecols=0)   # guardamos los valores de MJD de .txt
    RA_pos = np.loadtxt(pos_name, usecols=5)    # guardamos los valores de RA de .txt
    DEC_pos = np.loadtxt(pos_name, usecols=7)   # guardamos los valores de DEC de .txt
    t_i = MJD_pos[0]                            # primer valor de tiempo del .txt
    t_f = MJD_pos[-1:][0]                       # último valor de tiempo del .txt

    b = os.path.getsize(filename)
    size = int(header[0].get("nbits"))          # del header saca el tamaño en bits
    pack = size/8
    n_espectros = (((b-header[1])/pack)/nchans)-1 # Calculo del total de espectos disponibles en# el FIL
    tiempos = np.empty(n_espectros)

    n_real = 0
    for i in range(n_espectros):
        t_aux = str(time_file.readline())[0:26]      # sacamos el valor de tiempo del .ltf (dd/mm/yyyy)
        tiempos[i] = Time(t_aux, format='isot').mjd  # y lo pasamos a MJD

        if tiempos[i] >= t_i and tiempos[i] <= t_f:
            n_real += 1

    #crear el array con las dimensiones y "rellenarlo" con los datos que estan en los archivos
    espectros = np.empty([n_real,nchans+3])          # archivo de salida. Las columnas son: MJD, RA, DEC, y luego vienen los canales
    potencias = np.empty([n_real,4])                 # archivo de salida si piden potencia
    temp = np.empty(nchans)

#   -------------------------------------------------------------------------------------------------------
    j = 0 # para recorrer las filas de espectros y potencias
    m = 0 # para recorrer las filas de RA_pos y DEC_pos
    t_pos = t_i

    for i in range(n_espectros):  # para cada instante de observación

        for k in range(nchans):
            temp[k] = struct.unpack('f', f.read(pack))[0]

        if tiempos[i] >= t_i and tiempos[i] <= t_f:

            if t_pos < tiempos[i]:
                m += 1
                t_pos = MJD_pos[m]

            espectros[j, 0] = tiempos[i]       # en la primera columna guardamos el t del .fil
            espectros[j, 1] = RA_pos[m]        # en la segunda columna guardamos el RA del .txt
            espectros[j, 2] = DEC_pos[m]       # en la tercera columna guardamos el DEC del .txt

            for k in range(nchans):
                espectros[j, k+3] = temp[k]    # cargamos las medidas en cada canal de frecuencia para ese instante

            if opcion == 1:                    # si piden calcular potencia
                potencias[j, 0] = tiempos[i]   # en la primera columna guardamos el t del .fil
                potencias[j, 1] = RA_pos[m]    # en la segunda columna guardamos el RA del .txt
                potencias[j, 2] = DEC_pos[m]  # en la tercera columna guardamos el DEC del .txt
                potencias[j, 3] = np.mean(espectros[j, 3:])

            j += 1

    if opcion == 0:
        np.save(filename[0:len(filename)-4] + "_espectro.npy", espectros)
        return espectros
    elif opcion == 1:
        np.save(filename[0:len(filename)-4] + "_potencia.npy", potencias)
        return potencias