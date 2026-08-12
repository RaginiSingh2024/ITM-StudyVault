#include <stdio.h>   // printf(), scanf() ke liye
#include <stdlib.h>  // abs() function ke liye

int main() {

    // n = number of disk requests
    // head = initial position of disk head
    // disk_size = total number of disk tracks (0 to 199)
    int n, head, disk_size = 200;

    // req[] = disk requests array
    // temp = swapping ke liye (sorting)
    int req[20], temp;

    // User se number of requests lena
    printf("Enter number of requests: ");
    scanf("%d", &n);

    // Disk requests input lena
    printf("Enter disk requests:\n");
    for(int i = 0; i < n; i++) {
        scanf("%d", &req[i]);
    }

    // Initial head position input lena
    printf("Enter initial head position: ");
    scanf("%d", &head);

    // -------------------------------
    // STEP 1: Disk requests ko sort karna (ascending order)
    // C-SCAN algorithm me sorting zaroori hoti hai
    // -------------------------------
    for(int i = 0; i < n; i++) {
        for(int j = i + 1; j < n; j++) {
            if(req[i] > req[j]) {
                temp = req[i];
                req[i] = req[j];
                req[j] = temp;
            }
        }
    }

    // total = total disk head movement
    int total = 0;

    // -------------------------------
    // STEP 2: Disk head ko higher direction me move karna
    // (initial head position se end tak)
    // -------------------------------
    for(int i = 0; i < n; i++) {
        if(req[i] >= head) {
            total += abs(req[i] - head);  // distance calculate
            head = req[i];               // head ko update karna
        }
    }

    // -------------------------------
    // STEP 3: End of disk se start (0) par jump
    // Ye C-SCAN ka main feature hai
    // -------------------------------
    total += abs((disk_size - 1) - head); // last track tak jaana
    head = 0;                             // head ko start par laana
    total += disk_size - 1;               // circular jump cost

    // -------------------------------
    // STEP 4: Bachi hui requests serve karna
    // (jo initial head se chhoti thi)
    // -------------------------------
    for(int i = 0; i < n; i++) {
        if(req[i] < head) {
            total += abs(req[i] - head);
            head = req[i];
        }
    }

    // Final output: total disk head movement
    printf("Total head movement = %d\n", total);

    return 0;  // Program successful termination
}



//gcc cscan_disk.c -o cscan// how run this project in my terminal 
//./cscan //