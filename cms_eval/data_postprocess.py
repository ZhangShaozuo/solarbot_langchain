from math import e, pi
import re
import os
import ast
import sys
import torch
import random
import logging
import transformers
import pandas as pd
from bert_score import score
from tqdm.auto import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from credentials import *
from prompts import rating_template
pd.set_option('display.max_colwidth', None)  # Show full content of each column
pd.set_option('display.max_columns', None)   # Display all columns
pd.set_option('display.expand_frame_repr', False)

def rouge_eval(model_outputs, y):
    from rouge_score import rouge_scorer
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = {'rouge1':[], 'rouge2':[], 'rougeL':[]}
    for i, model_output in enumerate(model_outputs):
        if type(y[i]) == str:
            score = scorer.score(model_output, y[i])
            scores['rouge1'].append(score['rouge1'].fmeasure)
            scores['rouge2'].append(score['rouge2'].fmeasure)
            scores['rougeL'].append(score['rougeL'].fmeasure)
    for key, value in scores.items():
        print(f'{key}: {sum(value)/len(value)}')
    return scores

def bert_eval(model_outputs, y, scorer = None):
    if score is not None:
        P, R, F1 = scorer(model_outputs, y, lang='en', verbose=True)
    else:
        P, R, F1 = score(model_outputs, y, lang='en', verbose=True)
    print(f'P: {P.mean()}')
    print(f'R: {R.mean()}')
    print(f'F1: {F1.mean()}')
    return P, R, F1

def llm_eval(model_outputs, y, pipe = None):
    if pipe is None:
        device = torch.device(f"cuda:2")
        pipe = transformers.pipeline("text-generation",
                                    model='meta-llama/Llama-3.2-3B-Instruct',
                                    model_kwargs={
                                    "torch_dtype": torch.bfloat16},
                                    device=device)
    bar = tqdm(total=len(model_outputs))
    scores = []
    for i, model_output in enumerate(model_outputs):
        llm_score, t = None, random.uniform(0.95, 1.05)
        while llm_score is None:
            messages = [
                {"role": "system", "content": rating_template},
                {"role": "user", "content": f"Generated response: {model_output} \n Ground-truth response: {y[i]} "}]   
            outputs = pipe(messages, max_new_tokens=256, 
                           pad_token_id=pipe.tokenizer.eos_token_id,
                           temperature = t)
            try:
                llm_score = float(outputs[0]["generated_text"][-1]['content'])
            except (ValueError, KeyError, TypeError):
                print('Error: Invalid rating', outputs[0]["generated_text"][-1]['content'])
                llm_score, t = None, random.uniform(0.95, 1.05)
        llm_score = float(outputs[0]["generated_text"][-1]['content'])
        scores.append(llm_score)
        bar.update(1)
    return sum(scores) / len(scores)

def parse_texts(text):
    matchA = re.search(r"'result':\s*'(.*?)'", text)
    matchB = re.search(r"'result':\s*\"(.*?)\"", text)
    if matchA:
        return matchA.group(1)
    elif matchB:
        return matchB.group(1)
    else:
        breakpoint()
        print('Error: No match found')
        return None

def eval():
    scorer = score
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename = 'eval.log', level = logging.INFO, filemode='w')
    device = torch.device(f"cuda:2")
    pipe = transformers.pipeline("text-generation",
                            model='meta-llama/Llama-3.2-3B-Instruct',
                            model_kwargs={
                            "torch_dtype": torch.bfloat16},
                            device=device)
    for file in os.listdir('results'):
        if file.endswith('.xlsx') and 'length' not in file:
            df = pd.read_excel(f'results/{file}', index_col=0)
            logger.info(f'Processing {file}')
            model_outputs = df['Generated Reply']
            # model_outputs = model_outputs.apply(parse_texts)
            y = df['Processed Reply']
            rs = rouge_eval(model_outputs, y)
            rating = llm_eval(model_outputs, y, pipe=pipe)
            for key, value in rs.items():
                logger.info(f'{key}: {sum(value)/len(value)}')
            
            P, R, F1 = bert_eval(model_outputs.tolist(), y.tolist(), scorer=scorer)
            # P, R, F1 = bert_eval(model_outputs, y, scorer=scorer)
            logger.info(f'LlaMa Rating: {rating}')
            logger.info(f'P: {P.mean()}')
            logger.info(f'R: {R.mean()}')
            logger.info(f'F1: {F1.mean()}')

if __name__ == "__main__":
    eval()