# gotta get the socket api
import socket
import random
import struct
import threading

# Set host name and port used by server
HOST = 'attu3.cs.washington.edu'
PORT = 12235

# Student ID
SID = 160

# the > makes every packet we send big-endian
HEADER = '> L L H H' # packet header struct
BUF_SIZE = 2048

# Server socket timeout (udp/tcp)
TIMEOUT = 3

# Set max number of clients that can be served by TCP socket
MAX_CONNECTIONS = 1

# Lock for binding to empty ports
port_bind_lock = threading.Lock()

def s_stage_a(s_udp, udp_port, c_addr, c_packet):
    """
    Validates a1 packet and runs stage A2, server sending response packet to client.
    Note that stage A1 is completed in run_server()
    """
    c_struct = struct.Struct(f'{HEADER} 12s')
    c_plen, c_psecret, c_step, c_sid, payload = c_struct.unpack(c_packet)
    print(f'Received a1 packet from client: {c_addr}')

    # Validate a1 header and payload
    if (c_plen != 12 or c_psecret != 0 or c_step != 1 or c_sid != SID) :
        detectedFailure()
    if (payload.decode() != "hello world\0") :
        detectedFailure()

    # generating random num
    num = random.randint(5,50)
    len = random.randint(5,50)
    secretA = random.randint(1,500)

    s_payload_len = 16
    s_psecret = 0
    s_step = 2

    s_data = [s_payload_len, s_psecret, s_step, SID, num, len, udp_port, secretA]
    s_struct = struct.Struct(f'{HEADER} L L L L')
    s_packet = s_struct.pack(*s_data)

    # Send server packet
    s_udp.sendto(s_packet, c_addr)
    return (num, len, secretA)


def s_stage_b(s_udp, c_addr, num, length, secretA):
    """
    Runs stage B, also creating and binding the server tcp socket for use in stages B and C.
    Args: server udp port to use, client address, args from stage A.
    Returns the server tcp socket, the tcp port number, and secretB.
    """
    # stage b

    # ack information
    ack_struct = struct.Struct(f'{HEADER} L')
    ack_payload_len = 4
    ack_step = 1

    # client packet info
    pad_len = (4 - (length % 4)) % 4
    client_struct = struct.Struct(f'{HEADER} L {length}B {pad_len}x')

    # For each packet we need to receive, in order
    curr_packet_id = 0
    has_not_ackd = False
    while curr_packet_id != num :
        print(f'Checking for packet {curr_packet_id}')
        # Must receive client packet
        s_data, addr = s_udp.recvfrom(BUF_SIZE)

        # Validate client packet
        c_payload_len, c_psecret, c_step, c_sid, c_packet_id, *c_payload = client_struct.unpack(s_data)
        # verifying header payload len = length + 4
        if (c_payload_len != length + 4) :
            detectedFailure()
        # verify rest of header
        if (c_psecret != secretA or c_step != 1 or c_sid != SID) :
            detectedFailure()
        # verify payload is all 0s
        for zero in c_payload :
            if (zero != 0) :
                detectedFailure()
        # verifying the # zeros in the payload
        if (length != len(c_payload)) :
            detectedFailure()
        # verifying that packets arrive in order
        if (c_packet_id > curr_packet_id or c_packet_id < 0):
            detectedFailure()
        elif (c_packet_id < curr_packet_id):
            # for some reason a previous packet was resent, so ignore it
            continue

        # Decide to ack or not
        ack = random.randint(0,1)

        # ensures that the first packet we don't acknowledge
        if not has_not_ackd:
            ack = 0
            has_not_ackd = True

        if ack == 1 :
            print(f'Ack packet {curr_packet_id}')
            # Send ack
            ack_data = [ack_payload_len, secretA, ack_step, SID, c_packet_id]
            ack_packet = ack_struct.pack(*ack_data)
            s_udp.sendto(ack_packet, c_addr)

            # Ack'd this packet, so move on to next packet
            curr_packet_id += 1

    # Create tcp socket for stage C and D. Has to be created here since we
    # gotta return the tcp port but don't know which ones are open.

    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_port = bind_to_random_port(s_tcp)

    # Create packet for stage b2
    secretB = random.randint(1, 500)

    s_payload_len = 8
    s_step = 2

    s_data = [s_payload_len, secretA, s_step, SID, tcp_port, secretB]
    s_send_struct = struct.Struct(f'{HEADER} L L')
    s_packet = s_send_struct.pack(*s_data)
    s_udp.sendto(s_packet, c_addr)
    return(s_tcp, secretB)

def s_stage_c(c_tcp, secretB):
    # stage c2
    # Payload
    num2 = random.randint(5,20)
    len2 = random.randint(5,50)
    secretC = random.randint(1,500)
    randomChar = random.randint(97, 122)
    char_c = chr(randomChar).encode('utf-8')

    # Header
    payload_len = 13
    psecret = secretB # whatever came in from the header
    step = 2

    s_data = [payload_len, psecret, step, SID, num2, len2, secretC, char_c]
    s_struct = struct.Struct(f'{HEADER} L L L c 3x')
    s_packet = s_struct.pack(*s_data)

    c_tcp.send(s_packet)
    return (num2, len2, secretC, char_c)

