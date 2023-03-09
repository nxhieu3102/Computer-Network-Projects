from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from demo import app, db, bcrypt
from demo.models import User, Post
from demo.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
import os
import openai
'''
import numpy as np 
import json
from numpy.linalg import norm
import re
from time import time,sleep
from uuid import uuid4
import datetime

openai.api_key = "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"'''

from demo.chat import longtermmemory


posts = [
    {
        'category': 'ELECTRONICS',
        'title': 'Iphone 14 Pro',
        'content': 'Dynamic Island bubbles up music, sports scores, phone calls, and so much more — without taking you away from what you’re doing.',
        'image' : 'ip14pro.jpg'
    },
    {
        'category': 'HEALTH & PERSONAL CARE',
        'title': 'CeraVe Cream',
        'content': 'With hyaluronic acid, ceramides and MVE technology for 24 hour hydration. Rich, velvety texture that leaves skin feeling smooth, it is absorbed quickly for softened skin without greasy, sticky, feel.',
        'image' : 'cerave.jpg'
    }, 
    {
        'category': 'BEAUTY PICKS',
        'title': "L'Oreal Serum",
        'content': "Intensive hydrating 1.5 percent Pure Hyaluronic Acid Serum for face with Vitamin C moisturizes skin instantly for dewy glow and visibly plumped skin; Reduces wrinkles and boosts skin's radiance; Effective for all skin tones",
        'image' : 'loreal.jpg'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route("/register", methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in','success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else :
            flash('Login Unsuccessful, Please check username and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods = ['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)

'''
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
    files = os.listdir('chathistory/nexus')
    files = [i for i in files if '.json' in i]  
    result = list()
    for file in files:
        data = load_json('chathistory/nexus/%s' % file)
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
    prompt = open_file('chathistory/prompt_notes.txt').replace('<<INPUT>>', block)
    notes = gpt3_completion(prompt)
    vector = gpt3_embedding(block)
    info = {'notes': notes, 'uuids': identifiers, 'times': timestamps, 'uuid': str(uuid4()), 'vector': vector, 'time': time()}
    filename = 'notes_%s.json' % time()
    save_json('chathistory/internal_notes/%s' % filename, info)
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


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.0, top_p=1.0, tokens=400, freq_pen=0.0, pres_pen=0.0, stop=['USER:', 'RAVEN:']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
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
            if not os.path.exists('chathistory/gpt3_logs'):
                os.makedirs('chathistory/gpt3_logs')
            save_file('chathistory/gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def longtermmemory(text):
    timestamp = time()
    vector = gp3_embedding(text)
    timestring = timestamp_to_string(timestamp)
    message = '%s: %s' % ('USER',text)
    info = {'speaker': 'USER', 'time': timestamp, 'vector': vector, 'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    filename = 'log_%s_USER.json' % timestamp
    save_json('chathistory/nexus/%s' % filename, info)

    conversation = load_convo()
    memories = fetch_memories(vector, conversation, 10)
    notes = summarize_memories(memories)
    recent = get_last_messages(conversation, 4)
    prompt = open_file('chathistory/prompt_response.txt').replace('<<NOTES>>', notes).replace('<<CONVERSATION>>', recent)
    output = gpt3_completion(prompt)
    timestamp = time()
    vector = gpt3_embedding(output)
    timestring = timestamp_to_datetime(timestamp)
    message = '%s: %s' % ('RAVEN', output)
    info = {'speaker': 'RAVEN', 'time': timestamp, 'vector': vector, 'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    filename = 'log_%s_RAVEN.json' % time()
    save_json('chathistory/nexus/%s' % filename, info)
    return output
'''
@app.route("/predict", methods = ['POST'])
def predict():
    text = request.get_json().get("message")
    message = ''
    prompt = text
    if 'photo' in text.lower() or 'photograph' in text.lower() or 'image' in text.lower() or 'picture' in text.lower() or 'draw' in text.lower():
        model_engine = "image-alpha-001"
        num_images = 1
        size = "512x512"
        response_format = "url"
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=num_images,
                size=size,
                response_format=response_format,
                model=model_engine
            )
            image_url = response['data'][0]['url']
        except Exception as e:
            print(f"Error: {e}")
            image_url = ''
        message = {"answer" : image_url, "type" : "image"}
    else:
        response = longtermmemory(prompt)
        message = {"answer" : response, "type" : "text"}
    return jsonify(message)


    
    