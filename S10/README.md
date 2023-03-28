Managers and miners can access the queue at the same time, causing problems like multiple miners accessing the same value, the queue shifting and so on. To fix this, I used mutex so that only one thread can access the queue at a time.

However, there was a new problem where the queue was empty and the miner was waiting for data while the manager was waiting for the queue to be unlocked. To solve this, I added a condition variable called "can_pop" that is signaled at the end of a push operation.

Similarly, if the manager attempts to push to a full queue and the miner is waiting, I added a "can_add" condition variable to signal when a slot is available

Now, each slice of data is only received by one miner before finding solution.

Another problem occurred where the miners were waiting for data from an empty queue because the manager had already found a solution and left. To solve this, I added a flag that is turned on after a solution is found. If the flag is on, the push and pop operations send signals again so that nobody gets stuck.

And last problem is another miner could find a solution while our miner was iterating over the slice. I added a check in the for loop to make sure that we don't have a solution yet.
