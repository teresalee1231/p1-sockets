# gotta get the socket api
from pickle import FALSE, TRUE
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

BUF_SIZE = 2048

# Set max number of clients that can be served
MAX_CONNECTIONS = 10

# Set host name and port used by server
HOST = 'localhost'
PORT = 9999
# (?) for attu
# HOST = 'attu2.cs.washington.edu'
# PORT = 12235

# Student ID
SID = 160
HEADER = '> L L H H' # packet header struct

def s_stage_a(s_udp, c_addr, udp_port):
    """
    Runs remaining stage A, with server sending response packet to client.
    """
    # Create server packet
    num = random.randint(1,20)
    len = random.randint(0,20)
    secretA = random.randint(1,500)

    s_plen = 16
    s_psecret = 0
    s_step = 2

    s_data = [s_plen, s_psecret, s_step, SID, num, len, udp_port, secretA]
    s_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet = s_struct.pack(*s_data)

    # Send server packet
    s_udp.sendto(s_packet, c_addr)
    return (num, len, udp_port, secretA)

def s_stage_b(s_udp ,num, len, udp_port, secretA):
    # stage b
    # want to verify the recieved data
    aligned_len = math.ceil(len/4) * 4
    s_struct = struct.Struct(f'{HEADER} L {aligned_len}B')
    s_data = s_udp.recv(1024)
    packet_id, payload_len, psecret, c_num = s_struct.unpack(s_data)

    # do the verifying
    # if not valid
    # close_connection()

    # payload
    secretB = random.randint(1, 500)
    tcp_port = random.randint(1, 1000) + 1024
    # TODO: idk how much the payload length is oops lol
    s_payload_len = payload_len + 4
    s_step = 1
    acked_packet_id = 0

    ack = random.randint(0,1)
    if ack == 1 :
        acked_packet_id += 1
        # continue
    else :
        # if it isnt acked, then we should send it back and recieve again??
        # TODO: figure out the else branch
        s_udp.sendto(s_struct, (HOST, PORT))

    if (c_num == num) :
        s_data = [s_payload_len, psecret, s_step, SID, num, len, acked_packet_id ,tcp_port, secretB]
        s_send_struct = struct.Struct(f'{HEADER} L L')
        s_packet = s_send_struct.pack(*s_data)
        s_udp.sendto(s_packet, (HOST, PORT))
    return(tcp_port, secretB)

def s_stage_c(s_tcp, tcp_port, secretB):
#     #stage c
    # Payload
    num2 = random.randint(1,500)
    len2 = random.randint(1,500)
    secretC = random.randint(1,500)
    char_c = 'a'.encode('utf-8')

    # Header
    payload_len = 13
    psecret = secretB #whatever came in from the header
    step = 2

    aligned_len = math.ceil(payload_len/4) * 4
    #zeros = [0] * (aligned_len - payload_len)
    s_data = [payload_len, psecret, step, SID, num2, len2, secretC, char_c]
    s_struct = struct.Struct(f'{HEADER} L L L c 3x')
    s_packet = s_struct.pack(*s_data)

    tcp_c.send(s_packet)

    return (num2, len2, char_c, tcp_c, secretC)


def s_stage_d(num2, len2, char_c, tcp_c, secretC):
#     #stage d


    for i in range(num2):
        tcp_c.recv(1024)

    # Payload
    secretD = random.randint(1,500)

    # Header
    payload_len = 4
    psecret = secretC #whatever came in from the client header
    step = 3

    s_data = [payload_len, psecret, step, SID, secretD]
    s_struct = struct.Struct(f'{HEADER} L')
    s_packet = s_struct.pack(*s_data)
    tcp_c.send(s_packet)


def detectedFailure(client_socket):
    # need to close thread, not just the socket
    client_socket.send(bytes("We've detected that something you sent didn't follow the protocol, closing connection.", 'utf-8'))
    client_socket.close()


def old_server():
    """
    Old echoServer code.
    """
    # Creates a socket, s for server
    # AF_INET is just what we use (IPv4) AF_INET6 for IPv6,
    # SOCK_DGRAM = UDP, SOCK_STREAM = TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket Created!')

    # binds the socket to the address (ip address, port)? still not sure
    # for localhost
    s.bind(('localhost', 9999))

    # for attu. is gethostname necessary?
    # https://docs.python.org/2/howto/sockets.html
    # Might need to keep it as gethostname(), tried doing specific didnt work,
    # In here it explains also why we should use gethostname()

    # print(socket.gethostname())
    # s.bind((socket.gethostname(), 12235))


    # doesn't need to specify a number, the argument is "backlog" meaning
    # the number of unaccepted connections that the system will
    # allow before refusing new connections, basically how many can be connected?
    s.listen(MAX_CONNECTIONS)
    print('waiting for connections')

    c, addr = s.accept()
    print("Connected with ", addr)
    c.send(bytes("You've connected to the server!", 'utf-8'))

    while True:
        echo = c.recv(1024).decode()
        print("Client sent: ", echo)
        c.send(bytes(echo, 'utf-8'))


def handle_client(s_udp, c_addr, udp_port):
    """
    s_udp: server udp socket to use to send response in stage A, send/receive in stage B
    c_addr: client address
    udp_port: port number of s_udp
    Handles given client by running the rest of Stage A, and Stages B,C,D.
    """
    # Run stage A and B
    num, len, udp_port, secretA = s_stage_a(s_udp, c_addr, udp_port)
    # s_tcp, tcp_port, secretB = s_stage_b(s_udp, num, len, udp_port, secretA)

    # TODO: move this into end of stage b establish TCP connection with client
    tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_port = bind_to_open_port(tcp_s)
    tcp_s.listen(MAX_CONNECTIONS)

    c_tcp, addr = tcp_s.accept()
    print("Connected with ", addr)

    # stage c and d
    secretB = 123
    num2, len2, char_c, tcp_c, secretC = s_stage_c(tcp_port, secretB)
    s_stage_d(num2, len2, char_c, tcp_c, secretC)

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
    print('Created Server Socket')
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
        # STAGE A
        c_packet, c_addr = s_udp_a.recvfrom(BUF_SIZE)
        c_plen, c_psecret, c_step, c_sid, payload = c_struct.unpack(c_packet)

        # TODO: validate client header + payload

        # Create dedicated udp port for client to use in stage B.
        s_udp_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_port = bind_to_open_port(s_udp_b)

        # handle client via thread
        c_thread = threading.Thread(target = handle_client, args = (s_udp_b, c_addr, udp_port))
        c_thread.start()


if __name__ == '__main__':
    #old_server()
    run_server()
