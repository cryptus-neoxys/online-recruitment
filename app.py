#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date

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
	company_id = db.Column(db.String(), primary_key=True)
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
				if(len(user.userdata) == 0):
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
		print(user.username)
		print(user.usertype)
		print(type(user.userdata))  # []
		for row in user.userdata:
			print(row)

		if(user.usertype == 'company'):
			# print(dict(user.userdata))
			# company_name = user.userdata.company_name
			# company_id = user.userdata.company_id
			# company_vacancies = user.userdata.company_vacancies
			# company_type = user.userdata.company_type
			# company_email = user.userdata.company_email

			# company_data = {
			# 	"company_name" : user.userdata.company_name,
			# 	"company_id" : user.userdata.company_id,
			# 	"company_vacancies" : user.userdata.company_vacancies,
			# 	"company_type" : user.userdata.company_type,
			# 	"company_email" : user.userdata.company_email			
			# }
			return render_template('company.html', app_data=app_data, username=session['user'])
	else:
		return redirect(url_for('login'))

@app.route('/configure/<user_type>', methods=['GET', 'POST'])  
def configure(user_type):  
	if user_type == 'company':
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

	elif user_type == 'user':
		return 'configure_user'
	else:
		return redirect(url_for('home'))

# @app.route('/cofigure/<user_type>')
# def configure(user_type):
# 	print(user_type)
# 	if user_type == 'company':
# 		return 'configure_company'
# 	elif usertype == 'user':
# 		return 'configure_user'
# 	else:
# 		return redirect(url_for('home'))
	





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