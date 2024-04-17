import pandas as pd
from tqdm import tqdm

### Data prep.
result = []
target_words = [ 'Dexterity', 'Paraplegia', 'Quadriplegia', 'Speech disorder', 'Language disorder', 'Blindness', 'Astigmatism', 'Deafness', 'Hearing loss', 'Dyslexia', 'Asperger', 'Emotional disorders', 'Autism spectrum disorder', 'Dementia', 'Schizophrenia', 'Depression' ]

for target_word in target_words:
    df = pd.read_pickle('resources/processedDF.pkl')
    print(f'starting for {target_word}')
    df = df[df['searchWord']==target_word].copy()
    df_before_2000 = df[df['year'] < 2005]
    df_after_2000 = df[df['year'] >= 2005]
    random_state = 42

    sampled_abstracts_before_2000 = df_before_2000['abstract'].sample(n=10, random_state=random_state).reset_index(drop=True)
    sampled_abstracts_after_2000 = df_after_2000['abstract'].sample(n=10, random_state=random_state).reset_index(drop=True)
    sampled_abstracts = pd.concat([sampled_abstracts_before_2000, sampled_abstracts_after_2000], axis=1, ignore_index=True)
    sampled_abstracts.columns = ['before_2000', 'after_2000']
    for idx in tqdm(range(0,10)):
        row = [idx, target_word, sampled_abstracts['before_2000'][idx], sampled_abstracts['after_2000'][idx]]
        result.append(row)
        df = pd.DataFrame(result, columns=['Index', 'targetWord', 'Sentence A', 'Sentence B'])
        df.to_csv('annotation_task.csv', index=False)  # Save as CSV without the index column

