### This gears will pre-compute (encode) all sentences using BERT tokenizer for QA

tokenizer = None 

def loadTokeniser():
    global tokenizer
    from transformers import BertTokenizerFast
    tokenizer = BertTokenizerFast.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    return tokenizer




def qa(record):
    log("Called with "+ str(record))
    log("Trigger "+str(record[0]))
    log("Key "+ str(record[1]))
    log("Question  "+ str(record[2]))

    global tokenizer

    import redisAI
    import numpy as np

    sentence_key=record[1]
    question=record[2]
    hash_tag="{%s}" % hashtag()
    log("Shard_id "+hash_tag)
    if not tokenizer:
        tokenizer=loadTokeniser()

     

    token_key = f"tokenized:bert:qa:{sentence_key}"

    input_ids_question = tokenizer.encode(question, add_special_tokens=True, truncation=True, return_tensors="np")

    t=redisAI.getTensorFromKey(token_key)
    input_ids_context=np.frombuffer(redisAI.tensorGetDataAsBlob(t), dtype=np.int16).reshape(redisAI.tensorGetDims(t))
    log("Input ids context "+str(input_ids_context))
    log("Input ids content shape "+str(input_ids_context.shape))
    log("Input ids content dtype "+str(input_ids_context.dtype))
    input_ids = np.append(input_ids_question,input_ids_context)
    
    log("Combined input_ids shape"+ str(input_ids.shape))
    attention_mask = np.array([[1]*len(input_ids)])
    input_idss=np.array([input_ids])
    log("input ids "+ str(input_idss.shape))
    log("Attention mask shape "+str(attention_mask.shape))
    num_seg_a=input_ids_question.shape[1]
    log(str(num_seg_a))
    num_seg_b=input_ids_context.shape[0]
    # num_seg_b=redisAI.tensorGetDims(input_ids_context)[0]
    log("Tensor get dims "+str(num_seg_b))
    token_type_ids = np.array([0]*num_seg_a + [1]*num_seg_b)
    log("Segments id "+str(token_type_ids.shape))
    modelRunner = redisAI.createModelRunner(f'bert-qa{hash_tag}')

    input_idss_ts=redisAI.createTensorFromBlob('INT64', input_idss.shape, input_idss.tobytes())
    attention_mask_ts=redisAI.createTensorFromBlob('INT64', attention_mask.shape, attention_mask.tobytes())
    token_type_ids_ts=redisAI.createTensorFromBlob('INT64', token_type_ids.shape, token_type_ids.tobytes())
    redisAI.modelRunnerAddInput(modelRunner, 'input_ids', input_idss_ts)
    redisAI.modelRunnerAddInput(modelRunner, 'attention_mask', attention_mask_ts)
    redisAI.modelRunnerAddInput(modelRunner, 'token_type_ids', token_type_ids_ts)
    redisAI.modelRunnerAddOutput(modelRunner, 'answer_start_scores')
    redisAI.modelRunnerAddOutput(modelRunner, 'answer_end_scores')
    res = redisAI.modelRunnerRun(modelRunner)
    # redisAI.setTensorInKey('c{1}', res[0])
    log(str(res[0]))
    log("answer end"+str(res[1]))

    log(f"Model run on {hash_tag}")
    answer_start_scores = res[0]
    answer_end_scores = res[1]

    answer_start = np.argmax(answer_start_scores)
    answer_end = np.argmax(answer_end_scores) + 1
    log("Answer start "+str(answer_start))
    log("Answer end "+str(answer_end))
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer


gb = GB('CommandReader')
gb.map(qa)
gb.register(trigger='RunQABERT',mode="async_local")