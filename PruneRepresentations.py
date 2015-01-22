import os
import json,pickle

STIM = {}
aaestimpath = os.path.join('stimuli','AAE','pkl','words.pkl')
with open(aaestimpath,'rb') as f:
	STIM['AAE'] = pickle.load(f)

saestimpath = os.path.join('stimuli','SAE','pkl','words.pkl')
with open(saestimpath,'rb') as f:
	STIM['SAE']= pickle.load(f)

aaestimpath = os.path.join('stimuli','AAE','dialect','pkl','words.pkl')
try:
    with open(aaestimpath,'rb') as f:
	    STIM['AAEd'] = pickle.load(f)
except IOError:
    pass

saestimpath = os.path.join('stimuli','SAE','dialect','pkl','words.pkl')
try:
    with open(saestimpath,'rb') as f:
        STIM['SAEd'] = pickle.load(f)
except IOError:
    pass

minStart = 10
maxEnd = 0
pUnitUsed = []
SEM = []
N = {}

# Identify which phon units are used
for clab,corpus in STIM.items():
    for wlab,word in corpus.items():
        phon = word['phon']
        for i,p in enumerate(phon):
            try:
                pUnitUsed[i] = [x|y for x,y in zip(p,pUnitUsed[i])]
            except IndexError:
                # Should only happen first time slot is encountered
                pUnitUsed.append(p)

# Prune representations accordingly
for clab,corpus in STIM.items():
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

SEMT = list(zip(*SEM))
SEMUNITUSAGE = [sum(b) for b in SEMT]

# Save new stimuli
path = os.path.join('stimuli','AAE')
ppath = os.path.join(path,'pkl','words_pruned.pkl')
with open(ppath,'wb') as f:
    pickle.dump(STIM['AAE'],f)

jpath = os.path.join(path,'json','words_pruned.json')
with open(jpath,'wb') as f:
    json.dump(STIM['AAE'],f,indent=2, separators=(',', ': '))

path = os.path.join('stimuli','SAE')
ppath = os.path.join(path,'pkl','words_pruned.pkl')
with open(ppath,'wb') as f:
    pickle.dump(STIM['SAE'],f)

jpath = os.path.join(path,'json','words_pruned.json')
with open(jpath,'wb') as f:
    json.dump(STIM['SAE'],f,indent=2, separators=(',', ': '))

try:
    path = os.path.join('stimuli','SAE','dialect')
    ppath = os.path.join(path,'pkl','words_pruned.pkl')
    with open(ppath,'wb') as f:
        pickle.dump(STIM['SAEd'],f)

    jpath = os.path.join(path,'json','words_pruned.json')
    with open(jpath,'wb') as f:
        json.dump(STIM['SAEd'],f,indent=2, separators=(',', ': '))
except KeyError:
    pass

try:
    path = os.path.join('stimuli','AAE','dialect')
    ppath = os.path.join(path,'pkl','words_pruned.pkl')
    with open(ppath,'wb') as f:
        pickle.dump(STIM['AAEd'],f)

    jpath = os.path.join(path,'json','words_pruned.json')
    with open(jpath,'wb') as f:
        json.dump(STIM['AAEd'],f,indent=2, separators=(',', ': '))
except KeyError:
    pass

# Print out some stuff
N['sem'] = len(SEMUNITUSAGE)
N['phon'] = sum([sum(p) for p in pUnitUsed])
#N['homo'] = 2
#N['context'] = 1
print "N semantic units: {n:d}".format(n=N['sem'])
print "N phonological units: {n:d}".format(n=N['phon'])
#print "N homophone units: {n:d}".format(n=N['homo'])
#print "N context units: {n:d}".format(n=N['context'])

