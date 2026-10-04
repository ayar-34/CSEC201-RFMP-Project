import socket
import os  
# AI ASSISTED SECTION: Encryption imports 
from cryptography.hazmat.primitives import serialization  # AI PART
from cryptography.hazmat.primitives.asymmetric import rsa  # AI PART
from cryptography.hazmat.primitives.asymmetric import padding  # AI PART
from cryptography.hazmat.primitives import hashes  # AI PART
import base64  # AI PART
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # AI PART
from cryptography.hazmat.primitives import padding as sym_padding  # AI PART

# # AI PART - Caesar encryption/decryption functions
def caesar_encrypt(text, shift):
    encrypted_text = ""
    
    # Shift each character using its numeric value
    for char in text:
        # % 256 keeps the value within the byte range
        encrypted_text += chr((ord(char) + shift) % 256)

    return encrypted_text


# AI PART
def caesar_decrypt(text, shift):
    decrypted_text = ""
    
    # Reverse the shift to get the original characters back
    for char in text:
        decrypted_text += chr((ord(char) - shift) % 256)

    return decrypted_text

# Create the client socket and connect to the server
cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 43214


cSocket.connect(("127.0.0.1", port)) # host and port

# Ask the user if they want a secure or non secure connection
connection_mode = input("Choose connection mode (0 : Non-secure, 1: Secure): ")
startpacket = "(SS,RFMP,v1.0," + connection_mode + ")"

 
cSocket.send(startpacket.encode('utf-8')) # Send the start packet to the server


msg = cSocket.recv(2024) # Receive the server response


print("The server has responded:")
print(msg.decode("utf-8"))

# No encryption is used unless secure mode is selected
encryption_type = None # AI part

# AI PART - secure connection setup using RSA and a session key
if connection_mode == "1":
    public_key_bytes = msg[4:-1] #Remove the packet characters around the key so only the public key is left

    # Turn the received public key bytes into a key Python can use
    server_public_key = serialization.load_pem_public_key(public_key_bytes)

    print("Server public key loaded successfully")

    session_key = os.urandom(32)  # AI PART - generate a random 32-byte session key for encryption
    print("Session key generated")

    # AI PART - encrypt the session key using the server's RSA public key
    encrypted_session_key = server_public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    print("Session key encrypted with server public key")

    # Convert the encrypted bytes to Base64 so they can be placed inside the RFMP packet
    encrypted_session_key_b64 = base64.b64encode(encrypted_session_key).decode("utf-8")

    print("Encrypted session key converted to Base64")

    # Generate an RSA key pair for the client
    client_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    client_public_key = client_private_key.public_key()
    print("Client RSA keys generated")
    
    # Convert the public key to PEM bytes so it can be sent to the server
    client_public_key_bytes = client_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("Client public key converted to bytes")

    # Convert the key to Base64 so it can be included safely in the EC packet
    client_public_key_b64 = base64.b64encode(
        client_public_key_bytes).decode("utf-8")

    print("Client public key converted to Base64")


    encryption_type = input("Choose the type of encryption method (AES/Caesar) : ")
    encryption_packet = ("(EC," + encryption_type + "," + encrypted_session_key_b64 + "," + client_public_key_b64 + ")")
    if encryption_type == "Caesar":
        caesar_key = session_key[0] % 26  # # AI PART - use the first byte of the session key and keep the shift between 0 and 25
        
        
        
    cSocket.send(encryption_packet.encode("utf-8"))

    print("Encryption packet sent to server")

    response = cSocket.recv(2024)

    print("Server response:", response.decode("utf-8"))

