#!/usr/bin/env bash
cd /home/u15/agladstein/SimPrily_update/update_test

## This script should only be used on Ocelote

set -e # quits at first error

GOAL=$1
QUEMAX=$2
CHR=$3
OUT=/rsgrps/mfh4/Ariella/SimPrily_update/chr${CHR}

set -f

if [ -e switch.txt ] ; then

    echo ""
    echo "#################"
    date
    echo "pwd: ${PWD}"
    echo "Goal: ${GOAL}"
    echo "Que max: ${QUEMAX} "
    echo "Out path: ${OUT}"
    echo "chr: ${CHR}"

    qstat=/cm/shared/apps/pbspro/current/bin/qstat
    qsub=/cm/shared/apps/pbspro/current/bin/qsub

    #check number of completed simulations
    echo "Check for ${GOAL} completed runs in $OUT"
    COMP=$(find ${OUT} -type f | wc -l)
    echo "${COMP} runs have completed"

    if [ "$COMP" -ge "$GOAL" ]; then
        rm switch.txt
        echo "Goal completed. ${COMP} runs have completed in $OUT." | sendmail agladstein@email.arizona.edu
        exit
    else
        #check number of jobs in que
	JOBS=$($qstat | grep "agladstein" | cut -d " " -f1)
        echo $JOBS
        n=0
        for j in $JOBS; do
	        q=$($qstat -t $j | grep -w "Q" | wc -l)
	        n=$(($n + $q))
        done
        echo "You have $n jobs in the que"

        if [ "$n" -ge "$QUEMAX" ]; then
	        echo "That's enough jobs in the que"
	        exit
        else

            cd /home/u15/agladstein
	    echo 'pwd: 'pwd
            echo "rsync -za SimPrily_update/ /xdisk/agladstein/SimPrily_update; cd /xdisk/agladstein/SimPrily_update"
            rsync -za SimPrily_update/ /xdisk/agladstein/SimPrily_update
            cd /xdisk/agladstein/SimPrily_update
	    echo 'pwd: 'pwd

            echo "Submit to standard"
            echo "$qsub update_test/PBS/run_sims_update_chr${CHR}.pbs"
            $qsub update_test/PBS/run_sims_update_chr${CHR}.pbs
        fi
    fi
else
    echo "switch.txt does not exist"
    exit
fi
