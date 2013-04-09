# -*- coding: utf8 -*-
'''
This module contains statements to connect to a virtual machine
server and control it.
@author: Luis Barrios Hernández
@version: 6.3
'''
from __future__ import print_function

from network.manager.networkManager import NetworkManager, NetworkCallback
from network.exceptions.networkManager import NetworkManagerException
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T
from time import sleep

class TesterCallback(NetworkCallback):
    def __init__(self, packetHandler):
        self.__pHandler = packetHandler
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket(packet)
        packet_type = data["packet_type"]
        if (packet_type == VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA) :
            print("Domain connection data: ")
            print("VNC server IP address: " + data["VNCServerIP"])
            print("VNC server port: " + str(data["VNCServerPort"]))
            print("VNC server password: " + data["VNCServerPassword"])
        elif (packet_type == VM_SERVER_PACKET_T.SERVER_STATUS) :
            print("Virtual machine server status:")
            print("Active VMs: " + str(data["ActiveDomains"]))
            print("RAM: " + str(data["RAMInUse"]) +  "KB of " + str(data["RAMSize"]) + "KB in use")
            print("Storage space: " + str(data["FreeStorageSpace"]) +  "KB of " + str(data["AvailableStorageSpace"]) + "KB available")
            print("Temporary space: " + str(data["FreeTemporarySpace"]) +  "KB of " + str(data["AvailableTemporarySpace"]) + "KB available")
            print("Active VCPUs: " + str(data["ActiveVCPUs"]))
            print("Real CPUs: " + str(data["RealCPUs"]))
        elif (packet_type == VM_SERVER_PACKET_T.ACTIVE_VM_DATA) :
            print("Virtual machines' connection data")
            print(packet._getData())
        else :
            print("Error: a packet from an unexpected type has been received "+packet_type)
       

def printLogo():
    print('\t   _____                             _____ _                 _ ')
    print('\t  / ____|                           / ____| |               | |')
    print('\t | |    _   _  __ _ _ __  _   _ ___| |    | | ___  _   _  __| |')
    print('\t | |   | | | |/ _` | \'_ \| | | / __| |    | |/ _ \| | | |/ _` |')
    print('\t | |___| |_| | (_| | | | | |_| \__ \ |____| | (_) | |_| | (_| |')
    print('\t  \_____\__, |\__, |_| |_|\__,_|___/\_____|_|\___/ \__,_|\__,_|')
    print('\t         __/ | __/ |                                           ')
    print('\t        |___/ |___/ ')
    print()
    
def process_command(tokens, networkManager, pHandler, ip_address, port):
    if (len(tokens) == 0) :
        return False
    try :
        command = tokens.pop(0)
        if (command == "createvm") :
            userID = int(tokens.pop(0))
            machineID = int(tokens.pop(0))
            commandID = tokens.pop(0)
            p = pHandler.createVMBootPacket(userID, machineID, commandID)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "destroyvm") :
            machineID = tokens.pop(0)
            p = pHandler.createVMShutdownPacket(machineID)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "shutdown") :
            p = pHandler.createVMServerShutdownPacket()
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "status") :
            p = pHandler.createVMServerDataRequestPacket(VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "readConnectionData") :
            p = pHandler.createVMServerDataRequestPacket(VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "halt" ) :
            p = pHandler.createVMServerHaltPacket()
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "quit") :
            return True
        else :
            if (command != "help") :
                print("Error: unknown command")
            print("Usage: ")
            print("=====")
            print("\tcreatevm <userID> <machineID> <commandID> : creates a virtual machine ")
            print("\tshutdown: asks the virtual machine server to terminate")
            print("\tstatus: asks the virtual machine server the number of active VMs")
            print("\thalt: commands the virtual machine server to destroy all the virtual machines\n\t\t\
                and exit immediately")
            print("\thelp: prints the following help message")
            print("\tquit: closes this application")
    except Exception as e :
        print("Error: " + e.message)
    

if __name__ == "__main__" :
    print('*' * 80)
    print('*' * 80)
    printLogo()
    print('Virtual Machine Server tester')
    print('Version 6.3')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager("/home/luis/Certificates")
    networkManager.startNetworkService()
    # Create the packet handler
    pHandler = VMServerPacketHandler(networkManager)
    # Ask for the port and the IP address
    ip_address = raw_input("Server IP address: ")
    port = raw_input("Server port: ")
    try :
        port = int(port)
        networkManager.connectTo(ip_address, port, 10, TesterCallback(pHandler), True)
        while not networkManager.isConnectionReady(ip_address, port) :
            sleep(0.1)
        end = False
        while not end :
            command = raw_input('>')
            tokens = command.split()
            end = process_command(tokens, networkManager, pHandler, ip_address, port)
    
    except NetworkManagerException as e:
        print("Error: " + e.message)
    networkManager.stopNetworkService()
    
    
