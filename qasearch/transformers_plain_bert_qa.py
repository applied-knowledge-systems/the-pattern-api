tokenizer = None 
model = None

import torch


def loadTokeniser():
    global tokenizer
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad", torchscript=True)
    return tokenizer

def loadModel():
    global model
    from transformers import AutoModelForQuestionAnswering
    model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad", torchscript=True)
    return model

def qa(question, content_text):
    global tokenizer, model 

    if not tokenizer:
        tokenizer=loadTokeniser()

    if not model:
        model=loadModel()

    inputs = tokenizer.encode_plus(question, content_text, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]
    print(input_ids)

    answer_start_scores, answer_end_scores = model(**inputs,return_dict=False)
    answer_start = torch.argmax(
        answer_start_scores
    )  # Get the most likely beginning of answer with the argmax of the score
    answer_end = torch.argmax(answer_end_scores) + 1  # Get the most likely end of answer with the argmax of the score

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer

content_text="An impediment to future studies of airborne transmission of respiratory infections is the lack of established methods for the detection of airborne respiratory microorganisms appropriate for epidemiological studies"
question="Who performs viral transmission among adults?"
import time

t = time.process_time()
for i in range(20):
    answer=qa(question,content_text)
    print(answer)
elapsed_time = time.process_time() - t
print(f"Total {elapsed_time} seconds")
print(f"{elapsed_time/20} seconds per inference")


