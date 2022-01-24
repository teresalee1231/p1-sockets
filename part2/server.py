# gotta get the socket api
import socket
# import utility functions; call with utils.get_packet_header()
#import sys
#import os
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#import utils.helper
import random
import struct
import math
import threading

# Set host name and port used by server
HOST = 'localhost'
PORT = 9999
# (?) for attu
# HOST = 'attu2.cs.washington.edu'
# PORT = 12235

# Student ID
SID = 160
HEADER = '> L L H H' # packet header struct
BUF_SIZE = 2048

# Set max number of clients that can be served
MAX_CONNECTIONS = 10


def s_stage_a(s_udp, c_addr, udp_port):
    """
    Runs stage A2, server sending response packet to client.
    Note that stage A1 is completed in run_server()
    """
    # generating random num
    num = random.randint(1,20)
    len = random.randint(0,20)
    secretA = random.randint(1,500)

    s_payload_len = 16
    s_psecret = 0
    s_step = 2

    s_data = [s_payload_len, s_psecret, s_step, SID, num, len, udp_port, secretA]
    s_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet = s_struct.pack(*s_data)

    # Send server packet
    s_udp.sendto(s_packet, c_addr)
    return (num, len, udp_port, secretA)


def s_stage_b(s_udp, c_addr, num, len, udp_port, secretA):
    """
    Runs stage B, also creating and binding the server tcp socket for use in stages B and C.
    Args: server udp port to use, client address, args from stage A.
    Returns the server tcp socket, the tcp port number, and secretB.
    """
    # stage b
    # packet_id, payload_len, psecret, c_num = s_struct.unpack(s_data)

    # if not valid
    # close_connection()

    # ack information
    ack_struct = struct.Struct(f'{HEADER} L')
    ack_payload_len = 4
    ack_step = 1

    # client packet info
    aligned_len = math.ceil(len/4) * 4
    client_struct = struct.Struct(f'{HEADER} L {aligned_len}B')

    s_data, addr = s_udp.recvfrom(BUF_SIZE)

    packet_id = 0
    while packet_id != (num - 1) :
        ack = random.randint(0,1)
        if ack == 1 :
            c_payload_len, c_psecret, c_step, c_sid, c_packet_id, *c_payload = client_struct.unpack(s_data)
            ack_data = [ack_payload_len, secretA, ack_step, SID, c_packet_id]
            ack_packet = ack_struct.pack(*ack_data)
            s_udp.sendto(ack_packet, c_addr)
            packet_id = c_packet_id
            if (packet_id != (num - 1)):
                s_data, c_addr = s_udp.recvfrom(BUF_SIZE)

    # Create tcp socket for stage C and D. Has to be created here since we
    # gotta return the tcp port but don't know which ones are open.
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_port = bind_to_open_port(s_tcp)

    # Create packet for stage b2
    secretB = random.randint(1, 500)
    s_payload_len = 8
    s_step = 2
    s_data = [s_payload_len, secretA, s_step, SID, tcp_port, secretB]
    s_send_struct = struct.Struct(f'{HEADER} L L')
    s_packet = s_send_struct.pack(*s_data)
    s_udp.sendto(s_packet, c_addr)
    return(s_tcp, tcp_port, secretB)

def s_stage_c(c_tcp, secretB):
#     #stage c
    # Payload
    num2 = random.randint(1,20)
    len2 = random.randint(0,20)
    secretC = random.randint(1,500)
    char_c = 'a'.encode('utf-8')

    # Header
    payload_len = 13
    psecret = secretB #whatever came in from the header
    step = 2

    s_data = [payload_len, psecret, step, SID, num2, len2, secretC, char_c]
    s_struct = struct.Struct(f'{HEADER} L L L c 3x')
    s_packet = s_struct.pack(*s_data)

    c_tcp.send(s_packet)
    return (num2, len2, secretC, char_c)


