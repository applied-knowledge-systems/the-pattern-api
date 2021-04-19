tokenizer = None 
    
import numpy as np
# import torch
import os 

config_switch=os.getenv('DOCKER', 'local')
if config_switch=='local':
    startup_nodes = [{"host": "127.0.0.1", "port": "30001"}, {"host": "127.0.0.1", "port":"30002"}, {"host":"127.0.0.1", "port":"30003"}]
else:
    startup_nodes = [{"host": "rgcluster", "port": "30001"}, {"host": "rgcluster", "port":"30002"}, {"host":"rgcluster", "port":"30003"}]

try: 
    from redisai import ClusterClient
    redisai_cluster_client = ClusterClient(startup_nodes=startup_nodes)
except:
    print("Redis Cluster is not available")

def loadTokeniser():
    global tokenizer
    from transformers import BertTokenizerFast
    tokenizer = BertTokenizerFast.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    return tokenizer


def qa(question, sentence_key,hash_tag):
    ### question is encoded
    ### use pre-computed context/answer text tensor populated by tokeniser_gears_redisai.py

    global tokenizer

    if not tokenizer:
        tokenizer=loadTokeniser()

     

    token_key = f"tokenized:bert:qa:{sentence_key}"

    input_ids_question = tokenizer.encode(question, add_special_tokens=True, truncation=True, return_tensors="np")

    num_seg_a=len(input_ids_question)
    num_seg_b=redisai_cluster_client.tensorget(token_key,meta_only=True)['shape'][0]
    segment_ids = np.array([0]*num_seg_a + [1]*num_seg_b)

    redisai_cluster_client.tensorset(f'input_ids{hash_tag}', input_ids_question)
    # TODO: add torchscript (qa_append) to run numpy append input_ids_question and input_ids_context via torch.cat
    redisai_cluster_client.tensorset(f'token_type_ids{hash_tag}', segment_ids)

    redisai_cluster_client.modelrun(f'bert-qa{hash_tag}', [f'input_ids{hash_tag}', f'token_type_ids{hash_tag}'],
                        [f'answer_start_scores{hash_tag}', f'answer_end_scores{hash_tag}'])

    print(f"Model run on {hash_tag}")
    answer_start_scores = redisai_cluster_client.tensorget(f'answer_start_scores{hash_tag}')
    answer_end_scores = redisai_cluster_client.tensorget(f'answer_end_scores{hash_tag}')

    answer_start = np.argmax(answer_start_scores)
    answer_end = np.argmax(answer_end_scores) + 1

    input_ids = inputs["input_ids"].tolist()[0]
    
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer

if __name__ == "__main__":
    question="Effectiveness of community contact reduction"
    content_text="This would need tight coordination among pharmaceutical companies, governments, regulatory agencies, and the World Health Organization (WHO), as well as novel and out-of-the-box approaches to cGMP production, release processes, regulatory science, and clinical trial design."
    print(qa(question,content_text,'{62n}'))