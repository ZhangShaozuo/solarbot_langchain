from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA 

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from prompts import qa_template

import torchvision
# torchvision.disable_beta_transforms_warning()
from credentials import *

# Wrap prompt template in a PromptTemplate object
def set_qa_prompt():
    prompt = PromptTemplate(template=qa_template,
                            input_variables=['context', 'question'])
    return prompt


# Build RetrievalQA object
def build_retrieval_qa(llm, prompt, vectordb):
    dbqa = RetrievalQA.from_llm(llm=llm,
                                retriever=vectordb.as_retriever(search_kwargs={'k':2}),
                                return_source_documents=True,
                                prompt=prompt)
    return dbqa

# Instantiate QA object
def setup_dbqa(args):
    if args.embed_model == 'BAAI/bge-large-en-v1.5':
        embeddings = HuggingFaceEmbeddings(model_name= 'BAAI/bge-large-en-v1.5', #"sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cuda'})
        
    elif args.embed_model == 'openai':
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()
    
    if args.splitter == 'recursive':
        vectordb = FAISS.load_local(f'vectorstore/db_faiss_{args.chunk_size}_{args.chunk_overlap}', embeddings, allow_dangerous_deserialization=True)
    elif args.splitter == 'semantic':
        vectordb = FAISS.load_local(f'vectorstore/db_faiss_{args.breakpoint_threshold_type}', embeddings, allow_dangerous_deserialization=True)
    qa_prompt = set_qa_prompt()
    if args.generation_model == 'meta-llama/Llama-2-13b-chat-hf':
        from llm import llm
        dbqa = build_retrieval_qa(llm, qa_prompt, vectordb)
    elif args.generation_model == 'openai':
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI()
        dbqa = build_retrieval_qa(llm, qa_prompt, vectordb)

    return dbqa