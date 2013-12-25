#!/usr/bin/python -O
#
# A small program to simulate results from an experiment with an exponential distribution.
#
# - Make sure you understand the code below
# - Complete the evaluation_metric method so that it returns the mean
# - What do you expect the results to be?
# ----- I expect the result to be somewhere between 50% and 100%. Ideally it should be
# ----- around 90%.
# - "Run" the experiment. What's surprising.
# ----- The results fall into the ballpark of 75%-79%, which is kind of surprising. The
# ----- better_dist is 50% higher than individuals after all!
# - Change the metric to something that more often selects the "winning" distribution.
# ----- My new metric removes the top 2 from list to avoid cases where 1024 or 512 gets picked
# ----- and skews the result. Now I win rate is about 93-95%.
#

import math
import random


# Consider this the "true" population distribution of number of ratings
worse_dist = (
    [1024] * 1 +
     [512] * 2 +
     [256] * 4 +
     [128] * 8 +
      [64] * 16 +
      [32] * 32 +
      [16] * 64 +
       [8] * 128 +
       [4] * 256 +
       [2] * 512 +
       [1] * 1024

)

# better dist is 50% bigger than worse
better_dist = [x * 1.5 for x in worse_dist]

# Number of experiments to be simulated
num_experiments = 1000

# Number of subjects per experiment 
num_subjects = 100

def evaluation_metric(contribution_counts):
    """
        Given contributions counts (a list of floats)
        Returns a single float that is an evaluation metric.
        The float should captures the aggregate amount of work.
    """
    contribution_counts.remove(max(contribution_counts))
    contribution_counts.remove(max(contribution_counts))
    return sum(contribution_counts)/len(contribution_counts)

# make sure you understand this code.
num_better_wins = 0
for i in range(num_experiments):
    l = random.sample(worse_dist, num_subjects / 2)
    b = random.sample(better_dist, num_subjects / 2)
    if evaluation_metric(b) > evaluation_metric(l):
        num_better_wins += 1

print('better distribution won %.1f%% of the time' % (100.0 * num_better_wins / num_experiments))
