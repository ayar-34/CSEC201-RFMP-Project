import socket
from cryptography.hazmat.primitives import serialization  # AI PART
from cryptography.hazmat.primitives.asymmetric import rsa  # AI PART
import os  
from cryptography.hazmat.primitives.asymmetric import padding  # AI PART
from cryptography.hazmat.primitives import hashes  # AI PART
import base64  # AI PART
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # AI PART
from cryptography.hazmat.primitives import padding as sym_padding  # AI PART

# AI PART
def caesar_encrypt(text, shift):
    encrypted_text = ""

    for char in text:
        encrypted_text += chr((ord(char) + shift) % 256)

    return encrypted_text


# AI PART
def caesar_decrypt(text, shift):
    decrypted_text = ""

    for char in text:
        decrypted_text += chr((ord(char) - shift) % 256)

    return decrypted_text

cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 43214

# s.connect((host, port))
cSocket.connect((host, port))

connection_mode = input("Choose connection mode (0 : Non-secure, 1: Secure): ")
startpacket = "(SS,RFMP,v1.0," + connection_mode + ")"

 
cSocket.send(startpacket.encode('utf-8'))


msg = cSocket.recv(2024)


print("The server has responded:")
print(msg.decode("utf-8"))

encryption_type = None # AI part

if connection_mode == "1":
    public_key_bytes = msg[4:-1] # Extract public key only 
    server_public_key = serialization.load_pem_public_key(public_key_bytes)

    print("Server public key loaded successfully")

    session_key = os.urandom(32)  # AI PART
    print("Session key generated")

    encrypted_session_key = server_public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    print("Session key encrypted with server public key")


    encrypted_session_key_b64 = base64.b64encode(encrypted_session_key).decode("utf-8")

    print("Encrypted session key converted to Base64")

    client_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    client_public_key = client_private_key.public_key()
    print("Client RSA keys generated")

    client_public_key_bytes = client_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print("Client public key converted to bytes")


    client_public_key_b64 = base64.b64encode(
        client_public_key_bytes).decode("utf-8")

    print("Client public key converted to Base64")


    encryption_type = input("Choose the type of encryption method (AES/Caesar) : ")
    encryption_packet = ("(EC," + encryption_type + "," + encrypted_session_key_b64 + "," + client_public_key_b64 + ")")
    if encryption_type == "Caesar":
        caesar_key = session_key[0] % 26  # AI PART
        
        
        
    cSocket.send(encryption_packet.encode("utf-8"))

    print("Encryption packet sent to server")

    response = cSocket.recv(2024)

    print("Server response:", response.decode("utf-8"))

while True:
    
    command = input("Enter command: ")
    parts = command.split()
    
    if parts[0] == "exit":
            end_message = "(End)"
            cSocket.send(end_message.encode("utf-8"))  
    
            break

    if len(parts) == 3:
        command_packet = "(CM," + parts[0]+ "," + parts[1] + "," + parts[2] + ")"
    elif len(parts) == 2:
        command_packet = "(CM," + parts[0]+ "," + parts[1] + ")"
    
    elif len(parts) ==1 :
        command_packet = "(CM," + parts[0] + ")"
    


    print("Sending:", command_packet)
    cSocket.send(command_packet.encode("utf-8"))
    
    if parts[0] == "openWrite":
        text = input("Enter text to write to file: ")

        if encryption_type == "AES":
            # Encrypt the text using AES
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

        elif encryption_type == "Caesar":
            encrypted_text = caesar_encrypt(text, caesar_key)  # AI PART
            encrypted_text_b64 = base64.b64encode(encrypted_text.encode("latin-1")).decode("utf-8")  # AI PART
            data_packet = "(DP," + encrypted_text_b64 + ")"  # AI PARTD
            
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

        data_packet = data.decode("utf-8").strip("()").split(",")  # AI PART

        if encryption_type == "AES":
            iv = base64.b64decode(data_packet[1])  # AI PART
            encrypted_text = base64.b64decode(data_packet[2])  # AI PART

            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv))  # AI PART
            decryptor = cipher.decryptor()  # AI PART

            padded_text = decryptor.update(encrypted_text) + decryptor.finalize()  # AI PART

            unpadder = sym_padding.PKCS7(128).unpadder()  # AI PART
            text_bytes = unpadder.update(padded_text) + unpadder.finalize()  # AI PART

            text = text_bytes.decode("utf-8")  # AI PART

        elif encryption_type == "Caesar":
            encrypted_text = base64.b64decode(data_packet[1]).decode("latin-1")  # AI PART
            text = caesar_decrypt(encrypted_text, caesar_key)  # AI PART
        else:
            text = data_packet[1]
        
        print("File contents:", text)


    # Receiving from the server 
    if parts[0] == "pwd":
        current_d = cSocket.recv(2024)
        print("Path: ", current_d.decode("utf-8"))
        
    if parts[0] == "ls":
        lists = cSocket.recv(2024)
        print("Lists: ", lists.decode("utf-8"))
    
    if parts[0] == "size":
        size = cSocket.recv(2024)
        print("size: ", size.decode("utf-8"))
    
    if parts[0] == "exists":
        exits = cSocket.recv(2024)
        print("Exists: ", exits.decode("utf-8"))
   
cSocket.close()