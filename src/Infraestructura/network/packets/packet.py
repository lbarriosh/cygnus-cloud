# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packet.py    
    Version: 3.0
    Description: network packet definitions
    
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

from ccutils.enums import enum
from network.exceptions.packetException import PacketException

# Packet type enum type. DO NOT MODIFY!
Packet_TYPE = enum('DATA')

# Data type enum type. DO NOT MOFIFY!
_DATA_TYPE = enum("INT", "LONG", "STRING", "FLOAT")

__max_packet_length = 64 * 1024 # 64 KB

class _Packet(object):
    """
    These objects stand for network packets.
    @attention: in order to avoid priority issues that can cause errors or malfunctions in the network
    subsystem, _Packet instances MUST be created through a NetworkManager object.
    @attention: The single underscore methods are semi-private, and MUST NOT
    be used at the user's code.
    """
    def __init__(self, packetType=Packet_TYPE.DATA, priority= 10):
        """
        Creates an empty packet with the type and priority given as arguments
        Args:
            packetType: The new packet's type
            priority: The new packet's priority
        """
        self.__priority = priority
        self.__packetType = packetType
        self._data = ''
        self.__sender_ip = None
        self.__sender_port = None
        
    def _setSenderData(self, sender_ip, sender_port):
        """
        Stores the sender's data into the packet.
        Args:
            senderIP: the sender's IPv4 address
            sender_port: the sender's port
        Returns:
            Nothing
        """
        self.__sender_ip = sender_ip
        self.__sender_port = sender_port
        
    def getSenderData(self):
        """
        Returns the sender's IPv4 address and port
        Args:
            None
        Returns:
            A tuple (sender_ip, sender_port) containing the sender's IPv4
            address and port.
        """
        return (self.__sender_ip, self.__sender_port)
        
    def _setContent(self, priority, data, packetType=Packet_TYPE.DATA):
        """
        Sets the packet's content.
        Args:
            priority: the new packet's priority
            data: the new packet's data
            packetType: the new packet's type
        Returns:
            Nothing
        """
        self.__packetType = packetType
        self.__priority = priority
        self._data = data
        
    def writeInt(self, value):
        """
        Writes an integer value into the packet
        Args:
            value: an integer value
        Returns:
            Nothing
        Raises:
            PacketException: these exceptions will be raised when type errors are detected
                and when the packet has not enough room to hold the value.
        """
        self.__commonWriteCode(value, int, _DATA_TYPE.INT, True)
        
    def writeLong(self, value):
        """
        Writes a long integer value into the packet
        Args:
            value: a long integer value
        Raises:
            PacketException: these exceptions will be raised when type errors are detected
                and when the packet has not enough room to hold the value.
        """
        try :
            self.__commonWriteCode(value, long, _DATA_TYPE.LONG, True)
        except PacketException as e:
            if isinstance(value, int) :
                self.__commonWriteCode(value, long, _DATA_TYPE.LONG, False)
            else : raise e
        
    def writeString(self, value):
        """
        Writes a string into the packet
        Args:
            value: a string
        Raises:
            PacketException: these exceptions will be raised when type errors are detected
                and when the packet has not enough room to hold the value.
        """
        if not (isinstance(value, str) or isinstance(value, unicode)):
            raise PacketException("The given value is not an " + self.__extractTypeName(str) + " instance")
        if '$' in value :
            raise PacketException('Strings cannot contain the \'$\' character')
        self.__commonWriteCode(value, str, _DATA_TYPE.STRING, False)       
  
    
    def writeFloat(self, value):
        """
        Writes a float value into the packet.
        Args:
            value: a float value
        Raises:
            PacketException: these exceptions will be raised when type errors are detected
                and when the packet has not enough room to hold the value.
        """
        self.__commonWriteCode(value, float, _DATA_TYPE.FLOAT, True)
        
    def writeBool(self, value):
        """
        Writes a boolean value into the packet.
        Args:
            value: a bool value
        Raises:
            PacketException: these exceptions will be raised when type errors are detected
                and when the packet has not enough room to hold the value.
        """
        if not isinstance(value, bool) :
            raise PacketException("The given value is not a " + self.__extractTypeName(str(bool)) + " instance")
        if (value) :
            self.writeInt(1)
        else :
            self.writeInt(0)
            
    def dumpData(self, packet):
        """
        Dumps another packet's data into this one.
        Args:
            packet: the packet whose data will be written into this one.
        Returns:
            Nothing
        """
        self._data += packet._getData()
        
    def readInt(self):
        """
        Reads an integer value from the packet.
        @attention: All the read operations are destructive.
        Args:
            None
        Returns:
            the read int value. 
        Raises:
            PacketException: this exceptions will be raised when the value cannot be read
            from the packet.
        """
        return self.__commonReadCode(_DATA_TYPE.INT, int)
        
    def readLong(self):
        """
        Reads a long value from the packet
        @attention: All the read operations are destructive.
        Args:
            None
        Returns:
            the read long value.
        Raises:
            PacketException: this exceptions will be raised when the value cannot be read
            from the packet.
        """
        return self.__commonReadCode(_DATA_TYPE.LONG, long)
        
    def readBool(self):
        """
        Reads a bool value from the packet
        @attention: All the read operations are destructive.
        Args:
            None
        Returns:
            the read bool value.
        Raises:
            PacketException: this exceptions will be raised when the value cannot be read
            from the packet.
        """
        return self.readInt() == 1
        
    def readString(self):
        """
        Reads a string from the packet
        @attention: All the read operations are destructive.
        Args:
            None
        Returns:
            the read string. 
        Raises:
            PacketException: this exceptions will be raised when the value cannot be read
            from the packet.
        """
        return self.__commonReadCode(_DATA_TYPE.STRING, str)
    
    def readFloat(self):
        """
        Reads a float value from the packet        
        @attention: All the read operations are destructive.
        Args:
            None
        Returns:
            the read float value. 
        Raises:
            PacketException: this exceptions will be raised when the value cannot be read
            from the packet.
        """
        return self.__commonReadCode(_DATA_TYPE.FLOAT, float)
        
    def _serialize(self):
        """
        Converts the packet to a string
        Args:
            None
        Returns:
            A string with this packet's data, ready to be sent.
        """
        return str(self.__packetType) + "," + str(self.__priority) + "," + self._data
    
    def _getPacketType(self):
        """
        Returns the packet's type
        Args: 
            None
        Returns:
            This packet's type.
        """
        return self.__packetType
    
    def getPriority(self):
        """
        Returns the packet's priority
        Args:
            None
        Returns:
            This packet's priority
        """
        return self.__priority
    
    def _setData(self, data):
        """
        Changes the data stored on a packet
        Args:
            data: new packet data
        Returns:
            Nothing
        """
        self._data = data
        
    def transferData(self, packet):
        """
        Copies an existing packet's data into this packet
        Args:
            packet: the packet whose data we are going to copy
        Returns:
            Nothing
        """
        self._data = packet._data
        
    def _getData(self):
        """
        Returns this packet's data
        Args:
            None
        Returns:
            A string containing the packet's data
        @attention: This method must not be used from the client code, and will always be
        used with testing purposes.
        """
        return self._data
    
    @staticmethod
    def _deserialize(string):  
        """
        Converts a string to a readable packet
        Args:
            string: a serialized packet (in a string form)
        Returns:
            The deserialized packet. 
        Raises:
            PacketException: If the packet header is corrupt, a PacketException will be raised.
        """            
        # Read the packet header       
        (packetType, _comma, tail) = string.partition(",") 
        try :            
            packetType = int(packetType)
            # Check if the packet type has an invalid value. If so, an exception will be raised.
            Packet_TYPE.reverse_mapping[packetType]
        except Exception :
            raise PacketException("Invalid packet string: Unknown packet type")
        (priority, _comma, tail) = tail.partition(",")
        try :
            priority = int(priority)
        except Exception :
            raise PacketException("Invalid packet string: packet priority must be an integer")
        # Create the packet
        p = _Packet(packetType, priority)        
        p._setData(tail)
        # Return the readable packet
        return p        
        
        
    def __eq__(self, other):
        """
        Compares to packets by their content.
        Args:
            other: the other packet to consider
        Returns:
            True if both packets have identical content, and False otherwise.
        """
        if isinstance(other, _Packet):
            samePriority = self.__priority == other.__priority
            sameType = self.__packetType == other.__packetType
            sameContent = self._data == other._data
            return samePriority and sameType and sameContent
        else: 
            return False
        
    def __extractTypeName(self, dataType):
        """
        Extracts the type name from a Python type string (i.e. <type 'bool'>)
        Args: 
            dataType: a pythonic data type string
        Returns:
            A string with the type name (i.e. \'bool\' instead of \'<type \'bool\'>\')
        """
        (_head, _center, dataTypeStr) = str(dataType).partition("\'")
        (dataTypeStr, _center, _tail) = dataTypeStr.partition("\'")
        return dataTypeStr
    
    def hasMoreData(self):
        """
        Checks wether the packet has more data to read or not
        Args:
            None
        Returns:
            True if the packet has more data to read or False otherwise.
        """
        return self._data != ''
    
    def __commonWriteCode(self, value, dataType, field, checkType):
        """
        Code shared by all write operations
        Args:
            value: the value to write into the packet
            dataType: the expected value datatype (i.e. integer, boolean, float,...)
            field: the label to use in the data string
            checkType: when True, the value's data type will be checked. When False,
            the value will be written directly into the data string.
        Returns:
            Nothing
        Raises:
            PacketException: these exceptions will be raised when type errors are detected
                and when the packet has not enough room to hold the value.
        """
        if checkType and not isinstance(value, dataType):            
            raise PacketException("The given value is not an " + self.__extractTypeName(str(dataType)) + " instance")
        dataToAdd = str(value)
        newLength = len(self._data) + len(str(field)) + len(dataToAdd) + 2
        if (newLength > __max_packet_length):
            # The maximum TCP segment length is 65536 bytes. 536 bytes are reserved for the packet header.
            raise PacketException("There\'s not enough space to hold a " + self.__extractTypeName(str(dataType))\
                                   + " value")
        self._data += str(field) + '$' + dataToAdd + '$'
        
    def __commonReadCode(self, typeLabel, returnType):
        """
        Code shared by all read operations
        Args:
            typeLabel: The type label (i.e. int for integer values, string for strings, and so on)
            returnType: The value type to return (i.e. str for strings, int for integers, and so on).
        Returns:
            A value read from the packet. 
        Raises:
            PacketException: this exceptions will be raised when the packet's current value does not
            match with the type label and when the packet value and the type label do not match.
        """
        (label,_dollar,tail) = self._data.partition("$")
        if (typeLabel != int(label)) :
            raise PacketException("Can't read a " + self.__extractTypeName(returnType) + " value")
        (value,_dollar,tail) = tail.partition("$")
        try :
            returnValue = returnType(value)
        except Exception :
            raise PacketException("Invalid packet string: label and data types do not match")
        # Everything went OK => discard the read data
        self._data = tail
        # Return the read value
        return returnValue
        
