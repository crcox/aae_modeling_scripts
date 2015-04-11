#!/bin/bash

RunNum=${PWD##*/}

ls ../../../TRAINING/${RunNum}/wt | sed -n 's/^phase\([0-9]\+\).*\.wt/\1/p' | uniq > phases.list

while read p; do
  echo $p $(ls ../../../TRAINING/${RunNum}/wt/phase${p}* | sed -n 's/^.*\/phase[0-9]\+_\([0-9]\+\)\.wt/\1/p' | sort -n | tail -n1) > finalUpdate.list
done < phases.list

while read row; do
  phase=$(awk '{print $1}' <<< $row)
  update=$(awk '{print $2}' <<< $row)
  cp -v "../../../TRAINING/${RunNum}/wt/phase${phase}_${update}.wt" "wt/phase${phase}_init.wt"
done < finalUpdate.list