def s_stage_d(c_tcp, num2, len2, secretC, char_c):
#     #stage d
    for i in range(num2):
        c_tcp.recv(1024)

    # Payload
    secretD = random.randint(1,500)

    # Header
    payload_len = 4
    psecret = secretC #whatever came in from the client header
    step = 3

    s_data = [payload_len, psecret, step, SID, secretD]
    s_struct = struct.Struct(f'{HEADER} L')
    s_packet = s_struct.pack(*s_data)
    c_tcp.send(s_packet)


def detectedFailure(client_socket):
    # need to close thread, not just the socket
    client_socket.send(bytes("We've detected that something you sent didn't follow the protocol, closing connection.", 'utf-8'))
    client_socket.close()


def handle_client(s_udp, c_addr, udp_port):
    """
    Handles given client by running the rest of Stage A, and Stages B,C,D.
    Thread-safe (assuming s_udp won't be used by other threads).
    s_udp: server udp socket to use to send response in stage A, send/receive in stage B
    c_addr: client address
    udp_port: port number of s_udp
    """
    # Run stage A and B
    num, len, udp_port, secretA = s_stage_a(s_udp, c_addr, udp_port)
    s_tcp, tcp_port, secretB = s_stage_b(s_udp, c_addr, num, len, udp_port, secretA)

    # Establish TCP connection with client (tcp socket was made at end of stage B).
    s_tcp.listen(MAX_CONNECTIONS)
    c_tcp, c_tcp_addr = s_tcp.accept()
    print("Established client tcp connection:", c_tcp_addr)

    # stage c and d
    num2, len2, secretC, char_c = s_stage_c(c_tcp, secretB)
    s_stage_d(c_tcp, num2, len2, secretC, char_c)

def bind_to_open_port(s_socket):
    """
    Binds given server socket to an open port, returns the port number.
    """
    s_socket.bind((HOST, 0))
    return s_socket.getsockname()[1]

def run_server():
    """
    Runs the server.
    """

    # Create udp connection for Stage A
    print('Created Server UDP socket a')
    s_udp_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # binds the socket to the address (ip address, port)? still not sure
    # for localhost
    s_udp_a.bind(('localhost', 9999))

    # for attu. is gethostname necessary?
    # https://docs.python.org/2/howto/sockets.html
    # Might need to keep it as gethostname(), tried doing specific didnt work,
    # In here it explains also why we should use gethostname()

    # print(socket.gethostname())
    # s.bind((socket.gethostname(), 12235))

    # doesn't need to specify a number, the argument is "backlog" meaning
    # the number of unaccepted connections that the system will
    # allow before refusing new connections, basically how many can be connected?

    # udp, just opens a socket and receives, doesn't need listen, or accept
    #s.listen(MAX_CONNECTIONS)
    #print('waiting for connections')

    #c, addr = s.accept()
    #print("Connected with ", addr)
    #c.send(bytes("You've connected to the server!", 'utf-8'))


    # Wait for client udp packets
    c_struct = struct.Struct(f'{HEADER} 12s')
    while True:
        print("Waiting for client connection...")
        # STAGE A1 ---------------------------
        c_packet, c_addr = s_udp_a.recvfrom(BUF_SIZE)
        c_plen, c_psecret, c_step, c_sid, payload = c_struct.unpack(c_packet)
        print(f'Received a1 packet from client: {c_addr}')

        # TODO: validate client header + payload

        # Create dedicated udp port for client to use in stage A2 and B.
        # (to avoid concurrent access of s_udp_a)
        s_udp_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_port = bind_to_open_port(s_udp_b)
        print(f'Created server UDP socket b: {udp_port}')

        # handle the rest of client stages via thread
        print(f'Create client thread')
        c_thread = threading.Thread(target = handle_client, args = (s_udp_b, c_addr, udp_port))
        c_thread.start()

if __name__ == '__main__':
    run_server()
