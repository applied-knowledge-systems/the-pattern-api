### This gears will pre-compute (encode) all sentences using BERT tokenizer for QA

import logging
logging.disable(logging.INFO)
logger = logging.getLogger()
logger.disabled = True
import logging
logging.disable(logging.CRITICAL)
import re
def set_global_logging_level(level=logging.ERROR, prefices=[""]):
    """
    Override logging levels of different modules based on their name as a prefix.
    It needs to be invoked after the modules have been loaded so that their loggers have been initialized.

    Args:
        - level: desired level. e.g. logging.INFO. Optional. Default is logging.ERROR
        - prefices: list of one or more str prefices to match (e.g. ["transformers", "torch"]). Optional.
          Default is `[""]` to match all active loggers.
          The match is a case-sensitive `module_name.startswith(prefix)`
    """
    prefix_re = re.compile(fr'^(?:{ "|".join(prefices) })')
    for name in logging.root.manager.loggerDict:
        if re.match(prefix_re, name):
            logging.getLogger(name).setLevel(level)

tokenizer = None 

def loadTokeniser():
    global tokenizer
    logger = logging.getLogger()
    logger.disabled = True
    import transformers
    set_global_logging_level(logging.ERROR)
    from transformers import BertTokenizerFast
    tokenizer = BertTokenizerFast.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    # tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
    return tokenizer

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]



def parse_sentence(record):
    import redisAI
    import numpy as np
    global tokenizer
    if not tokenizer:
        tokenizer=loadTokeniser()
    hash_tag="{%s}" % hashtag()

    for idx, value in sorted(record['value'].items(), key=lambda item: int(item[0])):
        tokens = tokenizer.encode(value, add_special_tokens=False, max_length=511, truncation=True, return_tensors="np")
        tokens = np.append(tokens,tokenizer.sep_token_id).astype(np.int64) 
        tensor=redisAI.createTensorFromBlob('INT64', tokens.shape, tokens.tobytes())
        
        key_prefix='sentence:'
        sentence_key=remove_prefix(record['key'],key_prefix)
        token_key = f"tokenized:bert:qa:{sentence_key}:{idx}"
        # execute('SET', token_key, tokens)
        redisAI.setTensorInKey(token_key, tensor)
        execute('SADD',f'processed_docs_stage3_tokenized{hash_tag}', token_key)

gb = GB()
gb.foreach(parse_sentence)
gb.count()
gb.run('sentence:*',keyTypes=['hash'])