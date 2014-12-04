#!/usr/bin/env python

import pickle, json, sys
# Reminders about Lens example files:
# - Files begin with a header that set defaults.
# - The header is terminated with a semi-colon.
# - Each ``trial'' can be composed of many events.
# - In this model, there are three events:
#   1. Presentation
#   2. Settling---letting the recurrent dynamics happen
#   3. Evaluation---the targets are presented, and error assessed.
# - Each event lasts two ticks, so a full trial is 6 ticks.

class RangeGenerator:
    def __init__(self):
        self.i = 0
    def next(self,n):
        a = self.i
        b = a + n - 1
        self.i += n
        if a == b:
            rng = '{a}'.format(a=a)
        else:
            rng = '{a}-{b}'.format(a=a,b=b)
        return rng

def rep2str(x,N,OFFSET):
    if len(x) > 0:
        r = '{{{v}}} {x}'.format(v=1,x=' '.join([str(i) for i in x]))
    else:
        if N == 1:
            r = '{{{v}}} {x}'.format(v=0,x=OFFSET)
        else:
            x = [OFFSET,OFFSET+N-1]
            r = '{{{v}}} {x}'.format(v=0,x='-'.join([str(i) for i in x]))
    return r

pathToJSON = sys.argv[1]
with open(pathToJSON,'r') as f:
    jdat = json.load(f)

with open(jdat['stimuli'],'rb') as f:
	stimuli = pickle.load(f)

with open(jdat['phonDict'],'rb') as f:
	phonDict = pickle.load(f)

header = ['proc','min','max','grace','actI','actT','defI','defT']
words = stimuli.keys()
words.sort()

filename = 'ex/phase{p:02d}_{t}.ex'.format(
        p=jdat['phase'],
        t='test' if jdat['test'] else 'train'
    )

minStart = 10
maxEnd = 0
phonemes = [[],[],[],[],[],[],[],[],[],[]]
SEM = []
N = {}
for word in words:
    SEM.append(stimuli[word]['sem_rep'])
    for lang in ['AAE','SAE']:
        code = '{lang}_phon'.format(lang=lang)
        pcode = stimuli[word][code]
        n = len(pcode)
        for i,p in enumerate(pcode):
            if p == "_":
                continue
            if i < minStart:
                minStart = i
            if not p in phonemes[i]:
                phonemes[i].append(p)

        for i,p in enumerate(pcode[::-1]):
            if p == "_":
                continue
            if (n-i) > maxEnd:
                maxEnd = (n-i)
            break

SEMT = list(zip(*SEM))
SEMUNITUSAGE = [sum(b) for b in SEMT]
N['sem'] = len(SEMUNITUSAGE)

X = []
PHONUNITUSAGE = []
for i in range(minStart,maxEnd):
    M = [phonDict[p] for p in phonemes[i]]
    MT = list(zip(*M))
    X.append([any(row) for row in MT])
    PHONUNITUSAGE.append(sum(X[i]))

N['phon'] = sum(PHONUNITUSAGE)
N['homo'] = 2
N['context'] = 1
print "N semantic units: {n:d}".format(n=N['sem'])
print "N phonological units: {n:d}".format(n=N['phon'])
print "N homophone units: {n:d}".format(n=N['homo'])
print "N context units: {n:d}".format(n=N['context'])
print "minStart {n:d}".format(n=minStart)
print "maxEnd {n:d}".format(n=maxEnd)

# Extract data into a simpler, pre-processed structure.
REPS = {
    "input": {
        "sem":{"AAE":[],"SAE":[]},
        "phon":{"AAE":[],"SAE":[]},
        "homo":{"AAE":[],"SAE":[]},
        "context":{"AAE":[],"SAE":[]}
    },
    "output": {
        "sem":{"AAE":[],"SAE":[]},
        "phon":{"AAE":[],"SAE":[]},
        "homo":{"AAE":[],"SAE":[]}
    }
}

try:
    inputLayers = [jdat['inputLayers'].lower()]
except AttributeError:
    inputLayers = [x.lower() for x in jdat['inputLayers']]
try:
    outputLayers= [jdat['outputLayers'].lower()]
except AttributeError:
    outputLayers = [x.lower() for x in jdat['outputLayers']]

