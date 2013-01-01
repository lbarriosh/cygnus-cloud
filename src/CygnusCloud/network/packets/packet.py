# -*- coding: utf8 -*-
"""
This module contains all the packet-related definitions.
@author: Luis Barrios Hernández
@version: 1.0
"""

from utils.enums import enum
from network.exceptions.packetException import PacketException

Packet_TYPE = enum('TICK', 'TOCK', 'DATA')

class Packet(object):
    """
    A class that stands for a packet
    @attention: Packet instances MUST ONLY be created through a NetworkManager
    to avoid priority issues that can cause serious errors in the network
    subsystem.
    @attention: The single underscore methods are semi-private, and MUST NOT
    be used along the user's code.
    """
    def __init__(self, packetType=Packet_TYPE.DATA, priority= 10):
        """
        Creates an empty packet with the type and priority given as arguments
        """
        self.__priority = priority
        self.__packetType = packetType
        self.__data = ''
        
    def _setContent(self, priority, data, packetType=Packet_TYPE.DATA):
        """
        Fills the packet with its arguments. This method is only used to create
        unit tests.
        """
        self.__packetType = packetType
        self.__priority = priority
        self.__data = data
        
    def writeInt(self, value):
        """
        Writes an integer value into the packet
        """
        self.__commonWriteCode(value, int, "int", True)
        
    def writeLong(self, value):
        """
        Writes a long integer value into the packet
        """
        try :
            self.__commonWriteCode(value, long, "long", True)
        except PacketException as e:
            if isinstance(value, int) :
                self.__commonWriteCode(value, long, "long", False)
            else : raise e
        
    def writeString(self, value):
        """
        Writes a string into the packet
        """
        if not isinstance(value, str):
            raise PacketException("The given value is not an " + self.__extractTypeName(str) + " instance")
        if '·' in value :
            raise PacketException('Strings cannot contain the \'·\' character')
        self.__commonWriteCode(value, str, "string", False)       
  
    
    def writeFloat(self, value):
        """
        Writes a float value into the packet
        """
        self.__commonWriteCode(value, float, "float", True)
        
    def writeBool(self, value):
        """
        Writes a boolean value into the packet
        """
        self.__commonWriteCode(value, bool, "bool", True)
        
    def readInt(self):
        """
        Reads an integer value from the packet
        """
        return self.__commonReadCode("int", int)
        
    def readLong(self):
        """
        Reads a long value from the packet
        """
        return self.__commonReadCode("long", long)
        
    def readBool(self):
        """
        Reads a bool value from the packet
        """
        return self.__commonReadCode("bool", bool)
        
    def readString(self):
        """
        Reads a string from the packet
        """
        return self.__commonReadCode("string", str)
    
    def readFloat(self):
        """
        Reads a float value from the packet
        """
        return self.__commonReadCode("float", float)
        
    def _serialize(self):
        """
        Converts the packet to a string
        """
        return "Packet(" + str(self.__packetType) + "," + str(self.__priority) + ")<" + self.__data + ">"
    
    def _getPacketType(self):
        """
        Returns the packet's type
        """
        return self.__packetType
    
    def getPriority(self):
        """
        Returns the packet's priority
        """
        return self.__priority
    
    def _setData(self, data):
        """
        Changes the data stored on a packet
        """
        self.__data = data
    
    @staticmethod
    def _deserialize(string):  
        """
        Converts a string to a readable packet
        """            
        # Read the packet header
        (header, _openingpar, tail) = string.partition("(")
        if (header != "Packet"):
            raise PacketException("Invalid packet string: Unknown header format")       
        (packetType, _comma, tail) = tail.partition(",") 
        try :            
            packetType = int(packetType)
            # Check if the packet type has an invalid value. If so, an exception will be raised.
            Packet_TYPE.reverse_mapping[packetType]
        except Exception :
            raise PacketException("Invalid packet string: Unknown packet type")
        (priority, _closingpar, tail) = tail.partition(")")
        try :
            priority = int(priority)
        except Exception :
            raise PacketException("Invalid packet string: Packet priority must be an integer")
        # Read the packet data
        data = tail[1:-1]
        # Create the packet
        p = Packet(packetType, priority)        
        p._setData(data)
        # Return the readable packet
        return p        
        
        
    def __eq__(self, other):
        if isinstance(other, Packet):
            samePriority = self.__priority == other.__priority
            sameType = self.__packetType == other.__packetType
            sameContent = self.__data == other.__data
            return samePriority and sameType and sameContent
        else: 
            return False
        
    def __extractTypeName(self, dataType):
        """
        Extracts the type name from a Python type string (i.e. <type 'bool'>)
        """
        (_head, _center, dataTypeStr) = str(dataType).partition("\'")
        (dataTypeStr, _center, _tail) = dataTypeStr.partition("\'")
        return dataTypeStr
    
    def hasMoreData(self):
        """
        Checks wether the packet has more data to read or not
        """
        return self.__data != ''
    
    def __commonWriteCode(self, value, dataType, field, checkType):
        """
        Code shared by all write operations
        """
        if checkType and not isinstance(value, dataType):            
            raise PacketException("The given value is not an " + self.__extractTypeName(str(dataType)) + " instance")
        dataToAdd = str(value)
        newLength = len(self.__data) + len(field) + len(dataToAdd) + 2
        if (newLength > 16000):
            # The maximum length is 16383 bytes. 383 bytes are reserved for the packet header.
            raise PacketException("There\'s not enough space to hold a " + self.__extractTypeName(str(dataType))\
                                   + " value")
        self.__data += field + '·' + dataToAdd + '·'
        
    def __commonReadCode(self, typeLabel, returnType):
        """
        Code shared by all read operations
        """
        (label,_dot,tail) = self.__data.partition("·")
        if (typeLabel != label) :
            raise PacketException("Can't read a " + self.__extractTypeName(returnType) + " value")
        (value,_dot,tail) = tail.partition("·")
        try :
            returnValue = returnType(value)
        except Exception :
            raise PacketException("Invalid packet string: label and data do not match")
        # Everything went OK => discard the read data
        self.__data = tail
        # Return the read value
        return returnValue
        
