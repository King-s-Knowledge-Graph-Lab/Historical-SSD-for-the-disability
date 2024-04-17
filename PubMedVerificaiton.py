import os
import hashlib
from tqdm import tqdm

folder_path = 'PubMed'  
failed = []
for file in tqdm(os.listdir(folder_path)):
    if file.endswith('.xml.gz'):
        file_path = os.path.join(folder_path, file)
        
        md5_file = f'{file}.md5'
        md5_file_path = os.path.join(folder_path, md5_file)
        
        with open(md5_file_path, 'r') as f:
            provided_md5 = f.read().strip()
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        calculated_md5 = hash_md5.hexdigest()
        
        if provided_md5.split('=')[-1][1:] == calculated_md5:
            pass
        else:
        
            print(f'{file}: MD5 hash verification failed!')
            failed.append(file)