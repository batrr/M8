#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

void *manager();
void *miner();

uint64_t solution = 0;

typedef struct {
   uint64_t items[10];
   size_t length;
   pthread_mutex_t mtx;
   pthread_cond_t cv_can_add;
   pthread_cond_t cv_can_pop;
   bool flag;
} queue_t;

void queue_init(queue_t *this) {
   pthread_mutex_init(&this->mtx, NULL);
   this->length = 0;
   this->flag = false;
}

void queue_stop(queue_t *this) {
   pthread_mutex_lock(&this->mtx);
   this->flag = true;
   pthread_cond_signal(&this->cv_can_add);
   pthread_cond_signal(&this->cv_can_pop);
   pthread_mutex_unlock(&this->mtx);
}

int queue_can_add(queue_t *this) {
   return this->length + 1 < 10 || this->flag;
}

void queue_add(queue_t *this, uint64_t item) {
   pthread_mutex_lock(&this->mtx);
   while (!queue_can_add(this)) 
      pthread_cond_wait(&this->cv_can_add, &this->mtx);
   if(this->flag){
      pthread_cond_signal(&this->cv_can_add);
      pthread_cond_signal(&this->cv_can_pop);
      pthread_mutex_unlock(&this->mtx);
      return;
   }
   this->items[this->length] = item;
   this->length++;
   pthread_cond_signal(&this->cv_can_pop);
   pthread_mutex_unlock(&this->mtx);
}

int queue_can_pop(queue_t *this) {
   return this->length > 0 || this->flag;
}

uint64_t queue_pop(queue_t *this) {
   pthread_mutex_lock(&this->mtx);
   while (!queue_can_pop(this)) 
      pthread_cond_wait(&this->cv_can_pop, &this->mtx);
      pthread_cond_signal(&this->cv_can_pop);
   if(this->flag){
      pthread_cond_signal(&this->cv_can_add);
      pthread_cond_signal(&this->cv_can_pop);
      pthread_mutex_unlock(&this->mtx);
      return -1;
   }
   uint64_t result = this->items[0];
   this->length--;
   for (size_t i = 0; i < this->length; i++) {
      this->items[i] = this->items[i+1];
   }
   pthread_cond_signal(&this->cv_can_add);
   pthread_mutex_unlock(&this->mtx);
   return result;
}

uint64_t hash(uint64_t x) {
    x = (x ^ (x >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)) * UINT64_C(0x94d049bb133111eb);
    x = x ^ (x >> 31);
    return x;
}

const int N_MINERS = 100;

const uint64_t SLICE_SIZE = 10000000;
const uint64_t LOWER_BITS_MASK = 0xffffff;

uint64_t seed;

queue_t queue;

int main() {
   pthread_t thread_manager;
   pthread_t threads_miners[N_MINERS];

   srandom(time(NULL));
   seed = random();

   queue_init(&queue);

   assert(!pthread_create(&thread_manager, NULL, &manager, NULL));
   for (int i = 0; i < N_MINERS; i++) {
      assert(!pthread_create(&threads_miners[i], NULL, &miner, NULL));
   }
   assert(!pthread_join(thread_manager, NULL));
   int sum = 0;
   for (int i = 0; i < N_MINERS; i++) {
      assert(!pthread_join(threads_miners[i], NULL));
   }
   printf("%d\n", sum);

   exit(0);
}

void *manager() {
   uint64_t slice_base = SLICE_SIZE; // not starting with 0, our hash function is bad
   while (true) {
      queue_add(&queue, slice_base);
      if(solution)
         break;
      printf("sent %ld\n", slice_base);
      slice_base += SLICE_SIZE;
   }
   printf("manager sees solution %ld\n", solution);
   return NULL;
}

void *miner() {
   while (true) {
      uint64_t slice_base = queue_pop(&queue);
      if(solution)
         break;
      for (uint64_t i = slice_base; i < slice_base + SLICE_SIZE && solution == 0; i++) {
         uint64_t hashed = i ^ seed;
         for (int j = 0; j < 10; j++) {
            hashed = hash(hashed);
         }
         if ((hashed & LOWER_BITS_MASK) == 0) {
            solution = i;
            printf("miner found solution %ld\n", i);
            queue_stop(&queue);
            return NULL;
         }
      }
   }
   return NULL;
}

