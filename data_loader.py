import gzip

dir = 'openalex-snapshot'

path = f'{dir}/data/works/updated_date=2023-05-19/part_000.gz'

with gzip.open(path, 'rb') as f:
    file_content = f.read()
    print(file_content)