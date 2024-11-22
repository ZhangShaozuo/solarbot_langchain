import re
import os
import ast
import pandas as pd
from bert_score import score
import logging
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
    for file in os.listdir('results'):
        if file.endswith('.xlsx') and 'length' in file:
            df = pd.read_excel(f'results/{file}', index_col=0)
            logger.info(f'Processing {file}')
            model_outputs = df['Generated Reply']
            # model_outputs = model_outputs.apply(parse_texts)
            # y = df['Processed Reply']
            y = df['Final Reply Content']
            rs = rouge_eval(model_outputs, y)
            for key, value in rs.items():
                logger.info(f'{key}: {sum(value)/len(value)}')
            # P, R, F1 = bert_eval(model_outputs.tolist(), y.tolist(), scorer=scorer)
            P, R, F1 = bert_eval(model_outputs, y, scorer=scorer)
            logger.info(f'P: {P.mean()}')
            logger.info(f'R: {R.mean()}')
            logger.info(f'F1: {F1.mean()}')

if __name__ == "__main__":
    # df = pd.read_excel('results/CMS_generated_openai_512_64.xlsx', index_col=0)
    # model_outputs = df['Generated Reply']
    # y = df['Processed Reply']
    # model_outputs = model_outputs.apply(parse_texts)
    # rouge_eval(model_outputs, y)
    # bert_eval(model_outputs.tolist(), y.tolist())
    # breakpoint()
    eval()