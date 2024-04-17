from ftplib import FTP
from tqdm import tqdm
import os

# FTP server details
ftp_server = "ftp.ncbi.nlm.nih.gov"
ftp_directory = "/pubmed/baseline/"

# Connect to FTP server
ftp = FTP(ftp_server)
ftp.login()

# Navigate to the directory containing the dataset
ftp.cwd(ftp_directory)

# List files in the directory
file_list = ftp.nlst()

save_directory = "PubMed/"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)  # Create the save directory if it doesn't exist

# Download each file in binary mode
for file_name in tqdm(file_list, desc="Downloading"):
    file_path = os.path.join(save_directory, file_name)
    if not os.path.isfile(file_path):  # Check if the file does not already exist
        with open(file_path, 'wb') as local_file:
            ftp.retrbinary('RETR ' + file_name, local_file.write)

# Close the FTP connection
ftp.quit()

print("Dataset downloaded successfully.")
