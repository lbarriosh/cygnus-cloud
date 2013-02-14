# -*- coding: utf8 -*-
'''
    test "Todos o ninguno"
    Este test muestra como el servidor es capaz de enviar un paquete en paralelo
     a todos los usuarios que se encuentren conectados a un determinado puerto.
    Para probar el test:
        1. Ejecutar el server04 y esperar a que se indique que ya se encuentra disponible
        2. Ejecutar inmediatamente el módulo MultiClient varias veces
        3. Tras 20 segundos todos los clientes recibirán un paquete proviniente del servidor
        
    Módulos necesarios:
        -Multiclient,server04
'''
from network.manager.networkManager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.listenIn(8080, DummyCallback())
    print("The server is now ready")
    sleep(20)
    p = networkManager.createPacket(0)
    p.writeString("Hello clients!")    
    networkManager.sendPacket('', 8080, p)
    sleep(200)
    networkManager.stopNetworkService()