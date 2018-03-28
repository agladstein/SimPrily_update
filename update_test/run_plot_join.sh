#!/usr/bin/env bash

#set -euo pipefail

cd /vol_c/ABC_update

for OBS in {1..100}
do
    for CHR in {1..10}
    do
        DIR=obs${OBS}/chr${CHR}/ABC/
        echo "cd ${DIR}"
        cd ${DIR}
        echo "PWD: $PWD"
        echo "/vol_c/env/simprily_env/bin/python /vol_c/test_update/SimPrily_update/update_test/plot_joint.py ABC_update_estimate_10pls_100ret_model0_jointPosterior_3_3_Obs0.txt ABC_update_estimate_10pls_100ret_model0_MarginalPosteriorCharacteristics.txt results_param_observed.txt"
        /vol_c/env/simprily_env/bin/python /vol_c/test_update/SimPrily_update/update_test/plot_joint.py ABC_update_estimate_10pls_100ret_model0_jointPosterior_2_3_Obs0.txt ABC_update_estimate_10pls_100ret_model0_MarginalPosteriorCharacteristics.txt results_param_observed.txt
        cd /vol_c/ABC_update
        echo ""
    done
done