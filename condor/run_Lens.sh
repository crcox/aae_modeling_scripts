#!/bin/bash

## Set variables
root=$( pwd )
trainscript=$( ls -t *_train.tcl | head -1 )
export LENSDIR=$root/Lens

## Install Lens
if [ ! -f LensCRC.tgz ]; then
  wget -q "http://proxy.chtc.wisc.edu/SQUID/crcox/Lens/LensCRC.tgz"
fi
tar xzf "LensCRC.tgz"
chmod u+x $LENSDIR/Bin/lens-2.64
>&2 echo "INSTALLED Lens at ${root}/Lens/Bin"

## Setup environment
if [ -f wt.tgz ]; then
  # If a wt.tgz was transfered along with the job, unpack it.
  tar xzf "wt.tgz"
  >&2 echo "EXTRACTED wt.tgz"
  cd "wt"
  # if wt/init/ does not exist, create it.
  if [ ! -d "init" ]; then
    mkdir "init/"
    >&2 echo "CREATED init/"
  fi
  # if init_0.wt is not a symbolic link, move it into wt/init/. These are the
  # actual initial weights for this run of the network.
  if [ ! -h "init_0.wt" ]; then
    mv "init_0.wt" "init/"
    >&2 echo "MOVED init_0.wt --> init/init_0.wt"
  fi
  # Finally, find the newest file ending in .wt in the current directory and
  # symlink to it from init_0.wt. This will trick the training script into
  # initiallizing from that point.
  ln -v -s $( ls -t *.wt | head -1 ) "init_0.wt"
  >&2 echo "CREATED symlink: init_0.wt --> latest model state"
  cd $root
else
  mkdir "wt"
  >&2 echo "CREATED wt/"
fi

# Directory state before running lens
ls -ltr

# Run Lens
>&2 echo "STARTING LENS"
$LENSDIR/Bin/lens-2.64 -b "$trainscript"
>&2 echo "LENS ENDED"

# Package the weights for transfer and clean up
tar czf wt.tgz wt
rm -rf wt/
rm -rf Lens
rm -rf ex/
rm LensCRC.tgz
rm *.in *.tcl

# Directory state after running lens and cleaning up
ls -ltr

# Close connection to execute node and return remaining files.
exit
