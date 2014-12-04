#!/usr/bin/env python
from lensapi import network
import json

with open('network.json','rb') as f:
    jdat = json.load(f)
    filename = '.'.join([jdat["name"],'in'])
    with open(filename,'w') as f:
        network.writeNetworkDefinition(jdat,f)
        f.write('\n');
        network.writeLayerDefinitions(jdat,f)
        f.write('\n');
        network.writeConnectivityDefinitions(jdat,f)
