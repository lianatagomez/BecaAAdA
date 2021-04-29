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

#abrimos los canales

    header = sigproc.read_header(filename)
    f=open(filename,"rb")
    nchans = int(header[0].get("nchans"))
    f.seek(header[1]) # le dice a la estructura f que ubique al puntero en una cierta pos



    # abre el archivo con los valores de tiempo ltf.
    time_fil=filename[0:len(filename)-4]+'.ltf'  # nombre del archivo .ltf
    time_file=open(time_fil,"r")                 # abre el archivo .ltf}

    pos_fil = filename[0:len(filename)-4]+'.txt'
    pos_file = open(pos_fil,"r")

    MJD_pos = np.loadtxt(pos_fil, usecols=0) #guardas en el array lo que esta en eL pos_file en la columna cero
    RA_pos = np.loadtxt(pos_fil,usecols=5) #guardamos los datos de ascencion recta de la 5ta columna
    DEC_pos = np.loadtxt(pos_fil, usecols=7) #lo mismo pero de la declinacion en la 7ma col

    b = os.path.getsize(filename)
    size=int(header[0].get("nbits"))      # del header saca el tamaño en bits
    pack=size/8
    espectros=(((b-header[1])/pack)/nchans)-1 #Calculo del total de espectos disponibles en# el FIL
    RA_pos_FILTRADO = []
    DEC_pos_FILTRADO = []
    #crear el array con las dimensiones y "rellenarlo" con los datos que estan en los archivos

    #con esto completamos la primera columna con los tiempos
    ltf_fil= np.empty([0,nchans+1])
    potencias = np.empty([0,2])


    t0 = MJD_pos[0]
    for i in range(espectros):
        t_aux=str(time_file.readline())[0:26]
        t1 = Time(t_aux, format='isot').mjd

        if t1 > t0:  # luego definimos un afila auxiliar que le queremos agregar despues con una sola fila y tantas columnas como canales +1

            for t2 in MJD_pos:
                if t2 < t1:
                    continue
                if t2 > t1:

                    fila_aux = np.empty([1,nchans+1])
                    fila_aux[0, 0] = t1 #aqui guardamos el mjd en la primera col de la fila_aux
                    #RA_pos_FILTRADO.append(RA_pos[np.argwhere(abs(MJD_pos-t1) < 8.E-7)[0]][0])
                    RA_pos_FILTRADO.append(RA_pos[np.argwhere(MJD_pos==t0)[0]][0])
#ACA ESTA EL PROBLEMA, CON EL CRITERIO DEL MATCH, SI USAMOS UNA TOLERANCIA CHICA NO HAY Y SI ES MUY GRANDE HAY DEMASIADOS Y MANDA A TODOS A LA MISMA RA
                    DEC_pos_FILTRADO.append(DEC_pos[np.argwhere(MJD_pos==t0) [0]][0])
                    #para cada canal desempacamos lo que habia en c/u y lo metemos en el resto de las columnas
                    for j in range(nchans):
                        fila_aux[0,j+1]= struct.unpack('f', f.read(pack))[0]

                    t0 = t2

                    if base == 1:#calculamos la base y luego se la sacamos.
                        baseline_values = baseline(fila_aux[0,1:])
                        fila_aux[0,1:] -= baseline_values
                            # para cada fila promediar para sacar la potencia

                    ltf_fil = np.vstack((ltf_fil,fila_aux))

                    if opcion == 1:
                        aux =[t1, np.mean(fila_aux[0,1:])]


                        potencias = np.vstack((potencias, aux))

                    break


        else:
            continue

    if orden == "RA":
        potencias2 = np.empty([len(potencias),2])
        indices = np.argsort(RA_pos_FILTRADO)

        for i in range(len(indices)):
            potencias2[i,0] = RA_pos_FILTRADO[indices[i]]
            potencias2[i,1] = potencias[indices[i],1]
        potencias = potencias2

    elif orden == "DEC":
        potencias2 = np.empty([len(potencias),2])
        indices = np.argsort(DEC_pos_FILTRADO)
        for i in range(len(indices)):
            potencias2[i,0] = DEC_pos_FILTRADO[indices[i]]
            potencias2[i,1] = potencias[indices[i],1]
        potencias = potencias2
    elif orden == "MJD":
        pass
    else:
        print("Error debe ingresar una opcion válida. (MJD,DEC,RA)")

    if opcion == 0:
        np.save("ltf_fil.npy",ltf_fil)
        return ltf_fil
    elif opcion == 1:
        np.save("potencias.txt",potencias)
        return potencias

    else:
        "Error: se debe ingresar 0 para espectro o 1 para potencia"


