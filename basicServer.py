# gotta get the socket api
import socket

# Creates a socket, s for server
s = socket.socket()
print('Socket Created!')

# binds the socket to the address (ip address, port)? still not sure
s.bind(('localhost', 9999))


# doesn't need to specify a number, the argument is "backlog" meaning
# the number of unaccepted connections that the system will
# allow before refusing new connections, basically how many can be connected?
s.listen(3)
print('waiting for connections')

# the server just sits here
while True:
    # s.accept() returns a value in a pair
    # (conn, address) where conn is a new socket object
    # usable to send and receive data on the connection
    c, addr = s.accept()

    # remember that the client sent over the name
    # so we are receiving it 
    name = c.recv(1024).decode()

    # prints some information we were given
    print("Connected with ", addr, name)

    # Sends over message to the client!
    c.send(bytes('Welcome to the dungeuon', 'utf-8'))
