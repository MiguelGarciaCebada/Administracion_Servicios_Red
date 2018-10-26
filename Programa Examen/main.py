from MonitorManager import MonitorManager
from MinimoCuadrado import EjecutarMC
from HoltWinters import HW
import rrdtool, time

mm = MonitorManager()
mm.addAgent( 'local' , 'localhost' , 'v2c' , 161 , 'comunidadEquipo2_grupo4CM3' , 
		800000000, 700000000, 600000000,
		20, 60, 90,
		5500000, 6000000, 7000000)

def main():
	print("Examen")
	menu()


def menu():
	while 1:
		print("1. Inicio")
		print("2. Agregar Agente")
		print("3. Eliminar Agente")
		print("4. Estado agente")
		print("5. Calculo Minimos Cuadrados")
		print("6. Salir")
		print
		opc = input()

		if opc == 1:
			mm.showAll()


		if opc == 2:
			idAgente = raw_input("IdAgente: ")
			hostname = raw_input("Hostname: ")
			version = raw_input("Version: ")
			port = int(raw_input("Port: "))
			comunity = raw_input("Comunity: ")

			ramReady = 800000000
			ramSet = 700000000
			ramGo = 600000000
			cpuReady = 20
			cpuSet = 60
			cpuGo = 90
			hddReady = 5500000
			hddSet = 6000000
			hddGo = 7000000

			confOpc = raw_input("Desea configurar los umbrales de rendimiento? s/n")
			if confOpc == "s":
				ramReady = raw_input("RAM (ready): ")
				ramSet = raw_input("RAM (set): ")
				ramGo = raw_input("RAM (go): ")
				cpuReady = raw_input("CPU (ready): ")
				cpuSet = raw_input("CPU (set): ")
				cpuGo = raw_input("CPU (go): ")
				hddReady = raw_input("HDD (ready): ")
				hddSet = raw_input("HDD (set): ")
				hddGo = raw_input("HDD (go): ")

			if mm.addAgent(
				idAgente, hostname, version, port, comunity,
				ramReady, ramSet, ramGo,
				cpuReady, cpuSet, cpuGo,
				hddReady, hddSet, hddGo
			):
				print(idAgente + " registrado.")
			else:
				print("Ya existe el idAgente.")



		if opc == 3:
			idAgente = raw_input("IdAgente: ")
			if mm.removeAgent(idAgente):
				print(idAgente + " eliminado.")
			else:
				print("No se encontro el idAgente.")


		if opc == 4:
			idAgente = raw_input("IdAgente: ")
			if not mm.consulta(idAgente):
				print("No se encontro el idAgente.")
			

		if opc == 5:
			nombreArchivo = raw_input("Nombre rrd: ")
			varName = raw_input("Nombre de variable rrd: ")
			inicio = raw_input("Tiempo Inicio: ")
			fin = raw_input("Tiempo Final: ")
			umbral = raw_input("Umbral: ")
			mm.minimosCuadrados( nombreArchivo , varName , inicio , fin , umbral )


		if opc == 6:
			print("Cerrando monitores.")
			break;

main()
