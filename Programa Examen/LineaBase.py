import rrdtool, time, os, errno
from getSNMP import consultaSNMP, walkSNMP
from notify import sendAlertEmail

lbPath = os.getcwd() + "/rrd/lineaBase/"

def crearBasesLb(comunidad, ip, port, name):
	agentPath = lbPath + name + "/"
    	try:
        	os.makedirs(os.path.dirname(agentPath))
    	except OSError as exc:
        	if exc.errno != errno.EEXIST:
           		print("Error de directorios: Linea Base.")
            	raise

    	# 1 BD Trafico de RAM
    	ret = rrdtool.create(agentPath + name + "RAM.rrd",
        	"--start", 'N',
        	"--step", '60',
        	"DS:RAMload:COUNTER:600:U:U",
        	"RRA:AVERAGE:0.5:1:24"
    	)

    	if ret:
        	print(rrdtool.error())

    	# 2 BD Trafico de CPU

    	cores = walkSNMP(comunidad , ip , port , '1.3.6.1.2.1.25.3.3.1.2')
    	for coreOid, coreLoad in cores:
        	coreId = coreOid[(coreOid.rfind('.') + 1):]

        	ret = rrdtool.create(agentPath + name + coreId + "CPU.rrd",
            		"--start", 'N',
            		"--step", '60',
            		"DS:CPUload:GAUGE:600:U:U",
           		"RRA:AVERAGE:0.5:1:24"
        	)

        	if ret:
            		print(rrdtool.error())

    	# 3 BD Trafico de HDD
    	ret = rrdtool.create(agentPath + name + "HDD.rrd",
        	"--start", 'N',
        	"--step", '60',
        	"DS:HDDload:GAUGE:600:U:U",
        	"RRA:AVERAGE:0.5:1:24"
    	)

    	if ret:
        	print(rrdtool.error())



