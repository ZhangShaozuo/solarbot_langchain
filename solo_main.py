import io
import re
import timeit
import logging
import argparse
import msoffcrypto
import pandas as pd

from tqdm.auto import tqdm
from utils import setup_dbqa
from prompts import email_template


# import streamlit as st
def process_single(dbqa, input: str, expert_input: str, logger: logging.Logger):
    start = timeit.default_timer()
    response = dbqa.invoke({'query': input, 'context': expert_input})
    logging.info(dbqa.combine_documents_chain.llm_chain.prompt)
    end = timeit.default_timer() # End timer
    logger.info(f'\nAnswer: {response["result"]}')
    source_docs = response['source_documents']
    for i, doc in enumerate(source_docs):
        logger.info(f'Source Document {i+1}\n')
        if len(doc.metadata.keys())>0:
            logger.info(f'Document Name: {doc.metadata["source"]}')
        logger.info(f'Source Text: {doc.page_content}')
        logger.info('='* 50)
    logging.info(f"Time to retrieve response: {end - start}")
    return response['result']

def main(args):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename = 'solar_rag.log', level = logging.INFO, filemode='w')
    logging.info("Start seting up dbqa")
    dbqa = setup_dbqa(args)
    logging.info("Finish setting up dbqa")
    
    ## This is for encrypted CMS file
    # decrypted_workbook = io.BytesIO()
    # with open('CMS_preprocessed.xlsx', 'rb') as file:
    #     office_file = msoffcrypto.OfficeFile(file)
    #     office_file.load_key(password='BF122266Sept')
    #     office_file.decrypt(decrypted_workbook)
    # df = pd.read_excel(decrypted_workbook)[['Case Content','Final Reply Content']]

    df = pd.read_excel('CMS_preprocessed.xlsx')[['Case Content', 'Processed Content','Processed Reply']]
    bar = tqdm(total=len(df))
    results = []
    for idx, row in df.iterrows():
        bar.update(1)
        result = process_single(dbqa, row['Processed Content'], args.expert_input, logger)
        results.append(result)
    bar.close()
    df['Generated Reply'] = results
    if args.splitter == 'recursive':
        output_file = f'results/CMS_generated_{args.generation_model}_{args.chunk_size}_{args.chunk_overlap}.xlsx'
    elif args.splitter == 'semantic':
        output_file = f'results/CMS_generated_{args.generation_model}_{args.breakpoint_threshold_type}.xlsx'
    df.to_excel(output_file)
        
### construct def main(args) for single input process
def backend_warp(args):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename = 'solar_rag.log', level = logging.INFO, filemode='w')
    logging.info("Start seting up dbqa")
    dbqa = setup_dbqa(args)
    logging.info("Finish setting up dbqa")
    result = process_single(dbqa, args.user_input, args.expert_input, logger)
    logging.info(f"Answer: {result}")
    if args.style == 'email':
        result = email_template.format(generated_reply=result)
    return result

'''

'''

if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Langchain RAG - Solar PV Panel")
    ### input 
    parser.add_argument("--user_input", type=str, default="Hello, who are you?", required=False)
    parser.add_argument("--expert_input", type=str, default="", required=False)
    parser.add_argument("--style", type=str, help="e.g. email", default="email", required=False)
    parser.add_argument("--vector_store", type=str, help="vector store options", default="FAISS") # not important
    parser.add_argument("--splitter", type=str, help="text split method", default="semantic")
    ### model
    parser.add_argument("--embed_model", type=str, help="embeddings model", default='openai', required=False) # BAAI/bge-large-en-v1.5
    parser.add_argument("--generation_model", type=str, help="model", default="openai", required=False) #or openai, meta-llama/Llama-2-13b-chat-hf
    parser.add_argument("--chunk_size", type=int, help="chunk size", default=250, required=False)
    parser.add_argument("--chunk_overlap", type=int, help="chunk overlap", default=50, required=False)
    parser.add_argument("--breakpoint_threshold_type", type=str, default="standard_deviation", required=False)
    args = parser.parse_args()
    # main(args)
    backend_warp(args)