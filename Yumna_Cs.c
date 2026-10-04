/*
This is a simpler version of the python client, which talks to the python 
server over a TCP socket (which is windows winsock) on the localhost and 
port 43214.
*/


#include <stdio.h>
#include <winsock2.h>
#include <string.h>
#pragma comment(lib, "Ws2_32.lib")

/*
stdio.h : is used for printing and for input (like printf, and scanf)
winsock2.h: is the windows socket function such as socket, connect, send a recv
string.h: it gets string helpers like strlen, strncmp, and strrchr
The pragma: it tells the linker to include the winsock library
*/

int main(void) {
    WSADATA wsa; //this stores winsock startup info
    SOCKET clientSocket; //the socket handle that we use to talk/connect to the server
    struct sockaddr_in server; //server holds the server's address (such as family/ip/port)

    /*
    Windows requires winsock to be initialized before using sockets. 
    so we request for version 2.2 and if it fails then we exit. 
    */
    if (WSAStartup(MAKEWORD(2,2), &wsa) !=0){
        printf("Winsock initialzation failed.\n");
        return 1;
    }

    //we create a TCP socket
    clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(clientSocket == INVALID_SOCKET){
        printf("socket creation failed.. \n");
        WSACleanup();
        return 1;
    }

    //we fill in the server address
    server.sin_family = AF_INET;
    server.sin_port = htons(43214); //htons is used to convert the port to network byte order so the server can read the right port
    server.sin_addr.s_addr = inet_addr("127.0.0.1");

    //We connect to the python server. If it fails to connect then the server is probably not running
    if(connect(clientSocket, (struct sockaddr *)&server,
        sizeof(server)) == SOCKET_ERROR){
            printf("Connection failed. Is the python server running? \n");
            closesocket(clientSocket);
            WSACleanup();
            return 1;
        }

    printf("conneted to the python server! \n");
    char startPacket[] = "(SS,RFMP,v1.0,0)"; //the 0 means 'non-secure mode' which means that no encryption packet is required
    send(clientSocket, startPacket, strlen(startPacket), 0);

    printf("Start packet sent \n");

    char buffer[2024];
    int bytesReceieved;

    //We wait for the server to confirm the connection (CC) 
    bytesReceieved = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
    //we leave 1 byte free so we can add '\0' so that printf would know where the string ends
    if(bytesReceieved>0){
        buffer[bytesReceieved] = '\0';
        printf("Server response %s\n", buffer);
    }

    char filename[256];
    char commandPacket[300];

    printf("Enter file name to read: "); //we ask the user to input the file name to read
    scanf("%255s", filename); //%255s limits input so it wont overflow the 256 byte buffer

    sprintf(commandPacket, "(CM,openRead,%s)", filename); //we build the command packet in the protocol format

    //The operation phase where we ask the server to open the file and read it
    send(clientSocket, commandPacket, strlen(commandPacket), 0);
    printf("openRead command sent\n");

    //Receive the server's response if its a success (SC) or an error (EE)
    bytesReceieved = recv(clientSocket, buffer, sizeof(buffer)-1, 0);
    if(bytesReceieved > 0){
        buffer[bytesReceieved] = '\0';
        printf("Command response: %s\n", buffer);
    }

    //Receive the data packet containing the file contents
    bytesReceieved = recv(clientSocket, buffer, sizeof(buffer)-1,0);
    if(bytesReceieved>0){
        buffer[bytesReceieved] = '\0';
        printf("Data recieved: %s\n", buffer);
    
        /*
        Check the packet that start with "(DP," then skip the 4 characters
        then find the last ')' and replace it with '\0' so it can be removed
        which would only leave the file contents. 
        */
        if(strncmp(buffer, "(DP,",4) == 0){
            char *fileContents = buffer +4;
            char *end = strrchr(fileContents, ')'); /*strrchr searches from the end so that any ')'
                                                      inside the file will be kept and wont be removed
                                                      the only one removed will be the packets closing bracket.*/
            if(end != NULL){
                *end = '\0';
            }

            printf("File contents: %s\n", fileContents);
        }
    }

    //closing phase
    char endPacket[] = "(End)";
    send(clientSocket, endPacket, strlen(endPacket), 0);
    printf("End packet sent \n");

    //close the socket and release winsock resources
    closesocket(clientSocket);
    WSACleanup();
    return 0;
}