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
from network.tests.ConvCallback import ConvCallback
from time import sleep

if __name__ == "__main__" :
    listP = []
    listP1 = []
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.listenIn(8080,  ConvCallback(listP))
    networkManager.listenIn(8081,  ConvCallback(listP1))
    print("The server is now ready")
    #esperamos una respuesta
    while(len(listP) == 0):
        sleep(0.1)
    # Extraemos la contestacion
    ans = listP[0]
    #Se la enviamos al otro cliente
    p = networkManager.createPacket(0)
    p.writeString(ans)    
    networkManager.sendPacket(8081, p)
    #Esperamos al de regreso
    while(len(listP1) == 0):
        sleep(0.1)      
    # Extraemos la contestacion
    ans = listP1[0]
    #Se la enviamos al otro cliente
    p = networkManager.createPacket(0)
    p.writeString(ans)    
    networkManager.sendPacket(8080, p)

    
    sleep(200)
    networkManager.stopNetworkService()
