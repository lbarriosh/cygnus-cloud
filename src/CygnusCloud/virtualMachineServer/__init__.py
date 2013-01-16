from libvirtConnector import libvirtConnector
# Initialize libvirt event loop
libvirtConnector.virEventLoopNativeStart()


from virtualNetwork import VirtualNetworkManager
from VMClient import VMClient
from Constantes import *

# Configure the virtual network
virtualNetwork = VirtualNetworkManager()
virtualNetwork.createVirtualNetwork(VNName, gatewayIP, NetMask, \
                                    DHCPStartIP, DHCPEndIP)
VMClient.virtualNetwork = virtualNetwork

def destroyVirtualNetwork():
    virtualNetwork.destroyVirtualNetwork(VNName)