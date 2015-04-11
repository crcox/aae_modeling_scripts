#!/usr/bin/env python

import pickle
import os
import sys

wfile = os.path.join('pkl','words.pkl')
with open(wfile,'r') as f:
    jdat = pickle.load(f)

devoiced=0
postvocalic_reduction=0
consonant_cluster_reduction=0
wordsWithChanges=0
try:
    for w,info in jdat.items():
        devoiced+=int(info['devoiced'])
        postvocalic_reduction+=int(info['postvocalic_reduction'])
        consonant_cluster_reduction+=int(info['consonant_cluster_reduction'])
        wordsWithChanges+=any([info['devoiced'],info['postvocalic_reduction'],info['consonant_cluster_reduction']])
except KeyError:
    pass

if wordsWithChanges:
    with open('rules_applied.txt','w') as f:
        f.write('devoiced: {x:d}\n'.format(x=devoiced))
        f.write('postvocalic_reduction: {x:d}\n'.format(x=postvocalic_reduction))
        f.write('consonant_cluster_reduction: {x:d}\n'.format(x=consonant_cluster_reduction))
        f.write('wordsWithChanges: {x:d}\n'.format(x=wordsWithChanges))

wtxt = os.path.join('words.txt')
with open(wtxt,'w') as f:
    for w in sorted(jdat.keys()):
        f.write(w+'\n')

hfile = os.path.join('pkl','homo.pkl')
with open(hfile,'r') as f:
    jdat = pickle.load(f)

htxt = os.path.join('homo.txt')
with open(htxt,'w') as f:
    for w in sorted(jdat.keys()):
        f.write(w+'\n')
