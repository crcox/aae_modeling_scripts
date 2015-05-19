proc summarizeError {errorList} {
  set nExample [getObj testingSet.numExamples]
  set n [llength $errorList]
  set m [expr {$n / $nExample}]
  puts $n
  puts $m
  set errSubCount [list]
  set allErr 0
  set anyErr 0
  set phonErr 0
  set semErr 0
  for {set i 0} {$i < [expr {$m + 1}]} {incr i} {lappend errSubCount 0}
  for {set i 0} {$i < $nExample} {incr i} {
    set nErr 0
    for {set j 0} {$j < $m} {incr j} {
      if { [lindex $errorList [expr {$i + $nExample * $j}]] } {
        if { $j == 0 } { incr phonErr 1} else { incr semErr 1 }
        incr nErr 1
      }
    }
    if { $nErr } {
      incr anyErr
      if {$nErr == $m} { incr allErr 1 }
    }
  }
  set err [expr {$anyErr / $nExample}]

  puts [format "%12s%12s%12s" "Phon" "Sem" "Both"]
  puts [format "%12d%12d%12d" $phonErr $semErr $allErr]
  puts [format "%24s%12.2f" "Proportion with error:" $err]
  return $err
}
