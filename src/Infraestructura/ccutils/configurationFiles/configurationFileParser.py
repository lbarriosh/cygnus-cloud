#coding=utf-8

from ConfigParser import ConfigParser, NoOptionError

from ccutils.configurationFiles.invalidConfigurationFileException import InvalidConfigurationFileException

class ConfigurationFileParser(object):
    """
    Parser del fichero de configuración del repositorio
    """
    
    def __init__(self):
        """
        Inicializa el estado del parser
        Argumentos:
            Ninguno
        """
        self.__config = ConfigParser()
        self._dict = dict()
        
    def _getExpectedSections(self):
        raise NotImplementedError
    
    def _readConfigurationParameters(self):
        raise NotImplementedError
    
    def parseConfigurationFile(self, configurationFilePath):
        tmp = self.__config.read(configurationFilePath)
        if (tmp == []):
            raise InvalidConfigurationFileException("Configuration file not found")
        
        expectedSections = self._getExpectedSections()
        readSections = self.__config.sections()
        for section in expectedSections:
            if (not section in readSections) :
                raise InvalidConfigurationFileException("Invalid configuration file: the section {0} is missing".section)
            
        self._readConfigurationParameters()
        
    def _readString(self, section, parameter):
        try :
            self._dict[parameter] = self.__config.get(section, parameter)
        except Exception:
                raise InvalidConfigurationFileException("Invalid configuration file: the parameter '{0}' on section '{1}' is missing".\
                                                        format(parameter, section))
                
    def _readInt(self, section, parameter):
        self.__readTypedValue(section, parameter, self.__config.getint, "an integer")
        
    def _readFloat(self, section, parameter):
        self.__readTypedValue(section, parameter, self.__config.getfloat, "a float")
        
    def _readBoolean(self, section, parameter):
        self.__readTypedValue(section, parameter, self.__config.getboolean, "a boolean")
                
    def __readTypedValue(self, section, parameter, readMethod, typeString):
        try :
            self._dict[parameter] = readMethod(section, parameter)
        except NoOptionError:
                raise InvalidConfigurationFileException("Invalid configuration file: the parameter '{0}' on section '{1}' is missing".\
                                                        format(parameter, section))
        except ValueError:
                raise InvalidConfigurationFileException("Invalid configuration file: the parameter '{0}' on section '{1}' must be {2} value".\
                                                        format(parameter, section, typeString))                
        
    def getConfigurationParameter(self, parameterName):
        return self._dict[parameterName]