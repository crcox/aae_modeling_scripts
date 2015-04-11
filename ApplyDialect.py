#!/usr/bin/env python

# This script takes the raw data and creates a dictionary in the stimuli
# directory, both as json and pkl.
import os,json,pickle
import copy
import sys

dialect_map = sys.argv[1]
dialect_label = os.path.basename(dialect_map)
dialect_label = dialect_label.replace('mapping_','')


# Tab delimited
PHON_MAP = {}
with open(dialect_map) as f:
    for line in f:
        tmp = line.strip().split()
        PHON_MAP[tmp[0]] = [int(x) for x in tmp[1:]]

for stimpath in sys.argv[2:]:
    path,fext = os.path.split(stimpath)
    f,ext = os.path.splitext(fext)
    with open(stimpath,'rb') as pkl:
        STIM = pickle.load(pkl)
    for word in STIM.keys():
        phon = []
        for p in STIM[word]['phon_code']:
            phon.append(PHON_MAP[p])
        STIM[word]['phon'] = copy.copy(phon)

    ppath = os.path.join(path,'{w}_{lab}.pkl'.format(w=f,lab=dialect_label))
    with open(ppath,'wb') as pkl:
        pickle.dump(STIM,pkl)
