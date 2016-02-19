#!/bin/bash

if [ -d wt ]; then
	# Copy the most current weight file into the current directory as init_0.wt
	cp -v $( ls -t wt/*.wt | head -1 ) "init_0.wt"
fi
