#!/usr/bin/env python

from aae import rules
import json,pickle
import os

with open('stimopts.json','r') as f:
    jdat = json.load(f)

# Tab delimited
PHON_MAP = {}
with open(jdat['phon_map']) as f:
    for line in f:
        tmp = line.strip().split()
        PHON_MAP[tmp[0]] = [int(x) for x in tmp[1:]]

path = os.path.join('stimuli','SAE','pkl','words_master.pkl')
with open(path, 'r') as f:
    STIM = pickle.load(f)

AAE = STIM.copy()
for word,d in STIM.items():
    (p,dashes) = rules.stripdash(d['phon_code'])
    (AAE[word]['devoiced'],p) = rules.devoice(p)
    (AAE[word]['consonant_cluster_reduction'],p) = rules.consonant_cluster_reduction(p)
    (AAE[word]['postvocalic_reduction'],p) = rules.postvocalic_reduction(p)
    p_ = rules.applydash(p,dashes)

    phon = []
    for x in p_:
        phon.append(PHON_MAP[x])

    AAE[word]['phon_code'] = p_
    AAE[word]['phon'] = phon

HOMO = {}
for word,d in AAE.items():
    try:
        HOMO[d['phon_code']].append(word)
    except KeyError:
        HOMO[d['phon_code']] = [word]

for word,homo in HOMO.items():
    if len(homo) == 1:
        del HOMO[word]

path = os.path.join('stimuli','AAE')

ppath = os.path.join(path,'pkl','words_master.pkl')
with open(ppath,'wb') as f:
    pickle.dump(STIM,f)

jpath = os.path.join(path,'json','words_master.json')
with open(jpath,'wb') as f:
    json.dump(STIM,f,indent=2, separators=(',', ': '))

ppath = os.path.join(path,'pkl','homo_master.pkl')
with open(ppath,'wb') as f:
    pickle.dump(HOMO,f)

jpath = os.path.join(path,'json','homo_master.json')
with open(jpath,'wb') as f:
    json.dump(HOMO,f,indent=2, separators=(',', ': '))
