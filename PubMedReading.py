import gzip
import xml.etree.cElementTree as ET
import sqlite3
import os
import glob
from tqdm import tqdm

def PubMedDataReading(file_path, db_name):
    conn = sqlite3.connect(db_name, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        pmid TEXT PRIMARY KEY,
        title TEXT,
        abstract TEXT,
        year INTEGER,
        mesh_terms TEXT
    )
    """)
    
    with gzip.open(file_path, 'rt', encoding='utf-8') as file:
        articles = []
        for event, elem in ET.iterparse(file, events=('start', 'end')):
            if event == 'end' and elem.tag == 'PubmedArticle':
                abstract = elem.find('.//Abstract')
                if abstract is not None:
                    pmid = elem.find('.//PMID').text
                    title = elem.find('.//ArticleTitle').text
                    abstract_text = abstract.find('.//AbstractText').text
                    if abstract_text is not None:
                        pub_date = elem.find('.//PubDate')
                        year = None
                        if pub_date is not None:
                            year_elem = pub_date.find('./Year')
                            if year_elem is not None:
                                year = int(year_elem.text)
                        
                        mesh_terms = []
                        mesh_headings = elem.findall('.//MeshHeading')
                        for heading in mesh_headings:
                            descriptor = heading.find('DescriptorName')
                            if descriptor is not None:
                                mesh_terms.append(descriptor.text)
                            qualifiers = heading.findall('QualifierName')
                            for qualifier in qualifiers:
                                mesh_terms.append(qualifier.text)
                        mesh_terms_str = '|'.join(mesh_terms)
                        
                        articles.append((pmid, title, abstract_text, year, mesh_terms_str))
                
                elem.clear()
    
    cursor.executemany("""
    INSERT OR REPLACE INTO articles (pmid, title, abstract, year, mesh_terms)
    VALUES (?, ?, ?, ?, ?)
    """, articles)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    directory = "PubMed"
    file_paths = glob.glob(os.path.join(directory, "*.gz"))
    for f in tqdm(file_paths):
        PubMedDataReading(file_path=f, db_name="resources/pubmed_articles.db")