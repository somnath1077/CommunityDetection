#!/usr/bin/env zsh

### Job name
#BSUB -J NONOVERLAPPING_ITERATIVE[1-8]

### File / path where STDOUT & STDERR will be written
###    %J is the job ID, %I is the array ID
#BSUB -o FOO%J.%I

### Request the time you need for execution in minutes
### The format for the parameter is: [hour:]minute,
### that means for 80 minutes you could also use this: 1:20
# BSUB -W 60:00

### Request memory you need for your job in TOTAL in MB
# BSUB -M 1024

#BSUB -B
#BSUB -N
#BSUB -u jan.dreier@rwth-aachen.de

##############################################

# fail fast
set -e

echo "begin benchmark, LSB_JOBINDEX=" $LSB_JOBINDEX

tmpdir=tmpdir_$LSB_JOBINDEX
rm -rf $tmpdir
mkdir $tmpdir
cd $tmpdir
if [ $LSB_JOBINDEX -gt 4 ] ; then
    percentage=$((0.05 * ($LSB_JOBINDEX - 4)))
    size=small
else
    percentage=$((0.05 * ($LSB_JOBINDEX - 0)))
    size=big
fi
../benchmark_nonOverlapping.py -n 1000 -c $size -s $percentage -o ../../../output --samples_per_datapoint 100 -m "0.05 0.9 0.04" -i 1

#cd ..
#rm -rf $tmpdir

echo "end benchmark"
