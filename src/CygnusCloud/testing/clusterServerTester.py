# -*- coding: utf8 -*-
'''
This module contains statements to connect to a virtual machine
server and control it.
@author: Luis Barrios Hernández
@version: 1.0
'''
from __future__ import print_function

from network.manager.networkManager import NetworkManager, NetworkCallback
from network.exceptions.networkManager import NetworkManagerException
from clusterServer.networking.packets import MainServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from time import sleep

class TesterCallback(NetworkCallback):
    def __init__(self, packetHandler):
        self.__pHandler = packetHandler
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            print("Virtual machine server registration error")
            print("\t" + data["VMServerIP"])
            print("\t" + str(data["VMServerPort"]))
            print("\t" + data["VMServerName"])
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
        elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE):
            print("Virtual machine boot failure")
            print("\tMachine ID: " + data["VMID"])
            print("\tUser ID: " + str(data["UserID"]))
            print("\tReason: " + data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
            print("Virtual machine connection data")
            print("\tUser ID: " + str(data["UserID"]))
            print("\tVNC server IP address: " + data["VNCServerIPAddress"])
            print("\tVNC server port: " + str(data["VNCServerPort"]))
            print("\tVNC server password: " + data["VNCServerPassword"])
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_DATA) :
            print("VNC connection data")
            print("\tSegment " + str(data["Segment"]) + " of " + str(data["SequenceSize"]))
            print("\tVNC server IP address: " + data["VMServerIP"])
            print("\t" + str(data["Data"]))
       

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
            p = pHandler.createVMServerRegistrationPacket(ip, serverPort, name)
            networkManager.sendPacket(ip_address, port, p)
            return False  
        elif (command == "obtainVMServerStatus") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "obtainVMDistributionData") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "unregisterVMServer") :
            p = pHandler.createVMServerUnregistrationOrShutdownPacket(tokens.pop(0), bool(tokens.pop(0)), False)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "shutdownVMServer") :
            p = pHandler.createVMServerUnregistrationOrShutdownPacket(tokens.pop(0), bool(tokens.pop(0)), True)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "bootUpVMServer") :
            p = pHandler.createVMServerBootUpPacket(tokens.pop(0))
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "bootUpVM") :
            p = pHandler.createVMBootRequestPacket(int(tokens.pop(0)), long(tokens.pop(0)))
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "halt") :
            p = pHandler.createHaltPacket(True)
            networkManager.sendPacket(ip_address, port, p)
        elif (command == "getConnectionData") :
            p = pHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_DATA)
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
    print("\tregisterVMServer <IP> <Port> <Name>: registers a virtual machine server")
    print("\tobtainVMServerStatus: obtains all the virtual machine server's status")
    print("\tobtainVMDistributionData: obtains the virtual machines' distribution data")
    print("\tunregisterVMServer <Name or IP> <Halt?>: unregisters a virtual machine server")
    print("\tshutdownVMServer <Name or IP> <Halt?>: shuts down a virtual machine server")
    print("\tbootUpVMServer <Name or IP>: boots up a virtual machine server")
    print("\tobtainAvailableImagesData: shows available images' data")
    print("\tbootUpVM <Name> <UserID>: boots up a virtual machine")
    print("\tquit: closes this application")
    

if __name__ == "__main__" :
    print('*' * 80)
    print('*' * 80)
    printLogo()
    print('Main Server tester')
    print('Version 1.0')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager("/home/luis/Certificates")
    networkManager.startNetworkService()
    # Create the packet handler
    pHandler = MainServerPacketHandler(networkManager)
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
        print("Error: " + str(e))
    networkManager.stopNetworkService()
    
    
