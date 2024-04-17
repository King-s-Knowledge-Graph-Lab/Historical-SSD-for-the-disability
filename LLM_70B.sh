#!/bin/bash -l

#SBATCH --output=/scratch/prj/inf_wqp/ISWC_paper/70B_log.out
#SBATCH --job-name=gpu
#SBATCH --gres=gpu:1
#SBATCH --constraint=a100_80g

nvidia-smi
python LLMlabeling_70B.py