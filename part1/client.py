# gotta get the socket api
import socket
import struct
import math
import datetime
# import utility functions; call with utils.helper.get_packet_header()
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.helper

# Set host name and port used by server
# to test locally
#SERVER_HOST = 'localhost'
#STAGE_A_PORT = 9999

# to test against hw server
SERVER_HOST = 'attu2.cs.washington.edu'
STAGE_A_PORT = 12235

# Globals
BUF_SIZE = 1024      # size of data buffer
HEADER = '> L L H H' # packet header struct
STEP = 1             # client header step number; always 1
SID = 160            # header student id
TIMEOUT = 2.0         # client retransmit interval (seconds); >=0.5

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
    c.sendto(c_packet, (SERVER_HOST, STAGE_A_PORT))

    # receive server packet
    s_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet, s_addr = c.recvfrom(BUF_SIZE)
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

    # set client timeout to retransmission interval
    c.settimeout(TIMEOUT)

    # create client packet struct, with byte-aligned payload
    aligned_len = math.ceil(len/4) * 4
    c_struct = struct.Struct(f'{HEADER} L {aligned_len}B')
    zeros = [0] * aligned_len # create 0s list
    c_payload_len = 4 + len

    # for each packet
    for i in range(num):
        print(f'Transmit udp packet {i}.')
        # create packet to send
        c_data = [c_payload_len, secretA, STEP, SID, i] + zeros
        c_packet = c_struct.pack(*c_data)

        # packet transmission loop, waits for server ack
        s_ack_struct = struct.Struct(f'{HEADER} L')
        acked = False
        while not acked:
            # send packet
            print(f'\tSending: {c_packet.hex()}')
            # print(f'\tTime: {datetime.datetime.now().time()}')
            c.sendto(c_packet, (SERVER_HOST, udp_port))

            # check for ack
            try:
                # receive server ack packet
                s_packet, s_addr = c.recvfrom(BUF_SIZE)
                s_plen, s_psecret, s_step, s_sid, acked_packet_id = s_ack_struct.unpack(s_packet)
                print(f'\tReceived ack for packet {acked_packet_id}: {s_packet}')
                # print(f'\tTime: {datetime.datetime.now().time()}')
                acked = (i == acked_packet_id)
            except socket.timeout:
                print(f'Timeout for packet {i}, retransmit.')
                # print(f'\tTime: {datetime.datetime.now().time()}')
                acked = False
        # move on to next packet (next loop)

    # all packets sent and acked, so process final server packet
    # unset client timeout
    c.settimeout(None)

    # receive server response
    s_struct = struct.Struct(f'{HEADER} L L')
    s_packet, s_addr = c.recvfrom(BUF_SIZE)
    s_plen, s_psecret, s_step, s_sid, tcp_port, secretB = s_struct.unpack(s_packet)
    print(f'Received: {tcp_port} {secretB}')
    return (tcp_port, secretB)

def stage_c(tcp_port, secretB):
    """
    Returns tuple containing (num2, len2, secretC, c) from step c2.
    Args: values provided by server from stage_b
    Opens TCP connection to server on port tcp_port.
    Processes server c2 packet.
    """
    print("stage c")

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
    num, len, udp_port, secretA = stage_a(c)

    # temp:
    # num, len, udp_port, secretA = (5, 1, 5555, 1212)

    tcp_port, secretB = stage_b(c, num, len, udp_port, secretA)
    num2, len2, secretC, c = stage_c(tcp_port, secretB)
    secretD = stage_d(num2, len2, secretC, c)

    # Close shop
    c.close()

if __name__ == '__main__':
    run_client()
