import sqlite3
import csv, random, os
from tqdm import tqdm

def sampling(sample_size, target_db, csv_path):
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(papers)")
    column_names = [column[1] for column in cursor.fetchall()]

    cursor.execute("SELECT * FROM papers")
    data = cursor.fetchall()

    sampled_data = random.sample(data, sample_size)

    csv_filename = csv_path

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        writer.writerows(sampled_data)

    print(f"data size: {sample_size} / path: {csv_filename}")

    cursor.close()
    conn.close()

def keywordParsing():
    file_path = 'searchWord.txt'
    data_list = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data_list.append(line.strip())

    src_conn = sqlite3.connect('resources/pubmed_articles.db')
    src_cursor = src_conn.cursor()

    if os.path.exists('filtered_articles.db'):
        os.remove('filtered_articles.db')

    dst_conn = sqlite3.connect('filtered_articles.db')
    dst_cursor = dst_conn.cursor()

    dst_cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            pmid TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            year INTEGER,
            searchWord TEXT,
            mesh TEXT
        )
    ''')

    progress_bar = tqdm(total=len(data_list), unit='searchWord')

    for searchWord in data_list:
        src_cursor.execute(f"SELECT * FROM articles WHERE abstract LIKE '%{searchWord}%'")
        filtered_data = src_cursor.fetchall()
        filtered_data_with_searchWord = [(pmid, title, abstract, year, searchWord, mesh) for pmid, title, abstract, year, mesh in filtered_data]

        dst_cursor.executemany('''
            INSERT OR IGNORE INTO articles (pmid, title, abstract, year, searchWord, mesh)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', filtered_data_with_searchWord)

        progress_bar.update(1)
        progress_bar.set_description(f"Processing keyword: {searchWord}")

    dst_conn.commit()
    src_cursor.close()
    dst_cursor.close()
    src_conn.close()
    dst_conn.close()
    progress_bar.close()

def get_keyword_counts(target_db):
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    cursor.execute("SELECT keyword, COUNT(DISTINCT pmid) AS count FROM articles GROUP BY keyword")
    keyword_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    return keyword_counts

def save_keyword_counts_to_csv(keyword_counts, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Keyword', 'Count'])
        writer.writerows(keyword_counts)

    print(f"Keyword counts saved to: {csv_path}")

if __name__ == "__main__":

    ## PubMed ##
    #keywordParsing()
    sampling(10000, 'resources/pubmed_articles.db', 'resources/sampleSets/sampled_articles.csv') #data sampling code
    #sampling(10000, 'resources/pubmed_filtered_articles.db', 'resources/sampleSets/filtered_set.csv') #data sampling for each keyword

    #keyword_counts = get_keyword_counts('filtered_articles.db')
    #save_keyword_counts_to_csv(keyword_counts, 'resources/sampleSets/keywordCounts.csv')

    ## Arxiv ##
    #sampling(10000, 'resources/arxiv_papers.db', 'resources/sampleSets/sampled_articles_arxiv.csv')
