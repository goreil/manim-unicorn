#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Function to initialize the random number generator
void init_random() {
    srand(time(NULL));
}

// Function to get a random number in the range [0, RAND_MAX]
int foo() {
    // Initialize the random number generator
    init_random();
    return rand();
}

// Function to get a random number in a specific range [min, max]
int bar() {
    int min = 10;
    int max = 40;
    return min + rand() % (max - min + 1);
}

int main() {

    // Get a random number
    int a = foo();
    int b = bar();

    return a == b;
}

