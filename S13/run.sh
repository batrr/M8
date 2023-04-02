#!/bin/sh
gcc socket_server.c -o server
gcc socket_client.c -o client

./server > server.out &
server_pid=$!

./client > clientA.out &
clientA_pid=$!

./client > clientB.out &
clientB_pid=$!

wait $server_pid
wait $client_pidA
wait $client_pidB

echo "****************SERVER****************"
cat server.out 
echo "****************CLIENTA****************"
cat clientA.out 
echo "****************CLIENTB****************"
cat clientB.out 