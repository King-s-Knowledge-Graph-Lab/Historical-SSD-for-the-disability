#!/bin/bash -l

#SBATCH --output=/scratch/prj/inf_wqp/ISWC_paper/log.out
#SBATCH --job-name=gpu
#SBATCH --gres=gpu:1

python PubMedReading.py