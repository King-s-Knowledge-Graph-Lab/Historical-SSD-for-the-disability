import urllib, urllib.request
import xml.etree.ElementTree as ET
import sqlite3
from tqdm import tqdm
import time
import chardet


with open('searchWord.txt', 'r', encoding='utf-8') as file:
    lines_list = [line.strip() for line in file.readlines()]

conn = sqlite3.connect('resources/arxiv_papers.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS papers
            (id TEXT PRIMARY KEY, title TEXT, abstract TEXT, year INTEGER, searchWord TEXT)''')

for searchWord in tqdm(lines_list):

    max_results = 1000
    total_results = 10000
    if len(searchWord.split()) >= 2:
        searchWords = searchWord.split()
        search_query = "+AND+".join(f"all:{word}" for word in searchWords)
    else:
        search_query = f"all:{searchWord}"
    url_base = f'http://export.arxiv.org/api/query?search_query={search_query}&start=%d&max_results={max_results}'
    print(url_base)


    ns = {'atom': 'http://www.w3.org/2005/Atom'}


    total_inserted = 0

    for start in range(0, total_results, max_results):
        url = url_base % start
        data = urllib.request.urlopen(url)
        xml_data_bytes = data.read()
        encoding = chardet.detect(xml_data_bytes)['encoding']
        xml_data = xml_data_bytes.decode(encoding)

        root = ET.fromstring(xml_data)
        entries = root.findall('atom:entry', ns)

        for entry in entries:
            paper_id = entry.find('atom:id', ns).text.split('/')[-1]
            title = entry.find('atom:title', ns).text
            abstract = entry.find('atom:summary', ns).text
            published = entry.find('atom:published', ns).text
            year = int(published[:4])

            try:
                c.execute("INSERT INTO papers VALUES (?, ?, ?, ?, ?)", (paper_id, title, abstract, year, searchWord))
                total_inserted += 1
            except sqlite3.IntegrityError:
                pass  

        conn.commit()


    print(f"Total papers inserted: {total_inserted}")

conn.close()

