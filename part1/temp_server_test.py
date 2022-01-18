import socket
import struct

# create udp server
print("created server")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('localhost', 9999))

"""
STAGE A -------------------------------------------------------------
"""
print("stage a")

# receive client packet
ca_struct = struct.Struct('> L L H H 12s')
ca_packet, ca_addr = s.recvfrom(1024)
print("Received: " + str(ca_packet))

sa_packet = "stage a server udp packet".encode('utf-8')
print("Sending: " + str(sa_packet))
s.sendto(sa_packet, ca_addr)

"""
STAGE B -------------------------------------------------------------
"""

"""
STAGE C -------------------------------------------------------------
"""

"""
STAGE D -------------------------------------------------------------
"""
