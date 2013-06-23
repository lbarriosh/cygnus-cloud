# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: virtualNetworkManager.py    
    Version: 3.0
    Description: virtual network manager definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
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
    Virtual network manager exception class
    """
    pass

class VirtualNetworkManager(object):
    """
    Virtual network manager class
    """
    def __init__(self, runCommandsAsRoot=False):
        """
        Initializes the virtual network manager's state
        Args:
            runCommandsAsRoot: indicates wether the commands must be
            executed as the super-user or not.
        """
        self.__networksByIP = dict()
        self.__networksByName = dict();
        self.__runAsRoot = runCommandsAsRoot
        
    def createVirtualNetwork(self, networkName, gatewayIPAddress, netmask,
                                    dhcpStartIPAddress, dhcpEndIPAddress, bridgeName=None):
        """
        Creates a virtual network.
        Args:
            networkName: the virtual network's name
            gatewayIPAddress: the gateway's IPv4 address
            netmask: the gateway's netmask
            dhcpStartIPAddress: the DHCP server start address
            dhcpStopIPAddress: the DHCP server stop address
            bridgeName: bridge name. If it's none, it will be named after the virtual network.
        Returns:
            Nothing   
        """
        # Check errors
        if (self.__networksByIP.has_key(gatewayIPAddress) != 0) :
            raise VirtualNetworkManagerException("The gateway IP address " + \
                                                 gatewayIPAddress + " is already in use")
        if (self.__networksByName.has_key(networkName)):
            raise VirtualNetworkManagerException("The virtual network name " + networkName + \
                                                 " is already in use")
        xmlFilePath = "/tmp/networkConfig.xml"
        # Build the definition file
        self.__generateConfigurationFile(xmlFilePath, networkName, bridgeName,\
                                         gatewayIPAddress, netmask, dhcpStartIPAddress, dhcpEndIPAddress)
        
        # Create the virtual network. If it exists, it will be previously destroyed
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
        
        # Enable the virtual network
        runMethod("virsh net-start " + networkName, VirtualNetworkManagerException)
        
        # Delete the definition file
        ChildProcessManager.runCommandInForeground("rm " + xmlFilePath, VirtualNetworkManagerException)
        
        # Start the virtual network
        self.__networksByIP[gatewayIPAddress] = networkName
        self.__networksByName[networkName] = gatewayIPAddress
        
    def destroyVirtualNetwork(self, nameOrGatewayIPAddress):
        """
        Destroys a virtual network
        Args:
            nameOrGatewayIPAddress: the virtual network's name or its gateway's IPv4 address
        Returns:
            Nothing
        """
        
        # Check errors
        if (not self.__networksByName.has_key(nameOrGatewayIPAddress) and \
            not self.__networksByIP.has_key(nameOrGatewayIPAddress)) :
            raise VirtualNetworkManagerException("The virtual network with name or IPv4 gateway address "\
                                                 + nameOrGatewayIPAddress + " does not exist")
            
        # Get the virtual network's name
        networkName = nameOrGatewayIPAddress
        if (not self.__networksByName.has_key(nameOrGatewayIPAddress)):
            networkName = self.__networksByIP[nameOrGatewayIPAddress]        
        
        # Destroy it
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
        Generates a virtual network definition file
        Args:
            outputFilePath: the output file path
            networkName: the virtual network's name
            bridgeName: the bridge's name
            gatewayIPAddress: the gateway's IPv4 address
            netmask: the gateway's netmask
            dhcpStartIPAddress: the DHCP server start address
            dhcpStopIPAddress: the DHCP server stop address
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