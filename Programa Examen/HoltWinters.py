import rrdtool, time
from getSNMP import consultaSNMP
from Notify import check_aberration



def HW( ):
	createBD()
	prediction()
	graph()
	

def createBD():

	print("wea") 


def prediction():
	total_input_traffic = 0
	total_output_traffic = 0

	fname="netPred.rrd"

	while 1:
		total_input_traffic = int(consultaSNMP('comunidadEquipo2_grupo4CM3','localhost',161,'1.3.6.1.2.1.2.2.1.10.1'))
		total_output_traffic = int(consultaSNMP('comunidadEquipo2_grupo4CM3','localhost',161,'1.3.6.1.2.1.2.2.1.16.1'))

		valor = str(rrdtool.last(fname)+100)+":" + str(total_input_traffic)
		ret = rrdtool.update(fname, valor)
		rrdtool.dump(fname,'netP.xml')
		time.sleep(1)
		graph()

	if ret:
		print (rrdtool.error())
		time.sleep(300)




def graph():
	fname="netPred.rrd"
	title="Deteccion de comportamiento anomalo, valor de Alpha 0.1"
	endDate = rrdtool.last(fname) #ultimo valor del XML
	begDate = endDate - 36000

	rrdtool.tune(fname,'--alpha','0.1')
	ret = rrdtool.graph("netPalphaBajoFallas.png",
                        '--start', str(begDate), '--end', str(endDate), '--title=' + title,
                        "--vertical-label=Bytes/s",
                        '--slope-mode',
                        "DEF:obs="       + fname + ":inoctets:AVERAGE",
                        "DEF:outoctets=" + fname + ":outoctets:AVERAGE",
                        "DEF:pred="      + fname + ":inoctets:HWPREDICT",
                        "DEF:dev="       + fname + ":inoctets:DEVPREDICT",
                        "DEF:fail="      + fname + ":inoctets:FAILURES",

                     #"RRA:DEVSEASONAL:1d:0.1:2",
                     #"RRA:DEVPREDICT:5d:5",
                     #"RRA:FAILURES:1d:7:9:5""
                        "CDEF:scaledobs=obs,8,*",
                        "CDEF:upper=pred,dev,2,*,+",
                        "CDEF:lower=pred,dev,2,*,-",
                        "CDEF:scaledupper=upper,8,*",
                        "CDEF:scaledlower=lower,8,*",
                        "CDEF:scaledpred=pred,8,*",
                        "TICK:fail#FDD017:1.0:Fallas",
                        "LINE3:scaledobs#00FF00:In traffic",
                        "LINE1:scaledpred#FF00FF:Prediccion\\n",
                        "LINE1:outoctets#0000FF:Out traffic",
                        "LINE1:scaledupper#ff0000:Upper Bound Average bits in\\n",
                        "LINE1:scaledlower#0000FF:Lower Bound Average bits in")
