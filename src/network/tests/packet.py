# -*- coding: utf8 -*-
'''
Packet unit tests
@author: Luis Barrios Hernández
@version 1.0
'''
import unittest

from network.packet.packet import Packet, Packet_TYPE
from network.exceptions.packetException import PacketException

class PacketTests(unittest.TestCase):
    
    def setUp(self):
        self.p1 = Packet(Packet_TYPE.DATA, 10)

    def test_emptyPacket(self):       
        p2 = Packet(Packet_TYPE.DATA, 10)
        p2.__data = ' '
        p2.__packetType = Packet_TYPE.DATA
        p2.__priority = 10
        self.assertEquals(self.p1, p2, "Two empty packages of the same type\
            and with the same priority level must be equal")
        
    def test_writeSingleValue(self):        
        p2 = Packet(Packet_TYPE.DATA, 10)
        self.p1.writeString("It works")
        p2.__data = "string·It works·"
        self.assertEquals(self.p1, p2, "Two packages with the same type,\
            priority level and data must be equal")
        
    def test_writeMultipleValues(self):        
        p2 = Packet(Packet_TYPE.DATA, 10)
        self.p1.writeString("It works")
        self.p1.writeBool(True)
        self.p1.writeInt(10)
        self.p1.writeFloat(3.14159264)
        self.p1.writeLong(52)
        p2.__data = "string·It works·bool·True·int·10·float·3.14159264·"#long·52·"
        self.assertEquals(self.p1, p2, "Two packages with the same type,\
            priority level and data must be equal")
        
    def test_invalidWrite(self):
        self.assertRaises(PacketException, self.p1.writeBool, (10))
        self.assertRaises(PacketException, self.p1.writeString, (10))
        self.assertRaises(PacketException, self.p1.writeString, ('Invalid·String'))
        self.assertRaises(PacketException, self.p1.writeLong, ('foo'))
        self.assertRaises(PacketException, self.p1.writeInt, (1.0))
        self.assertRaises(PacketException, self.p1.writeFloat, (50))

if __name__ == "__main__":        
    unittest.main()