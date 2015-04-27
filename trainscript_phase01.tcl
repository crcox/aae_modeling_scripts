# function in the aae module. This script should be run from the root
# This script was automatically generated using the json2trainScript
# of an experiment folder, which will have sub-folders for individual
# runs of the experiment (00/, 01/, etc) and a folder for example
# files (ex/). Lens .in files should be in the root directory, as
# well. The subfolder for each run should have a folder for weights.
# Error, accuracy, and activation values will be written into separate
# files within the directory for each run.
proc main{} {
  global env
  global Test
  if {![ info exists env(PATH) ]} {
    set env(PATH) "/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/crcox/bin"
  }

  source "network_1.in"
  source bin/tcl/progress.tcl
  source bin/tcl/testErrAccRT.tcl

  setObject testGroupCrit 0.5
  setObject targetRadius 0
  setObject numUpdates 100000
  setObject weightDecay 5e-7
  setObject batchSize 1
  setObject zeroErrorRadius 0
  setObject learningRate 0.075
  setObject reportInterval 10000
  set OutputLayer "SemOutput"

  resetNet
  set wtfile [file join "wt" [format "init_%d.wt" [getObj totalUpdates]]]
  if {[file exists $wtfile]} {
    loadWeights $wtfile
  } else {
    saveWeights $wtfile
  }

  ################################################################################
  #                                Start Phase 1                                 #
  ################################################################################
  loadExamples [file join "ex" "train.ex"] -exmode PERMUTED
  useTrainingSet train
  loadExamples [file join "ex" "test.ex"] -exmode ORDERED
  useTestingSet test
  set errlog [open [file join "phase01_err.log"] w]
  set acclog [open [file join "phase01_acc.log"] w]
  set EARTcsv [open [file join "phase01_ErrAccRT.csv"] w]
  testErrAccRT $EARTcsv $OutputLayer
  test
  puts $errlog "[format "%.2f" $Test(totalError)] "
  puts $acclog "[format "%.2f" $Test(percentCorrect)] "
  while {$Test(percentCorrect) < 0.9} {
    train -a steepest
    testErrAccRT $EARTcsv $OutputLayer
    test
    puts $errlog "[format "%.2f" $Test(totalError)] "
    puts $acclog "[format "%.2f" $Test(percentCorrect)] "
    saveWeights [file join "wt" [format "phase01_%d.wt" [getObj totalUpdates]]]
  }
  close $errlog
  close $acclog
  exit 0
}

if { [catch {main} msg] } {
  puts stderr "unexpected script error: $msg"
  exit 1
}
