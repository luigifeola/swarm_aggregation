#!/bin/bash

#EXE=~/swarm_aggregation/src/rw_gradient_follower_irace.py
#FIXED_PARAMS=" /home/luigi/swarm_aggregation/config/config_batch.txt"
#SEED=443218415
#CONFIG_PARAMS="--a0 1.2591 --r0 0.7619 --st0 16 --a1 1.7857 --r1 0.5014 --st1 586 --a2 1.71 --r2 0.9054 --st2 948"
#
#
#OUT=$(python3 $EXE ${SEED} ${FIXED_PARAMS} ${CONFIG_PARAMS})
#echo $OUT

STDOUT=../std/c1-1-400998555.stdout

if [ "${STDOUT}" ]; then
    COST=$(tail -n 1 ${STDOUT} | grep -e '^[[:space:]]*[+-]\?[0-9]' | cut -f1)
    echo $COST
    # rm -f "${STDOUT}" "${STDERR}"
    exit 0
else
    error "${STDOUT}: No such file or directory"
fi