# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterServerTester.py    
    Version: 7.0
    Description: cluster server tester
    
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
from clusterServer.packetHandling.packetHandler import ClusterServerPacketHandler
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from time import sleep

class TesterCallback(NetworkCallback):
    def __init__(self, clusterServerPacketHandler):
        self.__repositoryPacketHandler = clusterServerPacketHandler
        
    def processPacket(self, packet):
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            print("Virtual machine server registration error")
            print("\tReason: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA or data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA or
              data["packet_type"] == PACKET_T.VM_SERVERS_RESOURCE_USAGE) :
            print("Virtual machine servers' current status")
            print("\tSegment " + str(data["Segment"]) + " of " + str(data["SequenceSize"]))
            for row in data["Data"] :
                print(row)
        elif (data["packet_type"] == PACKET_T.VM_SERVER_BOOTUP_ERROR):
            print("Virtual machine server bootup error")
            print("\tReason: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.VM_SERVER_UNREGISTRATION_ERROR):
            print("Virtual machine server unregistration error")
            print("\tReason: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.VM_SERVER_SHUTDOWN_ERROR):
            print("Virtual machine server shutdown error")
            print("\tReason: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE):
            print("Virtual machine boot failure")
            print("\tReason: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
            print("Virtual machine connection data")
            print("\tVNC server IP address: " + data["VNCServerIPAddress"])
            print("\tVNC server port: " + str(data["VNCServerPort"]))
            print("\tVNC server password: " + data["VNCServerPassword"])
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_VNC_DATA) :
            print("VNC connection data")
            print("\tSegment " + str(data["Segment"]) + " of " + str(data["SequenceSize"]))
            print("\tVNC server IP address: " + data["VMServerIP"])
            print("\t" + str(data["Data"]))
        elif (data["packet_type"] == PACKET_T.DOMAIN_DESTRUCTION_ERROR) :
            print("Domain destruction error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR) :
            print("Virtual machine configuration change error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.REPOSITORY_STATUS):
            print("Image repository status: {0} KB free, {1} KB in use, {2}".format(data["FreeDiskSpace"], data["AvailableDiskSpace"],
                                                                                    data["RepositoryStatus"]))
        elif (data["packet_type"] == PACKET_T.IMAGE_DEPLOYMENT_ERROR):
            print("Image deployment error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR):
            print("Image deletion error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.IMAGE_CREATION_ERROR):
            print("Image creation error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.IMAGE_EDITION_ERROR):
            print("Image edition error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR):
            print("Image deletion error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.AUTO_DEPLOY_ERROR):
            print("Image auto-deployment error: " + str(data["ErrorDescription"]))
        elif (data["packet_type"] == PACKET_T.COMMAND_EXECUTED):
            print("The cluster server says: command executed successfully")

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
        if (command == "registerVMServer") :
            ip = tokens.pop(0)
            serverPort = int(tokens.pop(0))
            name = tokens.pop(0)
            isEditionServer = tokens.pop(0) == "True"
            p = pHandler.createVMServerRegistrationPacket(ip, serverPort, name, isEditionServer, '')
            networkManager.sendPacket(ip_address, port, p)
            return False  
        elif (command == "obtainVMServerConfiguration") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "obtainVMDistributionData") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "obtainVMServerResourceUsage"):
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_RESOURCE_USAGE)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "unregisterVMServer") :
            p = pHandler.createVMServerUnregistrationOrShutdownPacket(tokens.pop(0), bool(tokens.pop(0)), True, "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "shutdownVMServer") :
            p = pHandler.createVMServerUnregistrationOrShutdownPacket(tokens.pop(0), bool(tokens.pop(0)), False, "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "bootUpVMServer") :
            p = pHandler.createVMServerBootPacket(tokens.pop(0), "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "bootUpVM") :
            p = pHandler.createVMBootRequestPacket(int(tokens.pop(0)), int(tokens.pop(0)), tokens.pop(0))
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "changeVMServerConfiguration") :
            p = pHandler.createVMServerConfigurationChangePacket(tokens.pop(0), tokens.pop(0), tokens.pop(0), 
                                                                 int(tokens.pop(0)), tokens.pop(0) == "True", '')
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "halt") :
            p = pHandler.createHaltPacket(True)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "obtainActiveVMsVNCData") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_VNC_DATA)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "destroyDomain") :
            p = pHandler.createDomainDestructionPacket(tokens.pop(0), "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "rebootDomain") :
            p = pHandler.createDomainRebootPacket(tokens.pop(0), "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "obtainImageRepositoryStatus") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_REPOSITORY_STATUS)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "deployImage"):
            p = pHandler.createImageDeploymentPacket(PACKET_T.DEPLOY_IMAGE, tokens.pop(0), int(tokens.pop(0)), "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "deleteImageFromServer"):
            p = pHandler.createImageDeploymentPacket(PACKET_T.DELETE_IMAGE_FROM_SERVER, tokens.pop(0), int(tokens.pop(0)), "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "createImage") :
            p = pHandler.createImageEditionPacket(PACKET_T.CREATE_IMAGE, int(tokens.pop(0)), 1, "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "editImage") :
            p = pHandler.createImageEditionPacket(PACKET_T.EDIT_IMAGE, int(tokens.pop(0)), 1, "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "deleteImageFromInfrastructure") :
            p = pHandler.createFullImageDeletionPacket(int(tokens.pop(0)), "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "deployEditedImage") :
            p = pHandler.createAutoDeployPacket(int(tokens.pop(0)), -1, "Auto-deploy")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "autoDeployImage") :
            p = pHandler.createAutoDeployPacket(int(tokens.pop(0)), int(tokens.pop(0)), "Auto-deploy")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "quit") :
            return True
        elif (command == "help") :
            displayHelpMessage()
            return False
    except Exception as e:
        print(e) 
        print("Error: invalid argument")
        displayHelpMessage()
        
def displayHelpMessage():
    print("Usage: ")
    print("=====")
    print("\tregisterVMServer <IP> <Port> <Name <IsEditionServer>: registers a virtual machine server")
    print("\tobtainVMServerConfiguration: prints all the virtual machine server's status")
    print("\tobtainVMDistributionData: prints the active virtual machines' distribution data")
    print("\tobtainVMServerResourceUsage: prints the active virtual machine server's resource usage")  
    print("\tobtainActiveVMsVNCData: prints the active virtual machines' VNC connection data")  
    print("\tobtainImageRepositoryStatus: prints the image repository status")
    print("\tunregisterVMServer <Name or IP> <Halt VMs?>: unregisters a virtual machine server")
    print("\tshutdownVMServer <Name or IP> <Halt VMs?>: shuts down a virtual machine server")    
    print("\tbootUpVMServer <Name or IP>: boots up a virtual machine server")
    print("\tchangeVMServerConfiguration <Name or IP> <New Name> <New IP> <New Port> <New image edition behavior>:")
    print("\t\tchanges a virtual machine server's configuration")
    print("\tHalt: shuts down a virtual machine server")        
    print("\tbootUpVM <ImageID> <UserID> <DomainID>: boots up a virtual machine")
    print("\tdestroyDomain <DomainID>: destroys a virtual machine")
    print("\trebootDomain <DomainID>: reboots a virtual machine")
    print("\tdeployImage <serverID> <imageID>: deploys an image on a virtual machine server")
    print("\tdeleteImageFromServer <serverID> <imageID>: deletes an image on a virtual machine server")
    print("\tcreateImage <sourceImageID>: creates a new image")
    print("\teditImage <editedImageID>: edits an image")
    print("\tdeleteImageFromInfrastructure <imageID>: deletes an image from the whole infrastructure")
    print("\tdeployEditedImage <imageID>: updates an edited image on all the virtual machine servers")
    print("\tautoDeployImage <imageID> <instances>: performs an auto-deployment operation")
    print("\tquit: closes this application")
    print("\thelp: prints this help message")

if __name__ == "__main__" :
    print('*' * 80)
    print('*' * 80)
    printLogo()
    print('Cluster Server tester')
    print('Version 7.0')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager(".")
    networkManager.startNetworkService()
    pHandler = ClusterServerPacketHandler(networkManager)
    ip_address = raw_input("Cluster server IP address: ")
    port = raw_input("Cluster server control connection port: ")
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