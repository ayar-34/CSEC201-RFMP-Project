import socket
import threading
from cryptography.hazmat.primitives.asymmetric import rsa  # AI PART
from cryptography.hazmat.primitives import serialization  # AI PART
import base64  # AI PART
from cryptography.hazmat.primitives.asymmetric import padding  # AI PART
from cryptography.hazmat.primitives import hashes  # AI PART


# Python Thread creation using class
class mythread(threading.Thread):

    def __init__(self, clientsocket, addr):
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket
        self.addr = addr

    def run(self):

        while True:
            req = self.clientsocket.recv(2024)

            if not req:
                break

            msg = req.decode("utf-8")
            packet = msg.strip("()").split(",")

            if packet[0] == "SS" and packet[1] == "RFMP" and packet[2] == "v1.0":
                print("Valid packets received")

                if packet[3] == "0":
                    print("test this is not secure")

                    confirm_packet = "(CC)"
                    self.clientsocket.send(
                        confirm_packet.encode("utf-8")
                    )

                elif packet[3] == "1":
                    print("test this is secure")

                    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)

                    public_key = private_key.public_key()

                    public_key_bytes = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

                    print("RSA keys generated")

                    confirm_packet = (b"(CC," + public_key_bytes + b")")

                    self.clientsocket.send(confirm_packet)

            elif packet[0] == "EC":
                print("Encryption packet received")

                algorithm = packet[1]
                encrypted_session_key_b64 = packet[2]

                encrypted_session_key = base64.b64decode(encrypted_session_key_b64)

                print("Algorithm:", algorithm)
                print("Encrypted session key decoded from Base64")

                session_key = private_key.decrypt(encrypted_session_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))

                print("Session key decrypted successfully")

                client_public_key_b64 = packet[3]

                client_public_key_bytes = base64.b64decode(client_public_key_b64)

                print("Client public key decoded from Base64")

                client_public_key = serialization.load_pem_public_key(client_public_key_bytes)

                print("Client public key loaded successfully")

                success_packet = "(SC)"

                self.clientsocket.send(success_packet.encode("utf-8"))

                print("Secure connection established successfully")

        self.clientsocket.close()


def main():

    start_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    host = socket.gethostname()
    port = 43214

    start_socket.bind((host, port))
    start_socket.listen(10)

    print("Server is running")

    while True:

        clientsocket, addr = start_socket.accept()

        client_thread = mythread(clientsocket,addr)

        client_thread.start()


if __name__ == '__main__':
    main()