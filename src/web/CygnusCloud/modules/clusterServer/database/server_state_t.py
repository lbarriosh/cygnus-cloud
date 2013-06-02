'''
Created on Jun 2, 2013

@author: luis
'''

from ccutils.enums import enum

SERVER_STATE_T = enum("BOOTING", "READY", "SHUT_DOWN", "RECONNECTING", "CONNECTION_TIMED_OUT")