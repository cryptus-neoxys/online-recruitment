#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

DEVELOPMENT_ENV  = True

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.config['SECRET_KEY'] = 'testkey'

db = SQLAlchemy(app)

class User(db.Model):
   username = db.Column(db.String(100), primary_key=True)
   name = db.Column(db.String(100), nullable=False)
   password = db.Column(db.String(100), nullable=False)
   usertype = db.Column(db.String(100), nullable=False)
   userdata = db.relationship('Company', backref='user', lazy=True)

def __repr__(self, username, password, usertype, name):
   self.username = username
   self.password = password
   self.usertype = usertype
   self.name = name

class Company(db.Model):
	company_id = db.Column(db.Integer(), primary_key=True)
	company_name = db.Column(db.String(100), nullable=False)
	company_email = db.Column(db.String(100), nullable=False)
	company_vacancies = db.Column(db.Integer())
	company_type =  db.Column(db.String(100), nullable=False)
	username = db.Column(db.String(100), db.ForeignKey('user.username'), nullable=False)

   


db.create_all() 

app_data = {
    "name":         "Recruitment",
    "description":  "Job Recruitment Portal",
    "author":       "Dev Sharma",
    "html_title":   "Recruitment",
    "project_name": "Recruitment",
    "keywords":     ""
}


@app.route('/')
def home():
	return render_template('home.html', app_data=app_data)


@app.route('/signup', methods=['POST', 'GET'])
#error condition for name is left
def signup():
	if request.method == 'POST':
		if not request.form['username']:
			flash('Please enter all the username', 'error')
			return render_template('signup.html', app_data=app_data)
		elif not request.form['password']:
			flash('Please enter all the password', 'error')
			return render_template('signup.html', app_data=app_data)
		else:
			username = request.form['username']
			password = request.form['password']
			name = request.form['name']
			usertype = request.form['usertype']
			new_user = User(username=username, password=password, name=name, usertype=usertype)
			
			db.session.add(new_user)
			db.session.commit()

			session['user'] = username

			return redirect(url_for('account'))
	else:
		return render_template('signup.html', app_data=app_data)


@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password =request.form['password']

		user = User.query.filter_by(username = username).first()
		
		
		if user:
			
			if user.password == password and user.username == username:
				#account

				session['user'] = username
				return redirect(url_for('account'))
			else:
				#wrong password
				flash('Wrong password', 'error')
				return render_template('login.html', app_data=app_data)
			
		else:
			flash('No such username', 'error')
			return render_template('login.html', app_data=app_data)
	else:
		if 'user' in session:
			return redirect(url_for('account'))	
		return render_template('login.html', app_data=app_data)



@app.route('/account', methods=['POST', 'GET'])
def account():
	if 'user' in session:
		return render_template('company.html', app_data=app_data, username=session['user'])
	else:
		return redirect(url_for('login'))

@app.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
	return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html', app_data=app_data)


@app.route('/service')
def service():
    return render_template('service.html', app_data=app_data)


@app.route('/contact')
def contact():
    return render_template('contact.html', app_data=app_data)


if __name__ == '__main__':
    app.run(debug=DEVELOPMENT_ENV)