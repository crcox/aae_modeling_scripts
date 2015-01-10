#!/usr/bin/env python

# This script takes the raw data and creates a dictionary in the stimuli
# directory, both as json and pkl.
import os,json,pickle

with open('stimopts.json','r') as f:
    jdat = json.load(f)

# Tab delimited
PHON_MAP = {}
with open(jdat['dialect_phon_map']) as f:
    for line in f:
        tmp = line.strip().split()
        PHON_MAP[tmp[0]] = [int(x) for x in tmp[1:]]

STIM = {}
with open(jdat['stim_master'], 'r') as f:
    with open(jdat['sem_map']) as fsem:
        for line in f:
            linesem = fsem.readline()
            sem = [int(x) for x in linesem.strip().split('\t')]
            data = line.strip().split()

            phon_code = data[2]
            phon = []
            for p in phon_code:
                phon.append(PHON_MAP[p])

            STIM[data[0]] = {
                    'orth_code': data[1],
                    'phon_code': data[2],
                    'freq': int(data[3]),
                    'phon': phon,
                    'sem': sem
                    }

HOMO = {}
for word,d in STIM.items():
    try:
        HOMO[d['phon_code']].append(word)
    except KeyError:
        HOMO[d['phon_code']] = [word]

for word,homo in HOMO.items():
    if len(homo) == 1:
        del HOMO[word]

path = os.path.join('stimuli','SAE','dialect')

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
