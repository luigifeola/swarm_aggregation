#!/bin/bash
#
#SBATCH --job-name=irace_tuning2_10
#SBATCH --output=Results/res_irace_tuning2_10.txt
#SBATCH --partition=long
#
#SBATCH --ntasks=1
#SBATCH --time=10-0:00
#SBATCH --mem-per-cpu=1000

module load releases/2020b
module load Python/3.8.6-GCCcore-10.2.0
module load R
srun /opt/cecisw/arch/easybuild/2020b/software/R/4.0.4-foss-2020b/lib64/R/library/irace/bin/irace --exec-dir=/home/unamur/fac_info/asion/swarm_aggregation/tuning2 --scenario scenario.txt
