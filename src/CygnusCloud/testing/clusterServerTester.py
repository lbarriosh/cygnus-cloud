# -*- coding: utf8 -*-
'''
Definiciones del tester del servidor de máquinas virtuales
@author: Luis Barrios Hernández
@version: 6.0
'''
from __future__ import print_function

from network.manager.networkManager import NetworkManager, NetworkCallback
from network.exceptions.networkManager import NetworkManagerException
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from time import sleep

class TesterCallback(NetworkCallback):
    def __init__(self, packetHandler):
        self.__pHandler = packetHandler
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            print("Virtual machine server registration error")
            print("\tServer IP: " + data["VMServerIP"])
            print("\tServer port: " + str(data["VMServerPort"]))
            print("\tServer name: " + data["VMServerName"])
            print("\tReason: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA or data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA) :
            print("Virtual machine servers' current status")
            print("\tSegment " + str(data["Segment"]) + " of " + str(data["SequenceSize"]))
            for row in data["Data"] :
                print(row)
        elif (data["packet_type"] == PACKET_T.VM_SERVER_BOOTUP_ERROR):
            print("Virtual machine server bootup error")
            print("\tServer name or IP address: " + data["ServerNameOrIPAddress"])
            print("\tReason: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_SERVER_UNREGISTRATION_ERROR):
            print("Virtual machine server unregistration error")
            print("\tServer name or IP address: " + data["ServerNameOrIPAddress"])
            print("\tReason: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_SERVER_SHUTDOWN_ERROR):
            print("Virtual machine server shutdown error")
            print("\tServer name or IP address: " + data["ServerNameOrIPAddress"])
            print("\tReason: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE):
            print("Virtual machine boot failure")
            print("\nImage ID: " + str(data["VMID"]))
            print("\tReason: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
            print("Virtual machine connection data")
            print("\tVNC server IP address: " + data["VNCServerIPAddress"])
            print("\tVNC server port: " + str(data["VNCServerPort"]))
            print("\tVNC server password: " + data["VNCServerPassword"])
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_DATA) :
            print("VNC connection data")
            print("\tSegment " + str(data["Segment"]) + " of " + str(data["SequenceSize"]))
            print("\tVNC server IP address: " + data["VMServerIP"])
            print("\t" + str(data["Data"]))
        elif (data["packet_type"] == PACKET_T.DOMAIN_DESTRUCTION_ERROR) :
            print("Domain destruction error: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR) :
            print("Virtual machine configuration change error: " + data["ErrorMessage"])

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
            isVanillaServer = tokens.pop(0) == "True"
            p = pHandler.createVMServerRegistrationPacket(ip, serverPort, name, isVanillaServer, '')
            networkManager.sendPacket(ip_address, port, p)
            return False  
        elif (command == "obtainVMServerStatus") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "obtainVMDistributionData") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "unregisterVMServer") :
            p = pHandler.createVMServerUnregistrationOrShutdownPacket(tokens.pop(0), bool(tokens.pop(0)), True, "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "shutdownVMServer") :
            p = pHandler.createVMServerUnregistrationOrShutdownPacket(tokens.pop(0), bool(tokens.pop(0)), False, "")
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "bootUpVMServer") :
            p = pHandler.createVMServerBootUpPacket(tokens.pop(0), "")
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
        elif (command == "obtainActiveVMsData") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_DATA)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "destroyDomain") :
            p = pHandler.createDomainDestructionPacket(tokens.pop(0), "")
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
    print("\tregisterVMServer <IP> <Port> <Name <IsVanillaServer>: registers a virtual machine server")
    print("\tobtainVMServerStatus: obtains all the virtual machine server's status")
    print("\tobtainVMDistributionData: obtains the virtual machines' distribution data")
    print("\tunregisterVMServer <Name or IP> <Halt?>: unregisters a virtual machine server")
    print("\tshutdownVMServer <Name or IP> <Halt?>: shuts down a virtual machine server")
    print("\tbootUpVMServer <Name or IP>: boots up a virtual machine server")
    print("\tbootUpVM <ImageID> <UserID> <DomainID>: boots up a virtual machine")
    print("\tdestroyDomain <DomainID>: destroys a virtual machine")
    print("\tobtainActiveVMsData: obtains the active virtual machines' data")
    print("\tchangeVMServerConfiguration <Name or IP> <New Name> <New IP> <New Port> <New vanilla image behavior>")
    print("\tquit: closes this application")
    

if __name__ == "__main__" :
    print('*' * 80)
    print('*' * 80)
    printLogo()
    print('Cluster Server tester')
    print('Version 6.0')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager("/home/luis/Certificates")
    networkManager.startNetworkService()
    # Create the packet handler
    pHandler = ClusterServerPacketHandler(networkManager)
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
    
    
