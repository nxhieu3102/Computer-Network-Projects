import os
import openai
import numpy as np 
import json
from numpy.linalg import norm
import re
from time import time,sleep
from uuid import uuid4
import datetime
import csv
import random

openai.api_key = os.getenv("OPENAI_API_KEY")

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=2)


def timestamp_to_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time).strftime("%A, %B %d, %Y at %I:%M%p %Z")


def gpt3_embedding(content, engine='text-embedding-ada-002'):
    content = content.encode(encoding='ASCII',errors='ignore').decode()
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']
    return vector


def similarity(v1, v2):
    return np.dot(v1, v2)/(norm(v1)*norm(v2)) 


def fetch_memories(vector, logs, count):
    scores = list()
    for i in logs:
        if vector == i['vector']:
            continue
        score = similarity(i['vector'], vector)
        i['score'] = score
        scores.append(i)
    ordered = sorted(scores, key=lambda d: d['score'], reverse=True)
    try:
        ordered = ordered[0:count]
        return ordered
    except:
        return ordered


def load_convo():
    files = os.listdir('demo/chathistory/nexus')
    files = [i for i in files if '.json' in i]  
    result = list()
    for file in files:
        data = load_json('demo/chathistory/nexus/%s' % file)
        result.append(data)
    ordered = sorted(result, key=lambda d: d['time'], reverse=False)  
    return ordered


def summarize_memories(memories):  
    memories = sorted(memories, key=lambda d: d['time'], reverse=False)  
    block = ''
    identifiers = list()
    timestamps = list()
    for mem in memories:
        block += mem['message'] + '\n\n'
        identifiers.append(mem['uuid'])
        timestamps.append(mem['time'])
    block = block.strip()
    if block == '':
        return "" # no conversation
    prompt = open_file('demo/chathistory/prompt_notes.txt').replace('<<INPUT>>', block)
    print(prompt)
    notes = gpt3_completion(prompt,"chathistory")
    vector = gpt3_embedding(block)
    info = {'notes': notes, 'uuids': identifiers, 'times': timestamps, 'uuid': str(uuid4()), 'vector': vector, 'time': time()}
    filename = 'notes_%s.json' % time()
    save_json('demo/chathistory/internal_notes/%s' % filename, info)
    return notes


def get_last_messages(conversation, limit):
    try:
        short = conversation[-limit:]
    except:
        short = conversation
    output = ''
    for i in short:
        output += '%s\n\n' % i['message']
    output = output.strip()
    return output


def gpt3_completion(prompt, filename, engine='text-davinci-003', temp=0.0, top_p=1.0, tokens=400, freq_pen=0.0, pres_pen=0.0, stop=['USER:', 'RAVEN:']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    filepath = 'demo/' + filename
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('[\r\n]+', '\n', text)
            text = re.sub('[\t ]+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            if not os.path.exists(filepath + '/gpt3_logs'):
                os.makedirs(filepath + '/gpt3_logs')
            save_file((filepath + '/gpt3_logs/%s') % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def save_longterm_memory(text):
    timestamp = time()
    vector = gpt3_embedding(text)
    timestring = timestamp_to_datetime(timestamp)
    message = '%s: %s' % ('USER',text)
    info = {'speaker': 'USER', 'time': timestamp, 'vector': vector, 'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    filename = 'log_%s_USER.json' % timestamp
    save_json('demo/chathistory/nexus/%s' % filename, info)

    conversation = load_convo()
    memories = fetch_memories(vector, conversation, 10)
    notes = summarize_memories(memories)
    recent = get_last_messages(conversation, 4)
    prompt = open_file('demo/chathistory/prompt_response.txt').replace('<<NOTES>>', notes).replace('<<CONVERSATION>>', recent)
    output = gpt3_completion(prompt,"chathistory")
    timestamp = time()
    vector = gpt3_embedding(output)
    timestring = timestamp_to_datetime(timestamp)
    message = '%s: %s' % ('RAVEN', output)
    info = {'speaker': 'RAVEN', 'time': timestamp, 'vector': vector, 'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    filename = 'log_%s_RAVEN.json' % time()
    save_json('demo/chathistory/nexus/%s' % filename, info)
    return output

def review_product(text1, text2):
    reviews = list()
    with open('demo/ProductReview/reviews.csv', 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            if text1 in row[0].lower() and text2 in row[0].lower():
                reviews.append(row[1] + ' - ' + row[2])
    random.seed()
    subset = random.choices(reviews, k=25)
    textblock = '\n-'.join(subset)
    prompt = open_file('demo/ProductReview/prompt.txt').replace('<<REVIEWS>>', textblock)
    response = gpt3_completion(prompt,"ProductReview")
    return response



 
