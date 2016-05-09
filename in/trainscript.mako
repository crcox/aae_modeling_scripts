<%
OutputLayers = ["{name:s}Output".format(name=name.title()) for name in CONFIG['target'].values()]
testGroupCrit = CONFIG['testGroupCrit'] if 'testGroupCrit' in CONFIG else 0.5
targetRadius = CONFIG['targetRadius'] if 'targetRadius' in CONFIG else 0
numUpdates = CONFIG['numUpdates']
weightDecay = CONFIG['weightDecay']
batchSize = CONFIG['batchSize']
zeroErrorRadius = CONFIG['zeroErrorRadius'] if zeroErrorRadius in CONFIG else 0
learningRate = CONFIG['learningRate']
momentum = CONFIG['momentum']
reportInterval = CONFIG['reportInterval']
SpikeThreshold = CONFIG['SpikeThreshold']
SpikeThresholdStepSize = CONFIG['SpikeThresholdStepSize']
TestEpoch = CONFIG['TestEpoch']
ErrorCriterion = CONFIG['ErrorCriterion']
InitialWeights = CONFIG['InitialWeights'] if 'InitialWeights' in CONFIG else 'init.wt'
%>
proc main {} {
  global env
  global Test
  if {![ info exists env(PATH) ]} {
    set env(PATH) "/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/crcox/bin"
  }

  source "network.in"
% for procfile in ProcFiles:
  source ${procfile}
% endfor
  setObject testGroupCrit ${testGroupCrit}
  setObject targetRadius ${targerRadius}
  setObject numUpdates ${UpdatesPerCall}
  setObject weightDecay ${WeightDecay}
  setObject batchSize ${BatchSize}
  setObject zeroErrorRadius ${zeroErrorRadius}
  setObject learningRate ${learningRate}
  setObject momentum ${momentum}
  setObject reportInterval ${reportInterval}
  set SpikeThreshold ${SpikeThreshold}
  set SpikeThresholdStepSize ${SpikeThresholdStepSize}
  set TestEpoch ${TestEpoch}
  set ErrorCriterion ${ErrorCriterion}

  set WeightDir "./wt"
  if { ![file exists $WeightDir]} {
    file mkdir $WeightDir
  }

  resetNet
  set wtfile ${InitialWeights}
  if {[file exists $wtfile]} {
    puts "Loading ${InitialWeights}..."
    loadWeights $wtfile
  } else {
    puts "Saving ${InitialWeights}..."
    saveWeights $wtfile
  }

  loadExamples [file join "ex" "train.ex"] -exmode PERMUTED
  useTrainingSet train
  loadExamples [file join "ex" "test.ex"] -exmode ORDERED
  useTestingSet test
  set errlog [open [file join "error.log"] w]
  set MFHCcsv [open [file join "MFHC.csv"] w]
  set errList [errorInUnits $MFHCcsv {${' '.join(OutputLayers)}}]
  set PError [summarizeError $errList 0]
  set err [getObj error]
  set errHistory [list]
  set i 0
  while {$PError <%text>></%text> $ErrorCriterion} {
    train -a steepest
    set err [getObj error]
    if { [llength $errHistory] == 10 } {
      set spike [detectSpike $errHistory $err $SpikeThreshold]
      if { $spike } {
        # Revert to the prior weight state and half the learning rate.
        puts "Spike!"
        loadWeights "oneBack.wt"
        setObject learningRate [expr {[getObj learningRate] / 2}]
        set SpikeThreshold [expr {$SpikeThreshold * $SpikeThresholdStepSize}]
        continue
      }
    }
    # Update and maintain the (cross-entropy) error history.
    lappend errHistory $err
    if {[llength $errHistory] <%text>></%text> 10} {
      set errHistory [lrange $errHistory 1 end]
    }

    # Log the (cross-entropy) error.
    puts $errlog [format "%.2f" $err]

    # Save the model weights. Periodically save to a persistent archive.
    saveWeights "oneBack.wt"
    incr i 1
    if { [expr {$i % $TestEpoch}] == 0 } {
      # Compute the (unit-wise) error
      set errList [errorInUnits $MFHCcsv {${' '.join(OutputLayers)}}]
      set PError [summarizeError $errList 0]
      set wtfile [file join $WeightDir [format "%d.wt" [getObj totalUpdates]]]
      file copy "oneBack.wt" $wtfile
    }
  }
  file delete "oneBack.wt"
  close $errlog
  close $MFHCcsv
  exit 0
}

if { [catch {main} msg] } {
  puts stderr "unexpected script error: $msg"
  exit 1
}
