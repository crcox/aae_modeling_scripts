#!/bin/bash

# Make the weight directory if it does not exist
if [ ! -d wt]; then
	mkdir wt
fi
# Move the weight files into it.
mv -v *.wt wt/
