# -*- coding: utf8 -*-
'''
XML editor definitions
@author: Luis Barrios Hernández
@version: 1.0
'''

try :
    import etree.cElementTree as ET
except ImportError:
    import etree.ElementTree as ET
    
class ConfigurationFileEditorException(Exception):
    pass
    
class ConfigurationFileEditor(object):
    def __init__(self, inputFilePath):
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
        
    def setDomainIdentifiers(self, name, uuid):
        self.__name = name
        self.__uuid = uuid
        
    def setNetworkConfiguration(self, virtualNetwork, macAddress):
        self.__virtualNetworkName = virtualNetwork
        self.__macAddress = macAddress
        
    def setVNCServerConfiguration(self, ipAddress, port, password):
        self.__vncServerIPAddress = ipAddress
        self.__vncServerPort = port
        self.__vncServerPassword = password
        
    def setImagePaths(self, osPath, dataPath):
        self.__osImagePath = osPath
        self.__dataImagePath = dataPath
        
    def generateConfigurationString(self):
        self.__checkErrors()
        # Everything is OK now. Let's do it!
        # Parse the source XML file
        tree = ET.parse(self.__inputFilePath)
        root = tree.getroot()
        # Change the domain's name
        name = root.find("name")
        name.text = self.__name
        # Change the domain's UUID
        uuid = root.find("uuid")
        uuid.text = self.__uuid
        # Change the domain's network configuration
        devices = root.find("devices")
        interface = devices.find("interface")
        mac = interface.find("mac")
        mac.set("address", self.__macAddress)
        source = interface.find("source")
        source.set("network", self.__virtualNetworkName)
        # Change the domain's data disk image path
        for disk in devices.iter("disk") :
            target = disk.find("target")
            source = disk.find("source")
            if (target.get("dev") == "vda") :
                # Operating system disk 
                source.set("file", self.__osImagePath)
            else :
                # Data disk
                source.set("file", self.__dataImagePath)
        # Change the VNC server configuration
        graphics = devices.find("graphics")
        graphics.set("port", str(self.__vncServerPort))
        graphics.set("passwd", self.__vncServerPassword)
        listen = graphics.find("listen")
        listen.set("address", self.__vncServerIPAddress)
        # Write the new XML file to its path
        return tree.tostring(root)
    
    def __checkErrors(self):
        if (self.__name == None or self.__uuid == None) :
            raise ConfigurationFileEditorException("The domain identifiers have not been set")
        if (self.__virtualNetworkName == None or self.__macAddress == None) :
            raise ConfigurationFileEditorException("The network configuration parameters have not been set")
        if (self.__vncServerIPAddress == None or self.__vncServerPassword == None or self.__vncServerPort == None) :
            raise ConfigurationFileEditorException("The VNC server configuration parameters have not been set")
        if (self.__dataImagePath == None or self.__osImagePath == None) :
            raise ConfigurationFileEditorException("The data image path has not been set")
        
if __name__ == "__main__" :
    editor = ConfigurationFileEditor("/home/luis/Squeeze_AMD64.xml", "/home/luis/Squeeze_AMD64_M.xml")
    editor.setDomainIdentifiers("squeeze_clone", "new_uuid")
    editor.setNetworkConfiguration("foo", "mac_addr")
    editor.setVNCServerConfiguration("192.168.100.100", 8080, "gominolas")
    editor.setImagePaths("os_image_path", "data_image_path")
    editor.generateOutputFile()
    