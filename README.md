### Environment Setup

Note: 

PyTorch installation is not universal for every machine, refer to [here](https://pytorch.org/get-started/locally/) for more different commands. If not working, you may skip this step (as the current approach utilizes OpenAI API)

```jsx
conda create -n solarchat python=3.9
conda activate solarchat
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install -r requirements.txt
```

### Running
Before running, you need to have a OpenAI API key. Refer to [here](https://beta.openai.com/docs/developer-quickstart/your-api-keys) for more information.
The key should reside in a file named `credentials.py` by adding the following line:
```jsx
os.environ["OPENAI_API_KEY"] = 'your-key'
``` 
Text generation:
```jsx
python solo_main.py \
    --embed_model openai \
    --generation_model openai \
    --splitter semantic \
    --breakpoint_threshold_type gradient \
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there." \
    --style email
```

The simplified command below is identical to the previous command, meaning the default setting is

1. OpenAI as the text embedding model and generation model
2. Split document text based on semantic similarity
3. Email template as the output style

```jsx
python solo_main.py --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there."
```

The command to include the  expert’s optional input is

```jsx
python solo_main.py \
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there." \
    --expert_input "Any text"
```

### Database Build

1. Alter the documents in ‘/source’ directory
2. Execute the examplary command

```jsx
python db_build.py --embed_model openai --splitter semantic --breakpoint_threshold_type gradient
```

### Resource Allocation
1. Space requirement: 74 Mb (without LLM), 6.0 Gb (with Llama-3.2-3B)
2. chatGPT fee: 0.006 USD per token processed
3. Open-Source LLM requires GPU with 16 Gb memory

### Integration - API
The backend is fully operated using FastAPI (in chat_api.py). The API can be accessed via the following command:

```
curl -X POST "https://69b89e759ee6e7.lhr.life/query" -H "Content-Type: application/json" -d @curl_input.txt
```
Sample output
```json
{"result":"\nDear Sir/Madam,\nThank you for contacting us. \nWe will investigate the situation and ensure the timely removal of the solar panel in front of the resident's block as per the communicated schedule. Thank you for bringing this to our attention.\nLet us know if there is any other issue.\nBest Regards,\nHDB Team\n"}
```

### Non-Outstanding Items
> The scripts of evaluting CMS dataset have been groupped into '/cms_eval' directory
> llm.py stores the Huggingface pipeline
They can be discarded for platform integration