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
```jsx
python solo_main.py \
    --embed_model openai \
    --generation_model openai \
    --splitter semantic \
    --breakpoint_threshold_type standard_deviation \
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there."
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
    --user_input "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there."
    --expert_input "Any text"
```

### Database Build

1. Alter the documents in ‘/source’ directory
2. Execute the command