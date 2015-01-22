" Collapse phon and sem reps onto one line.
:%s/\n \+\([0-9]\+,\?\)/\1/

" Move closing ] for phon patterns to prev line.
:%s/\n      \(\],\?\)/\1/

" Move closing ] for sem patterns to prev line.
:%s/\([01]\)\n \+\(\],\?\)/\1\2/
