# gotta get the socket api
from pickle import FALSE, TRUE
import socket
# import utility functions; call with utils.get_packet_header()
import sys
import os
import math
from part1.client import stage_c
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.helper
import random
import struct

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


def s_stage_a(c):
    s_struct = struct.Struct(f'{HEADER} 12s')
    sent_data = c.recv(1024)

    payload_len, psecret, step, studentNum, payload = s_struct.unpack(sent_data)

    # verify payload
    # if payload != hello world
    # close_connection()

    # generating random num
    num = random.randint(9999)
    len = random.randint(9999)
    udp_port = random.randint(9999)
    secretA = random.randint(9999)

    s_payload_len = 16
    #s_psecret =
    s_step = 0

    s_data = [s_payload_len, psecret, s_step, SID, num, len, udp_port, secretA]
    s_our_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet = s_our_struct.pack(*s_data)
    #sending
    c.sendto(s_packet, (HOST, PORT))

    #stage a
    return (num, len, udp_port, secretA)


              #temp s variable
def s_stage_b(c,num, len, udp_port, secretA):
    # transmit nump UDP packets on port udp_port (from stage a)

    # want to verify the recieved data
    aligned_len = math.ceil(len/4) * 4
    s_struct = struct.Struct(f'{HEADER} L {aligned_len}B')
    s_data = c.recv(1024)

    # do the verifying
    # if not valid
    # close

    packet_id = 0
    while packet_id != num :
        ack = random.randint(1)
        if ack == 1 :


    secretB = "temp"
    tcp_port = "temp"
    #do the sending



#     #stage b

def s_stage_c(tcp_port, secretB):
#     #stage c

    tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_s.bind(('localhost', tcp_port))
    tcp_s.listen(MAX_CONNECTIONS)
    print('waiting for connections')

    tcp_c, addr = tcp_s.accept()
    print("Connected with ", addr)
    tcp_c.send(bytes("You've connected to the server!", 'utf-8'))


    # Payload
    num2 = random.randint(500)
    len2 = random.randint(500)
    secretC = random.randint(500)
    char_c = 'a'

    # Header
    payload_len = 13
    psecret = secretB #whatever came in from the header
    step = 2

    aligned_len = math.ceil(payload_len/4) * 4
    zeros = [0] * (aligned_len - payload_len)
    s_data = [payload_len, psecret, step, SID, num2, len2, secretC, char_c] + zeros
    s_struct = struct.Struct(f'{HEADER} L L L 1s 3B')
    s_packet = s_struct.pack(*s_data)
    
    tcp_c.send(s_packet)

    return (num2, len2, char_c, tcp_c, secretC)


def s_stage_d(num2, len2, char_c, tcp_c, secretC):
#     #stage d

    # Payload
    secretD = random.randint(500)

    # Header
    payload_len = 4
    psecret = secretC #whatever came in from the client header
    step = 3

    s_data = [payload_len, psecret, step, SID, secretD]
    s_struct = struct.Struct(f'{HEADER} L')
    s_packet = s_struct.pack(*s_data)
    tcp_c.send(s_packet)


def detectedFailure(client_socket):
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
    s.listen(MAX_CONNECTIONS)
    print('waiting for connections')

    c, addr = s.accept()
    print("Connected with ", addr)
    c.send(bytes("You've connected to the server!", 'utf-8'))



    # Run Stages

    num, len, udp_port, secretA = s_stage_a(c)
    tcp_port, secretB = s_stage_b(num, len, udp_port, secretA)
    num2, len2, char_c, tcp_c, secretC = s_stage_c(tcp_port, secretB)
    s_stage_d(num2, len2, char_c, tcp_c, secretC)


if __name__ == '__main__':
    old_server()
    #run_server()



