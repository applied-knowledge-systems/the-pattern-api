tokenizer = None 
model = None


import torch

try: 
    from redisai import ClusterClient
    rc_list=json.loads(config.config(section='rediscluster_docker')['rediscluster'])
    rediscluster_client = RedisCluster(startup_nodes=rc_list, decode_responses=True)
except:
    log("RedisCluster is not available")
import numpy as np

def loadTokeniser():
    global tokenizer
    from transformers import BertTokenizerFast
    tokenizer = BertTokenizerFast.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    return tokenizer


def qa(question, content_text,hash_tag):

    global tokenizer

    if not tokenizer:
        tokenizer=loadTokeniser()


    inputs = tokenizer.encode_plus(question, content_text, add_special_tokens=True, truncation=True, return_tensors="pt")
    input_ids = inputs['input_ids'].numpy()
    attention_mask = inputs['attention_mask'].numpy()
    token_type_ids = inputs['token_type_ids'].numpy()
    


    rediscluster_client.tensorset(f'input_ids{hash_tag}', input_ids)
    rediscluster_client.tensorset(f'attention_mask{hash_tag}', attention_mask)
    rediscluster_client.tensorset(f'token_type_ids{hash_tag}', token_type_ids)

    rediscluster_client.modelrun(f'bert-qa{hash_tag}', [f'input_ids{hash_tag}', f'attention_mask{hash_tag}', f'token_type_ids{hash_tag}'],
                        [f'answer_start_scores{hash_tag}', f'answer_end_scores{hash_tag}'])

    print(f"Model run on {hash_tag}")
    answer_start_scores = r.tensorget(f'answer_start_scores{hash_tag}')
    answer_end_scores = r.tensorget(f'answer_end_scores{hash_tag}')

    answer_start = np.argmax(answer_start_scores)
    answer_end = np.argmax(answer_end_scores) + 1

    input_ids = inputs["input_ids"].tolist()[0]
    
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer

if __name__ == "__main__":
    question="Effectiveness of community contact reduction"
    content_text="This would need tight coordination among pharmaceutical companies, governments, regulatory agencies, and the World Health Organization (WHO), as well as novel and out-of-the-box approaches to cGMP production, release processes, regulatory science, and clinical trial design."
    print(qa(question,content_text))