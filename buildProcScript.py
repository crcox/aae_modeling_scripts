#!/usr/bin/env python
from lensapi import proctcl
import json
import sys
import os

jpath = sys.argv[1]
ext = os.path.splitext(jpath)[1]
if not ext == '.json':
    print "Input file must be json formatted."
    raise IOError

with open(jpath,'r') as f:
    jdat = json.load(f)

try:
    edir = jdat['expdir']
except KeyError:
    edir = ''
try:
    os.makedirs(edir)
except OSError:
    pass
filename = "{netname}_train.tcl".format(netname=jdat['name'])
fpath = os.path.join(edir,filename)

with open(fpath,'w') as f:
    sw = proctcl.ScriptWriter(f, jdat)
    sw.writeFrontMatter()
    sw.source('{infile}.in'.format(infile=jdat['name']))
    for tclProcFile in os.listdir('bin/tcl/'):
        sw.source('bin/tcl/{f}'.format(f=tclProcFile))

    for objField,value in jdat['networkObjects'].items():
        sw.setObj(objField, value)

    sw.writeHeading('Start loop over subjects')
    with sw.for_('subject',1,jdat['nsubjects']):
        sw.resetNet()

        weightfile = '[file join $subject "wt" [format "init_%d.wt" [getObj totalUpdates]]]'
        sw.setVar('wtfile', weightfile)

        with sw.if_('[file exists $wtfile]') as if_:
            if_.loadWeights("$wtfile")

        with sw.else_() as else_:
            else_.saveWeights("$wtfile")

        jdatOrig = jdat.copy()
        for i in range(len(jdat['phase'])):
            jdat.update(jdat['phase'][i])
            phase = i + 1
            for objField, value in jdat['networkObjects'].items():
                if not jdat['networkObjects'][objField] == jdatOrig['networkObjects'][objField]:
                    sw.setObj(objField, value)

            sw.writeHeading('Start Phase {n}'.format(n=phase))

            if len(jdat['phase']) > 1:
                examplefile = '[file join "ex" "phase{p:02d}" "train.ex"]'.format(p=phase)
            else:
                examplefile = '[file join "ex" "train.ex"]'

            sw.loadExamples(examplefile, jdat['training_mode'])
            trainset = 'train'
            sw.useTrainingSet(trainset)

            if len(jdat['phase']) > 1:
                examplefile = '[file join "ex" "phase{p:02d}" "test.ex"]'.format(p=phase)
            else:
                examplefile = '[file join "ex" "test.ex"]'

            sw.loadExamples(examplefile, jdat['testing_mode'])
            testset = 'test'
            sw.useTestingSet(testset)

            errpath = '[file join $subject "phase{p:02d}_err.log"]'.format(p=phase)
            accpath = '[file join $subject "phase{p:02d}_acc.log"]'.format(p=phase)
#            actpath = '[file join $subject "phase{p:02d}_act.out.gz"]'.format(p=phase)
            EARTpath = '[file join $subject "phase{p:02d}_ErrAccRT.csv"]'.format(p=phase)

            errlog = sw.openFileConnection(errpath, 'errlog', 'w')
            acclog = sw.openFileConnection(accpath, 'acclog', 'w')
            EARTcsv = sw.openFileConnection(EARTpath, 'EARTcsv', 'w')
            sw.testErrAccRT(EARTcsv)
            sw.test()
            sw.writeError(errlog)
            sw.writeAccuracy(acclog)

            # +++ Start the training loop
            with sw.while_(jdat['accuracy_criterion']) as while_:
                while_.train(jdat['algorithm'])

                while_.testErrAccRT(EARTcsv)
                #while_.openNetOutputFile(actpath, binary=True, append=True)
                while_.test()
                #while_.closeNetOutputFile()
                while_.writeError(errlog)
                while_.writeAccuracy(errlog)
                if jdat['log_weights'] == True:
                    weightfile = '[file join $subject "wt" [format "phase{p:02d}_%d.wt" [getObj totalUpdates]]]'.format(p=phase)
                    while_.saveWeights(weightfile)

            # Add line breaks to error and accuracy logs
            sw.closeFileConnection(errlog)
            sw.closeFileConnection(acclog)
            jdat.update(jdatOrig)
