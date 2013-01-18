# -*- coding: utf8 -*-
'''
This module contains statements to connect to a virtual machine
server and control it.
@author: Luis Barrios Hernández
@version: 1.0
'''
from __future__ import print_function

from network.manager import NetworkManager, NetworkCallback
from network.exceptions.networkManager import NetworkManagerException
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T
from time import sleep

class TesterCallback(NetworkCallback):
    def __init__(self, packetHandler):
        self.__pHandler = packetHandler
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket()
        packet_type = VM_SERVER_PACKET_T.reverse_mapping[data["packet_type"]]
        if (packet_type == VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA) :
            print("Domain connection data: ")
            print("VNC server IP address: " + data["VNCServerIP"])
            print("VNC server port: " + data["VNCServerPort"])
            print("VNC server password: " + data["VNCServerPassword"])
        elif (packet_type == VM_SERVER_PACKET_T.SERVER_STATUS) :
            print("Virtual machine server " +  + " status: ")
            print(packet.readInt() +  " active VMs")
        else :
            print("Error: a packet from an unexpected type has been received")
       

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
    
def process_command(tokens, networkManager, pHandler, port):
    if (len(tokens) == 0) :
        return False
    command = tokens.pop(0)
    if (command == "createvm") :
        p = pHandler.createVMBootPacket(long(tokens.pop(0)), 1)
        networkManager.sendPacket(port, p)
        return False
    elif (command == "shutdown") :
        p = pHandler.createVMServerShutdownPacket()
        networkManager.sendPacket(port, p)
        return False
    elif (command == "status") :
        p = pHandler.createVMServerStatusRequestPacket()
        networkManager.sendPacket(port, p)
        return False
    elif (command == "halt" or command == "quit") :
        p = pHandler.createVMServerHaltPacket()
        networkManager.sendPacket(port, p)
        return command == "quit"        
    else :
        if (command != "help") :
            print("Error: unknown command")
        print("Usage: ")
        print("=====")
        print("\tcreatevm <ID>: creates a virtual machine ")
        print("\tshutdown: asks the virtual machine server to terminate")
        print("\thalt: commands the virtual machine server to destroy all the virtual machines\n\t\t\
            and exit immediately")
        print("\thelp: prints the following help message")
        print("\tquit: closes this application")
    

if __name__ == "__main__" :
    print('*' * 80)
    print('*' * 80)
    printLogo()
    print('Virtual Machine Server tester')
    print('Version 1.0')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    # Create the packet handler
    pHandler = VMServerPacketHandler(networkManager)
    # Ask for the port and the IP address
    ip_address = raw_input("Server IP address: ")
    port = raw_input("Server port: ")
    try :
        port = int(port)
        networkManager.connectTo(ip_address, port, 10, TesterCallback(pHandler))
        while not networkManager.isConnectionReady(port) :
            sleep(0.1)
        end = False
        while not end :
            command = raw_input('>')
            tokens = command.split()
            end = process_command(tokens, networkManager, pHandler, 8080)
    
    except NetworkManagerException as e:
        print("Error: " + str(e))
    networkManager.stopNetworkService()
    
    
