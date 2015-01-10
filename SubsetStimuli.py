#!/usr/bin/env python

import json,pickle
import os
import random

with open('subsetopts.json','r') as f:
    opts = json.load(f)

path = os.path.join('stimuli','SAE','pkl','words_master.pkl')
with open(path,'r') as f:
    SAE = pickle.load(f)

path = os.path.join('stimuli','AAE','pkl','words_master.pkl')
with open(path,'r') as f:
    AAE = pickle.load(f)

path = os.path.join('stimuli','SAE','pkl','homo_master.pkl')
with open(path,'r') as f:
    HOMO = pickle.load(f)

words = SAE.keys()
words_diff = [ w for w in AAE.keys() if any([
        AAE[w]['devoiced'],
        AAE[w]['consonant_cluster_reduction'],
        AAE[w]['postvocalic_reduction']])
    ]

words_same = [w for w in words if not w in words_diff]
words_homo = []
for ph, wrds in HOMO.items():
    words_homo.extend(wrds)

#words_homo = [w for w in words if D[w]['SAE_homo']]

while True:
    samp = random.sample(words_homo,opts['n_homo_sae'])
    skip_list = []
    for w in samp:
        if w in skip_list:
            continue
        skip_list.append(w)
        samp.extend(HOMO[SAE[w]['phon_code']])
    samp = list(set(samp))
    n_same = sum([1 for w in samp if w in words_same])
    n_diff = sum([1 for w in samp if w in words_diff])

    random.shuffle(words_diff)
    for w in words_diff:
        if not w in samp:
            samp.append(w)
            n_diff+=1

        if len(list(set(samp) & set(words_diff))) == opts['n_diff_aae']:
            print "n_diff:",n_diff
            break

    random.shuffle(words_same)
    for w in words_same:
        if not w in samp:
            samp.append(w)
            n_same+=1

        if n_same == opts['n'] - opts['n_diff_aae']:
            print "n_same:",n_same
            break

    sae_samp = [SAE[w]['phon_code'] for w in samp]
    aae_samp = [AAE[w]['phon_code'] for w in samp]
    aae_u = len(set(aae_samp))
    sae_u = len(set(sae_samp))
    if (opts['n']-sae_u) > opts['n_homo_sae']:
        break

samp.sort()

## Subset the full datasets
AAE = {word: AAE[word] for word in samp}
SAE = {word: SAE[word] for word in samp}

## Document Homophones
# AAE
HOMO_AAE = {}
for word,d in AAE.items():
    try:
        HOMO_AAE[d['phon_code']].append(word)
    except KeyError:
        HOMO_AAE[d['phon_code']] = [word]

for word,homo in HOMO_AAE.items():
    if len(homo) == 1:
        del HOMO_AAE[word]

# SAE
HOMO_SAE = {}
for word,d in SAE.items():
    try:
        HOMO_SAE[d['phon_code']].append(word)
    except KeyError:
        HOMO_SAE[d['phon_code']] = [word]

for word,homo in HOMO_SAE.items():
    if len(homo) == 1:
        del HOMO_SAE[word]

## Write AAE sample data
path = os.path.join('stimuli','AAE')
ppath = os.path.join(path,'pkl','words.pkl')
jpath = os.path.join(path,'json','words.json')
with open(ppath,'wb') as f:
    pickle.dump(AAE,f)

with open(jpath,'wb') as f:
    json.dump(AAE,f,indent=2, separators=(',', ': '))

ppath = os.path.join(path,'pkl','homo.pkl')
jpath = os.path.join(path,'json','homo.json')
with open(ppath,'wb') as f:
    pickle.dump(HOMO_AAE,f)

with open(jpath,'wb') as f:
    json.dump(HOMO_AAE,f,indent=2, separators=(',', ': '))

## Write SAE sample data
path = os.path.join('stimuli','SAE')
ppath = os.path.join(path,'pkl','words.pkl')
jpath = os.path.join(path,'json','words.json')
with open(ppath,'wb') as f:
    pickle.dump(SAE,f)

with open(jpath,'wb') as f:
    json.dump(SAE,f,indent=2, separators=(',', ': '))

ppath = os.path.join(path,'pkl','homo.pkl')
jpath = os.path.join(path,'json','homo.json')
with open(ppath,'wb') as f:
    pickle.dump(HOMO_SAE,f)

with open(jpath,'wb') as f:
    json.dump(HOMO_SAE,f,indent=2, separators=(',', ': '))

for lang in ['AAE','SAE']:
    dpath = os.path.join('stimuli',lang,'dialect','pkl','words_master.pkl')
    if os.path.isfile(dpath):
        with open(dpath,'rb') as f:
            DW = pickle.load(f)
        DW = {w: DW[w] for w in samp}

        ## Document Homophones
        DH = {}
        for word,d in DW.items():
            try:
                DH[d['phon_code']].append(word)
            except KeyError:
                DH[d['phon_code']] = [word]

        for word,homo in DH.items():
            if len(homo) < 2:
                del DH[word]

        path = os.path.join('stimuli',lang,'dialect')
        ppath = os.path.join(path,'pkl','words.pkl')
        jpath = os.path.join(path,'json','words.json')
        with open(ppath,'wb') as f:
            pickle.dump(SAE,f)

        with open(jpath,'wb') as f:
            json.dump(SAE,f,indent=2, separators=(',', ': '))

        ppath = os.path.join(path,'pkl','homo.pkl')
        jpath = os.path.join(path,'json','homo.json')
        with open(ppath,'wb') as f:
            pickle.dump(HOMO_SAE,f)

        with open(jpath,'wb') as f:
            json.dump(HOMO_SAE,f,indent=2, separators=(',', ': '))
