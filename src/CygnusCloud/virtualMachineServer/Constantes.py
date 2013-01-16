'''
Created on 14/01/2013

@author: saguma
'''

serverIP = '127.0.0.1'
serverPort = 8080
listenPort = 8080

websocketServerIP = '127.0.0.1'

passwordLength = 64

userDB = 'CygnusCloud'
passwordDB = 'cygnuscloud2012' 
DBname = 'DBVMServer'
userDBMac = 'CygnusCloud'
passwordDBMac = 'cygnuscloud2012' 
DBnameMac = 'DBVMServer'

ConfigFilePath = '/home/luis/kvm-images/'
SourceImagePath = '/home/luis/kvm-images/'
ExecutionImagePath = '/home/luis/runningInstances/'
websockifyPath = '/home/luis/websockify/websockify'

ConnectionDataPriority = 5

#Virtual network settings
VNName = "default" # Changed it
gatewayIP = "192.168.77.1"
NetMask = "255.255.255.0"
DHCPStartIP = "192.168.77.2"
DHCPEndIP = "192.168.77.254"