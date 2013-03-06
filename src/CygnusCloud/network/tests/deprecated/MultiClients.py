# -*- coding: utf8 -*-
'''
    Test que comprueba si el servidor es capaz de recibir los paquetes enviados
    desde varios clientes.
    Para realizarse la prueba debe ejecutarse este módulo el número de clientes 
     que se desee
    Testeado con server 03
'''
import time
from network.manager.networkManager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    
    # Fase 1 :Creamos y conectamos a los clientes
    #Cliente 1
    client1 = NetworkManager()
    client1.startNetworkService()
    client1.connectTo('127.0.0.1', 8080, 20, DummyCallback())
  
    while(not client1.isConnectionReady('127.0.0.1', 8080)):
        sleep(0.1)
    #Fase 2: Cada cliente envia su paquete
    #Cliente 1
    p1 = client1.createPacket(0)
    p1.writeString("I am Client " + str(time.localtime()[3]) + ":" 
                    + str(time.localtime()[4]) + ":" + str(time.localtime()[5]))        
    client1.sendPacket('127.0.0.1', 8080, p1)
   
    #Fase 3: Esperamos y cerramos las conexiones
    sleep(200)
    #Cliente 1
    client1.stopNetworkService()
