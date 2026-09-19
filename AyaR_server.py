import socket 

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host= socket.gethostname()
port = 4321

start_socket.bind((host,port))
start_socket.listen(10) 

while True: 
    clientsocket, addr = start_socket.accept()
    
    while True:
        req = clientsocket.recv(2024)
        msg = req.decode("utf-8")
        packet = msg.strip("()").split(",") # so now we have the packet in a list 
        if packet[0] == "SS" and packet[1] == "RFMP" and packet[2] == "v1.0":
            print(" Valid packets recived")
            
            if packet[3] == "0":
                print("test this is not secure")
                confirm_packet = "(CC)"
                clientsocket.send(confirm_packet.encode("utf-8"))

                
        clientsocket.close()

                