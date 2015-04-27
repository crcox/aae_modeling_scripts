#!/usr/bin/env python
from lensapi import network
import json
import os

with open('network.json','rb') as f:
    jdat = json.load(f)

try:
    edir = jdat['expdir']
except KeyError:
    edir = ''
try:
    os.makedirs(edir)
except OSError:
    pass
filename = '.'.join([jdat["name"],'in'])
fpath = os.path.join(edir,filename)

with open(fpath,'w') as f:
    network.writeNetworkDefinition(jdat,f)
    f.write('\n');
    network.writeLayerDefinitions(jdat,f)
    f.write('\n');
    network.writeConnectivityDefinitions(jdat,f)
