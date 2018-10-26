from pysnmp.hlapi import *

def consultaSNMP(comunidad,host,puerto,oid):
	errorIndication, errorStatus, errorIndex, varBinds = next(
	        getCmd(SnmpEngine(),
              		CommunityData(comunidad),
               		UdpTransportTarget((host, puerto)),
               		ContextData(),
               		ObjectType(ObjectIdentity(oid))))

    	if errorIndication:
        	print(errorIndication)
    	elif errorStatus:
        	print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    	else:
        	for oid, value in varBinds:
           		resultado = value.prettyPrint()
    	return resultado


def walkSNMP(comunidad, host, puerto, oid):
  	objects = []
  	for(errorIndication,
    		errorStatus,
    		errorIndex,
    		varBinds
  	) in nextCmd(SnmpEngine(), 
    		CommunityData(comunidad),
    		UdpTransportTarget((host, puerto)),
    		ContextData(),                                                           
    		ObjectType(ObjectIdentity(oid)),
    		lexicographicMode=False
  	):
    		if errorIndication:
      			print(errorIndication)
    		elif errorStatus:
      			print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    		else:
      			for oid, value in varBinds:
        			objects.append((oid.prettyPrint(), value.prettyPrint()))
	return objects
