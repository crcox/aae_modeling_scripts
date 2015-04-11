#!/bin/bash

edir=$1
if [ ! -d ${edir}/json ]
then
  mkdir ${edir}/json
fi
cp *.json ${edir}/json
