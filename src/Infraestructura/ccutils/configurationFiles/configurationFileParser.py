#coding=utf-8

'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: configurationFileParser.py    
    Version: 3.0
    Description: ConfigParser-based configuration file parser
    
    Copyright 2012-13 Luis Barrios Hernández

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

from ConfigParser import ConfigParser, NoOptionError

from ccutils.configurationFiles.invalidConfigurationFileException import InvalidConfigurationFileException

class ConfigurationFileParser(object):
    """
    A ConfigParser-based generic configuration file parser.
    """    
    def __init__(self):
        """
        Initializes the parser's state
        Args:
            None
        """
        self.__config = ConfigParser()
        self._dict = dict()
        
    def _getExpectedSections(self):
        """
        Returns a list with the expected section headers.
        Args:
            None
        Returns:
            a list of strings containing the expected section headers
        """
        raise NotImplementedError
    
    def _readConfigurationParameters(self):
        """
        Reads the parsed configuration parameters.
        Args:
            None
        Returns:
            Nothing
        Raises: InvalidConfigurationFileException. This exception will be raised
            when 
            - an expected configuration parameter is missing, or when
            - a configuration parameter has an invalid value
        """
        raise NotImplementedError
    
    def parseConfigurationFile(self, configurationFilePath):
        """
        Parses the configuration file
        Args:
            None
        Returns:
            Nothing
        Raises: InvalidConfigurationFileException. This exception will be raised
            when 
             - an expected configuration parameter is missing, when
             - a configuration paramieter has an invalid value, or when
             - an expected section header is missing
        """
        tmp = self.__config.read(configurationFilePath)
        if (tmp == []):
            raise InvalidConfigurationFileException("Configuration file not found")
        
        expectedSections = self._getExpectedSections()
        readSections = self.__config.sections()
        
        if ("Uninitialized file" in readSections):
            raise InvalidConfigurationFileException("Invalid configuration file: you must initialize it before proceeding")
        
        for section in expectedSections:
            if (not section in readSections) :
                raise InvalidConfigurationFileException("Invalid configuration file: the section {0} is missing".section)
            
        self._readConfigurationParameters()
        
    def _readString(self, section, parameter):
        """
        Reads a string parameter's value
        Args:
            section: a section header
            parameter: a parameter name
        Returns:
            Nothing
        Raises:
            InvalidConfigurationFileException. This exception will be raised when 
            - the parameter is missing, or when
            - the parameter has an invalid value.
        """
        try :
            self._dict[parameter] = self.__config.get(section, parameter)
        except Exception:
                raise InvalidConfigurationFileException("Invalid configuration file: the parameter '{0}' on section '{1}' is missing".\
                                                        format(parameter, section))
                
    def _readInt(self, section, parameter):
        """
        Reads an integer parameter's value
        Args:
            section: a section header
            parameter: a parameter name
        Returns:
            Nothing
        Raises:
            InvalidConfigurationFileException. This exception will be raised when 
            - the parameter is missing, or when
            - the parameter has an invalid value.
        """
        self.__readTypedValue(section, parameter, self.__config.getint, "an integer")
        
    def _readFloat(self, section, parameter):
        """
        Reads a float parameter's value
        Args:
            section: a section header
            parameter: a parameter name
        Returns:
            Nothing
        Raises:
            InvalidConfigurationFileException. This exception will be raised when 
            - the parameter is missing, or when
            - the parameter has an invalid value.
        """
        self.__readTypedValue(section, parameter, self.__config.getfloat, "a float")
        
    def _readBoolean(self, section, parameter):
        """
        Reads a boolean parameter's value
        Args:
            section: a section header
            parameter: a parameter name
        Returns:
            Nothing
        Raises:
            InvalidConfigurationFileException. This exception will be raised when 
            - the parameter is missing, or when
            - the parameter has an invalid value.
        """
        self.__readTypedValue(section, parameter, self.__config.getboolean, "a boolean")
                
    def __readTypedValue(self, section, parameter, readMethod, typeString):
        """
        Reads a typed parameter's value
        Args:
            section: a section header
            parameter: a parameter name
        Returns:
            Nothing
        Raises:
            InvalidConfigurationFileException. This exception will be raised when 
            - the parameter is missing, or when
            - the parameter has an invalid value.
        """
        try :
            self._dict[parameter] = readMethod(section, parameter)
        except NoOptionError:
                raise InvalidConfigurationFileException("Invalid configuration file: the parameter '{0}' on section '{1}' is missing".\
                                                        format(parameter, section))
        except ValueError:
                raise InvalidConfigurationFileException("Invalid configuration file: the parameter '{0}' on section '{1}' must be {2} value".\
                                                        format(parameter, section, typeString))                
        
    def getConfigurationParameter(self, parameterName):
        """
        Returns a configuration parameter's value
        Args:
            parameterName: the configuration parameter's name
        Returns:
            the configuration parameter's value
        Raises: KeyError. This exception will be raised when the configuration
            parameter does not exist.
        """
        return self._dict[parameterName]