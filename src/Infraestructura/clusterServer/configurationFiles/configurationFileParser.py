#coding=utf-8

from ccutils.configurationFiles.configurationFileParser import ConfigurationFileParser

class ClusterServerConfigurationFileParser(ConfigurationFileParser):
    """
    Parser del fichero de configuración del repositorio
    """
    
    def __init__(self):
        """
        Inicializa el estado del parser
        Argumentos:
            Ninguno
        """
        ConfigurationFileParser.__init__(self)
        
    def _getExpectedSections(self):
        return ['Database configuration', 'Network configuration', 'Load balancer configuration', 'Other settings', 'Image repository connection data']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'dbUser', 'dbUserPassword']
        for key in keys:
            self._readString('Database configuration', key)        
        
        self._readBoolean('Network configuration', 'useSSL')
        self._readString('Network configuration', 'certificatePath')
        self._readInt('Network configuration', 'listenningPort')
        
        self._readString('Load balancer configuration', 'loadBalancingAlgorithm')
        keys = ['vCPUsWeight', 'vCPUsExcessThreshold', 'ramWeight', 'storageSpaceWeight', 'temporarySpaceWeight']
        for key in keys:
            self._readFloat('Load balancer configuration', key)
            
        keys = ['vmBootTimeout', 'statusUpdateInterval']
        for key in keys:
            self._readFloat('Other settings', key)
        self._readFloat('Other settings', 'averageCompressionRatio')
        
        self._readString('Image repository connection data', 'imageRepositoryIP')
        self._readInt('Image repository connection data', 'imageRepositoryPort')