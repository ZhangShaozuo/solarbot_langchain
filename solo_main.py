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
    msg = 'Source Documents: \n'
    for srd in response['source_documents']:
        msg += srd.metadata['source'] + '\n'
        msg += srd.page_content + '\n'
    return response['result'], msg
        
### construct def main(args) for single input process
def backend_warp(args):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename = 'solar_rag.log', level = logging.INFO, filemode='w')
    logging.info("Start seting up dbqa")
    dbqa = setup_dbqa(args)
    logging.info("Finish setting up dbqa")
    result, source_docs = process_single(dbqa, args.user_input, args.expert_input, logger)
    logging.info(f"Answer: {result}")
    if args.style == 'email':
        result = email_template.format(generated_reply=result)
    if args.return_docs:
        logging.info(f"Source Documents: {source_docs}")
        return result + source_docs
    else:
        return result

if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Langchain RAG - Solar PV Panel")
    ### input 
    parser.add_argument("--user_input", type=str, default="Hello, who are you?", required=False)
    parser.add_argument("--expert_input", type=str, default="The expert can provide their experience and guides, their inputs will be the prioritised context", help='', required=False)
    parser.add_argument("--style", type=str, help="The template to warp up the model response. Supported style: email", default="email", required=False)
    parser.add_argument("--return_docs", type=bool, help="Whether to return the source documents", default=True, required=False)
    parser.add_argument("--vector_store", type=str, help="The type of vector store(database) used. Supported type: FAISS", default="FAISS") # not important
    parser.add_argument("--splitter", type=str, help="Text split method. Supported types: recursive, semantic, manual", default="manual")
    ### model
    parser.add_argument("--embed_model", type=str, help="Model used to embed the document segments/chunks. Supported types: BAAI/bge-large-en-v1.5, openai", default='openai', required=False)
    parser.add_argument("--generation_model", type=str, help="Model used to generate responses, supported models: openai, meta-llama/Llama-3.2-3B-Instruct", default="openai", required=False) 
    parser.add_argument("--chunk_size", type=int, help="The max size of each chunk, applied for recursive splitter. Choices: 250, 512, 1024", default=250, required=False)
    parser.add_argument("--chunk_overlap", type=int, help="The overlap between two consecutive chunks, applied for recursive splitter. Choices: 50, 64, 128", default=50, required=False)
    parser.add_argument("--breakpoint_threshold_type", type=str, help="The attributes of SemanticChunker, indicating the ways of when to split the sentences. Choices: gradient, interquartile, standard_deviation", default="gradient", required=False)
    
    args = parser.parse_args()
    backend_warp(args)