#!/usr/bin/env python

import os
import pickle
import sys

STIM = []
for filepath in sys.argv[1:]:
    with open(filepath,'rb') as pkl:
        STIM.append(pickle.load(pkl))

minStart = 10
maxEnd = 0
pUnitUsed = []
N = {}

# Identify which phon units are used
for corpus in STIM:
    for wlab,word in corpus.items():
        phon = word['phon']
        for i,p in enumerate(phon):
            try:
                pUnitUsed[i] = [x|y for x,y in zip(p,pUnitUsed[i])]
            except IndexError:
                # Should only happen first time slot is encountered
                pUnitUsed.append(p)

# Prune representations accordingly
for clab,corpus in enumerate(STIM):
    for wlab,word in corpus.items():
        phon = word['phon']
        code = word['phon_code']
        codep = []
        for i,p in enumerate(phon):
            pp = [x for x,y in zip(p,pUnitUsed[i]) if y]
            STIM[clab][wlab]['phon'][i] = pp
            if pp:
                codep.append(code[i])
        STIM[clab][wlab]['phon_code'] = codep

# Save new stimuli
for i,filepath in enumerate(sys.argv[1:]):
    p,fext = os.path.split(filepath)
    f,ext = os.path.splitext(fext)
    ppath = os.path.join(p,'{w}_pruned.pkl'.format(w=f))
    with open(ppath,'wb') as pkl:
        pickle.dump(STIM[i],pkl)

# Print out some stuff
N['phon'] = sum([sum(p) for p in pUnitUsed])
print "N phonological units: {n:d}".format(n=N['phon'])
