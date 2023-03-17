#include <stdio.h>
#include <stdlib.h>
#include <spawn.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

int main() {

    const int NUM_CATS = 100;
    pid_t child_pids[100];

    for (int i = 0; i < NUM_CATS; i++) {
        // Argv are command line arguments.
        // By convention, the first arguments needs to be the command name.
        char* argv[] = {"cat", NULL};
        pid_t last_child_pid;
        // The first argument to posix_spawn is a pointer - figure out why.
        int status = posix_spawn(&last_child_pid, "./cat", NULL, NULL, argv, NULL);
        if (status < 0) {
            printf("failed to spawn a cat, terminating the experiment\n");
            return 1;
        }
        child_pids[i] = last_child_pid;
    }
    sleep(1);

    // Now, measure the number of cats still alive!
    int cats_alive = 0; // = ???


    for (int i = 0; i < NUM_CATS; i++) {
        pid_t child_pid = child_pids[i];
        int status;
        pid_t return_pid = waitpid(child_pid, &status, WNOHANG);
        
        if (return_pid == 0) {
            printf("cat %d is alive\n", i);
            cats_alive++;
        } else if (return_pid == child_pid) {
            printf("cat %d is dead(%d)\n", i, WEXITSTATUS(status));
        } else{
            printf("smth wrong");    
        }
    }

    printf("%d cats are ok\n", cats_alive);

    // say no to orphans
    for (int i = 0; i < NUM_CATS; i++) {
        pid_t child_pid = child_pids[i];
        int status;
        pid_t return_pid = waitpid(child_pid, &status, WNOHANG); 
        
        if (return_pid == 0) {
            kill(child_pid, SIGKILL);
        }
    }

}