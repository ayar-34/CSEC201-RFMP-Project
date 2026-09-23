import socket 

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host= socket.gethostname()
port = 43214

start_socket.bind((host,port))
start_socket.listen(10) 

while True: 
    clientsocket, addr = start_socket.accept()
    
    while True:
        req = clientsocket.recv(2024)
        
        if not req:
            break
        msg = req.decode("utf-8")
        packet = msg.strip("()").split(",") # so now we have the packet in a list 
        if packet[0] == "SS" and packet[1] == "RFMP" and packet[2] == "v1.0":
            print(" Valid packets recived")
            
            if packet[3] == "0":
                print("test this is not secure")
                confirm_packet = "(CC)"
                clientsocket.send(confirm_packet.encode("utf-8"))
                
            elif packet[3] == "1":
                print("test this is secure")
                confirm_packet = "(CC, Server_public_key)"
                clientsocket.send(confirm_packet.encode("utf-8"))
            else:
                print("not valid")

                
    
    clientsocket.close()

                