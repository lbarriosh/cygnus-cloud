# -*- coding: utf8 -*-

from network.manager.networkManager import NetworkCallback

class ClusterServerCallback(NetworkCallback):
    """
    Callback que procesará todos los paquetes recibidos desde el servidor de cluster.
    """

    def __init__(self, processor):
        """
        Inicializa el estado del callback.
        Argumentos:
            processor: el objeto que procesará todos los paquetes enviados desde el servidor de cluster.
        """
        self.__processor = processor
        
    def processPacket(self, packet):
        """
        Procesa un paquete enviado desde el servidor de cluster.
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        self.__processor.processClusterServerIncomingPackets(packet)