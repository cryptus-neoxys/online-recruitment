#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import json

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
   

def __repr__(self, username, password, usertype, name):
   self.username = username
   self.password = password
   self.usertype = usertype
   self.name = name

class Company(db.Model):
	company_id = db.Column(db.String(), primary_key=True)
	company_name = db.Column(db.String(100), nullable=False)
	company_email = db.Column(db.String(100), nullable=False)
	company_vacancies = db.Column(db.Integer())
	company_type =  db.Column(db.String(100), nullable=False)
	username = db.Column(db.String(100), nullable=False)

class Applicant(db.Model):
	applicant_id = db.Column(db.String(100), primary_key=True)
	applicant_email = db.Column(db.String(100), primary_key=False)
	applicant_number = db.Column(db.String(100), primary_key=False)
	applicant_dob = db.Column(db.String(100), primary_key=False)
	applicant_location = db.Column(db.String(1000), primary_key=False)
	username = db.Column(db.String(100), nullable=False)

class Skill(db.Model):
	applicant_id = db.Column(db.String(100), primary_key=True)
	skill = db.Column(db.String(150), primary_key=True)
	
class Post(db.Model):
	post_id = db.Column(db.Integer(), primary_key=True)
	company_id = db.Column(db.String(), nullable=False)
	company_name = db.Column(db.String(100), nullable=False)
	job_type = db.Column(db.String(100), nullable=False)
	job_description = db.Column(db.String(1000), nullable=False)

class Application(db.Model):
	applicant_id = db.Column(db.String(100), primary_key=True)
	post_id = db.Column(db.String(100), primary_key=True)
	company_id = db.Column(db.String(100), nullable=False)

	





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
			session['user_type'] = usertype

			return redirect(url_for('configure', user_type=usertype))
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
				session['usertype'] = user.usertype
				if(user.usertype=='company'):
					if(not Company.query.filter_by(username = username).first()):
						return redirect(url_for('configure', user_type=user.usertype))
				else:
					if(not Applicant.query.filter_by(username = username).first()):
						return redirect(url_for('configure', user_type=user.usertype))
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
		user = User.query.filter_by(username = session['user']).first()
		if user.usertype == 'company':
			company = Company.query.filter_by(username = session['user']).first()
			company = company.__dict__
			return render_template('company.html', app_data=app_data, company=company)
		else:
			applicant = Applicant.query.filter_by(username = session['user']).first()
			applicant = applicant.__dict__
			return render_template('applicant.html', app_data=app_data, applicant=applicant)
	else:
		return redirect(url_for('login'))

@app.route('/configure/<user_type>', methods=['GET', 'POST'])  
def configure(user_type):
	if user_type == 'company' and user_type==session['usertype']:
		if(not Company.query.filter_by(username = session['user']).first()):
			if request.method != 'POST':
				ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
				now = datetime.now()
				date = now.strftime("%Y%m%d%H%M%S")

				company_id = ''.join(ip.split('.')) + date;

				print(session['user'])

				return render_template('configure_company.html', app_data=app_data, company_id=company_id, username=session['user'])
			else:
				company_name = request.form['company_name']
				company_type = request.form['company_type']
				company_vacancies = request.form['company_vacancies']
				company_id = request.form['company_id']
				company_email = request.form['company_email']


				new_company = Company(company_id=company_id, username=session['user'],company_email=company_email, company_vacancies=int(company_vacancies), company_name=company_name, company_type=company_type)
				
				db.session.add(new_company)
				db.session.commit()

				print(company_name, company_type, company_vacancies)
				return redirect(url_for('account'))
		else:
			return redirect(url_for('account'))

	if user_type == 'applicant' and user_type==session['usertype']:
		if(not Applicant.query.filter_by(username = session['user']).first()):
			if request.method != 'POST':
				ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
				now = datetime.now()
				date = now.strftime("%Y%m%d%H%M%S")
				applicant_id = 'U' + ''.join(ip.split('.')) + date;
				return render_template('configure_user.html', app_data=app_data, applicant_id=applicant_id, username=session['user'])
			else:
				applicantobj = {
					'applicant_name' : request.form['applicant_name'],
					'applicant_email' : request.form['applicant_email'],
					'applicant_number' : request.form['applicant_number'],
					'applicant_dob' : request.form['applicant_dob'],
					'applicant_location' : request.form['applicant_location'],
					'applicant_id' : request.form['applicant_id']
				}

				print(applicantobj)

				new_applicant = Applicant(applicant_id=applicantobj['applicant_id'], applicant_email=applicantobj['applicant_email'], applicant_number=applicantobj['applicant_number'], applicant_dob=applicantobj['applicant_dob'], applicant_location=applicantobj['applicant_location'], username=session['user'])
				
				db.session.add(new_applicant)
				db.session.commit()

				return redirect(url_for('account'))
		else:	
			return redirect(url_for('account'))
	else:
		return redirect(url_for('home'))

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
	if request.method == 'GET':
		if 'user' in session:
			if session['usertype'] == 'company':
				company = Company.query.filter_by(username = session['user']).first().__dict__
				return render_template('newpost.html', app_data=app_data, company=company)		
			else:
				return 'begone bitch you a peasant'
		else:
			return redirect(url_for('login'))
	else:
		print(request.form['companyid'])
		now = datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		new_post = Post(post_id=timestamp ,company_id=request.form['companyid'], company_name=request.form['companyname'], job_type=request.form['job_type'], job_description=request.form['job_description'])			
		db.session.add(new_post)
		db.session.commit()
		
		return redirect(url_for('home'))

	



@app.route('/findjob', methods=['GET', 'POST'])
def findjob():
	posts = Post.query.filter_by().all()
	all_post = []
	for post in posts:
		temp = post.__dict__
		del temp['_sa_instance_state']
		company = Company.query.filter_by(company_id = temp['company_id']).first().__dict__
		temp['company_email'] = company['company_email']

		all_post.append(temp)
	print(all_post)
	all_post.reverse()

	return render_template('findjob.html', app_data=app_data, posts=all_post )

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