#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>

#define MAX 80
#define PORT 8080
#define SA struct sockaddr

const uint64_t SLICE_SIZE = 10000000;

// Driver function
int main()
{
    int sockfd, connfd, len;
    struct sockaddr_in servaddr, cli;

    // socket create and verification
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1)
    {
        printf("socket creation failed...\n");
        exit(0);
    }
    else
        printf("Socket successfully created..\n");
    bzero(&servaddr, sizeof(servaddr));

    // assign IP, PORT
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    // Binding newly created socket to given IP and verification
    if ((bind(sockfd, (SA *)&servaddr, sizeof(servaddr))) != 0)
    {
        printf("socket bind failed...\n");
        exit(0);
    }
    else
        printf("Socket successfully bound..\n");

    // Now server is ready to listen and verification
    if ((listen(sockfd, 5)) != 0)
    {
        printf("Listen failed...\n");
        exit(0);
    }
    else
        printf("Server listening..\n");
    len = sizeof(cli);

    srandom(time(NULL));
    uint64_t seed = random();
    uint64_t slice_base = SLICE_SIZE; // not starting with 0, our hash function is bad
    for (;;)
    {
        // Accept the data packet from client and verification
        connfd = accept(sockfd, (SA *)&cli, &len);
        if (connfd < 0)
        {
            printf("server accept failed...\n");
            exit(0);
        }
        else
            printf("server accept the client...\n");
        uint64_t x;
        read(connfd, &x, sizeof(x));
        if (x == 0)
        {
            write(connfd, &seed, sizeof(seed));
            write(connfd, &slice_base, sizeof(slice_base));
            printf("Server sent slice %ld\n", slice_base);
        }
        else
        {
            printf("Server found %ld\n", x);
            break;
        }

        slice_base += SLICE_SIZE;
        close(connfd);
    }

    // After chatting close the socket
    close(sockfd);
}