from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from demo import app, db, bcrypt
from demo.models import User, Post
from demo.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
import os
import openai

openai.api_key = "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"

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
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
    else:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.6,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        message = {"answer" : response.choices[0].text, "type" : "text"}
    return jsonify(message)


    
    