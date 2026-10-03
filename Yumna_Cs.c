#include <stdio.h>
#include <winsock2.h>
#include <string.h>

#pragma comment(lib, "Ws2_32.lib")

int main(void) {
    WSADATA wsa;
    SOCKET clientSocket;
    struct sockaddr_in server;
    
    if (WSAStartup(MAKEWORD(2,2), &wsa) !=0){
        printf("Winsock initialzation failed.\n");
        return 1;
    }

    clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(clientSocket == INVALID_SOCKET){
        printf("socket creation failed.. \n");
        WSACleanup();
        return 1;
    }

    server.sin_family = AF_INET;
    server.sin_port = htons(43214);
    server.sin_addr.s_addr = inet_addr("127.0.0.1");

    if(connect(clientSocket, (struct sockaddr *)&server,
        sizeof(server)) == SOCKET_ERROR){
            printf("Connection failed. Is the python server running? \n");
            closesocket(clientSocket);
            WSACleanup();
            return 1;
        }

    printf("conneted to the python server! \n");
    char startPacket[] = "(SS,RFMP,v1.0,0)"; //the 0 means 'non-secure mode'
    send(clientSocket, startPacket, strlen(startPacket), 0);

    printf("Start packet sent \n");

    char buffer[2024];
    int bytesReceieved;

    bytesReceieved = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
    if(bytesReceieved>0){
        buffer[bytesReceieved] = '\0';
        printf("Server response %s\n", buffer);
    }

    char commandPacket[] = "(CM,openRead,yayy.txt)";
    send(clientSocket, commandPacket, strlen(commandPacket), 0);
    printf("openRead command sent \n");

    bytesReceieved = recv(clientSocket, buffer, sizeof(buffer)-1, 0);
    if(bytesReceieved > 0){
        buffer[bytesReceieved] = '\0';
        printf("Command response: %s\n", buffer);
    }

    bytesReceieved = recv(clientSocket, buffer, sizeof(buffer)-1,0);
    if(bytesReceieved>0){
        buffer[bytesReceieved] = '\0';
        printf("Data recieved: %s\n", buffer);
    
        if(strncmp(buffer, "(DP,",4) == 0){
            char *fileContents = buffer +4;
            char *end = strrchr(fileContents, ')');
            if(end != NULL){
                *end = '\0';
            }

            printf("File contents: %s\n", fileContents);
        }
    }

    closesocket(clientSocket);
    WSACleanup();
    return 0;
}