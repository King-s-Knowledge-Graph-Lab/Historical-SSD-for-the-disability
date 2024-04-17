import pandas as pd
df = pd.read_pickle('resources/processedDF.pkl')

import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaForMaskedLM, AdamW
import gc

# Define the dataset class
class AbstractDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_length):
        self.dataframe = dataframe
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        abstract = self.dataframe.iloc[idx]['processed_abstracts']
        encoding = self.tokenizer.encode_plus(
            abstract,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten()
        }

# Initialize the RoBERTa tokenizer
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

# Set the device (GPU if available, else CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Set up the learning rate and loss function
learning_rate = 2e-5
criterion = torch.nn.CrossEntropyLoss()

# Fine-tune the model for each year
num_epochs = 50
max_length = 512


# Group the DataFrame by year
grouped_df = df[df['year'] >= 1970].groupby('year')

for year, year_df in grouped_df:
    print(f"Fine-tuning for year: {year}")
    
    # Create the dataset and dataloader for the current year
    dataset = AbstractDataset(year_df, tokenizer, max_length)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    # Initialize a new RoBERTa model for each year
    model = RobertaForMaskedLM.from_pretrained('roberta-base')
    model.to(device)
    
    # Set up the optimizer for the current year's model
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    
    # Fine-tune the model for the current year
    model.train()
    for epoch in range(num_epochs):
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            
            # Create masked input ids
            mask_indices = torch.bernoulli(torch.full(input_ids.shape, 0.15)).bool()
            masked_input_ids = input_ids.clone()
            target_ids = input_ids.clone()
            masked_input_ids[mask_indices] = tokenizer.mask_token_id
            
            optimizer.zero_grad()
            outputs = model(masked_input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            
            # Reshape logits and target_ids for loss calculation
            logits = logits.view(-1, tokenizer.vocab_size)
            target_ids = target_ids.view(-1)
            
            # Calculate the loss
            loss = criterion(logits, target_ids)
            loss.backward()
            optimizer.step()
        
        print(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss.item()}')
    
    # Save the fine-tuned model for the current year
    model.save_pretrained(f'resources/fine-tuned/fine_tuned_roberta_{year}')
    del model
    del optimizer
    torch.cuda.empty_cache()  # Clear memory cache
    torch.cuda.synchronize()  # Wait for all kernels to finish
    gc.collect()  # Collect garbage

