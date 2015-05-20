proc detectSpike {errHistory err} {
	set n [llength errHistory]
	set sum 0
	foreach e $errHistory {set sum [expr {$sum + $e}]}
	set mean [expr {$sum / $n}]
	set var 0
	foreach e $errHistory {
		set diff [expr {$mean - $e}]
		set var [expr {$var + $diff*$diff}]
	}
	set x [expr {$var / $n}]
	set std [expr sqrt($x)]

	set crit [expr {$mean + 2*$std}]
	puts $crit
	puts $err
	if { $err > $crit } {
		set spike Yes
		puts "Spike!"
	} else {
		set spike No
	}
	return $spike
}	