def EjecutarLb(monitor, comunidad, ip, port, name, times):
	agentPath = lbPath + name + "/"

    	# 1 RAM de interfaz
    	availableRam = int(consultaSNMP(comunidad, ip, port, '1.3.6.1.4.1.2021.4.6.0'))

    	value = "N:" + str(availableRam)
    	rrdtool.update(str(agentPath + name) + 'RAM.rrd', value)

	# 1 Grafica RAM de interfaz
    	finalTime = int(rrdtool.last(str(agentPath + name) + "RAM.rrd"))
    	initialTime = finalTime - 1800

    	ret = rrdtool.graphv(
		str(agentPath + name) + "RAM.png",
		"--start", str(initialTime),
		"--vertical-label=Carga RAM",
		"--title=USO DE RAM - LINEA DE BASE",
		"--color", "ARROW#009900",
		'--vertical-label', "Uso de RAM (%)",
		'--lower-limit', '0',
		'--upper-limit', '800000000',
		"DEF:carga=" + str(agentPath + name) + "RAM.rrd:RAMload:AVERAGE",

		# ---LINEA DE BASE
		"HRULE:" + str(monitor.ramRsg[0]) + "#000000:Umbral 1",
		"HRULE:" + str(monitor.ramRsg[1]) + "#00BB00:Umbral 2",
		"HRULE:" + str(monitor.ramRsg[2]) + "#BB0000:Umbral 3",

		# ---GRAFICAR AREA RAM
		"AREA:carga#00FF00:RAM Storage",

		# ---ENTRADA DE RAM
		"VDEF:RAMlast=carga,LAST",
		"VDEF:RAMmin=carga,MINIMUM",
		"VDEF:RAMavg=carga,AVERAGE",
		"VDEF:RAMmax=carga,MAXIMUM",
		"COMMENT:        Last              Now             Min                 Avg               Max//n",
		"GPRINT:RAMlast:%12.0lf%s",
		"GPRINT:RAMmin:%10.0lf%s",
		"GPRINT:RAMavg:%13.0lf%s",
		"GPRINT:RAMmax:%13.0lf%s"
	)
    
	#print("Ram: " + str(availableRam))
	if availableRam <= monitor.ramRsg[2]:
		if not monitor.ramOverflow:
	    		monitor.ramOverflow = True
	    		#print("Umbral 3 superado")
	    		sendAlertEmail(
			'Umbral de RAM superado: ' + name + ' ' + str(availableRam) + '/' + str(monitor.ramRsg[2]),
			str(agentPath + name) + 'RAM.png',
			str(agentPath + name) + 'RAM.rrd'
	    	)
	else:
		if monitor.ramOverflow:
	    		monitor.ramOverflow = False

	#-----------------------------------------------------------------------------------------
	# 2 CPU de interfaz
    
   	cores = walkSNMP(comunidad , ip , port , '1.3.6.1.2.1.25.3.3.1.2')
    	for coreOid, coreLoad in cores:
		coreId = coreOid[(coreOid.rfind('.') + 1):]
		coreLoad = int(coreLoad)

		value = "N:" + str(coreLoad)
		rrdtool.update(str(agentPath + name + coreId) + 'CPU.rrd', value)

		# 2 Grafica CPU por nucleo de interfaz
		finalTime = int(rrdtool.last(str(agentPath + name + coreId) + "CPU.rrd"))
		initialTime = finalTime - 1800

		ret = rrdtool.graphv(
		    str(agentPath + name + coreId) + "CPU.png",
		    "--start", str(initialTime),
		    "--vertical-label=Carga CPU",
		    "--title=USO DE CPU - LINEA DE BASE",
		    "--color", "ARROW#009900",
		    '--vertical-label', "Uso de CPU (%)",
		    '--lower-limit', '0',
		    '--upper-limit', '100',
		    "DEF:carga=" + str(agentPath + name + coreId) + "CPU.rrd:CPUload:AVERAGE",

		    # ---LINEA DE BASE
		    "HRULE:" + str(monitor.cpuRsg[0]) + "#000000:Umbral 1",
		    "HRULE:" + str(monitor.cpuRsg[1]) + "#00BB00:Umbral 2",
		    "HRULE:" + str(monitor.cpuRsg[2]) + "#BB0000:Umbral 3",

		    # ---GRAFICAR AREA CPU
		    "AREA:carga#00FF00:CPU load",

		    # ---ENTRADA DE CPU
		    "VDEF:CPUlast=carga,LAST",
		    "VDEF:CPUmin=carga,MINIMUM",
		    "VDEF:CPUavg=carga,AVERAGE",
		    "VDEF:CPUmax=carga,MAXIMUM",
		    "COMMENT:        Last              Now             Min                 Avg               Max//n",
		    "GPRINT:CPUlast:%12.0lf%s",
		    "GPRINT:CPUmin:%10.0lf%s",
		    "GPRINT:CPUavg:%13.0lf%s",
		    "GPRINT:CPUmax:%13.0lf%s"
		)

		#print("CoreLoad " + coreId + ": " + str(coreLoad))
		if coreLoad >=  monitor.cpuRsg[2]:
		   	if not coreId in monitor.cpuOverflow:
		        	monitor.cpuOverflow.append(coreId)
		        	#print("Umbral 3 superado")
		        	sendAlertEmail(
		            		'Umbral de CPU (' + coreId + ') superado: ' + name + ' ' + str(coreLoad) + '/' + str(monitor.cpuRsg[2]),
		            		str(agentPath + name + coreId) + 'CPU.png',
		            		str(agentPath + name + coreId) + 'CPU.rrd'
		        	)
		else:
		    	if coreId in monitor.cpuOverflow:
		        	monitor.cpuOverflow.remove(coreId)
    
    	#-----------------------------------------------------------------------------------------
    	# 3 HDD de interfaz
    	hddLoad = int(consultaSNMP(comunidad, ip, port, '1.3.6.1.2.1.25.2.3.1.6.1'))

    	value = "N:" + str(hddLoad)
    	rrdtool.update(str(agentPath + name) + 'HDD.rrd', value)

    	# 3 Grafica HDD de interfaz
    	finalTime = int(rrdtool.last(str(agentPath + name) + "HDD.rrd"))
    	initialTime = finalTime - 1800

    	ret = rrdtool.graphv(str(agentPath + name) +"HDD.png",
		"--start", str(initialTime),
		"--vertical-label=Carga HDD",
		"--title=USO DE HDD - LINEA DE BASE",
		"--color", "ARROW#009900",
		'--vertical-label', "Uso de HDD (%)",
		'--lower-limit', '0',
		'--upper-limit', '10000000',
		"DEF:carga=" + str(agentPath + name) + "HDD.rrd:HDDload:AVERAGE",

		# ---LINEA DE BASE
		"HRULE:" + str(monitor.hddRsg[0]) + "#000000:Umbral 1",
		"HRULE:" + str(monitor.hddRsg[1]) + "#00BB00:Umbral 2",
		"HRULE:" + str(monitor.hddRsg[2]) + "#BB0000:Umbral 3",

		# ---GRAFICAR AREA HDD
		"AREA:carga#00FF00:HDD load",

		# ---ENTRADA DE HDD
		"VDEF:HDDlast=carga,LAST",
		"VDEF:HDDmin=carga,MINIMUM",
		"VDEF:HDDavg=carga,AVERAGE",
		"VDEF:HDDmax=carga,MAXIMUM",
		"COMMENT:        Last              Now             Min                 Avg               Max//n",
		"GPRINT:HDDlast:%12.0lf%s",
		"GPRINT:HDDmin:%10.0lf%s",
		"GPRINT:HDDavg:%13.0lf%s",
		"GPRINT:HDDmax:%13.0lf%s"
    	)

    	#print("HDD: " + str(hddLoad))
    	if hddLoad >=  monitor.hddRsg[2]:
        	if not monitor.hddOverflow:
            		monitor.hddOverflow = True
            		#print("Umbral 3 superado")
            		sendAlertEmail(
                		'Umbral de HDD superado: ' + name + ' ' + str(hddLoad) + '/' + str(monitor.hddRsg[2]),
                		str(agentPath + name) + 'HDD.png',
                		str(agentPath + name) + 'HDD.rrd'
            		)

    	else:
        	if monitor.hddOverflow:
            		monitor.hddOverflow = False
