# -*- coding: utf8 -*-
'''
Domain configuration file generator
@author: Luis Barrios Hernández
@version 1.0
'''
import xml.etree.ElementTree as ET

class DomainConfigFileGeneratorException(Exception):
    """
    An exception class for the domain configuration file generator.
    """
    pass

class DomainConfigFileGenerator(object):
    """
    The domain configuration file generator class
    """
    def __init__(self):
        self.__name = None
        self.__uuid = None
        self.__memory = None
        self.__currentMemory = None
        self.__vcpu = None
    
    def setName(self, domainName):
        """
        Sets the domain name
        Args:
            domainName: the domain name to set
        Returns:
            Nothing
        Raises:
            DomainConfigFileGeneratorException: this exception will be raised if the
            domain name is already set.
        """
        if (self.__name != None):
            raise DomainConfigFileGeneratorException("The domain name is already set")
        self.__name = domainName
        
    def setUUID(self, domainUUID):
        """
        Sets the domain UUID
        Args:
            domainUUID: the domain UUID to set
        Returns:
            Nothing
        Raises:
            DomainConfigFileGeneratorException: this exception will be raised if the
            domain UUID is already set.
        """
        if (self.__uuid != None):
            raise DomainConfigFileGeneratorException("The domain UUID is already set")
        self.__uuid = domainUUID
        
    def setMemory(self, amount):
        """
        Sets the domain's memory amount
        Args:
            amount: The amount of memory (in bytes)
        Returns:
            Nothing
        Raises:
            DomainConfigurationException: this exception will be raised if the domain's memory
            amount is already set.
        """
        if (self.__memory != None) :
            raise DomainConfigFileGeneratorException("The domain memory amount is already set")
        self.__memory = amount
        
    def setCurrentMemory(self, amount):
        """
        Sets the domain's current memory amount
        Args:
            amount: The amount of current memory (in bytes)
        Returns:
            Nothing
        Raises:
            DomainConfigurationException: this exception will be raised if the domain's current memory
            amount is already set.
        """
        if (self.__currentMemory != None) :
            raise DomainConfigFileGeneratorException("The domain current memory amount is already set")
        self.__currentMemory = amount
        
        
    def setVCPU(self, vcpus):
        """
        Sets the domain's virtual CPU number
        Args:
            amount: The domain's virtual CPU number
        Returns:
            Nothing
        Raises:
            DomainConfigurationException: this exception will be raised if the domain's virtual CPU number is already set. 
        """
        if (self.__vcpu != None) :
            raise DomainConfigFileException("The virtual CPU number is already set")
        self.__vcpu = vcpus
    
        
    def generateXMLFile(self, outputFilePath):
        """
        Generates the .xml file
        Args:
            outputFilePath: the output file path
        Returns:
            Nothing
        Raises:
            DomainConfigFileGeneratorException: this exception will be raised if the
            file generator does not have all the required data.
        """
        self.__checkErrors()
        # Generate the root element
        root = ET.Element("domain")        
        root.set("type", "kvm")
        # Generate the name and UUID elements
        name = ET.SubElement(root, "name")
        name.text = self.__name
        uuid = ET.SubElement(root, "uuid")
        uuid.text = self.__uuid
        # Generate the memory, current memory and VCPU elements
        memory = ET.SubElement(root, "memory")
        memory.text = str(self.__memory)
        currentMemory = ET.SubElement(root, "currentMemory")
        currentMemory.text = str(self.__currentMemory)
        vcpu = ET.SubElement(root, "vcpu")
        vcpu.text = str(self.__vcpu)        
        tree = ET.ElementTree(root)
        tree.write(outputFilePath)
        
    def __checkErrors(self) :
        """
        Checks if the file generator is properly configured or not.
        Args:
            None
        Returns:
            Nothing
        Raises:
            DomainConfigFileGeneratorException: this exception will be raised if the
            file generator does not have all the required data.
        """
        if (self.__name == None) :
            raise DomainConfigFileGeneratorException("The domain name is not set")
        if (self.__uuid == None):
            raise DomainConfigFileGeneratorException("The domain UUID is not set")
        if (self.__memory == None) :
            raise DomainConfigFileGeneratorException("The memory size is not set")
        if (self.__currentMemory == None) :
            DomainConfigFileGeneratorException("The current memory size is not set")
        if (self.__vcpu == None) :
            DomainConfigFileGeneratorException("The virtual CPU number is not set")
        
if __name__ == "__main__" :
    gen = DomainConfigFileGenerator()
    gen.setName("Squeeze-AMD64")
    gen.setUUID("34ed2109-cd6d-6048-d47c-55bea73e39fd")
    gen.setMemory(1048576)
    gen.setCurrentMemory(1048576)
    gen.setVCPU(1)
    gen.generateXMLFile("/home/luis/output.xml")