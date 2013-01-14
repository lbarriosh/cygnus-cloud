# -*- coding: utf8 -*-
'''
VirtualNetworkManager definitions.
@author: Luis Barrios Hernández
@version 1.0
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
    
from utils.commands import runCommand

from time import sleep
    
class VirtualNetworkManagerException(Exception):
    """
    Virtual network manager exception class
    """
    pass

class VirtualNetworkManager(object):
    """
    This class provides methods to create, destroy
    and to open ports in virtual machine networks.
    """
    def __init__(self):
        self.__networksByIP = dict()
        self.__networksByName = dict();
        
    def createVirtualNetwork(self, networkName, gatewayIPAddress, netmask,
                                    dhcpStartIPAddress, dhcpEndIPAddress, bridgeName=None):
        """
        Creates a virtual network.
        Args:
            networkName: the new virtual network's name
            gatewayIPAddress: the gateway IPv4 address
            netmask: the IPv4 netmask
            dhcpStartIPAddress: the first IP address that the DHCP server will assign to a
            host.
            dhcpStopIPAddress: the last IP address that the DHCP server will assign to a
            host.
            bridgeName: the new virtual network's bridge name. If it's None, the new network
            and its bridge will have the same name.
        Returns:
            Nothing
        Raises:
            VirtualNetworkManagerException: this exceptions will be raised when the gateway
            IP address or the virtual network name is already in use. 
            
        """
        # Check if this network already exists
        if (self.__networksByIP.has_key(gatewayIPAddress) != 0) :
            raise VirtualNetworkManagerException("The gateway IP address " + \
                                                 gatewayIPAddress + " is already in use")
        if (self.__networksByName.has_key(networkName)):
            raise VirtualNetworkManagerException("The virtual network name " + networkName + \
                                                 " is already in use")
        xmlFilePath = "/tmp/networkConfig.xml"
        # Generate the .xml configuration file
        self.__generateConfigurationFile(xmlFilePath, networkName, bridgeName,\
                                         gatewayIPAddress, netmask, dhcpStartIPAddress, dhcpEndIPAddress)
        # Create the virtual network
        runCommand("virsh net-define " + xmlFilePath, VirtualNetworkManagerException)
        
        # Start it
        runCommand("virsh net-start " + networkName, VirtualNetworkManagerException)
        
        # Delete the .xml file
        runCommand("rm " + xmlFilePath, VirtualNetworkManagerException)
        
        # Register the new virtual network
        self.__networksByIP[gatewayIPAddress] = networkName
        self.__networksByName[networkName] = gatewayIPAddress
        
    def destroyVirtualNetwork(self, nameOrIPAddress):
        """
        Destroys a virtual network. 
        Args:
            nameOrIPAddress: the gateway IPv4 address or the networkName of the virtual network to destroy.
        Returns:
            nothing
        Raises:
            VirtualNetworkManagerException: this exception will be raised when the virtual network
            does not exist.
        """
        if (not self.__networksByName.has_key(nameOrIPAddress) and \
            not self.__networksByIP.hasKey(nameOrIPAddress)) :
            raise VirtualNetworkManagerException("The network with networkName or IPv4 gateway address "\
                                                 + nameOrIPAddress + " does not exist")
        # Fetch the virtual network's networkName
        networkName = nameOrIPAddress
        if (not self.__networksByName.has_key(nameOrIPAddress)):
            networkName = self.__networksByIP[nameOrIPAddress]
        # Destroy the virtual network
        runCommand("virsh net-destroy " + networkName, VirtualNetworkManagerException)
        runCommand("virsh net-undefine " + networkName, VirtualNetworkManagerException)
        # Delete it from the internal data structures
        ip = self.__networksByName[networkName]
        self.__networksByName.pop(networkName)
        self.__networksByIP.pop(ip)
    
        
    @staticmethod
    def __generateConfigurationFile(outputFilePath, networkName, bridgeName, gatewayIPAddress, netmask,
                                    dhcpStartIPAddress, dhcpEndIPAddress):
        """
        Generates a network configuration file.
        """
        network = ET.Element("network")
        # Generate the name sub-element
        name = ET.SubElement(network, "name")
        name.text = networkName
        # Generate the bridge sub-element
        if (bridgeName == None) :
            ET.SubElement(network, "bridge", {"name":networkName})
        else :
            ET.SubElement(network, "bridge", {"name":bridgeName})
        # Generate the forward sub-element
        ET.SubElement(network, "forward")
        # Generate the ip sub-element
        ip = ET.SubElement(network, "ip", {"address" : gatewayIPAddress, "netmask" : netmask})
        # Generate the dhcp sub-element
        dhcp = ET.SubElement(ip, "dhcp")
        ET.SubElement(dhcp, "range", {"start" : dhcpStartIPAddress, "end" : dhcpEndIPAddress})        
        # Write the generated tree to the specified file
        tree = ET.ElementTree(network)
        tree.write(outputFilePath)
        
if __name__ == "__main__":
    # Generate the virtual network foo
    vnm = VirtualNetworkManager()
    vnm.createVirtualNetwork("net1", "172.20.20.1", "255.0.0.0", "172.20.0.2", "172.20.255.254")
    sleep(30)
    vnm.destroyVirtualNetwork("net1")