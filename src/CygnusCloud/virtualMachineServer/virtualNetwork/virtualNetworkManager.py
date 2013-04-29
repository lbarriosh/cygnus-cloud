# -*- coding: utf8 -*-
'''
Gestor de red virtual
@author: Luis Barrios Hernández
@version 3.0
'''
try :
    import etree.cElementTree as ET
except ImportError:
    try :
        import xml.etree.cElementTree as ET
    except ImportError:
        try :
            import etree.ElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
    
from ccutils.processes.childProcessManager import ChildProcessManager
    
class VirtualNetworkManagerException(Exception):
    """
    Clase de excepción para el gestor de red virtaul
    """
    pass

class VirtualNetworkManager(object):
    """
    Estos objetos crean y destruyen redes virtuales
    """
    def __init__(self, runCommandsAsRoot=False):
        """
        Inicializa el estado del gestor de red virtual.
        Argumentos:
            runCommandsAsRoot: indica si hay que ejecutar los comandos
            como el superusuario o como un usuario normal
        """
        self.__networksByIP = dict()
        self.__networksByName = dict();
        self.__runAsRoot = runCommandsAsRoot
        
    def createVirtualNetwork(self, networkName, gatewayIPAddress, netmask,
                                    dhcpStartIPAddress, dhcpEndIPAddress, bridgeName=None):
        """
        Creates a virtual network.
        Argumentos:
            networkName: el nombre de la red virtual
            gatewayIPAddress: la IP de la puerta de enlace
            netmask: la máscara de red
            dhcpStartIPAddress: la primera dirección IP que asignará el servidor DHCP
            dhcpStopIPAddress: la última dirección IP que asignará el servidor DHCP
            bridgeName: el nombre del bridge. Si es None, el bridge y la red virtual se llamarán igual
        Devuelve:
            Nada
        Lanza:
            VirtualNetworkManagerException: se lanza cuando la IP de la puerta de enlace,
            el nombre del bridge o el nombre de la red ya están en uso.            
        """
        # Comprobnar errores
        if (self.__networksByIP.has_key(gatewayIPAddress) != 0) :
            raise VirtualNetworkManagerException("The gateway IP address " + \
                                                 gatewayIPAddress + " is already in use")
        if (self.__networksByName.has_key(networkName)):
            raise VirtualNetworkManagerException("The virtual network name " + networkName + \
                                                 " is already in use")
        xmlFilePath = "/tmp/networkConfig.xml"
        # Generar el fichero de configuración
        self.__generateConfigurationFile(xmlFilePath, networkName, bridgeName,\
                                         gatewayIPAddress, netmask, dhcpStartIPAddress, dhcpEndIPAddress)
        
        # Crear la red virtual (si ya existe, la destruimos)    
        if (self.__runAsRoot) :
            runMethod = ChildProcessManager.runCommandInForegroundAsRoot
        else :
            runMethod = ChildProcessManager.runCommandInForeground
            
        try :
            runMethod("virsh net-destroy " + networkName, Exception)
        except Exception :
            pass
        try :
            runMethod("virsh net-undefine " + networkName, Exception)
        except Exception :
            pass
        
        runMethod("virsh net-define " + xmlFilePath, VirtualNetworkManagerException)
        
        # Arrancar la red virtual
        runMethod("virsh net-start " + networkName, VirtualNetworkManagerException)
        
        # Borrar el fichero de definición
        ChildProcessManager.runCommandInForeground("rm " + xmlFilePath, VirtualNetworkManagerException)
        
        # Registrar la red virtual
        self.__networksByIP[gatewayIPAddress] = networkName
        self.__networksByName[networkName] = gatewayIPAddress
        
    def destroyVirtualNetwork(self, nameOrGatewayIPAddress):
        """
        Destruye una red virtual 
        Argumentos:
            nameOrGatewayIPAddress: la IP de la puerta de enlace de la red virtual o el nombre de la red virtual.
        Devuelve:
            Nada
        Lanza:
            VirtualNetworkManagerException: se lanza si la red virtual no existe
        """
        
        # Comprobar errores
        if (not self.__networksByName.has_key(nameOrGatewayIPAddress) and \
            not self.__networksByIP.has_key(nameOrGatewayIPAddress)) :
            raise VirtualNetworkManagerException("The virtual network with name or IPv4 gateway address "\
                                                 + nameOrGatewayIPAddress + " does not exist")
            
        # Averiguar el nombre de la red
        networkName = nameOrGatewayIPAddress
        if (not self.__networksByName.has_key(nameOrGatewayIPAddress)):
            networkName = self.__networksByIP[nameOrGatewayIPAddress]        
        
        # Destruirla
        if (self.__runAsRoot) :
            runMethod = ChildProcessManager.runCommandInForegroundAsRoot
        else :
            runMethod = ChildProcessManager.runCommandInForeground
        
        runMethod("virsh net-destroy " + networkName, VirtualNetworkManagerException)
        runMethod("virsh net-undefine " + networkName, VirtualNetworkManagerException)

        ip = self.__networksByName[networkName]
        self.__networksByName.pop(networkName)
        self.__networksByIP.pop(ip)
    
        
    @staticmethod
    def __generateConfigurationFile(outputFilePath, networkName, bridgeName, gatewayIPAddress, netmask,
                                    dhcpStartIPAddress, dhcpEndIPAddress):
        """
        Genera un fichero de configuración de la red.
        Argumentos:
            outputFilePath: la ruta en la que se guardará ese fichero
            networkName: el nombre de la red virtual
            bridgeName: el nombre del bridge
            gatewayIPAddress: la IP de la puerta de enlace
            netmask: la máscara de red
            dhcpStartIPAddress: la primera IP que asignará el servidor DHCP
            dhcpEndIPAddress: la última IP que asignará el servidor DHCP
        """
        network = ET.Element("network")
        
        name = ET.SubElement(network, "name")
        name.text = networkName
        
        if (bridgeName == None) :
            ET.SubElement(network, "bridge", {"name":networkName})
        else :
            ET.SubElement(network, "bridge", {"name":bridgeName})
        
        ET.SubElement(network, "forward")
        
        ip = ET.SubElement(network, "ip", {"address" : gatewayIPAddress, "netmask" : netmask})
        
        dhcp = ET.SubElement(ip, "dhcp")
        ET.SubElement(dhcp, "range", {"start" : dhcpStartIPAddress, "end" : dhcpEndIPAddress})        
        
        tree = ET.ElementTree(network)
        tree.write(outputFilePath)