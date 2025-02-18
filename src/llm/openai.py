import json

from bs4 import BeautifulSoup

from llm.prompt import system_prompt, user_prompt


def llm_data_report_request(client, data:dict, model='DeepSeek-R1', char_limit=280):

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": system_prompt()},
            {"role": "user",
             "content": user_prompt(json.dumps(data))},
        ]
    )
    text = response.choices[0].message.content
    if '<think>' in text:
        text = remove_tag_segment(text, 'think')
    text = limit_text(text, char_limit)
    return text.strip()

def remove_tag_segment(text, tag='think'):
    soup = BeautifulSoup(text, 'html.parser')
    for tag in soup.find_all(tag):
        tag.decompose()
    text = soup.get_text()
    return text

def limit_text(text, limit):
    if len(text) > limit:
        text = text[:limit]
        segments = text.split('. ')
        text = '. '.join(segments[:-1])
    return text
