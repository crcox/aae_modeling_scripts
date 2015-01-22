" Collapse homophone lists onto one line
:%s/\n    \("[a-z]\+"\)/\1/

" Bring closing bracket up to previous line.
:%s/\n  \(\],\?\)/\1/
