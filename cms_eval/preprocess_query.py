import io
import pandas as pd
import msoffcrypto

from tqdm.auto import tqdm
from openai import OpenAI
from credentials import *

def preprocess(query, client):
    prompt = "If the text is an email, extract the actual content present in the email; if the input text contains noises, remove the noise. Otherwise, just yield the original content: " + query
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        model="gpt-4o-mini",
    )
    return response.choices[0].message.content


def main():
    decrypted_workbook = io.BytesIO()
    with open('CMS.xlsx', 'rb') as file:
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(password='BF122266Sept')
        office_file.decrypt(decrypted_workbook)

    # `filename` can also be a file-like object.
    # workbook = openpyxl.load_workbook(filename=decrypted_workbook)
    df = pd.read_excel(decrypted_workbook)[['Case Content','Final Reply Content']]
    df = df[df['Case Content'].apply(lambda x: isinstance(x, str)) & df['Final Reply Content'].apply(lambda x: isinstance(x, str))]

    bar = tqdm(total=len(df))
    contents, replies = [], []
    client = OpenAI()
    for _, row in df.iterrows():
        bar.update(1)
        content = preprocess(row['Case Content'], client)
        reply = preprocess(row['Final Reply Content'], client)
        contents.append(content)
        replies.append(reply)
    df['Processed Content'] = contents
    df['Processed Reply'] = replies
    df.to_excel('CMS_preprocessed.xlsx')

### construct def main(args) for single input process
'''
python solo_main.py --embed_model BAAI/bge-large-en-v1.5 --generation_model openai
python solo_main.py --embed_model openai --generation_model openai
'''

if __name__ == "__main__":
    main()