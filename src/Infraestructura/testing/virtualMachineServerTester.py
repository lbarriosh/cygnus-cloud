# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: virtualMachineServerTester.py    
    Version: 8.0
    Description: virtual machine server tester
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín
        
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from __future__ import print_function

from network.manager.networkManager import NetworkManager, NetworkCallback
from network.exceptions.networkManager import NetworkManagerException
from virtualMachineServer.packetHandling.packetHandler import VMServerPacketHandler
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T
from time import sleep

class TesterCallback(NetworkCallback):
    def __init__(self, packetHandler):
        self.__repositoryPacketHandler = packetHandler
        
    def processPacket(self, packet):
        data = self.__repositoryPacketHandler.readPacket(packet)
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
            print("Active CPUs: " + str(data["ActiveVCPUs"]))
            print("Physical CPUs: " + str(data["PhysicalCPUs"]))
        elif (packet_type == VM_SERVER_PACKET_T.ACTIVE_VM_DATA) :
            print("Virtual machines' connection data")
            print(packet._getData())
        elif (packet_type == VM_SERVER_PACKET_T.ACTIVE_DOMAIN_UIDS):
            print("Active domain IDs: " + str(data["Domain_UIDs"]))
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR) :
            print("Image edition error: " + str(data["ErrorDescription"]))  
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_DELETION_ERROR) :
            print("Image deletion error: " + str(data["ErrorDescription"]))
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_DEPLOYMENT_ERROR):
            print("Image deployment error: " + str(data["ErrorDescription"]))
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITED):
            print("The virtual machine server says: the image {0} has been edited".format(data["ImageID"]))
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_DELETED):
            print("The virtual machine server says: the image deletion request has been processed")
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_DEPLOYED):
            print("The virtual machine server says: the image deployment request has been processed")
        elif (packet_type == VM_SERVER_PACKET_T.INTERNAL_ERROR):
            print("The virtual machine server says: internal error")
        else :
            print("Error: a packet from an unexpected type has been received "+ str(packet_type))       

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
            machineID = int(tokens.pop(0))
            userID = int(tokens.pop(0))
            commandID = tokens.pop(0)
            p = pHandler.createVMBootPacket(machineID, userID, commandID)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "destroyvm") :
            machineID = tokens.pop(0)
            p = pHandler.createVMShutdownPacket(machineID)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "rebootvm") :
            machineID = tokens.pop(0)
            p = pHandler.createVMRebootPacket(machineID)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "rebootvm"):
            machineID = tokens.pop(0)
            p = pHandler.createVMRebootPacket(machineID)
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
        elif (command == "getConnectionData") :
            p = pHandler.createVMServerDataRequestPacket(VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "halt" ) :
            p = pHandler.createVMServerHaltPacket()
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "editImage") :
            p = pHandler.createImageEditionPacket(tokens.pop(0), int(tokens.pop(0)), int(tokens.pop(0)), tokens.pop(0) == "True", "1", 1)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "deployImage"):
            p = pHandler.createImageDeploymentPacket(tokens.pop(0), int(tokens.pop(0)), int(tokens.pop(0)), "1")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "deleteImage") :
            p = pHandler.createDeleteImagePacket(int(tokens.pop(0)), "1")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "quit") :
            return True
        else :
            if (command != "help") :
                print("Error: unknown command")
            print("Usage: ")
            print("=====")
            print("\tcreatevm <imageID> <userID> <machineID> : creates a virtual machine ")
            print("\tdestroyvm <machineID>: destroys an active virtual machine")
            print("\trebootvm <machineID>: reboots an active virtual machine")
            print("\tshutdown: asks the virtual machine server to terminate")
            print("\tstatus: asks the virtual machine server for the number of active VMs")
            print("\tgetConnectionData: asks the virtual machine server for the active VMs' VNC connection data")
            print("\teditImage <ImageRepositoryIP> <ImageRepositoryPort> <ImageID> <Modify>: creates or edits an image in the virtual machine server")
            print("\tdeployImage <ImageRepositoryIP> <ImageRepositoryPort> <ImageID>: deploys an existing image in the virtual machine server")
            print("\tdeleteImage <ImageID>: deletes an image from the virtual machine server")
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
    print('Version 8.0')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager(".")
    networkManager.startNetworkService()
    pHandler = VMServerPacketHandler(networkManager)
    ip_address = raw_input("VM Server IP address: ")
    port = raw_input("VM Server control connection port: ")
    try :
        port = int(port)
        networkManager.connectTo(ip_address, port, 10, TesterCallback(pHandler), True)
        while not networkManager.isConnectionReady(ip_address, port) :
            sleep(0.1)
        end = False
        while not end :
            command = raw_input('> ')
            tokens = command.split()
            end = process_command(tokens, networkManager, pHandler, ip_address, port)
    
    except NetworkManagerException as e:
        print("Error: " + e.message)
    networkManager.stopNetworkService()