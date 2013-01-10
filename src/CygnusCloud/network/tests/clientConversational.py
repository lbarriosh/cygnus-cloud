# -*- coding: utf8 -*-
'''
    Test que simula un chat entre un cliente y un servidor
    Este test se ejecuta junto al módulo serverConversational y requiere
     del módulo ConvCallback
'''
from network.manager import NetworkManager
from network.tests.ConvCallback import ConvCallback
from time import sleep

if __name__ == "__main__" :
    listP = []
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.connectTo('127.0.0.1', 8080, 20, ConvCallback(listP))
    while not networkManager.isConnectionReady(8080):
        sleep(0.1)

    
    #Creamos el string gordo
    ans = ""
    while ans != "bye":
        p = networkManager.createPacket(0)
        print(">>")
        ans = raw_input()
        p.writeString(ans)
        #enviamos el mensaje        
        networkManager.sendPacket(8080, p)
        #esperamos una respuesta
        while(len(listP) == 0):
            sleep(0.1)
        #Extraemos la contestación
        print("<<" + listP[0])
        
    sleep(10)
    networkManager.stopNetworkService()
