from langchain_community.vectorstores import Chroma, FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, UnstructuredMarkdownLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
import argparse

from credentials import *

# Load PDF file from data path
def vector_build(args):
    loaders = {
        '.pdf':DirectoryLoader(args.doc_path,
                            glob="*.pdf",
                            loader_cls=PyPDFLoader),
        '.mdx': DirectoryLoader(args.doc_path,
                            glob="*.mdx",
                            loader_cls=UnstructuredMarkdownLoader,
                            ),
        '.txt': DirectoryLoader(args.doc_path,
                            glob="*.txt",
                            loader_cls=TextLoader)
    }
    documents = []
    for loader in loaders.values():
        documents.extend(loader.load())
    #documents = loader.load()

    if args.embed_model == 'BAAI/bge-large-en-v1.5':
        embeddings = HuggingFaceEmbeddings(model_name=args.embed_model, #'sentence-transformers/all-MiniLM-L6-v2',
                                        model_kwargs={'device': 'cuda'})
    elif args.embed_model == 'openai':
        embeddings = OpenAIEmbeddings()
    else:
        raise NotImplementedError
    # Split text from PDF into chunks
    if args.splitter == 'recursive':
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=args.chunk_size,
                                                    chunk_overlap=args.chunk_overlap)
        texts = text_splitter.split_documents(documents)
        if args.vector_store == 'FAISS':
            # Build and persist FAISS vector store
            vectorstore = FAISS.from_documents(texts, embeddings)
            vectorstore.save_local(f'vectorstore/db_faiss_{args.chunk_size}_{args.chunk_overlap}')
        else: ## chroma
            raise NotImplementedError
    if args.splitter == 'semantic':
        text_splitter = SemanticChunker(embeddings,
                                        breakpoint_threshold_type=args.breakpoint_threshold_type)
        documents_str = [doc.page_content for doc in documents]
        texts = text_splitter.create_documents(documents_str)
        if args.vector_store == 'FAISS':
            # Build and persist FAISS vector store
            vectorstore = FAISS.from_documents(texts, embeddings)
            vectorstore.save_local(f'vectorstore/db_faiss_{args.breakpoint_threshold_type}')
        else:
            raise NotImplementedError
'''
python db_build.py
python db_build.py --embed_model openai --chunk_size 250 --chunk_overlap 50 --embed_model openai
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="db build")
    parser.add_argument("--doc_path", type=str, help="doc_path", default="source/")
    parser.add_argument("--embed_model", type=str, help="embed_model", default='BAAI/bge-large-en-v1.5')
    parser.add_argument("--vector_store", type=str, help="vector_store", default='FAISS', required=False)
    parser.add_argument("--splitter", type=str, help="splitter", default='recursive', required=True)
    parser.add_argument("--chunk_size", type=int, help="chunk_size", default=250, required=False)
    parser.add_argument("--chunk_overlap", type=int, help="chunk_overlap", default=50, required=False)
    parser.add_argument("--breakpoint_threshold_type", type=str, default="standard_deviation", required=False)
    args = parser.parse_args()
    vector_build(args)