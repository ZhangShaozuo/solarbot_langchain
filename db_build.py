from langchain_core.documents.base import Document
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
    if args.splitter == 'manual':
        docs = []
        for doc in os.listdir(args.doc_path):
            if doc.endswith('.pdf'):
                continue
            doc_path = os.path.join(args.doc_path, doc)
            f = open(doc_path, "r", encoding='utf-8')
            handbook = f.read().split('\n\n')
            ''''''
            for page in handbook:
                begin_idx, end_idx = page.find("["), page.find("]")
                if begin_idx != -1 and end_idx != -1 and end_idx > begin_idx:
                    meta_data = {'source': doc, 'headline': page[begin_idx:end_idx+1]}
                    page_content = page[end_idx+2:]
                else:
                    meta_data = {'source': doc, 'headline': None}
                    page_content = page
                doc_obj = Document(page_content=page_content)
                doc_obj.metadata = meta_data
                docs.append(doc_obj)
            f.close()
        if args.vector_store == 'FAISS':
            # Build and persist FAISS vector store
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(f'vectorstore/db_faiss_{args.splitter}')
        else:
            raise NotImplementedError
'''
python db_build.py
python db_build.py --embed_model openai --chunk_size 250 --chunk_overlap 50 --splitter recursive
python db_duild.py --splitter manual --embed_model openai
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="db build")
    parser.add_argument("--doc_path", type=str, help="The path that store all the documents", default="source/")
    parser.add_argument("--embed_model", type=str, help="Model used to embed the document segments/chunks. Supported types: BAAI/bge-large-en-v1.5, openai", default='BAAI/bge-large-en-v1.5')
    parser.add_argument("--vector_store", type=str, help="vector_store", default='FAISS', required=False)
    parser.add_argument("--splitter", type=str, help="Text split method. Supported types: recursive, semantic, manual", default='recursive', required=True)
    parser.add_argument("--chunk_size", type=int, help="The max size of each chunk, applied for recursive splitter. Choices: 250, 512, 1024", default=250, required=False)
    parser.add_argument("--chunk_overlap", type=int, help="The overlap between two consecutive chunks, applied for recursive splitter. Choices: 50, 64, 128", default=50, required=False)
    parser.add_argument("--breakpoint_threshold_type", type=str, default="The attributes of SemanticChunker, indicating the ways of when to split the sentences. Choices: gradient, interquartile, standard_deviation", required=False)
    args = parser.parse_args()
    vector_build(args)