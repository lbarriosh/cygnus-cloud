# -*- coding: utf8 -*-
'''
Domain configuration file generator
@author: Luis Barrios Hernández
@version 1.0
'''
try :
    import etree.cElementTree as ET
except ImportError:
    import etree.ElementTree as ET

from xml.exceptions.domain import DomainConfigurationException

class LibvirtXMLFileGenerator(object):
    """
    The domain configuration file generator class
    """
    def __init__(self):
        self.__name = None
        self.__uuid = None
        self.__memory = None
        self.__currentMemory = None
        self.__vcpu = None
        self.__bootSequence = None
        self.__features = None
        self.__clock_offset = None
        self.__event_handlers = None
    
    def setName(self, domainName):
        """
        Sets the domain name
        Args:
            domainName: the domain name to set
        Returns:
            Nothing
        Raises:
            DomainConfigurationException: this exception will be raised if the
            domain name is already set.
        """
        if (self.__name != None):
            raise DomainConfigurationException("The domain name is already set")
        self.__name = domainName
        
    def setUUID(self, domainUUID):
        """
        Sets the domain UUID
        Args:
            domainUUID: the domain UUID to set
        Returns:
            Nothing
        Raises:
            DomainConfigurationException: this exception will be raised if the
            domain UUID is already set.
        """
        if (self.__uuid != None):
            raise DomainConfigurationException("The domain UUID is already set")
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
            raise DomainConfigurationException("The domain memory amount is already set")
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
            raise DomainConfigurationException("The domain current memory amount is already set")
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
            raise DomainConfigurationException("The virtual CPU number is already set")
        self.__vcpu = vcpus
        
    def setFeatures(self, acpi, apic, pae):
        if not (isinstance(acpi, bool) and isinstance(apic, bool) and isinstance(pae, bool)) :
            raise DomainConfigurationException("The supplied arguments must boe bool instances")
        if (self.__features != None) :
            raise DomainConfigurationException("The domain features are already set")
        self.__features = (acpi, apic, pae)
    
    def setBootSequence(self, seq):
        if (self.__bootSequence != None) :
            raise DomainConfigurationException("The boot sequence is already set")
        LibvirtXMLFileGenerator.__checkBootSequence(seq)
        self.__bootSequence = seq
        
    def setClockOffset(self, offset):
        if (self.__clock_offset != None) :
            raise DomainConfigurationException("The clock offset is already set")
        if (offset != "localtime" and offset != "utc") :
            raise DomainConfigurationException("Wrong clock offset value: must be either \'localtime\' or \'utc\'")
        self.__clock_offset = offset
        
    def setEventHandlers(self, pwroff, reboot, crash):     
        if (self.__event_handlers != None) :
            raise DomainConfigurationException("The event handlers are already configured")
        LibvirtXMLFileGenerator.checkEventHandler(pwroff)
        LibvirtXMLFileGenerator.checkEventHandler(reboot)
        LibvirtXMLFileGenerator.checkEventHandler(crash)
        self.__event_handlers = (pwroff, reboot, crash)
        
    @staticmethod
    def checkEventHandler(string):
        if (string != "destroy" and string != "restart") :
            raise DomainConfigurationException("The event handlers must be either \'destroy\' or \'restart\'")
        
    @staticmethod
    def __checkBootSequence(seq):
        if (seq == []) :
            raise DomainConfigurationException("The boot sequence must not be empty")
        for device in seq :
            if (device != "fd" and device != "hd" and device != "cdrom" and device != "network") :
                raise DomainConfigurationException("Unknown boot device")
        
    def generateXMLFile(self, outputFilePath):
        """
        Generates the .xml file
        Args:
            outputFilePath: the output file path
        Returns:
            Nothing
        Raises:
            DomainConfigurationException: this exception will be raised if the
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
         
        # Generate the OS element
        os = ET.SubElement(root, "os")
        _type = ET.SubElement(os, "type")
        _type.set("arch", "x86_64")
        _type.set("machine", "pc-1.0")
        _type.text = "hvm"
        for bootDevice in self.__bootSequence :
            boot = ET.SubElement(os, "boot")
            boot.set("dev", bootDevice)        
        
        # Generate the features element
        features = ET.SubElement(root, "features")
        (acpi, apic, pae) = self.__features
        if (acpi) :
            ET.SubElement(features, "acpi")
        if (apic) :
            ET.SubElement(features, "apic")
        if (pae):
            ET.SubElement(features, "pae")    
            
        # Configure the event handlers
        (pwroff, reboot, crash) = self.__event_handlers
        handler = ET.SubElement(root, "on_poweroff")
        handler.text = pwroff
        handler = ET.SubElement(root, "on_reboot")
        handler.text = reboot
        handler = ET.SubElement(root, "on_crash")
        handler.text = crash
        
        # Generate the .xml file
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
            DomainConfigurationException: this exception will be raised if the
            file generator does not have all the required data.
        """
        if (self.__name == None) :
            raise DomainConfigurationException("The domain name is not set")
        if (self.__uuid == None):
            raise DomainConfigurationException("The domain UUID is not set")
        if (self.__memory == None) :
            raise DomainConfigurationException("The memory size is not set")
        if (self.__currentMemory == None) :
            raise DomainConfigurationException("The current memory size is not set")
        if (self.__vcpu == None) :
            raise DomainConfigurationException("The virtual CPU number is not set")
        if (self.__bootSequence == None):
            raise DomainConfigurationException("The boot sequence is not set")
        if (self.__features == None) :
            raise DomainConfigurationException("The domain features are not set")
        if (self.__clock_offset == None) :
            raise DomainConfigurationException("The clock offset is not set")
        if (self.__event_handlers == None) :
            raise DomainConfigurationException("The event handlers are not configured")
        
if __name__ == "__main__" :
    gen = LibvirtXMLFileGenerator()
    gen.setName("Squeeze-AMD64")
    gen.setUUID("34ed2109-cd6d-6048-d47c-55bea73e39fd")
    gen.setMemory(1048576)
    gen.setCurrentMemory(1048576)
    gen.setVCPU(1)
    gen.setBootSequence(["fd", "cdrom", "hd"])
    gen.setFeatures(True, True, True)
    gen.setClockOffset("utc")
    gen.setEventHandlers("destroy","restart", "restart")
    gen.generateXMLFile("/home/luis/output.xml")