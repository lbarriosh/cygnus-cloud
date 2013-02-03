# -*- coding: utf8 -*
'''
Created on 14/01/2013

@author: saguma
'''

mysqlRootsPassword = ""
databaseName = "VMServerDB"
# Cuidado con esto: si está mal puesta, cascará al arrancar
vncNetworkInterface = "eth0"
databaseUserName = "cygnuscloud"
databasePassword = "cygnuscloud"
listenningPort = 15800

passwordLength = 64

# Descomentad el que uséis en vuestra máquina y comentad el resto

#ConfigFilePath = '/home/saguma/Documentos/Universidad/CygnusCloud/Configuraciones/'
#SourceImagePath = '/home/saguma/Documentos/Universidad/CygnusCloud/Imagenes/'
#ExecutionImagePath = '/home/saguma/Documentos/Universidad/CygnusCloud/ImagenesEjecucion/'
#websockifyPath = '/home/saguma/Descargas/kanaka-noVNC-d55f537/utils/websockify'

ConfigFilePath = '/home/luis/VirtualMachineServer/configuraciones/'
SourceImagePath = '/home/luis/VirtualMachineServer/imagenes/'
ExecutionImagePath = '/home/luis/VirtualMachineServer/imagenes_en_ejecucion/'
websockifyPath = '/home/luis/VirtualMachineServer/noVNC/utils/websockify'
CertificatePath = '/home/luis/Certificates'

#Virtual network settings
VNName = "ccnet" # Quizá deberíamos cambiar de nombre: puede chocar con algunas distros
gatewayIP = "192.168.77.1"
NetMask = "255.255.255.0"
DHCPStartIP = "192.168.77.2"
DHCPEndIP = "192.168.77.254"