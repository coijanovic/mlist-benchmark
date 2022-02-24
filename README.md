# Memberlist Benchmark

This repository contains a script to benchmark the processing of our proposed membership list for Signal.

## Configuration

The benchmark is configured via variables in `main.py`

- `NUMPROC`: Number of processes to process the membership list in parallel
- `NUMREP`: Number of repetitions of the processing
- `NUMENTRIES`: Number of entries in the membership list.
	Should be evenly divisible by `NUMPROC`

## Execution

The benchmark is intended to be run in a docker container:

1. Set the desired parameters as described above
2. `docker build -t mlb .`
3. `docker run mlb`
