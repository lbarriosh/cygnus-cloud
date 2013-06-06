#coding=utf-8

from ccutils.configurationFiles.configurationFileParser import ConfigurationFileParser

class ClusterEndpointConfigurationFileParser(ConfigurationFileParser):
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
        return ['Database configuration', 'Network configuration', 'Other settings', 'Cluster server connection data']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'websiteUser', 'websiteUserPassword',
                'endpointUser', 'endpointUserPassword']
        for key in keys:
            self._readString('Database configuration', key)
            
        self._readBoolean('Network configuration', 'useSSL')
        self._readString('Network configuration', 'certificatePath')
        
        self._readString('Cluster server connection data', 'clusterServerIP')
        self._readInt('Cluster server connection data', 'clusterServerListenningPort')
        
        keys = ['statusDBUpdateInterval', 'minCommandInterval', 'commandTimeout', 'commandTimeoutCheckInterval']
        for key in keys:
            self._readInt('Other settings', key)