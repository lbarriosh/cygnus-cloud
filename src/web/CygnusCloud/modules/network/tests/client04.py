'''
    Test que comprueba si el servidor es capaz de recibir un paquete con un
     String de 15000 caracteres.
    Testeado con server 03
'''
from network.manager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.connectTo('127.0.0.1', 8080, 20, DummyCallback())
    p = networkManager.createPacket(0)
    #Creamos el string gordo
    bigS = ""
    for i in range(15000):
        bigS += 's'
    p.writeString(bigS)        
    networkManager.sendPacket(8080, p)
    sleep(100)
    networkManager.stopNetworkService()
