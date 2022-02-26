# Memberlist Benchmark

This repository contains a script to benchmark the processing of our proposed membership list for Signal.

## Execution

The benchmark is intended to be run in a docker container:

1. Set the desired parameters as described above
2. `docker build -t mlb .`
3. `docker run -v /path/to/repo/data:/data mlb python /code/main.py NUMREP NUMENTRIES`

## Configuration

As described above, the benchmark is configurated via commandline arguments:

- `NUMREP`: Number of repetitions for processing the membership list
- `NUMENTRIES`: Number of entries in the membership list

## Output

A log containing statistics of the benchmark run is created in the repositories `data/` folder (which might need to be created).

