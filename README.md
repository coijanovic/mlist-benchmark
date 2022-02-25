# Memberlist Benchmark

This repository contains a script to benchmark the processing of our proposed membership list for Signal.

## Execution

The benchmark is intended to be run in a docker container:

1. Set the desired parameters as described above
2. `docker build -t mlb .`
3. `docker run mlb python /code/main.py NUMPROC NUMREP NUMENTRIES`

## Configuration

As described above, the benchmark is configurated via commandline arguments:

- NUMPROC: The number of processes running in parallel
- NUMREP: Number of repetitions for processing the membership list
- NUMENTRIES: Number of entries in the membership list