def s_stage_d(c_tcp, num2, len2, secretC, char_c):
    pad_len = (4 - (len2 % 4)) % 4
    c_struct = struct.Struct(f'{HEADER} {len2}c {pad_len}x')

    # recreate client packet to check its bytes against tcp stream
    chars = [char_c] * len2  # payload character array
    c_data = [len2, secretC, 1, SID] + chars
    c_sample_packet = c_struct.pack(*c_data)

    # packet validation loop variables
    c_packet_len = len(c_sample_packet)
    curr_packet = 0     # iterate up to num2 -1
    curr_byte = 0       # current byte in c_sample_packet
    validated_all_packets = False

    # iterate each tcp packet
    while not validated_all_packets:
        c_packet_stream = c_tcp.recv(BUF_SIZE)

        # iterate bytes in the tcp stream
        for b in c_packet_stream:
            if (b != c_sample_packet[curr_byte]):
                detectedFailure()
            # continue looping through sample packet
            curr_byte += 1
            if (curr_byte == c_packet_len):
                print(f'Finished validating packet {curr_packet}')
                curr_byte = 0
                curr_packet += 1
            # check if validated all packets
            if (curr_packet == num2):
                validated_all_packets = True
                break

    # Payload
    secretD = random.randint(1,500)

    # Header
    payload_len = 4
    psecret = secretC #whatever came in from the client header
    step = 2

    s_data = [payload_len, psecret, step, SID, secretD]
    s_struct = struct.Struct(f'{HEADER} L')
    s_packet = s_struct.pack(*s_data)
    c_tcp.send(s_packet)

def detectedFailure():
    # need to close thread
    raise Exception("There was an error in validating one of the packets")


def handle_client(c_addr, c_a1_packet):
    """
    Handles given client by running the rest of Stage A, and Stages B,C,D.
    Thread-safe (assuming s_udp won't be used by other threads).
    c_addr: client address
    c_a1_packet: step a1 packet from client
    """

    try:
        # Create dedicated udp port for client to use in stage A2 and B.
        # (to avoid concurrent access of s_udp_a)
        s_udp_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_udp_b.settimeout(TIMEOUT)
        udp_port = bind_to_random_port(s_udp_b)
        print(f'Created server UDP socket for a2/b: {udp_port}')
        # Run stage A and B
        num, len, secretA = s_stage_a(s_udp_b, udp_port, c_addr, c_a1_packet)
        s_tcp, secretB = s_stage_b(s_udp_b, c_addr, num, len, secretA)
    except Exception as e:
        print(f'There was an error in stage A/B: {str(e)}')
        return
    finally:
        s_udp_b.close()

    try:
        # Establish TCP connection with client (tcp socket was made/bound at end of stage B)
        s_tcp.listen(MAX_CONNECTIONS)
        c_tcp, c_tcp_addr = s_tcp.accept()
        c_tcp.settimeout(TIMEOUT)
        print("Established client tcp connection:", c_tcp_addr)
    except:
        print("There was an error establishing TCP connection with client")
        s_tcp.close()
        return

    try:
        # Run stage c and d
        num2, len2, secretC, char_c = s_stage_c(c_tcp, secretB)
        s_stage_d(c_tcp, num2, len2, secretC, char_c)
    except Exception as e:
        print(f'There was an error in stage C/D: {str(e)}')
        return
    finally:
        s_tcp.close()
        c_tcp.close()


def bind_to_random_port(s_socket):
    """
    Binds given server socket to a random port, returns the port number. Thread-safe.
    """
    with port_bind_lock:
        bound = False
        # try 100 times to find an open port
        for i in range(0, 100):
            try:
                # s_socket.bind((socket.gethostname(), random.randint(1024, 65535)))
                s_socket.bind((HOST, random.randint(1024, 65535)))
                bound = True
                break
            except:
                bound = False
        if bound == False:
             raise Exception("Could not find an open port to bind to.")
    return s_socket.getsockname()[1]

def run_server():
    """
    Runs the server.
    """

    # Create udp connection for Stage A
    print('Created Server UDP socket a')
    s_udp_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s_udp_a.bind((HOST, PORT))
    # s_udp_a.bind((socket.gethostname(), PORT))

    # Wait for client udp packets
    try:
        while True:
            print("Waiting for client connection...")
            # Recieve A1 packet ---------------------------
            c_packet, c_addr = s_udp_a.recvfrom(BUF_SIZE)

            # handle the rest of client stages via thread
            print(f'Create client thread')
            c_thread = threading.Thread(target = handle_client, args = (c_addr, c_packet))
            c_thread.start()
    except:
        print("Closing server")
        s_udp_a.close()

if __name__ == '__main__':
    run_server()
