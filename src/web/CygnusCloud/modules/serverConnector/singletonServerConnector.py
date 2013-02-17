# -*- coding: utf-8 -*-
from serverConnector.constants import rootPassword,certificatesPath,dbStatusName,webUserName,webUserPass,updateUserName,updateUserPass,serverIp, \
    serverPort,statusInterval,dbStatusPath
from clusterServer.connector.clusterServerConnector import ClusterServerConnector
from clusterServer.connector.clusterServerConnector import GenericWebCallback

class Singleton(object):
	staticConnector = None # None la primera vez. Después, no
	
	@staticmethod
	def getInstance():
		if (Singleton.staticConnector == None) :
			print "Entra en el singleton"
			# El atributo estático no está inicializado => lo inicializamos
			staticConnector = ClusterServerConnector(GenericWebCallback())
			staticConnector.connectToDatabase(rootPassword,dbStatusName,dbStatusPath, webUserName, webUserPass,updateUserName, updateUserPass)
			staticConnector.connectToClusterServer(certificatesPath,True,serverIp ,serverPort, statusInterval)
		return staticConnector
