# -*- coding: utf8 -*-
'''
_Packet unit tests
@author: Luis Barrios Hernández
@version 1.0
'''
import unittest

from network.packet import _Packet, Packet_TYPE
from network.exceptions.packetException import PacketException

class PacketTests(unittest.TestCase):    
    
    def test_emptyPacket(self):    
        p1 = _Packet(Packet_TYPE.DATA, 10)   
        p2 = _Packet()
        p2._setContent(10, '', Packet_TYPE.DATA)
        self.assertEquals(p1, p2, "Two empty packages of the same type\
            and with the same priority level must be equal")
        
    def test_writeSingleValue(self): 
        p1 = _Packet(Packet_TYPE.DATA, 10)
        p2 = _Packet()
        p1.writeString("It works")
        p2._setContent(10, "string·It works·")
        self.assertEquals(p1, p2, "Two packages with the same type,\
            priority level and data must be equal")
        
    def test_writeMultipleValues(self):   
        p1 = _Packet(Packet_TYPE.DATA, 10)     
        p2 = _Packet()
        p1.writeString("It works")
        p1.writeBool(False)
        p1.writeInt(10)
        p1.writeFloat(3.14159264)
        p1.writeLong(52)
        p2._setContent(10, "string·It works·bool·False·int·10·float·3.14159264·long·52·")
        self.assertEquals(p1, p2, "Two packages with the same type,\
            priority level and data must be equal")
        
    def test_invalidWrites(self):
        p1 = _Packet(Packet_TYPE.DATA, 10)
        self.assertRaises(PacketException, p1.writeBool, (10))
        self.assertRaises(PacketException, p1.writeString, (10))
        self.assertRaises(PacketException, p1.writeString, ('Invalid·String'))
        self.assertRaises(PacketException, p1.writeLong, ('foo'))
        self.assertRaises(PacketException, p1.writeInt, (1.0))
        self.assertRaises(PacketException, p1.writeFloat, (50))
        
    def test_serialize(self):
        p1 = _Packet(Packet_TYPE.DATA, 10)
        p1.writeFloat(3.14159264)
        p1.writeString("It works")         
        p1.writeInt(10)  
        p1.writeBool(True)       
        p1.writeLong(52)
        self.assertEquals(p1._serialize(),
                          "_Packet(" + str(Packet_TYPE.DATA) + \
                          ",10)<float·3.14159264·string·It works·int·10·bool·True·long·52·>",
                          "The serialized strings must match")
         
    def test_deserialize(self):
        rawdata = "_Packet(" + str(Packet_TYPE.DATA) + ", 10)<int·10·float·3.14159264·>"
        p1 = _Packet._deserialize(rawdata)
        expected = _Packet(Packet_TYPE.DATA, 10)
        expected._setData("int·10·float·3.14159264·")
        self.assertEquals(p1, expected, "The deserialized packets must be equals")
        
    def test_read(self):
        rawdata = "_Packet(" + str(Packet_TYPE.DATA) + ", 10)<int·10·float·3.14159264·string·Hello, world!·int·0·long·60·>"
        p1 = _Packet._deserialize(rawdata)
        self.assertEquals(10, p1.readInt(), "The read integer must have the expected value")    
        self.assertEquals(3.14159264, p1.readFloat(), "The read float must have the expected value")   
        self.assertEquals("Hello, world!",p1.readString(), "The read string must have the expected value") 
        self.assertEquals(False, p1.readBool(), "The read bool must have the expected value")
        self.assertEquals(60L, p1.readLong(), "The read long must have the expected value")
        self.assertFalse(p1.hasMoreData(), "The packet should be empty after reading all its data")
        
    def test_invalidReads(self):
        rawdata = "_Packet(" + str(Packet_TYPE.DATA) + ", 10)<int·10·>"
        p1 = _Packet._deserialize(rawdata)
        self.assertRaises(PacketException, p1.readFloat)
        self.assertRaises(PacketException, p1.readString)
        self.assertRaises(PacketException, p1.readLong)
        self.assertRaises(PacketException, p1.readBool)
        self.assertIsInstance(p1.readInt(), int, "The read value must be an integer")
        
    def test_malformedPackages(self):
        # Wrong header 1: empty string
        rawData = ""
        self.assertRaises(PacketException, _Packet._deserialize, (rawData))
        # Wrong header 2: unknown package type
        rawData = "_Packet(-100, 0)<>"
        self.assertRaises(PacketException, _Packet._deserialize, (rawData))
        # Wrong header 3: crap priority
        rawData = "_Packet(-100, 0.1)<>"
        self.assertRaises(PacketException, _Packet._deserialize, (rawData))
        # Wrong data
        rawData = "_Packet(0, 10)<·int·hello, world!>"
        p = _Packet._deserialize(rawData)
        self.assertRaises(PacketException, p.readInt)

if __name__ == "__main__":        
    unittest.main()
