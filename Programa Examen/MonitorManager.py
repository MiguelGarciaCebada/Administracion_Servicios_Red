import json
import threading, time
import os.path
from Procesamiento import crearBases
from Procesamiento import crearBaseHW
from Procesamiento import Ejecutar
from pysnmp.hlapi import *
from Monitor import Monitor
from getSNMP import consultaSNMP
from LineaBase import crearBasesLb
from MinimoCuadrado import EjecutarMC


class MonitorManager():
	def __init__(self):
		self.data = {}
		self.data['agents'] = [] 
		self.pool = {}

		if os.path.exists('agents.json'):
			with open('agents.json', 'r') as f:
				self.data = json.load(f)
			for agent in self.data['agents']:
				t = Monitor(agent)
				self.pool.update({agent['idAgent']: t})
				t.start()


	def consulta( self , idAgent ):
		encontrado = False
		for agent in self.data['agents']:
			if idAgent==agent['idAgent']:
				print("Informacion del agentes")
				print( "Nombre del host: " + agent['idAgent'] )
				print( "IP del host: " + agent['hostname'] )
				print( "Version: " + agent['version'] )
				print( "Numero de Interfaces de Red: " + consultaSNMP( agent['comunity'] , agent['hostname'] ,'1.3.6.1.2.1.2.1.0') )
				print( "Tiempo actividad desde ult reset: " + consultaSNMP( agent['comunity'] , agent['hostname'] ,'1.3.6.1.2.1.1.3.0') )
				print( "Ubicacion fisica: " + consultaSNMP( agent['comunity'] , agent['hostname'] ,'1.3.6.1.2.1.1.6.0') )
				print( "Contacto admin: " + consultaSNMP( agent['comunity'] , agent['hostname'] ,'1.3.6.1.2.1.1.4.0') )
				print
				encontrado = True
		return encontrado


	def showAll(self):
		print("Numero de agentes: " + str(len(self.pool)))

		for t in self.pool.values():
			try:
				numInts = int(t.getAgentInfo('1.3.6.1.2.1.2.1.0'))
				print(" * "  + t.agent['idAgent'] + " : " + str(numInts) + " Interfaces de Red")
				for i in range(1, numInts + 1):
					print("\t - Interfaz " + str(i) + " (" + self.getStatus(int(t.getAgentInfo('1.3.6.1.2.1.2.2.1.8.' + str(i)))) + ")")
			except:
				print(" * "  + t.agent['idAgent'] + " : Sin acceso a ifNumber.")



	def getStatus(self, status):
		if status == 1:
			return "up"
		elif status == 2:
			return "down"
		else:
			return "testing"


	def addAgent(
		self, idAgent, hostname, version, port, comunity,
		ramReady, ramSet, ramGo,
		cpuReady, cpuSet, cpuGo,
		hddReady, hddSet, hddGo
	):		
		
		if idAgent in self.pool:
			return False

		tiempo_actual = int(time.time())		

		newAgent = {  
		    'idAgent': idAgent,
		    'hostname': hostname,
		    'version': version,
		    'port': port,
		    'comunity': comunity,
		    'time': tiempo_actual,	
		    'ramReady': ramReady,
		    'ramSet': ramSet,
		    'ramGo': ramGo,
		    'cpuReady': cpuReady,
		    'cpuSet': cpuSet,
		    'cpuGo': cpuGo,
		    'hddReady': hddReady,
		    'hddSet': hddSet,
		    'hddGo': hddGo
		}

		t = Monitor(newAgent)
		self.pool.update({idAgent: t})
		t.start()

		self.data['agents'].append(newAgent)
		with open('agents.json', 'w') as f:
		    json.dump(self.data, f)

		crearBases( idAgent )	
		crearBaseHW( idAgent )	
		crearBasesLb( comunity, hostname, port, idAgent ) 	

		return True

	def removeAgent(self, idAgent):
		if not idAgent in self.pool:
			return False
		else:
			self.pool[idAgent].join()
			a = self.pool.pop(idAgent)
			self.data['agents'].remove(a.agent)

			with open('agents.json', 'w') as f:
			    json.dump(self.data, f)
			return True



	def minimosCuadrados(self, name, varName, initialTime, finalTime, umbral):
		EjecutarMC(name, varName, initialTime, finalTime, umbral)
