# -*- coding: utf8 -*-
'''
    Test que simula un chat entre un cliente y un servidor
    Este test se ejecuta junto al módulo clientConversational y requiere
     del módulo ConvCallback
'''
from network.manager import NetworkManager
from network.tests.ConvCallback import ConvCallback
from time import sleep

if __name__ == "__main__" :
    listP = []
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.listenIn(8080, ConvCallback(listP))
    
    print("The server is now ready")
    
    ans = ""
    while ans != "bye":
        #esperamos una respuesta
        while(len(listP) == 0):
            sleep(0.1)
        # Extraemos la contestacion
        ans = listP[0]
        print("<<" + ans)
        if ans != "bye" :
            p = networkManager.createPacket(0)
            print(">>")
            ans = raw_input()
            p.writeString(ans)
            while not networkManager.isConnectionReady(8080):
                sleep(0.1)
            #enviamos el mensaje        
            networkManager.sendPacket(8080, p)

        
    sleep(10)
    networkManager.stopNetworkService()