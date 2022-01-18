# gotta get the socket api
import socket
import struct
# import utility functions; call with utils.helper.get_packet_header()
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.helper

# Set host name and port used by server
SERVER_HOST = 'localhost'
UDP_PORT = 9999
# HOST = 'attu2.cs.washington.edu'
# PORT = 12235

# Step number is always 1
STEP = 1

# Student ID. TODO: move to utils as global var
SID = 160

def stage_a(c):
    """
    Returns tuple containing (num, len, udp_port, secretA) from step a2.
    Args: udp socket to send data over
    Sends "hello world" UDP packet to attu2.cs.washington.edu on port 12235.
    Processes server UDP response.
    """
    print("stage a")

    # create packet to send
    c_struct = struct.Struct('> L L H H 12s')
    payload_len = 12
    psecret = 0
    payload = "hello world\0"
    c_data = [payload_len, psecret, STEP, SID, payload.encode('utf-8')]
    c_packet = c_struct.pack(*c_data)

    print(f'Sending: {str(c_packet)}')
    c.sendto(c_packet, (SERVER_HOST, UDP_PORT))

    # receive server packet
    s_struct = struct.Struct('> L L L L')
    s_packet, s_addr = c.recvfrom(1024)
    num, len, udp_port, secretA = s_struct.unpack(s_packet)
    print(f'Received: {num} {len} {udp_port} {secretA}')

def stage_b(num, len, udp_port, secretA):
    """
    Returns tuple containing (tcp_port, secretB) from step b2.
    Args: values provided by server from stage_a
    Sends num UDP packets to server on port udp_port, resending if needed.
    Processes all server UDP ack packets for each packet.
    Processes server b2 packet.
    """

def stage_c(tcp_port, secretB):
    """
    Returns tuple containing (num2, len2, secretC, c) from step c2.
    Args: values provided by server from stage_b
    Opens TCP connection to server on port tcp_port.
    Processes server c2 packet.
    """

def stage_d(num2, len2, secretC, c):
    """
    Returns secretD.
    Args: values provided by server from stage_d
    Sends num2 packets to server (on port tcp_port?).
    Processes server d2 packet.
    """

def run_client():
    """
    Runs the client and its stages.
    """
    # Create client UDP socket. TODO: do we need to support ipv6
    print("created client")
    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Run stages
    num, len, udp_port, secretA = stage_a
    tcp_port, secretB = stage_b(num, len, udp_port, secretA)
    num2, len2, secretC, c = stage_c(tcp_port, secretB)
    secretD = stage_d(num2, len2, secretC, c)

    # Close shop
    c.close()

if __name__ == '__main__':
    run_client()
