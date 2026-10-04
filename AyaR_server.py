import socket
import threading
import os
from cryptography.hazmat.primitives.asymmetric import rsa  # AI PART
from cryptography.hazmat.primitives import serialization  # AI PART
import base64  # AI PART
from cryptography.hazmat.primitives.asymmetric import padding  # AI PART
from cryptography.hazmat.primitives import hashes  # AI PART
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # AI PART
from cryptography.hazmat.primitives import padding as sym_padding  # AI PART

# AI PART functions used to encrypt and decrypt text using Caesar
def caesar_encrypt(text, shift):
    encrypted_text = ""
    
    # Shift each character using its numeric value
    for char in text:
        encrypted_text += chr((ord(char) + shift) % 256)

    return encrypted_text


# AI PART
def caesar_decrypt(text, shift):
    decrypted_text = ""
    
    # Reverse the shift to get the original characters back
    for char in text:
        decrypted_text += chr((ord(char) - shift) % 256)

    return decrypted_text

# Create a separate thread so that we can have multiple clients connect at the same tim
class mythread(threading.Thread):

    def __init__(self, clientsocket, addr):
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket #Store the client's socket and address for this thread
        self.addr = addr

    def run(self):

        while True:
            # Wait to receive a packet from this client
            req = self.clientsocket.recv(2024)
            
            # Stop the thread if the client disconnects
            if not req:
                break
            
            
            # Convert received bytes to text, remove brackets and split packet fields
            msg = req.decode("utf-8")
            packet = msg.strip("()").split(",")
            
            # Check that the client sent a valid RFMP start packet
            if packet[0] == "SS" and packet[1] == "RFMP" and packet[2] == "v1.0":
                print("Valid packets received")
                
                # Mode 0 starts a connection without encryption
                if packet[3] == "0":
                    print("test this is not secure")
                    secure_mode = False

                    confirm_packet = "(CC)"
                    self.clientsocket.send(confirm_packet.encode("utf-8"))
                    
                # Mode 1 starts a secure connection
                elif packet[3] == "1":
                    print("test this is secure")
                    secure_mode = True
                    
                    # AI PART - generate the server RSA private and public keys
                    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)

                    public_key = private_key.public_key()

                    # Convert the public key to PEM bytes so it can be sent to the client
                    public_key_bytes = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

                    print("RSA keys generated")

                    confirm_packet = (b"(CC," + public_key_bytes + b")")

                    self.clientsocket.send(confirm_packet)
                    
                    
            # Handles the encryption packet sent by the client
            elif packet[0] == "EC":
                print("Encryption packet received")
                
                # Convert the Base64 session key from the packet back into bytes
                algorithm = packet[1]
              
                encrypted_session_key_b64 = packet[2]

                encrypted_session_key = base64.b64decode(encrypted_session_key_b64)

                print("Algorithm:", algorithm)
                print("Encrypted session key decoded from Base64")
                
                # AI PART - decrypt the session key using the server's RSA private key
                session_key = private_key.decrypt(encrypted_session_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))

                if algorithm == "Caesar":
                    caesar_key = session_key[0] % 26  # AI PART keep the Caesar shift between 0 and 25
                print("Session key decrypted successfully")


                # Decode and load the client's public key
                client_public_key_b64 = packet[3]
                client_public_key_bytes = base64.b64decode(client_public_key_b64)
                print("Client public key decoded from Base64")

                client_public_key = serialization.load_pem_public_key(client_public_key_bytes)
                print("Client public key loaded successfully")

                success_packet = "(SC)"
                self.clientsocket.send(success_packet.encode("utf-8"))

                print("Secure connection established successfully")
            
            elif packet[0] == "EE":
                print()
                
            # Handle the command requested by the client
            elif packet[0] == "CM":
                
                
                if packet [1] == "mkdir": # Makes directory 
                    try:
                        os.mkdir(packet[2]) # the os.mkdir() creates that directory on the server
                        # packet[2] contains the name of the new directory 
                        success_packet = "(SC)" # Send SC to tell the client the command was successful
                        self.clientsocket.send(success_packet.encode("utf-8"))
                        
                    except FileExistsError: # If the directory already exists it would send an error 
                        error_packet = "(EE,2,File already exists)"
                        self.clientsocket.send(error_packet.encode("utf-8"))
                        
                
                elif packet[1] == "cd":
                    try:
                        # packet[2] contains the directory the client wants to move into
                        # os.chdir() changes the current working directory
                        os.chdir(packet[2])
                        success_packet = "(SC)"
                        self.clientsocket.send(success_packet.encode("utf-8"))
                    except FileNotFoundError: # an error would happend if the directory wasn't found 
                        error_packet = "(EE,3,Directory not found)"
                        self.clientsocket.send(error_packet.encode("utf-8")) 
                        

                elif packet[1] == "del":
                    # packet[2] is the filename sent by the client
                    # os.remove() deletes that file from the server
                    os.remove(packet[2])
                    success_packet = "(SC)"
                    self.clientsocket.send(success_packet.encode("utf-8"))                    
                
                elif packet[1] == "ren":
                    # packet[2] is the old name and packet[3] is the new name
                    # os.rename() changes the file or directory name
                    os.rename(packet[2], packet[3]) 
                    success_packet = "(SC)"
                    self.clientsocket.send(success_packet.encode("utf-8"))
                    
                elif packet[1] == "rmdir":
                    # packet[2] contains the directory name that client wants to remove
                    # os.rmdir() removes the directory the client wants
                    os.rmdir(packet[2])
                    success_packet = "(SC)"
                    self.clientsocket.send(success_packet.encode("utf-8"))
                    
                elif packet[1] == "ls":
                    # os.listdir() gets the files and folders in the directory
                    # Convert the list to a string so it can be sent through the socket
                    listing =str( os.listdir()) 
                    success_packet = "(SC)" 
                    
                    self.clientsocket.send(success_packet.encode("utf-8")) # Send confirmation that the CM wored
                    self.clientsocket.send(listing.encode("utf-8")) # sends the client the actual list
                
                elif packet[1] == "size":
                    
                    # packet[2] contains the filename
                    # os.path.getsize() gets the file size in bytes
                    packet_size = str(os.path.getsize(packet[2])) #use str to  convert into string 
                    success_packet = "(SC)"
                    # Send success first, then send the file size
                    self.clientsocket.send(success_packet.encode("utf-8"))
                    self.clientsocket.send(packet_size.encode("utf-8"))
                    
                elif packet[1] == "exists":
                    # Check whether the file or directory in packet[2] exists or ont
                    # The result will be True or False and is converted to a string use str
                    exits = str(os.path.exists(packet[2]))
                    success_packet = "(SC)"
                    self.clientsocket.send(success_packet.encode("utf-8"))
                    self.clientsocket.send(exits.encode("utf-8"))
                                      
                
                elif packet[1] == "pwd": 
                    # os.getcwd() gets the server's current working directory
                    current_directory = os.getcwd()
                    success_packet = "(SC)"
                    self.clientsocket.send(success_packet.encode("utf-8"))
                    self.clientsocket.send(current_directory.encode("utf-8")) # sends the current directory path to client 
                    
                elif packet[1] == "touch":
                    # packet[2] contains the new filename
                    # Opening with "w" creates the file and close() leaves it empty
                    open(packet[2], "w").close()
                    success_packet = "(SC)"
                    self.clientsocket.send(success_packet.encode("utf-8"))
                
                   
                elif packet[1] == "openRead":
                    try:
                        # packet[2] contains the name of the file the client wants to read
                        # Open the file in read mode and store all of its contents in text
                        file = open(packet[2], "r")
                        text = file.read()
                        if secure_mode == True and algorithm == "AES": # Checks if client picked secure mode and if AES was chosen
                            
                            # Encryption is handled here before the file contents are sent
                            text_bytes = text.encode("utf-8")  # AI PART
                            padder = sym_padding.PKCS7(128).padder()  # AI PART
                            padded_text = padder.update(text_bytes) + padder.finalize()  # AI PART
                            iv = os.urandom(16)  # AI PART

                            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv))  # AI PART

                            encryptor = cipher.encryptor()  # AI PART
                            encrypted_text = encryptor.update(padded_text) + encryptor.finalize()  # AI PART
                            iv_b64 = base64.b64encode(iv).decode("utf-8")  # AI PART
                            encrypted_text_b64 = base64.b64encode(encrypted_text).decode("utf-8")  # AI PART
                            data_packet = "(DP," + iv_b64 + "," + encrypted_text_b64 + ")"  # AI PART
                        elif secure_mode == True and algorithm == "Caesar":
                            encrypted_text = caesar_encrypt(text, caesar_key)  # AI PART
                            encrypted_text_b64 = base64.b64encode(encrypted_text.encode("latin-1")).decode("utf-8")  # AI PART
                            data_packet = "(DP," + encrypted_text_b64 + ")"  # AI PART
                        else:
                            data_packet = "(DP," + text + ")"
                        
                        file.close() # Closes the file
                        success_packet = "(SC)" # Tell the client that openRead was successful
                        self.clientsocket.send(success_packet.encode("utf-8"))
                        self.clientsocket.send(data_packet.encode("utf-8"))  # Send the file contents inside the DP packet
                        
                    except FileNotFoundError: # Send an error packet if the requested file does not exist
                        error_packet = "(EE,1,File not found)"
                        self.clientsocket.send(error_packet.encode("utf-8"))        
                   
                # packet[2] contains the filename the client wants to write to
                # "w" opens the file for writing and creates it if it does not exist
                elif packet[1] == "openWrite":
                    file = open(packet[2], "w")
                
                else:
                    # If packet[1] is not any of the commands
                    # it will send an EE packet to tell the client the command is invalid 
                    error_packet = "(EE,4,Invalid command)"
                    self.clientsocket.send(error_packet.encode("utf-8"))
                    
                    
            # DP contains the file data sent by the client for openWrite
            elif packet[0] == "DP":
                # If AES was selected then the received data  must be decrypted before writing
                if secure_mode == True and algorithm == "AES":
                    
                    # Convert the Base64 IV and encrypted text back into bytes
                    iv = base64.b64decode(packet[1])  # AI PART
                    encrypted_text = base64.b64decode(packet[2])  # AI PART

                    # Create the AES cipher using the same session key and received IV
                    cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv))  # AI PART
                    decryptor = cipher.decryptor()  # AI PART
                    
                    # Decrypt the encrypted file contents
                    padded_text = decryptor.update(encrypted_text) + decryptor.finalize()  # AI PART

                    unpadder = sym_padding.PKCS7(128).unpadder()  # AI PART
                    text_bytes = unpadder.update(padded_text) + unpadder.finalize()  # AI PART
                    
                    # Convert the decrypted bytes back into normal readable text
                    text = text_bytes.decode("utf-8")  # AI PART

                elif secure_mode == True and algorithm == "Caesar": # If Caesar was selected then it will decode and decrypt the received text
                    # Decode Base64 first because the encrypted text was encoded before sending
                    encrypted_text = base64.b64decode(packet[1]).decode("latin-1")  # AI PART
                    text = caesar_decrypt(encrypted_text, caesar_key)  # AI PART

                else:
                    # In non secure mode the packet[1] already contains the original text
                    text = packet[1]

                # Write the final plain text into the file opened by openWrite
                file.write(text)
                file.close() # Closes the file 

                success_packet = "(SC)"
                self.clientsocket.send(success_packet.encode("utf-8"))
            
            elif packet[0] == "End": # If the client entered End it would exit the loop 
                break
         

        self.clientsocket.close() # Closes the clients connection 


def main():
    
    # Create the main TCP socket 
    start_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    port = 43214

    start_socket.bind(("127.0.0.1", port))
    start_socket.listen(10) # it listens for potential connections and can deal with 10 waiting clients

    print("Server is running")
    
    
    # Keep the server running so it can accept multiple clients
    while True:

        clientsocket, addr = start_socket.accept() # Wait for a client to connect and get its socket and address
        client_thread = mythread(clientsocket,addr) # Create a separate thread to handle this client

        # Start the thread so the server can continue accepting other clients
        client_thread.start() 


if __name__ == '__main__':
    main()