# Estate-IQ: Chatbot Q&A for Solar-PV related issues and Data Query

## Environment Setup

Note:
PyTorch installation is not universal for every machine, refer to [here](https://pytorch.org/get-started/locally/) for more different commands. If not working, you may skip this step (as the current pipeline supports both invoking OpenAI API and hosting local LLM model).

```jsx
conda create -n solarchat python=3.9
conda activate solarchat
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install -r requirements.txt
```

## Usage

Before running, you need to have a OpenAI API key. Refer to [here](https://beta.openai.com/docs/developer-quickstart/your-api-keys) for more information. The key should reside in a file named `credentials.py` by adding the following line:

```jsx
os.environ["OPENAI_API_KEY"] = 'your-key'
# HuggingFace token is optional
hf_token = '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'
login(token=hf_token, add_to_git_credential=False)
```

Text generation:

```jsx
python solo_main.py \
    --embed_model openai \
    --generation_model openai \
    --splitter manual \
    --return_docs 1 \
    --breakpoint_threshold_type gradient \
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there." \
    --style email
```

(In response to HDB's requirement, we add a choice ```--return_docs``` indicating whether to return the contexts/evidence retrieved, which is set to ```1```(True) by default)

The simplified command below is identical to the previous command, meaning the default setting is

1. OpenAI as the text embedding model and generation model
2. Split document text based on semantic similarity
3. Email template as the output style

```jsx
python solo_main.py \ 
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there."
```

The command to include the  expert’s optional input is

```jsx
python solo_main.py \
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there." \
    --expert_input "Any text"
```

### Database Build

1. Update the documents in ```/source``` directory
2. Execute the examplary command

```jsx
python db_build.py --embed_model openai --splitter semantic --breakpoint_threshold_type gradient
```

## Resource Allocation

1. Space requirement: 100 Mb (without LLM), 6.0 Gb (with Llama-3.2-3B)
2. chatGPT fee: 0.006 USD per token processed
3. Open-Source LLM requires GPU with 16 Gb memory

## Integration - API

The backend is fully operated using FastAPI (in chat_api.py). The API can be accessed via the following command:

```jsx
curl -X POST "https://uidshpdhkp.sutd.org/query" -H "Content-Type: application/json" -d @curl_input.json
```

Sample output

```json
{"result":"\nDear Sir/Madam,\nThank you for contacting us. \nThe lifespan of solar panels is typically around 25 years, as per industry standards and warranties provided by manufacturers.\nLet us know if there is any other issue.\nBest Regards,\nHDB Team\nSource Documents: \nquestionaire.txt\nSolar panels generally have a lifespan of 25 years. The Power Purchase Agreement between the Town Councils and solar vendor typically last for 20 years with an option to extend for five more years. At the end of the contract, the solar panels are removed from the rooftops. \nprocessed_handbook.txt\nA solar PV system is an investment that should last a long time, typically two to three decades for grid-connected applications. The industry standard for a PV module warranty is 20-25 years on the power output.\n"}
```

A demonstration of the operating API can be found in ```demo``` directory (deprecated).

### How to host the API from the source code

There are mutliple ways to start FastAPI server, one straightforward way is to run

```jsx
uvicorn chat_api:app --reload
```

under the parent directory of ```chat_api.py```. This will start a server at ```http://127.0.0.1:8000```.

## Non-Outstanding Items

1. The scripts of evaluting CMS dataset have been groupped into '/cms_eval' directory.

2. llm.py stores the Huggingface pipeline. They can be discarded for platform integration.
