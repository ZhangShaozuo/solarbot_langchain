from transformers import AutoTokenizer
from langchain_huggingface import HuggingFacePipeline
import transformers
import torch
import torchvision

from credentials import *
torchvision.disable_beta_transforms_warning()

device = torch.device(f"cuda:2")
# llm = HuggingFacePipeline.from_model_id(
#                 model_id="meta-llama/Llama-3.2-3B-Instruct",
#                 task="text-generation",
#                 pipeline_kwargs={"max_new_tokens": 50},
#             )

from langchain_huggingface import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_id = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
pipe = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, max_new_tokens=128, device=device
)
llm = HuggingFacePipeline(pipeline=pipe)