homophoneCounter = {"AAE":{},"SAE":{}}
for word in words:
    for lang in ["SAE","AAE"]:
        OFFSET = 0
        if 'phon' in inputLayers:
            code = '{lang}_phon'.format(lang=lang)
            pcode = stimuli[word][code][minStart:maxEnd]
            ppat = []
            for pind,p in enumerate(pcode):
                ppat.extend([b for i,b in enumerate(phonDict[p]) if X[pind][i]==True])
            x = [i for i, e in enumerate(ppat) if int(e) == 1]
            r = rep2str(x,N['phon'],OFFSET)
            REPS['input']['phon'][lang].append(r)
            OFFSET += N['phon']

            if jdat['disambiguateHomophones']:
                try:
                    homophoneCounter[lang][pcode] += 1
                except KeyError:
                    homophoneCounter[lang][pcode] = 0
                nhomo = homophoneCounter[lang][pcode]
                hcode = '{n:02b}'.format(n=nhomo)
                x = [i+OFFSET for i,x in enumerate(hcode) if int(x) == 1]
                r = rep2str(x,N['homo'],OFFSET)
                REPS['input']['homo'][lang].append(r)
                OFFSET += N['homo']

        if 'sem' in inputLayers:
            spat = stimuli[word]['sem_rep']
            x = [i+OFFSET for i, e in enumerate(spat) if int(e) == 1]
            r = rep2str(x,N['sem'],OFFSET)
            REPS['input']['sem'][lang].append(r)
            OFFSET += N['sem']

        if jdat['context']:
            x = [OFFSET] if lang=='AAE' else []
            r = rep2str(x,N['context'],OFFSET)
            REPS['input']['context'][lang].append(r)

        OFFSET = 0
        if 'phon' in outputLayers:
            code = '{lang}_phon'.format(lang=lang)
            pcode = stimuli[word][code][minStart:maxEnd]
            ppat = []
            for pind,p in enumerate(pcode):
                ppat.extend([b for i,b in enumerate(phonDict[p]) if X[pind][i]==True])
            x = [i for i, e in enumerate(ppat) if int(e) == 1]
            r = rep2str(x,N['phon'],OFFSET)
            REPS['output']['phon'][lang].append(r)
            OFFSET += N['phon']

            if jdat['disambiguateHomophones']:
                nhomo = homophoneCounter[lang][pcode]
                hcode = '{n:02b}'.format(n=nhomo)
                x = [i+OFFSET for i,x in enumerate(hcode) if int(x) == 1]
                r = rep2str(x,N['homo'],OFFSET)
                REPS['output']['homo'][lang].append(r)
                OFFSET += N['homo']

        if 'sem' in outputLayers:
            spat = stimuli[word]['sem_rep']
            x = [i+OFFSET for i, e in enumerate(spat) if int(e) == 1]
            r = rep2str(x,N['sem'],OFFSET)
            REPS['output']['sem'][lang].append(r)
            OFFSET += N['sem']

# This is mostly for debugging.
with open('ex/REPS.json','w') as f:
    json.dump(REPS,f,sort_keys=False,indent=2,separators=(',',': '))

with open(filename,'w') as f:
    for key in header:
        try:
            line = '{key}: {val}\n'.format(key=key,val=jdat[key])
            f.write(line)
        except:
            pass
    f.write(';\n\n')

    for iword,word in enumerate(words):
        ex = stimuli[word]
        for temp in jdat['templates']:
            language = temp['language'].upper()

            try:
                inputType = [temp['inputType'].lower()]
            except AttributeError:
                inputType = [x.lower() for x in temp['inputType']]
            try:
                targetType = [temp['targetType'].lower()]
            except AttributeError:
                targetType = [x.lower() for x in temp['targetType']]

	        nameLine = 'name: {word}_{itype}_{ttype}_{lang}\n'.format(
	                word=word.lower(),
	                itype=''.join(inputType),
	                ttype=''.join(targetType),
	                lang=language
	            )

	        freqLine = 'freq: {freq:d}\n'.format(freq=ex['freq'])

            eventCountLine = '{eventCount}\n'.format(eventCount=len(temp['events']))

            f.write(nameLine)
            f.write(freqLine)
            f.write(eventCountLine)

            for ievent,event in enumerate(temp['events']):
                INPUT = []
                RngGen = RangeGenerator()
                for ilayer in inputLayers:
                    if not ilayer in inputType:
                        INPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N[ilayer])))
                        if ilayer == 'phon':
                            if jdat['disambiguateHomophones']:
                                INPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N['homo'])))
                            if jdat['context']:
                                INPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N['context'])))

                    else:
                        if event['i'] < 0:
                            INPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N[ilayer])))
                            if ilayer == 'phon':
                                if jdat['disambiguateHomophones']:
                                    INPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N['homo'])))
                                if jdat['context']:
                                    INPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N['context'])))
                        else:
                            RngGen.next(N[ilayer]) # Just to increment, not for use
                            INPUT.append(REPS['input'][ilayer][language][iword])
                            if ilayer == 'phon':
                                if jdat['disambiguateHomophones']:
                                    RngGen.next(N['homo']) # Just to increment, not for use
                                    INPUT.append(REPS['input']['homo'][language][iword])
                if jdat['context']:
                    INPUT.append(REPS['input']['context'][language][iword])

                OUTPUT= []
                RngGen = RangeGenerator()
                for ilayer in outputLayers:
                    if not ilayer in targetType:
                        OUTPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N[ilayer])))
                        if ilayer == 'phon':
                            if jdat['disambiguateHomophones']:
                                OUTPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N['homo'])))

                    else:
                        if event['t'] < 0:
                            OUTPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N[ilayer])))
                            if ilayer == 'phon':
                                if jdat['disambiguateHomophones']:
                                    OUTPUT.append('{{{v}}} {r}'.format(v='-',r=RngGen.next(N['homo'])))
                        else:
                            RngGen.next(N[ilayer]) # Just to increment, not for use
                            OUTPUT.append(REPS['output'][ilayer][language][iword])
                            if ilayer == 'phon':
                                if jdat['disambiguateHomophones']:
                                    RngGen.next(N['homo']) # Just to increment, not for use
                                    OUTPUT.append(REPS['output']['homo'][language][iword])
                eventLine = '[{i}] i: {inp} t: {tgt}\n'.format(i=ievent,inp=' '.join(INPUT),tgt=' '.join(OUTPUT))
                f.write(eventLine);

            f.write(';\n\n')
