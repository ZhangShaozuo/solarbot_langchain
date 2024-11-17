## unused import
# from langchain.llms import CTransformers
# from ctransformers import AutoModelForCausalLM
# from torch import cuda, bfloat16
## deprecated import
# from langchain import PromptTemplate, LLMChain, HuggingFacePipeline
# from langchain import HuggingFacePipeline
from transformers import AutoTokenizer

# from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_huggingface import HuggingFacePipeline
import transformers
import torch
import torchvision
torchvision.disable_beta_transforms_warning()
model_id = "meta-llama/Llama-2-13b-chat-hf"#"mistralai/Mistral-7B-v0.1"
hf_auth = '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'
from huggingface_hub import login
login(token=hf_auth, add_to_git_credential=False)

#llm = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-7B-Chat-GGML", model_type='llama', gpu_layers=50, model_file='llama-2-7b-chat.ggmlv3.q8_0.bin')  # Load model from GGML model repo.
#tokenizer = AutoTokenizer.from_pretrained("TheBloke/Llama-2-7B-Chat-GGML")  # Load tokenizer from original model repo.

#token='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'
#"C:\Users\somii\.cache\huggingface\hub\models--TheBloke--Llama-2-7B-Chat-GGML\snapshots\b616819cd4777514e3a2d9b8be69824aca8f5daf\llama-2-7b-chat.ggmlv3.q8_0.bin"
# Local CTransformers wrapper for Llama-2-7B-Chat

# llm = CTransformers(model='TheBloke/Llama-2-13B-Chat-GGML',#model = 'TheBloke/Llama-2-70B-Chat-GGML',# # Location of downloaded GGML model
#                     model_file='llama-2-13b-chat.ggmlv3.q8_0.bin',#model_file='llama-2-70b-chat.ggmlv3.q4_0.bin',#model_file='llama-2-7b-chat.ggmlv3.q8_0.bin',
#                     model_type='llama', # Model type Llama
#                     config={'max_new_tokens': 200,
#                             'temperature': 0.01, 
#                             'repetition_penalty': 1.1},
#                     cache_dir = '/data/rima',
#                    gpu_layers=50)

# bnb_config = transformers.BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_quant_type='nf4',
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_compute_dtype=bfloat16
# )

# model_config = transformers.AutoConfig.from_pretrained(
#     model_id,
#     use_auth_token=hf_auth
# )

tokenizer = AutoTokenizer.from_pretrained(model_id)
#device_map = 
model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    #config=model_config,
    #quantization_config=bnb_config,
    device_map='auto',
    # use_auth_token=hf_auth,
    # cache_dir = "/data/rima"
)
model.eval()

pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.float16,
    device_map='auto',
    max_length=8000,
    eos_token_id = tokenizer.eos_token_id,
    repetition_penalty=1.1
)

llm = HuggingFacePipeline(cache=False, pipeline=pipeline, model_kwargs={'temperature': 0.5, 'repetition_penalty': 1.1})

