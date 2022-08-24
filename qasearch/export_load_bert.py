from transformers import BertForQuestionAnswering,BertTokenizerFast
import torch
from redisai import ClusterClient
import numpy as np

import os 

config_switch=os.getenv('DOCKER', 'local')
REDISGRAPH_PORT=os.getenv('REDISGRAPH_PORT', "9001")
if config_switch=='local':
    startup_nodes = [{"host": "127.0.0.1", "port": "30001"}, {"host": "127.0.0.1", "port":"30002"}, {"host":"127.0.0.1", "port":"30003"}]
    host="127.0.0.1"
    port=REDISGRAPH_PORT
else:
    startup_nodes = [{"host": "rgcluster", "port": "30001"}, {"host": "rgcluster", "port":"30002"}, {"host":"rgcluster", "port":"30003"}]
    host="redisgraph"
    port=REDISGRAPH_PORT

def export_bert():
    model = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad", torchscript=True)
    model.eval()

    inputs = [torch.ones(1, 2, dtype=torch.int64),
            torch.ones(1, 2, dtype=torch.int64),
            torch.ones(1, 2, dtype=torch.int64)]

    with torch.no_grad():
        traced_model = torch.jit.trace(model, inputs)

    torch.jit.save(traced_model, "traced_bert_qa.pt")

def load_bert():
    model_file = 'traced_bert_qa.pt'

    with open(model_file, 'rb') as f:
        model = f.read()
    cc = ClusterClient(startup_nodes = startup_nodes)
    hash_tags = cc.execute_command("RG.PYEXECUTE",  "gb = GB('ShardsIDReader').map(lambda x:hashtag()).run()")[0]
    print(hash_tags)
    for hash_tag in hash_tags:
        print("Loading model bert-qa{%s}" %hash_tag.decode('utf-8'))
        cc.modelset('bert-qa{%s}' %hash_tag.decode('utf-8'), 'TORCH', 'CPU', model)
        print(cc.infoget('bert-qa{%s}' %hash_tag.decode('utf-8')))

def main():
    export_bert()
    load_bert()
if __name__ == "__main__":
    main()
