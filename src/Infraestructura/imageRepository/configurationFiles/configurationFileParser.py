#coding=utf-8

from ccutils.configurationFiles.configurationFileParser import ConfigurationFileParser

class ImageRepositoryConfigurationFileParser(ConfigurationFileParser):
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
        return ['Database configuration', 'Network configuration', 'FTP Server configuration']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'dbUser', 'dbUserPassword']
        for key in keys:
            self._readString('Database configuration', key)
            
        self._readString('Network configuration', 'certificatePath')
        self._readInt('Network configuration', 'commandsPort')
        self._readBoolean('Network configuration', 'useSSL')
        
        keys = ['FTPListenningInterface', 'FTPRootDirectory', 'FTPUserName']
        for key in keys:
            self._readString('FTP Server configuration', key)
        
        keys = ['FTPPort', 'maxConnections', 'maxConnectionsPerIP', 'FTPPasswordLength']
        for key in keys:
            self._readInt('FTP Server configuration', key)
            
        keys = ['uploadBandwidthRatio', 'downloadBandwidthRatio']
        for key in keys:
            self._readFloat('FTP Server configuration', key)