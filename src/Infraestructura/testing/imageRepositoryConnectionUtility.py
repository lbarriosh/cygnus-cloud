# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: imageRepositoryConnectionUtility.py    
    Version: 1.0
    Description: image repository connection utility
    
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
from imageRepository.packetHandling.packet_t import PACKET_T
from imageRepository.packetHandling.packetHandler import ImageRepositoryPacketHandler
from time import sleep
from ftp.ftpClient import FTPClient

class TesterCallback(NetworkCallback):    
    def __init__(self, packetHandler, ip_address):
        self.__repositoryPacketHandler = packetHandler
        self.__ip_address = ip_address
        
    def processPacket(self, packet):
        global user_input
        global workingDirectory
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data['packet_type'] == PACKET_T.ADDED_IMAGE_ID) :
            print("The new image ID is: {0}".format(data['addedImageID']))
            print("Please write it down. You'll need it later")
        elif (data['packet_type'] == PACKET_T.RETR_REQUEST_ERROR or data['packet_type'] == PACKET_T.RETR_ERROR) :
            print("Retrieve error: " + str(data['errorDescription']))
        elif (data['packet_type'] == PACKET_T.RETR_REQUEST_RECVD) :
            print("The image repository says: retrieve request received")
        elif (data['packet_type'] == PACKET_T.RETR_START) :
            print("Downloading file...")
            ftpClient = FTPClient()
            ftpClient.connect(self.__ip_address, data['FTPServerPort'], 5, data['username'], data['password'])
            ftpClient.retrieveFile(data['fileName'], workingDirectory, data['serverDirectory']) 
            ftpClient.disconnect()
            print("Transfer completed")
        elif (data['packet_type'] == PACKET_T.STOR_REQUEST_ERROR or data['packet_type'] == PACKET_T.STOR_ERROR) :
            print("Store error: " + str(data['errorCode']))
            user_input = False
        elif (data['packet_type'] == PACKET_T.STOR_REQUEST_RECVD) :
            print("The image repository says: store request received")
        elif (data['packet_type'] == PACKET_T.STOR_START) :
            print("Uploading file...")
            ftpClient = FTPClient()
            ftpClient.connect(self.__ip_address, data['FTPServerPort'], 100, data['username'], data['password'])
            if (data['fileName'] == '') :
                fileName = raw_input('File to upload (its name MUST be the given image ID): ')
            else :
                fileName = data['fileName']
            ftpClient.storeFile(fileName, workingDirectory, data['serverDirectory']) 
            ftpClient.disconnect()
            print("Transfer completed")
            user_input = False
        elif (data['packet_type'] == PACKET_T.DELETE_REQUEST_RECVD):
            print("The image repository says: delete request received")
        elif (data['packet_type'] == PACKET_T.STATUS_DATA):
            print("Image repository disk usage: {0} KB free, {1} KB available".format(data["FreeDiskSpace"], data["TotalDiskSpace"]))   
        elif (data['packet_type'] == PACKET_T.IMAGE_EDITION_CANCELLED):
            print("The image repository says: image edition cancelled")  
        else:
            print("Error: a packet from an unexpected type has been received " + str(data['packet_type']))
       

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
    global user_input
    if (len(tokens) == 0) :
        return False
    try :
        command = tokens.pop(0)
        if (command == "halt" ) :
            p = pHandler.createHaltPacket()
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "quit") :
            return True
        elif (command == "createImage"):
            p = pHandler.createAddImagePacket()
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "retrieveImage"):
            p = pHandler.createRetrieveRequestPacket(int(tokens.pop(0)), len(tokens) == 0)
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "storeImage"):
            user_input = True
            p = pHandler.createStoreRequestPacket(int(tokens.pop(0)))
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "deleteImage") :
            p = pHandler.createDeleteRequestPacket(int(tokens.pop(0)))
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "status"):
            p = pHandler.createStatusRequestPacket()
            networkManager.sendPacket(ip_address, port, p)
            return False
        elif (command == "cancel_image_edition"):
            p = pHandler.createCancelEditionPacket(int(tokens.pop(0)))
            networkManager.sendPacket(ip_address, port, p)
            return False
        else :
            if (command != "help") :
                print("Error: unknown command")
            print("Usage: ")
            print("=====")           
            print("\tcreateImage: creates a new image")
            print("\tretrieveImage <imageID>: downloads an image from the repository")
            print("\tstoreImage <imageID>: uploads a file to the repository")
            print("\tdeleteImage <imageID>: deletes an image from the repository")
            print("\tstatus: prints the image repository's current status")
            print("\thalt: shuts down the image repository")
            print("\thelp: prints the following help message")
            print("\tquit: closes this application")
    except Exception as e :
        print("Error: " + e.message)
        user_input = False
    

if __name__ == "__main__" :
    global user_input
    global workingDirectory
    user_input = False   
    print('*' * 80)
    print('*' * 80)
    printLogo()
    print('Image repository connection utility')
    print('Version 1.0')
    print('*' * 80)
    print('*' * 80)
    print()
    networkManager = NetworkManager(".")
    networkManager.startNetworkService()
    pHandler = ImageRepositoryPacketHandler(networkManager)
    ip_address = raw_input("Image repository IP address: ")
    port = raw_input("Image repository control connection port: ")
    try :
        port = int(port)
        networkManager.connectTo(ip_address, port, 10, TesterCallback(pHandler, ip_address), True)
        while not networkManager.isConnectionReady(ip_address, port) :
            sleep(0.1)
        correct = False
        while not correct: 
            workingDirectory = raw_input("Working directory: ")
            answer = raw_input("The working directory is \'{0}\'. Is this correct? [Y/n] ".format(workingDirectory))
            correct = answer == "Y" or answer == "y" or answer == ""
        end = False
        while not end :
            if (not user_input) :
                command = raw_input('> ')
                tokens = command.split()
                end = process_command(tokens, networkManager, pHandler, ip_address, port)
            else :
                sleep(0.1)
    
    except NetworkManagerException as e:
        print("Error: " + e.message)
    networkManager.stopNetworkService()