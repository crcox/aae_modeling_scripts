#!/usr/bin/env python

import os,json,pickle,sys
from aae import parse,rules

stimoptspath = sys.argv[1]
with open(stimoptspath,'r') as f:
    jdat = json.load(f)

AAE_RULES = ['consonant_cluster_reduction', 'postvocalic_reduction']

PHON_MAP = parse.phonology(jdat['phon_map'])
SEM_MAP  = parse.semantics(jdat['sem_map'])

CORPUS = parse.corpus(jdat['stim_master'], SEM_MAP, PHON_MAP, jdat['phon_map'], 'SAE')
CORPUS,changelog = parse.altpronunciation(CORPUS, 'AAE', AAE_RULES, PHON_MAP)

HOMO = parse.homophones(CORPUS)

for k,v in changelog.items():
    print "{k:s}: {n:d}".format(k=k, n=len(v))


#root = os.path.join('stimuli','SAE')
#ppath = os.path.join(root,'pkl','words_master.pkl')
#with open(ppath,'wb') as f:
#    pickle.dump(STIM,f)
#
#jpath = os.path.join(root,'json','words_master.json')
#with open(jpath,'wb') as f:
#    json.dump(STIM,f,indent=2, separators=(',', ': '))
#
#ppath = os.path.join(root,'pkl','homo_master.pkl')
#with open(ppath,'wb') as f:
#    pickle.dump(HOMO,f)
#
#jpath = os.path.join(root,'json','homo_master.json')
#with open(jpath,'wb') as f:
#    json.dump(HOMO,f,indent=2, separators=(',', ': '))
