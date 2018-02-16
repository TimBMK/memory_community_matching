#!/usr/bin/env python3




def match(timeseries, memory=2, *,
                      memory_weights=None, score_threshold=.1):
    """
    Matches community detections from single snapshots in a timeseries
    to get temporal communities that stretch over multiple timesteps.

    The jaccard index of the communities is taken as the matching
    strength. The Hungarian algorithm is used for the underlying matching
    (scipy implementation). 

    When matching the current timestep, all communities up to (memory)
    timesteps in the past are taken into account. The current communities
    are scored against the past communities within the memory distance
    as well as against temporal communities that were already detected
    in the previous steps (also within the memory distance). In the later
    case, the sum of weighted jaccard indices is used as matching score.

    arguments:

    timeseries -- a list of dicts. each list item is a timestep and
    contains a dict. the keys are identifiers for the communities and the
    values are sets of identifiers for the community members. see example

    memory -- the number of timesteps to look back in the timeseries
    for matching.

    memory_weights -- a list of length (memory) with weights. if None is
    given, 1/i weighting is used so older communities have less influence
    on the matching score.

    score_threshold -- memory weighted jaccard indices under the
    threshold will not be included in the matching
    """


    temporal_communities_dict = {}
    # stores community membership as automorphism on the communities
    # for a (t, i) tuple of timestep t and community number i, it stores
    # the next (t, i) tuple in a chain backward in time, that this
    # community is attached to. following these chains gives the temporal
    # communities.

    if not memory_weights:
        memory_weights = [ 1/i for i in range(1, memory+1) ]


    for i in range(1, len(timeseries)):
        
        # timestep i
        print('step', i)
        
        base_communities = timeseries[i]     # the communities to match
        
        # helper variables
        all_match_costs = []
        seen = set()    # remember that these comm. were already checked
        timesteps = []  # which timestamps are used for this iteration


        for j in range(1, memory+1):

            # compare with timestep i-j
            #print('memory', j, i-j)
            
            if i-j < 0:
                break         # beginning of timeseries reached

            communities = timeseries[i-j]

            # the negative weighted jaccard indices to use for matching
            match_costs = np.zeros((len(base_communities), 
                                    len(communities)), dtype=np.float)
        

            for k, A in base_communities.items():
        
            
                for l, B in communities.items():
                    
                    if (i-j,l) in seen:
                        # this community is part of an already detected
                        # temporal community. its jaccard index (* memory
                        # weight) was already added to the score of the 
                        # latest community in this temporal community.
                        continue

                    intersection = len(A & B)

                    if intersection:    # at least one member overlaps

                        jaccard_index = intersection / len(A | B)
                        score = jaccard_index * memory_weights[j-1]

                        """
                        check if this community is part of an already
                        detected temporal community. if so, add the
                        scores for past members of the temp. comm. to
                        this communities' score (within memory range)
                        """
                        timestep, group = i-j, l
                        
                        while True:
                            try:
                                # look up previous member in temp. comm.
                                # chain. if none found, this comm. is not
                                # member of a detected temp. comm.
                                timestep, group = temporal_communities_dict[(timestep,group)]
                            except KeyError:
                                break
                                
                            if timestep < i-memory:
                                # stay within memory range
                                break
                                
                            
                            C = timeseries[timestep][group]
                            intersection = len(A & C)
                            
                            if intersection:
                                
                                jaccard_index = intersection / len(A | C)
                                score += jaccard_index * memory_weights[i-timestep-1]
                                
                            seen.add((timestep,group))
                            # previously matched comm. don't count
                            # separately, because they are added to the
                            # latest temp. comm. member's score.
                            # don't visit this comm. again
                            

                        match_costs[k][l] = -1 * score
                        # scipy implementation uses costs (neg. strength) 
                        
            #print(match_costs)
            
            all_match_costs.append(match_costs)
            timesteps.append(i-j)
            
        # aggregate results from memory steps
        #print(all_match_costs)
        match_costs_array = np.hstack(all_match_costs)
        sizes = [_[1] for _ in map(np.shape, all_match_costs)]
        group_names_dict = { }  # keeps track of indices in stacked array
        counter = 0
        for e, s in enumerate(sizes):
            group_names_dict.update({_+counter:(timesteps[e],_) for _ in range(s)})
            counter += s
            

        # match
        matches = np.dstack(linear_sum_assignment(match_costs_array))[0]


        # filter (only matches above threshold
        for k, l in matches:

            #print(j, k)
        
            if match_costs_array[k][l] > - score_threshold:
                continue
            
            #print('match')
            #print(match_costs[j][k])
        
            temporal_communities_dict[(i,k)] = group_names_dict[l]
        

    return temporal_communities_dict



