# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: definitionFileEditor.py    
    Version: 4.0
    Description: Domain definition file editor
    
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
            
class DefinitionFileEditorException(Exception):
    """
    Domain definition file editor exception class
    """
    pass
    
class DefinitionFileEditor(object):
    """
    Domain definition file editor
    """
    def __init__(self, inputFilePath):
        """
        Initializes the editor's state
        Args:
            inputFilePath: the pattern .xml file path
        """
        self.__inputFilePath = inputFilePath
        self.__name = None
        self.__uuid = None
        self.__virtualNetworkName = None
        self.__macAddress = None
        self.__vncServerIPAddress = None
        self.__vncServerPort = None
        self.__vncServerPassword = None
        self.__dataImagePath = None
        self.__osImagePath = None
        self.__useQEMUWebsockets = None
        
    def setDomainIdentifiers(self, name, uuid):
        """
        Stores the domain identifiers
        Args:
            name: a domain name
            uuid: a domain UUID
        Returns:
            Nothing
        """
        self.__name = name
        self.__uuid = uuid
        
    def setVirtualNetworkConfiguration(self, virtualNetwork, macAddress):
        """
        Stores the virtual network configuration parameters
        Args:
            name: the virtual network's name
            macAddress: the domain's MAC address
        Returns:
            Nothing
        """
        self.__virtualNetworkName = virtualNetwork
        self.__macAddress = macAddress
        
    def setVNCServerConfiguration(self, ipAddress, port, password, useQEMUWebsockets):
        """
        Stores the VNC server configuration parameters
        Args:
            ip_address: the VNC server's IP address
            port: the VNC server's port
            password: the VNC server's password
            useQEMUWebsockets: indicates whether the QEMU native websockets or the
                websockify daemon must be used.
        """
        self.__vncServerIPAddress = ipAddress
        self.__vncServerPort = port
        self.__vncServerPassword = password
        self.__useQEMUWebsockets = useQEMUWebsockets
        
    def setImagePaths(self, osImagePath, dataImagePath):
        """
        Stores the disk images paths
        Args:
            osImagePath: the OS disk image path
            dataImagePath: the data disk image path
        Returns:
            Nothing
        """
        self.__osImagePath = osImagePath
        self.__dataImagePath = dataImagePath
        
    def generateConfigurationString(self):
        """
        Generates the domain configuration string
        Args:
            None
        Returns:
            the generated domain configuration string
        Raises:
            DefinitionFileEditorException: this exception will be raised when a required parameter
                has not been set.
        """
        self.__checkErrors()
        tree = ET.parse(self.__inputFilePath)
        root = tree.getroot()
        
        name = root.find("name")
        name.text = self.__name

        uuid = root.find("uuid")
        uuid.text = self.__uuid

        devices = root.find("devices")
        interface = devices.find("interface")
        mac = interface.find("mac")
        mac.set("address", self.__macAddress)
        source = interface.find("source")
        source.set("network", self.__virtualNetworkName)
        
        for disk in devices.iter("disk") :
            target = disk.find("target")
            source = disk.find("source")
            if (target.get("dev") == "vda") :
                # First hard drive. This one will store the OS data.
                source.set("file", self.__osImagePath)
            else :
                # Second hard drive. This one will store the domain's data and its
                # page file.
                source.set("file", self.__dataImagePath)
        
        graphics = devices.find("graphics")
        graphics.set("port", str(self.__vncServerPort))
        if (self.__useQEMUWebsockets) :
            graphics.set("websocket", str(self.__vncServerPort + 1))
        graphics.set("passwd", self.__vncServerPassword)
        listen = graphics.find("listen")
        listen.set("address", self.__vncServerIPAddress)
        
        return ET.tostring(root)
    
    def __checkErrors(self):
        """
        Checks if all the domain configuration parameters have been set
        Args:
            None
        Returns:
            Nothing
        Lanza:
            DefinitionFileEditorException: this exception will be raised when a required parameter
                has not been set.
        """
        if (self.__name == None or self.__uuid == None) :
            raise DefinitionFileEditorException("The domain identifiers have not been set")
        if (self.__virtualNetworkName == None or self.__macAddress == None) :
            raise DefinitionFileEditorException("The network configuration parameters have not been set")
        if (self.__vncServerIPAddress == None or self.__vncServerPassword == None or self.__vncServerPort == None or self.__useQEMUWebsockets == None) :
            raise DefinitionFileEditorException("The VNC server configuration parameters have not been set")
        if (self.__dataImagePath == None or self.__osImagePath == None) :
            raise DefinitionFileEditorException("The data image path has not been set")    