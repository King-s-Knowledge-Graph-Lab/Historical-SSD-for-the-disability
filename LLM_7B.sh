#!/bin/bash -l

#SBATCH --output=/scratch/prj/inf_wqp/ISWC_paper/7B_log.out
#SBATCH --job-name=gpu
#SBATCH --gres=gpu:1
#SBATCH --constraint=a100_80g


nvidia-smi
python LLMlabeling_7B.py