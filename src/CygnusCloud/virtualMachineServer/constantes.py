# -*- coding: utf8 -*
'''
Created on 14/01/2013

@author: saguma
'''

createVirtualNetworkAsRoot = True

mysqlRootsPassword = ""
databaseName = "VMServerDB"
# Cuidado con esto: si está mal puesta, cascará al arrancar
vncNetworkInterface = "lo"
databaseUserName = "cygnuscloud"
databasePassword = "cygnuscloud"
listenningPort = 15800

passwordLength = 46 # Esto NO es por casualidad

# Descomentad el que uséis en vuestra máquina y comentad el resto

configFilePath = '/home/saguma/Documentos/Universidad/CygnusCloud/Configuraciones/'
sourceImagePath = '/home/saguma/Documentos/Universidad/CygnusCloud/Imagenes/'
executionImagePath = '/home/saguma/Documentos/Universidad/CygnusCloud/ImagenesEjecucion/'
websockifyPath = '/home/saguma/Descargas/kanaka-noVNC-d55f537/utils/websockify'
certificatePath = '/home/saguma/CygnusCloud/Certificados/'

#configFilePath = '/home/luis/VirtualMachineServer/configuraciones/'
#sourceImagePath = '/home/luis/VirtualMachineServer/imagenes/'
#executionImagePath = '/home/luis/VirtualMachineServer/imagenes_en_ejecucion/'
#websockifyPath = '/home/luis/VirtualMachineServer/noVNC/utils/websockify'
#certificatePath = '/home/luis/Certificates'

#Virtual network settings
vnName = "ccnet" # Quizá deberíamos cambiar de nombre: puede chocar con algunas distros
gatewayIP = "192.168.77.1"
netMask = "255.255.255.0"
dhcpStartIP = "192.168.77.2"
dhcpEndIP = "192.168.77.254"