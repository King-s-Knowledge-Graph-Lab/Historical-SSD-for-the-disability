from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
from tqdm import tqdm
import pandas as pd

access_token = "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"
login(token=access_token)

model_name = "meta-llama/Llama-2-70b-chat-hf"


model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", load_in_4bit=True,  use_auth_token=access_token)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True, use_auth_token=access_token)

### Data prep.
result = []
target_words = [ 'Dexterity', 'Paraplegia', 'Quadriplegia', 'Speech disorder', 'Language disorder', 'Blindness', 'Astigmatism', 'Deafness', 'Hearing loss', 'Dyslexia', 'Asperger']

target_words = list(reversed(target_words))

for target_word in target_words:
    df = pd.read_pickle('resources/processedDF.pkl')
    print(f'starting for {target_word}')
    df = df[df['searchWord']==target_word].copy()
    df_before_2000 = df[df['year'] < 2005]
    df_after_2000 = df[df['year'] >= 2005]
    random_state = 42

    sampled_abstracts_before_2000 = df_before_2000['abstract'].sample(n=100, random_state=random_state).reset_index(drop=True)
    sampled_abstracts_after_2000 = df_after_2000['abstract'].sample(n=100, random_state=random_state).reset_index(drop=True)
    sampled_abstracts = pd.concat([sampled_abstracts_before_2000, sampled_abstracts_after_2000], axis=1, ignore_index=True)
    sampled_abstracts.columns = ['before_2000', 'after_2000']
    for idx in tqdm(range(0,100)):

        prompt = f"""###Task: Identify semantic drift in a target word by comparing its usage in two sentences from different time periods.

        ###Instructions:
        You will be given a target word and two sentences containing that word, each from a different timestamp (e.g., Sentence A from 2000 and Sentence B from 2020).
        Analyze the context and meaning of the target word in each sentence.
        Determine if the target word has undergone a significant change in meaning or connotation between the two timestamps.
        Provide a label indicating whether semantic drift has occurred: "Changed" if the meaning has significantly shifted, or "Unchanged" if the meaning remains similar.
        Briefly explain your reasoning for the label.

        ###Data to be labelled:
        Target word: {target_word}
        Sentence A: {sampled_abstracts['before_2000'][idx]}
        Sentence B: {sampled_abstracts['after_2000'][idx]}

        ###Answer
        """

        model_inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
        output = model.generate(**model_inputs)
        answer = tokenizer.decode(output[0], skip_special_tokens=True)
        row = [idx, target_word, sampled_abstracts['before_2000'][idx], sampled_abstracts['after_2000'][idx], answer]
        result.append(row)
        df = pd.DataFrame(result, columns=['Index', 'targetWord', 'Sentence A', 'Sentence B', 'Answer'])
        df.to_csv('70B_reverse.csv', index=False)  # Save as CSV without the index column

