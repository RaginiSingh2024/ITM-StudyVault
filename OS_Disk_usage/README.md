# C-SCAN Disk Scheduling – OS Disk Usage Project

This project is a simple implementation of the **C-SCAN (Circular SCAN)** disk scheduling algorithm in C.

It calculates the **total head movement** required to serve a given list of disk I/O requests, assuming:

- Disk tracks are numbered from `0` to `199` (total `200` tracks)
- You provide:
  - Number of disk requests
  - The sequence of requested track numbers
  - The initial disk head position

The program then:

- Sorts the requests in ascending order
- Moves the disk head towards higher-numbered tracks first
- Jumps from the last track back to track `0` (circular movement)
- Continues serving the remaining lower-numbered requests
- Prints the **total head movement**.

---

## Files

- `cscan_disk.c`  
  C program implementing the C-SCAN disk scheduling algorithm.

---

## How to Compile

Make sure you are inside the `OS_Disk_usage` folder in your terminal, then run:

```bash
gcc cscan_disk.c -o cscan
```

This will create an executable named `cscan` in the same folder.

---

## How to Run

After compiling, run the program using:

```bash
./cscan
```

The program will ask for:

1. **Number of requests** (e.g. `5`)
2. **Disk requests** (space-separated or newline-separated track numbers, e.g. `98 183 37 122 14`)
3. **Initial head position** (e.g. `53`)

Example terminal session:

```text
Enter number of requests: 5
Enter disk requests:
98 183 37 122 14
Enter initial head position: 53
Total head movement = 236
```

*(The above numbers are just an example; your output will depend on your input.)*

---

## Notes

- Maximum supported requests in the current code: **20** (array size `req[20]`).
- Disk size is currently set to **200 tracks** (`0` to `199`) inside the code.
- You can modify these limits in `cscan_disk.c` if needed.

---

## Requirements

- Any standard C compiler (e.g. `gcc` on Linux/macOS).
- A terminal or command prompt to compile and run the program.

---

## Author / Course

Operating Systems – Disk Scheduling (C-SCAN) implementation.

You can extend this project by:

- Adding other algorithms (FCFS, SSTF, SCAN, LOOK, C-LOOK)
- Comparing total head movement between algorithms
- Adding input validation and better output formatting.
