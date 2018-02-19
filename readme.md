# Matching for Temporal Community Detection with Memory


This package implements a matching procedure for temporal community detection on networks. The details are in our paper: This is part of a modular approach to temporal community detection: for a complete analysis pipeline, other tools are needed.


## Dependencies
* python3
* numpy
* scipy.optimize


## Input

We want to find temporal communities in a network. The first part is to use community detection on the timeseries of static snapshots of the temporal network. The static community detection is not implemented in this package.

The input data for this package is a list of items (network nodes) and their membership in static communities for each timestep of the timeseries. We use a dict of python sets for each timestep (see test.py).

## Output

The output is a list, containing for each detected temporal community a set of its members as a tuple of (timestep, community name).

## Memory

The results of the static communtity detection are matched with the results from adjacent timesteps to get a temporal community detection. Memory is used to match communities against other communities from past timestepts. The length of memory and the memory kernel with weights for each memory length can be adjusted using the `memory` and `memory_weights` parameters.

Our method goes through the data chronologically and matches communites backwards to all previous timesteps within the memory length. The Hungarian algorithm is used for matching. It maximizes the sum of all memory weighted jaccard indices between all communities within the memory length.


## Example

```python
import memory_community_matching

timeseries = [

        { 'orange': { 1, 2, 3 },
          'violet': { 4, 5, 6 },
          'green':  { 7, 8, 9 } },

        { 'violet': { 2, 3, 4, 5, 6 },
          'green':  { 7, 8 },
          'yellow': { 9 } },

        { 'orange': { 1, 2, 3 },
          'violet': { 4, 5, 6, 7 },
          'green':  { 8, 9 } }
    ]

temporal_communities = memory_community_matching.matching(timeseries, 2)
print(temporal_communties)
# [{(0, 'violet'), (1, 'violet'), (2, 'violet')}, {(0, 'orange'), (2, 'orange')}, {(2, 'green'), (1, 'green'), (0, 'green')}]

## Authors

This method was developed and implemented by Philipp Lorenz-Spreen, Frederik Wolf, Jonas Braun and Philipp Hövel at TU Berlin.

If you reference this method, please cite 
