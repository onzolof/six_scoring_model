import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel

MAX_TEXT_LENGTH = 1024
MODELS = [
    "bert-base-uncased",
    "bert-large-uncased",
]

model_implementations = {}


def calculate_similarity(model_name, text_a, text_b):
    tokenizer = model_implementations[model_name]['tokenizer']
    model = model_implementations[model_name]['model']

    inputs = tokenizer([text_a, text_b], padding=True, truncation=True, return_tensors="pt", max_length=MAX_TEXT_LENGTH)

    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)

    # Calculate the cosine similarity between the embeddings
    similarity = cosine_similarity(embeddings[0].reshape(1, -1), embeddings[1].reshape(1, -1))
    return round(similarity[0][0] * 100, 0)


for current_model_name in MODELS:
    tokenizer_instance = BertTokenizer.from_pretrained(current_model_name)
    model_instance = BertModel.from_pretrained(current_model_name)
    model_implementations[current_model_name] = dict(tokenizer=tokenizer_instance, model=model_instance)
