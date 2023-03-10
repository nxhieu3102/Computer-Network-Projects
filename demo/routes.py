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

from demo.chat import longtermmemory, productReview


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
    elif 'review' in text.lower():
        temp = text.lower().split()
        text1 = temp[-1]
        text2 = temp[-2]
        response = productReview(text1,text2)
        message = {"answer" : response, "type" : "text"}
    else:
        response = longtermmemory(prompt)
        message = {"answer" : response, "type" : "text"}
    return jsonify(message)


    
    