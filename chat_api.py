from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from utils import setup_dbqa
from prompts import email_template
import timeit

# Initialize FastAPI app
app = FastAPI()

# Initialize logging
logging.basicConfig(filename='solar_rag.log', level=logging.INFO, filemode='w')
logger = logging.getLogger(__name__)

# Input schema for API request
class QueryRequest(BaseModel):
    user_input: str = "Hello, who are you?"
    expert_input: str = ""
    style: str = "email"
    return_docs: bool = True
    vector_store: str = "FAISS"
    splitter: str = "manual"
    embed_model: str = "openai"
    generation_model: str = "openai"
    chunk_size: int = 250
    chunk_overlap: int = 50
    breakpoint_threshold_type: str = "gradient"

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

@app.post("/query")
def query(request: QueryRequest):
    """API endpoint for processing a single query."""
    try:
        logging.info("Start setting up dbqa")
        dbqa = setup_dbqa(request)
        logging.info("Finish setting up dbqa")
        result, source_docs = process_single(dbqa, request.user_input, request.expert_input, logger)
        logging.info(f"Answer: {result}")
        if request.style == 'email':
            result = email_template.format(generated_reply=result)
        if request.return_docs:
            logging.info(f"Source Documents: {source_docs}")
            return {"result": result + source_docs}
        else:
            return {"result": result}
        result = process_single(dbqa, request.user_input, request.expert_input, logger)
        logging.info(f"Answer: {result}")
        if request.style == 'email':
            result = email_template.format(generated_reply=result)
        return {"result": result}
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
