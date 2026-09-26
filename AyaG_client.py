import socket
from cryptography.hazmat.primitives import serialization  # AI PART
from cryptography.hazmat.primitives.asymmetric import rsa  # AI PART
import os  # AI PART
from cryptography.hazmat.primitives.asymmetric import padding  # AI PART
from cryptography.hazmat.primitives import hashes  # AI PART
import base64  # AI PART

cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 43214

# s.connect((host, port))
cSocket.connect((host, port))

startpacket = "(SS,RFMP,v1.0,1)"
 
cSocket.send(startpacket.encode('utf-8'))


msg = cSocket.recv(2024)


print("The server has responded:")
print(msg.decode("utf-8"))

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
    client_public_key_bytes
).decode("utf-8")

print("Client public key converted to Base64")

encryption_packet = (
    "(EC,AES,"
    + encrypted_session_key_b64
    + ","
    + client_public_key_b64
    + ")"
)

cSocket.send(encryption_packet.encode("utf-8"))

print("Encryption packet sent to server")
cSocket.close()