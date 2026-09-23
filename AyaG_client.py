import socket

cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 4321

# s.connect((host, port))
cSocket.connect((host, port))

startpacket = "(SS,RFMP,v1.0,0)"

cSocket.send(startpacket.encode('utf-8'))


msg = cSocket.recv(2024)
print ("The server has responded: " + msg.decode('utf-8'))

cSocket.close()