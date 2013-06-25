# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: libvirtConnector.py    
    Version: 3.0
    Description: libvirt connector definitions
    
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

import threading
import libvirt
try :
    import xml.etree.cElementTree as ET
except ImportError:
    import etree.ElementTree as ET
    
class LibvirtConnector(object):
    """
    libvirt connector
    """
     
    # Hypervisor names
    KVM = "qemu"
    Xen = "xen"  
    
    def __init__(self, hypervisor, startCallback, shutdownCallback):
        """
        Initializes the connector's state
        Args:
            hypervisor: the hypervisor to use's name
            startCallback: domain start events callback
            shutdownCallback: domain stop events callback
        """
        # Initialize the event loop thread
        self.__startVirEventLoop()            
        
        self.__startCallback = startCallback
        self.__shutdownCallback = shutdownCallback
        # Build the hypervisor's URI and connect to it
        uri = ""
        uri += hypervisor
        uri += "://"
        uri += "/system"
        self.__libvirtConnection = libvirt.open(uri)
        self.__libvirtConnection.domainEventRegisterAny(None,
                                              libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                              self.__configureDomainEventHandlers, None) 
           
    def __configureDomainEventHandlers(self, conn, domain, eventID, detail, data):
        """
        Configures libvirt's event handlers
        Args:
            conn: unused
            domain: the domain associated with the event
            eventID: unused
            detail: unused
            data: unused
        Returns:
            Nothing
        """
        eventHandler = {
         libvirt.VIR_DOMAIN_EVENT_DEFINED: self.__onDomainDefined,
         libvirt.VIR_DOMAIN_EVENT_UNDEFINED: self.__onDomainUndefined,
         libvirt.VIR_DOMAIN_EVENT_STARTED: self.__onDomainStarted,
         libvirt.VIR_DOMAIN_EVENT_SUSPENDED: self.__onDomainSuspended,
         libvirt.VIR_DOMAIN_EVENT_RESUMED: self.__onDomainResumed,
         libvirt.VIR_DOMAIN_EVENT_STOPPED: self.__onDomainStopped,
         libvirt.VIR_DOMAIN_EVENT_SHUTDOWN: self.__onDomainShutDown}
        eventHandler[eventID](domain)
        
    def __onDomainDefined(self, domain):
        """
        Handles a domain definition event
        Args:
            domain: the defined domain
        Returns:
            Nothing
        """
        pass    
    
    def __onDomainSuspended(self, domain):
        """
        Handles a domain suspension event
        Args:
            domain: the suspended domain
        Returns:
            Nothing
        """
        pass    
    
    def __onDomainResumed(self, domain):
        """
        Handles a domain resume event
        Args:
            domain: the resumed domain
        Returns:
            Nothing
        """
        pass    
    
    def __onDomainUndefined(self, domain):
        """
        Handles a domain undefinition event
        Args:
            domain: the undefined domain
        Returns:
            Nothing
        """
        pass    
   
    def __onDomainStopped(self, domain):
        """
        Handles a domain stop event
        Args:
            domain: the stopped domain
        Returns:
            Nothing
        """
        self.__shutdownCallback._onDomainStop(domain.name())
        pass    
    
    def __onDomainShutDown(self, domain):
        """
        Handles a domain shut down event
        Args:
            domain: the shut down domain
        Returns:
            Nothing
        """
        pass    
    
    def __onDomainStarted(self, domain):
        """
        Handles a domain start event
        Args:
            domain: the started domain
        Returns:
            Nothing
        """
        xmlTree = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        graphics_element = xmlTree.find('.//graphics')
        vnc_port = graphics_element.attrib['port']
        vnc_password = graphics_element.attrib['passwd']
        listen_element = graphics_element.find('.//listen')
        vnc_server_ip = listen_element.attrib['address']
        domainInfo = {"name" : domain.name(),
                      "VNCport" : int(vnc_port),
                      "VNCip" : vnc_server_ip,
                      "VNCpassword" : vnc_password}
        self.__startCallback._onDomainStart(domainInfo)    
    
    def startDomain(self, definitionFile):
        """
        Starts a domain
        Args:
            definitionFile: the domain configuration string
        Returns:
            Nothing
        """
        self.__libvirtConnection.createXML(definitionFile, libvirt.VIR_DOMAIN_NONE)        
    
    def destroyAllDomains(self):
        """
        Destroys all the domains
        Args:
            None
        Returns:
            Nothing    
        """
        domainIDs = self.__libvirtConnection.listDomainsID()
        for domainID in domainIDs:
            domain = self.__libvirtConnection.lookupByID(domainID)
            domain.destroy()    
           
    def destroyDomain(self, domainName):
        """
        Destroy a domain
        Args:
            domainName: the domain to destroy's name
        Returns:
            Nothing
        """             
        targetDomain = self.__libvirtConnection.lookupByName(domainName)
        targetDomain.destroy()
        
    def shutdownDomain(self, domainName):
        """
        Shuts down a domain
        Args:
            domainName: the domain to shut down's name
        Returns:
            Nothing
        """             
        targetDomain = self.__libvirtConnection.lookupByName(domainName)
        targetDomain.shutdown()
        
    def rebootDomain(self, domainName):
        """
        Reboots a domain
        Args:
            domainName: the domain to reboot's name
        Returns:
            Nothing
        """             
        targetDomain = self.__libvirtConnection.lookupByName(domainName)
        targetDomain.reset(0) # The flags are unused at the current version of the libvirt API
            
    def getActiveDomainNames(self):
        """
        Returns the active domains' names
        Args:
            None
        Returns:
            a list containing the active domains' names
        """
        domainIDs = self.__libvirtConnection.listDomainsID()
        result = []
        for domainID in domainIDs:
            domain = self.__libvirtConnection.lookupByID(domainID)
            xmlTree = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
            domainName = xmlTree.find('.//name').text
            result.append(domainName)
        return result   
    
    def getNumberOfDomains(self):
        """
        Returns the number of domains
        Args:
            None
        Returns:
            The number of domains
        """
        return self.__libvirtConnection.numOfDomains()
    
    def getStatusData(self):
        """
        Returns libvirt's status data
        Args:
            None
        Returns:
            A dictionary with two keys:
            - memory: the domains' RAM total RAM size
            - #vcpus: the domain's total VCPUs.
        """
        idsMV = self.__libvirtConnection.listDomainsID()
        vcpus = 0
        for idVM in idsMV :
            domain = self.__libvirtConnection.lookupByID(idVM)
            info = domain.info()
            vcpus += info[3]
        return {"#domains" : self.__libvirtConnection.numOfDomains(),
                "#vcpus" : vcpus}    

    def __startVirEventLoop(self):
        """
        Starts the libvirt event loop
        Args:
            None
        Returns:
            Nothing
        """
        def runVirEventLoop():
            while True:
                libvirt.virEventRunDefaultImpl()
        libvirt.virEventRegisterDefaultImpl()
        self.__eventLoopThread = threading.Thread(target=runVirEventLoop, name="libvirt event loop")
        self.__eventLoopThread.setDaemon(True)
        self.__eventLoopThread.start()