# DistantHomologyDetection
Detecting distant homologies using DL

## Quick Tutorial:

1. Type ```git clone https://github.com/martinez-zacharya/DistantHomologyDetection``` in your home directory on the HPC
3. Download Miniconda by running ```wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh``` and then ```sh ./Miniconda3-latest-Linux-x86_64.sh```.
4. Run ```conda env create -f environment.yml``` in the home directory of the repo to set up the proper conda environment and then ```conda activate RemoteHomologyTransformer``` to activate the environment.
5. Shift your current working directory to the scripts folder.
6. Change the email in the tutorial_slurm file to your email and save the file (You can use https://s3-us-west-2.amazonaws.com/imss-hpc/index.html to make your own slurm files).
7. Activate your conda environment by typing ```conda activate RemoteHomologyTransformer```.
8. You can view the arguments for the command line tool by typing ```python3 main.py -h```.
9. To run the tutorial analysis, run ```sbatch tutorial_slurm```.
10. Remember, don't run big jobs on the login nodes on the HPC, only submit them using slurm (If this is confusing, just let me know and I can explain more).
11. You can now safely exit the ssh instance to the HPC if you want
