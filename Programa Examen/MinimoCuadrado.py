import rrdtool , time , os , errno
from getSNMP import consultaSNMP
from os.path import basename

mcPath = os.getcwd() + "/rrd/minimosCuadrados/"

def EjecutarMC( rrdpath , varName , initialTime , finalTime , umbral ):

	try:
                os.makedirs(os.path.dirname(mcPath))
        except OSError as exc:
                if exc.errno != errno.EEXIST:
                        print("Error de directorios: Minimos Cuadrados.")
			raise
	
	name = basename(rrdpath)
	name = name[:(name.rfind('.'))]

	ret = rrdtool.graph( str(mcPath + name) + ".png",
                 "--start", str(initialTime),
                 "--end",str(finalTime),
                 "--vertical-label=Carga CPU",
                 "--title=MINIMOS CUADRADOS",
                 "--color", "ARROW#009900",
                 '--vertical-label', "Carga",
                 '--lower-limit', '0',
                 '--upper-limit', '100',

                 # ---CARGAS
                 "DEF:carga=" + rrdpath + ".rrd:"+varName+":AVERAGE",

                 # ---GRAFICAR AREA RAM
                 "AREA:carga#00FF00:CPU load",

                 # ---LINEA DE BASE
                 #"HRULE:30#000000:Umbral 1",
                 #"HRULE:35#00BB00:Umbral 2",
                 "HRULE:"+str(umbral)+"#BB0000:Umbral",

                 # ---ENTRADA DE CPU
                 "LINE1:30",
                 #"AREA:5#ff000022:stack",
                 "VDEF:CPUlast=carga,LAST",
                 "VDEF:CPUmin=carga,MINIMUM",
                 "VDEF:CPUavg=carga,AVERAGE",
                 "VDEF:CPUmax=carga,MAXIMUM",
                 "COMMENT:          Now             Min               Avg                Max",
                 "GPRINT:CPUlast:%12.0lf%s",
                 "GPRINT:CPUmin:%10.0lf%s",
                 "GPRINT:CPUavg:%13.0lf%s",
                 "GPRINT:CPUmax:%13.0lf%s",

                 # ---METODO DE MINIMOS CUADRADOS
                 "VDEF:a=carga,LSLSLOPE",
                 "VDEF:b=carga,LSLINT",
                 'CDEF:avg2=carga,POP,a,COUNT,*,b,+',
                 "LINE2:avg2#FFBB00",

		# ---Punto
		'CDEF:cintersect=avg2,0,EQ,avg2,0,IF,'+str(umbral)+',+,a,/,b,+,100,/,3600,*,'+initialTime+',+',
		#'CDEF:Cintersect=avg2,'+str(umbral)+',EQ,avg2,0,IF',
		"VDEF:pintersect=cintersect,MAXIMUM",
		"COMMENT: Punto",
		"GPRINT:pintersect:%8.0lf",
 	)

	print("Archivo generado en " + mcPath)
	
