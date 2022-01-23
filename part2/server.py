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


def s_stage_a(s):
    s_struct = struct.Struct(f'{HEADER} 12s')
    sent_data, c_addr = s.recvfrom(1024)

    payload_len, psecret, step, studentNum, payload = s_struct.unpack(sent_data)

    # verify payload
    # if payload != hello world
    # close_connection()

    # generating random num
    num = random.randint(1,500)
    len = random.randint(1,500)
    udp_port = random.randint(1,500)
    secretA = random.randint(1,500)

    s_payload_len = 16
    s_step = 0

    s_data = [s_payload_len, psecret, s_step, SID, num, len, udp_port, secretA]
    s_our_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet = s_our_struct.pack(*s_data)
    #sending
    s.sendto(s_packet, c_addr)
    return (num, len, udp_port, secretA)


def s_stage_b(c,num, len, udp_port, secretA):
    # stage b

    # needs to listen to the new port udp_port
    s_new_port = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('New UDP_PORT Socket Created!')
    s_new_port.bind(('localhost', udp_port))

    # packet_id, payload_len, psecret, c_num = s_struct.unpack(s_data)

    # if not valid
    # close_connection()

    # payload
    secretB = random.randint(1, 500)
    tcp_port = random.randint(1, 1000) + 1024
    s_payload_len = 4
    s_step = 1
    packet_id = 0

    aligned_len = math.ceil(len/4) * 4
    client_struct = struct.Struct(f'{HEADER} L {aligned_len}B')
    while packet_id == (num - 1) :
        ack = random.randint(0,1)
        s_data = c.recvfrom(1024)
        if ack == 1 :
            payload_len, psecret, step, studentNum, a_packet_id, a_plen = client_struct.unpack(s_data)
            sendback = [s_payload_len, secretA, s_step, SID, a_packet_id]
            sb_struct = struct.Struct(f'{HEADER} L')
            packed = sb_struct.pack(*sendback)
            c.sendto(packed, (HOST, PORT))
            packet_id = a_packet_id

    s_payload_len = 8
    s_data = [s_payload_len, secretA, s_step, SID,tcp_port, secretB]
    s_send_struct = struct.Struct(f'{HEADER} L L')
    s_packet = s_send_struct.pack(*s_data)
    c.sendto(s_packet, (HOST, PORT))
    return(tcp_port, secretB)

def s_stage_c(tcp_port, secretB):
#     #stage c

    tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind(('localhost', tcp_port))
    tcp_s.listen(MAX_CONNECTIONS)
    print('waiting for connections')

    tcp_c, addr = tcp_s.accept()
    print("Connected with ", addr)
    #tcp_c.send(bytes("You've connected to the server!", 'utf-8'))


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




def run_server():
    """
    Runs the server.
    """

    print('Created Server Socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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


    # udp, just opens a socket and receives, doesn't need listen, or accept
    #s.listen(MAX_CONNECTIONS)
    #print('waiting for connections')

    #c, addr = s.accept()
    #print("Connected with ", addr)
    #c.send(bytes("You've connected to the server!", 'utf-8'))



    # Run Stages

    num, len, udp_port, secretA = s_stage_a(s)
    tcp_port, secretB = s_stage_b(num, len, udp_port, secretA)

    # testing stage c and d
    # tcp_port = 1000
    # secretB = 1000
    num2, len2, char_c, tcp_c, secretC = s_stage_c(tcp_port, secretB)
    s_stage_d(num2, len2, char_c, tcp_c, secretC)


if __name__ == '__main__':
    #old_server()
    run_server()
