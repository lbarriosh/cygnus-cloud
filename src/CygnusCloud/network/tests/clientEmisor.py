# -*- coding: utf8 -*-
'''
    Prueba 'Puente':
        Un cliente se conecta al servidor por el puerto 8080. Otro cliente
         se conecta a este mismo servidor por el puerto 8081. El primer cliente
         envia un paquete al servidor, este lo recibe y redirecciona su contenido
         al segundo cliente.
         Trascurrido 20 segundos el proceso se repite en sentido contrario
         
         Para llevar a cabo la prueba será necesario ejecutar:
             1. ejecutar el serverWridge y esperar a que se informe de que la conexión 
                 está disponible
            2. Ejecutar el clientReceptor.
            3. Inmediatamente después ejecutar clientEmisor.
        
        Módulos necesarios:
            -serverWridge,clientEmisor,clientReceptor
'''


from network.manager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.connectTo('127.0.0.1', 8080, 20, DummyCallback())
    sleep(2)
    p = networkManager.createPacket(0)
    p.writeString("Hello Client 2!")    
    networkManager.sendPacket(8080, p)
    p = networkManager.createPacket(0)
    sleep(100)
    networkManager.stopNetworkService()