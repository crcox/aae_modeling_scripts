#!/bin/bash

# Identify job directories (everything in the current directoy that is not
# named "shared"
jobdirs=$( find ./ -type d -regex "\./[0-9][0-9][0-9]" -print | sort -n )
root=$(pwd)
printf "" > sweep.dag
for jobdir in $jobdirs; do
  job=${jobdir##*/}
  ./FillProcessTemplate.pl process.lens $job process.yaml > $job/process.sub;
  ./FillDAGTemplate.pl subdag.template $job process.yaml > $job/${job}_dag;
  printf "SPLICE %s %s/%s/%s_dag\n" $job $root $job $job >> sweep.dag
done
