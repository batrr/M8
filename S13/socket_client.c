#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdint.h>

#define MAX 80
#define PORT 8080
#define SA struct sockaddr

const uint64_t SLICE_SIZE = 10000000;
const uint64_t LOWER_BITS_MASK = 0xfffffff;

uint64_t hash(uint64_t x)
{
    x = (x ^ (x >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)) * UINT64_C(0x94d049bb133111eb);
    x = x ^ (x >> 31);
    return x;
}

int get_sockfd()
{
    int sockfd;
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
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    servaddr.sin_port = htons(PORT);

    if (connect(sockfd, (SA *)&servaddr, sizeof(servaddr)) != 0)
    {
        printf("connection with the server failed...\n");
        exit(0);
    }
    else
        printf("connected to the server..\n");
    return sockfd;
}
int main()
{
    for (;;)
    {
        int sockfd = get_sockfd();

        uint64_t x = 0;
        write(sockfd, &x, sizeof(x));

        uint64_t seed, slice_base;
        read(sockfd, &seed, sizeof(seed));
        read(sockfd, &slice_base, sizeof(slice_base));

        // close the socket
        close(sockfd);

        printf("Client got slice %ld\n", slice_base);
        for (uint64_t i = slice_base; i < slice_base + SLICE_SIZE; i++)
        {
            uint64_t hashed = i ^ seed;
            for (int j = 0; j < 10; j++)
            {
                hashed = hash(hashed);
            }
            if ((hashed & LOWER_BITS_MASK) == 0)
            {
                x = i;
                printf("Client found %ld\n", x);
                int sockfd = get_sockfd();
                write(sockfd, &x, sizeof(x));
                printf("Sent result to server\n");
                close(sockfd);
                return;
            }
        }
    }
}