while True: # Keep asking the user for commands until they enter exit

    
    command = input("Enter command: ") # User enters command they want to use
    parts = command.split() # Split the user's input into parts, for example: "openRead file.txt" so it becomes ["openRead", "file.txt"]
    
    if parts[0] == "exit": # End the connection when the user enters exit

            end_message = "(End)"
            cSocket.send(end_message.encode("utf-8"))  
    
            break

     # Create the command packet depending on the number of inputs by checking how long parts is 
    if len(parts) == 3:
        command_packet = "(CM," + parts[0]+ "," + parts[1] + "," + parts[2] + ")"
    elif len(parts) == 2:
        command_packet = "(CM," + parts[0]+ "," + parts[1] + ")"
    
    elif len(parts) ==1 :
        command_packet = "(CM," + parts[0] + ")"
    

    # Send the command packet to the server
    print("Sending:", command_packet)
    cSocket.send(command_packet.encode("utf-8"))
    
    # Handle the openWrite command and get the text from the user
    if parts[0] == "openWrite":
        text = input("Enter text to write to file: ")

        # AI PART - encrypt the text using AES
        if encryption_type == "AES":
            # Encrypt the text using AES
            text_bytes = text.encode("utf-8")  # AI PART convert the user's text into bytes before encrypting it
            
            # AI PART - add padding so the text fits the AES block size
            padder = sym_padding.PKCS7(128).padder()  # AI PART
            padded_text = padder.update(text_bytes) + padder.finalize()  # AI PART

            iv = os.urandom(16)  # AI PART # AI PART - create a random 16-byte IV for AES

            # AI PART - create the AES cipher using the session key and CBC mode
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv))  # AI PART
            encryptor = cipher.encryptor()  # AI PART encrypt the padded file text
            encrypted_text = encryptor.update(padded_text) + encryptor.finalize()  # AI PART


            # Convert binary values to Base64 so they can safely be sent inside the packet
            iv_b64 = base64.b64encode(iv).decode("utf-8")  # AI PART
            encrypted_text_b64 = base64.b64encode(encrypted_text).decode("utf-8")  # AI PART

            data_packet = "(DP," + iv_b64 + "," + encrypted_text_b64 + ")"  # AI PART
            
        # AI PART - encrypt the text using Caesar
        elif encryption_type == "Caesar":
            encrypted_text = caesar_encrypt(text, caesar_key)  # AI PART
            encrypted_text_b64 = base64.b64encode(encrypted_text.encode("latin-1")).decode("utf-8")  # AI PART
            data_packet = "(DP," + encrypted_text_b64 + ")"  # AI PART
            
        #In non secure mode, send the text without encryption
        else:
            data_packet = "(DP," + text + ")"

        cSocket.send(data_packet.encode("utf-8"))
    
            
            

    response = cSocket.recv(2024)
    print("Command response:", response.decode("utf-8"))
    response_packet = response.decode("utf-8").strip("()").split(",")
    
    if response_packet[0] == "EE":
        continue
    
    if parts[0] == "openRead":
        data = cSocket.recv(2024)
        print("Data received:", data.decode("utf-8"))

        data_packet = data.decode("utf-8").strip("()").split(",")  # Remove the brackets and split the received DP packet into its separate fields


        if encryption_type == "AES":
            iv = base64.b64decode(data_packet[1])  # AI PART Convert the Base64 packet values back into their original bytes

            encrypted_text = base64.b64decode(data_packet[2])  # AI PART
            
            # AI PART use the same session key and received IV to decrypt the file contents
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv)) 

            decryptor = cipher.decryptor()  # AI PART

            padded_text = decryptor.update(encrypted_text) + decryptor.finalize()  # AI PART
            
            # Remove the AES padding that was added before encryption
            unpadder = sym_padding.PKCS7(128).unpadder()  # AI PART
            text_bytes = unpadder.update(padded_text) + unpadder.finalize()  # AI PART

            # Convert the decrypted bytes back into readable text
            text = text_bytes.decode("utf-8")  # AI PART

        elif encryption_type == "Caesar":
            encrypted_text = base64.b64decode(data_packet[1]).decode("latin-1")  # AI PART
            text = caesar_decrypt(encrypted_text, caesar_key)  # AI PART
        else:
            text = data_packet[1]
        
        print("File contents:", text)


    # Receiving from the server 
    if parts[0] == "pwd":
        # Receive the current directory path from the server
        current_d = cSocket.recv(2024)   
        print("Path: ", current_d.decode("utf-8"))
        
    if parts[0] == "ls":
        # receive the list of files and folders from the server
        lists = cSocket.recv(2024)
        print("Lists: ", lists.decode("utf-8"))

    if parts[0] == "size":
        #Receive whether the requested file exists or not
        size = cSocket.recv(2024)
        print("size: ", size.decode("utf-8"))
    
    if parts[0] == "exists":
        # Receive whether the requested file exists or not
        exits = cSocket.recv(2024)
        print("Exists: ", exits.decode("utf-8"))
   
cSocket.close() #Closes the client socket