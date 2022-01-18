# gotta get the socket api
import socket
import struct
import math
# import utility functions; call with utils.helper.get_packet_header()
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.helper

# Set host name and port used by server
SERVER_HOST = 'localhost'
# SERVER_HOST = 'attu2.cs.washington.edu'

# Globals
HEADER = '> L L H H'

# Client step number is always 1.
STEP = 1
# Student ID.
SID = 160

def stage_a(c):
    """
    Returns tuple containing (num, len, udp_port, secretA) from step a2.
    Args: client udp socket c
    Sends "hello world" UDP packet to attu2.cs.washington.edu on port 12235.
    Processes server UDP response.
    """
    print("stage a")

    # create packet to send
    c_struct = struct.Struct(f'{HEADER} 12s')
    c_payload_len = 12
    c_psecret = 0
    payload = "hello world\0"
    c_data = [c_payload_len, c_psecret, STEP, SID, payload.encode('utf-8')]
    c_packet = c_struct.pack(*c_data)

    print(f'Sending: {str(c_packet)}')
    c.sendto(c_packet, (SERVER_HOST, 9999))

    # receive server packet
    s_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet, s_addr = c.recvfrom(1024)
    s_plen, s_psecret, s_step, s_sid, num, len, udp_port, secretA = s_struct.unpack(s_packet)
    print(f'Received: {num} {len} {udp_port} {secretA}')
    return (num, len, udp_port, secretA)

def stage_b(c, num, len, udp_port, secretA):
    """
    Returns tuple containing (tcp_port, secretB) from step b2.
    Args: client udp socket c, values provided by server from stage_a
    Sends num UDP packets to server on port udp_port, resending if needed.
    Processes all server UDP ack packets for each packet.
    Processes server b2 packet.
    """
    print("stage b")
    # create client packet struct, with byte-aligned payload
    aligned_len = math.ceil(len/4) * 4
    c_struct = struct.Struct(f'{HEADER} L {aligned_len}B')
    # create 0s char list
    zeros = [0] * aligned_len

    for i in range(num):
        # create packet to send
        c_payload_len = 4 + len
        c_data = [c_payload_len, secretA, STEP, SID, i] + zeros
        print(c_data)
        c_packet = c_struct.pack(*c_data)

        print(f'Sending: {c_packet}')
        c.sendto(c_packet, (SERVER_HOST, udp_port))

        # TODO process server response

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
    # num, len, udp_port, secretA = stage_a(c)

    # temp:
    num, len, udp_port, secretA = (5, 1, 5555, 1212)

    tcp_port, secretB = stage_b(c, num, len, udp_port, secretA)
    num2, len2, secretC, c = stage_c(tcp_port, secretB)
    secretD = stage_d(num2, len2, secretC, c)

    # Close shop
    c.close()

if __name__ == '__main__':
    run_client()
