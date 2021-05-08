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

    b = os.path.getsize(filename)
    size = int(header[0].get("nbits"))          # del header saca el tamaño en bits
    pack = size/8
    espectros = (((b-header[1])/pack)/nchans)-1 # Calculo del total de espectos disponibles en# el FIL

    #crear el array con las dimensiones y "rellenarlo" con los datos que estan en los archivos
    ltf_fil = np.empty([0,nchans+3])            # archivo de salida. Las columnas son: MJD, RA, DEC, y luego vienen los canales
    potencias = np.empty([0,2])                 # archivo de salida si piden potencia

    t0 = MJD_pos[0]                             # primer valor de tiempo del .txt
    for i in range(espectros):                  # para cada instante de observación
        t_aux=str(time_file.readline())[0:26]   # sacamos el valor de tiempo del .ltf (dd/mm/yyyy)
        t1 = Time(t_aux, format='isot').mjd     # y lo pasamos a MJD

        if t1 > t0:                             # si t1 es mayor que to

            for j in range(len(MJD_pos)):                  # buscamos el t2 del .txt que le siga a t1
                if MJD_pos[i] < t1:
                    continue
                if MJD_pos[i] >= t1:

                    fila_aux = np.empty([1,nchans+3])    # creamos una fila auxiliar que sumar al archivo de salid
                    fila_aux[0, 0] = MJD_pos[i]    # en la primera columna guardamos el t del .fil
                    fila_aux[0, 1] = RA_pos[i]     # en la segunda columna guardamos el RA del .txt
                    fila_axu[0, 2] = DEC_pos[i]    # en la tercera columna guardamos el DEC del .txt

                    for j in range(nchans):
                        fila_aux[0,j+3]= struct.unpack('f', f.read(pack))[0]    # cargamos las medidas en cada canal de frecuencia para ese instante

                    if base == 1:
                        fila_aux[0, 1:] -= baseline(fila_aux[0, 1:])       # calculamos la base y luego se la sacamos.

                    ltf_fil = np.vstack((ltf_fil, fila_aux))

                    if opcion == 1:                                      # si piden calcular potencia
                        aux = [fila_aux[0, 0], fila_aux[0, 1], fila_aux[0, 2], np.mean(fila_aux[0,3:])]
                        potencias = np.vstack((potencias, aux))

                    break

        else:
            continue

    if orden == "RA":
        potencias = potencias[ potencias[:,1].argsort ]

    elif orden == "DEC":
        potencias = potencias[ potencias[:,2].argsort ]

    elif orden == "MJD":
        pass

    else:
        print("Error debe ingresar una opcion válida. (MJD,DEC,RA)")

    if opcion == 0:
        np.save("ltf_fil.npy", ltf_fil)
        return ltf_fil
    elif opcion == 1:
        np.save("potencias.txt", potencias)
        return potencias

    else:
        "Error: se debe ingresar 0 para espectro o 1 para potencia"