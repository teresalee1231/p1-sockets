# gotta get the socket api
import socket
import struct
import math
import time

# to test against hw server
# SERVER_HOST = 'attu2.cs.washington.edu'
# STAGE_A_PORT = 12235

# to test against our server
SERVER_HOST = 'attu3.cs.washington.edu'
STAGE_A_PORT = 12235

# Globals
BUF_SIZE = 2048      # size of data buffer
HEADER = '> L L H H' # packet header struct
STEP = 1             # client header step number; always 1
SID = 160            # header student id
TIMEOUT = 0.6        # client retransmit interval (seconds); >=0.5

def stage_a(c_udp):
    """
    Returns tuple containing (num, len, udp_port, secretA) from step a2.
    Args: client udp socket c
    Sends "hello world" UDP packet to SERVER_HOST on STAGE_A_PORT.
    Processes server UDP response.
    """
    print("\n\nSTAGE A")

    # create packet to send
    c_struct = struct.Struct(f'{HEADER} 12s')
    c_payload_len = 12
    c_psecret = 0
    payload = "hello world\0".encode('utf-8')   # turn string to bytes
    c_data = [c_payload_len, c_psecret, STEP, SID, payload]
    c_packet = c_struct.pack(*c_data)

    print(f'Sending: {str(c_packet)}')
    c_udp.sendto(c_packet, (SERVER_HOST, STAGE_A_PORT))

    # receive server packet
    s_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet, s_addr = c_udp.recvfrom(BUF_SIZE)
    s_plen, s_psecret, s_step, s_sid, num, len, udp_port, secretA = s_struct.unpack(s_packet)
    validate_header(s_plen, s_psecret, s_step, s_sid, 16, 0, 2)
    print(f'Received: {num} {len} {udp_port} {secretA}')
    return (num, len, udp_port, secretA)

def stage_b(c_udp, num, len, udp_port, secretA):
    """
    Returns tuple containing (tcp_port, secretB) from step b2.
    Args: client udp socket c_udp, values provided by server from stage_a
    Sends num UDP packets to server on port udp_port, resending if needed.
    Processes all server UDP ack packets for each packet.
    Processes server b2 packet.
    """
    print("\n\nSTAGE B")

    # set client timeout to retransmission interval
    c_udp.settimeout(TIMEOUT)

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
            c_udp.sendto(c_packet, (SERVER_HOST, udp_port))
            # check for ack
            try:
                # receive server ack packet
                s_packet, s_addr = c_udp.recvfrom(BUF_SIZE)
                s_plen, s_psecret, s_step, s_sid, acked_packet_id = s_ack_struct.unpack(s_packet)
                validate_header(s_plen, s_psecret, s_step, s_sid, 4, secretA, 1)
                acked = (i == acked_packet_id)
            except socket.timeout:
                acked = False
        # move on to next packet (next loop)

    # all packets sent and acked, so process final server packet
    # unset client timeout
    c_udp.settimeout(None)

    # receive server response
    s_struct = struct.Struct(f'{HEADER} L L')
    s_packet, s_addr = c_udp.recvfrom(BUF_SIZE)
    s_plen, s_psecret, s_step, s_sid, tcp_port, secretB = s_struct.unpack(s_packet)
    validate_header(s_plen, s_psecret, s_step, s_sid, 8, secretA, 2)
    print(f'Received: {tcp_port} {secretB}')
    return (tcp_port, secretB)

def stage_c(c_tcp, secretB):
    """
    Returns tuple containing (num2, len2, secretC, c) from step c2.
    Args: client tcp socket c_tcp, values provided by server from stage_b
    Processes server c2 packet.
    """
    print("\n\nSTAGE C")
    # receive server packet
    s_struct = struct.Struct(f'{HEADER} L L L c 3x') # 3x for 3 pad bytes
    s_packet = c_tcp.recv(BUF_SIZE)
    s_plen, s_psecret, s_step, s_sid, num2, len2, secretC, character = s_struct.unpack(s_packet)
    validate_header(s_plen, s_psecret, s_step, s_sid, 13, secretB, 2)
    print(f'Received: {num2} {len2} {secretC} {character}')
    return (num2, len2, secretC, character)

def stage_d(c_tcp, num2, len2, secretC, character):
    """
    Returns secretD.
    Args: client tcp socket c_tcp, values provided by server from stage_d
    Sends num2 packets to server via c_tcp.
    Processes server d2 packet.
    """
    print("\n\nSTAGE D")
    # create client packet struct, with 4-byte-aligned payload
    pad_len = (4 - (len2 % 4)) % 4
    c_struct = struct.Struct(f'{HEADER} {len2}c {pad_len}x')

    # create packet to send
    chars = [character] * len2  # payload character array
    c_data = [len2, secretC, STEP, SID] + chars
    c_packet = c_struct.pack(*c_data)

    # send num2 packets to server
    for i in range(num2):
        print(f'Sending tcp packet {i}.')
        c_tcp.sendall(c_packet)     # sendall ensures all bytes are sent

    # receive server packet
    s_struct = struct.Struct(f'{HEADER} L')
    s_packet = c_tcp.recv(BUF_SIZE)
    s_plen, s_psecret, s_step, s_sid, secretD = s_struct.unpack(s_packet)
    validate_header(s_plen, s_psecret, s_step, s_sid, 4, secretC, 2)
    print(f'Received: {secretD}')
    return secretD

def validate_header(s_plen, s_psecret, s_step, s_sid, plen, psecret, step):
    """
    Prints a message if the server header was incorrect.
    Technically the client doesn't have to check this.
    """
    if (s_plen != plen or s_psecret != psecret or s_step != step or s_sid != SID):
        print("Whoops the server sent an incorrect header")

def run_client():
    """
    Runs the client and its stages.
    """
    # Create client UDP socket.
    print("RUN CLIENT STAGES")
    c_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Run stages A and B
    num, len, udp_port, secretA = stage_a(c_udp)
    tcp_port, secretB = stage_b(c_udp, num, len, udp_port, secretA)

    # Create client TCP connection.
    c_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_tcp.connect((SERVER_HOST, tcp_port))

    # Run stages C and D
    num2, len2, secretC, character = stage_c(c_tcp, secretB)
    secretD = stage_d(c_tcp, num2, len2, secretC, character)

    # Close shop
    c_udp.close()
    c_tcp.close()

    # Print results
    print("\n\nFINISHED CLIENT STAGES")
    print(f'secretA: {secretA}')
    print(f'secretB: {secretB}')
    print(f'secretC: {secretC}')
    print(f'secretD: {secretD}')

if __name__ == '__main__':
    run_client()
