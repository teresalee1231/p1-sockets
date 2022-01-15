# gotta get the socket api
import socket

# Creates a socket, s for server
s = socket.socket()
print('Socket Created!')

# binds the socket to the address (ip address, port)? still not sure
# for localhost
# s.bind(('localhost', 9999))

# for attu
print(socket.gethostname())
s.bind((socket.gethostname(), 12235))


# doesn't need to specify a number, the argument is "backlog" meaning
# the number of unaccepted connections that the system will
# allow before refusing new connections, basically how many can be connected?
s.listen(3)
print('waiting for connections')

c, addr = s.accept()
print("Connected with ", addr)
c.send(bytes("You've connected to the server!", 'utf-8'))

while True:
    echo = c.recv(1024).decode()
    print("Client sent: ", echo)
    c.send(bytes(echo, 'utf-8'))