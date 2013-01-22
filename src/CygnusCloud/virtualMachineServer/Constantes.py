'''
Created on 14/01/2013

@author: saguma
'''

serverIP = '127.0.0.1'
serverPort = 15800
listenPort = 15800

websocketServerIP = '127.0.0.1'

passwordLength = 64

userDB = 'CygnusCloud'
passwordDB = 'cygnuscloud2012' 
DBname = 'DBVMServer'
userDBMac = 'CygnusCloud'
passwordDBMac = 'cygnuscloud2012' 
DBnameMac = 'DBVMServer'

ConfigFilePath = '/home/saguma/Documentos/Universidad/CygnusCloud/Configuraciones/'
SourceImagePath = '/home/saguma/Documentos/Universidad/CygnusCloud/Imagenes/'
ExecutionImagePath = '/home/saguma/Documentos/Universidad/CygnusCloud/ImagenesEjecucion/'
websockifyPath = '/home/saguma/Descargas/kanaka-noVNC-d55f537/utils/websockify'

ConnectionDataPriority = 5

#Virtual network settings
VNName = "default" # Changed it
gatewayIP = "192.168.77.1"
NetMask = "255.255.255.0"
DHCPStartIP = "192.168.77.2"
DHCPEndIP = "192.168.77.254"