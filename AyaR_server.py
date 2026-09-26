import socket 
from cryptography.hazmat.primitives.asymmetric import rsa #AI PART
from cryptography.hazmat.primitives import serialization # AI PART

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

                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )

                public_key = private_key.public_key()
                public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)

                print("RSA keys generated")
                confirm_packet = b"(CC," + public_key_bytes + b")"
                clientsocket.send(confirm_packet)
                
    
    clientsocket.close()

                