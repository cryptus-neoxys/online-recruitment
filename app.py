from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import json
from sqlalchemy.orm import sessionmaker

DEVELOPMENT_ENV  = True

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.config['SECRET_KEY'] = 'testkey'

db = SQLAlchemy(app)

class User(db.Model):
   username = db.Column(db.String(100), primary_key=True)
   name = db.Column(db.String(100), nullable=False)
   password = db.Column(db.String(100), nullable=False)
   user_type = db.Column(db.String(100), nullable=False)

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

class Post(db.Model):
	post_id = db.Column(db.Integer(), primary_key=True)
	company_id = db.Column(db.String(), nullable=False)
	company_name = db.Column(db.String(100), nullable=False)
	job_type = db.Column(db.String(100), nullable=False)
	job_description = db.Column(db.String(1000), nullable=False)
	post_time = db.Column(db.Date(), nullable=False)

class Application(db.Model):
	applicant_id = db.Column(db.String(100), primary_key=True)
	post_id = db.Column(db.String(100), primary_key=True)
	company_id = db.Column(db.String(100), nullable=False)
	applicant_skill = db.Column(db.String(1000), nullable=False)
	application_time = db.Column(db.Date(), nullable=False)
	application_status = db.Column(db.String(100), nullable=False, default='pending')

class Offer_Letter(db.Model):
	offer_id = db.Column(db.String(100), primary_key=True)
	company_id = db.Column(db.String(100), nullable=False)
	applicant_id = db.Column(db.String(100), nullable=False)
	offer_date = db.Column(db.Date(), nullable=False)
	package = db.Column(db.Integer(), nullable=False)
	details = db.Column(db.String(1000), nullable=False)
	
db.create_all()



app_data = {
    "name":         "Recruitment",
    "description":  "Job Recruitment Portal",
    "author":       "Dev Sharma",
    "html_title":   "Recruitment",
    "project_name": "Recruitment",
    "keywords":     "",
    "end-point" : "https://127.0.0.1:5000"
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
			user_type = request.form['user_type']
			new_user = User(username=username, password=password, name=name, user_type=user_type)
			
			db.session.add(new_user)
			db.session.commit()

			session['user'] = username
			session['user_type'] = user_type
			return redirect(url_for('configure', user_type=user_type))
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
				session['user_type'] = user.user_type
				if(user.user_type=='company'):
					if(not Company.query.filter_by(username = username).first()):
						return redirect(url_for('configure', user_type=user.user_type))
				else:
					if(not Applicant.query.filter_by(username = username).first()):
						return redirect(url_for('configure', user_type=user.user_type))
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
		if user.user_type == 'company':
			company = Company.query.filter_by(username = session['user']).first()
			company = company.__dict__
			applications = Application.query.filter_by(company_id = company['company_id']).all()
			all_application = []
			hired = []
			rejected = []
			for application in applications:
				
				application = application.__dict__
				
				applicant = Applicant.query.filter_by(applicant_id = application['applicant_id']).first().__dict__
				user = User.query.filter_by(username = applicant['username']).first().__dict__

				application['applicant'] = applicant
				applicant['applicant_name'] = user['name']
				del application['_sa_instance_state']
				del application['applicant']['_sa_instance_state']
				application['application_time'] = application['application_time'].strftime('%m/%d/%Y')
				# del applicant['_sa_instance_state']
				# del applicant['applicant']['_sa_instance_state']
				print(application)
				if application['application_status'] == 'reject':
					rejected.append(application)
				elif application['application_status'] == 'hire':
					hired.append(application)
				else:
					all_application.append(application)

			print(all_application)
			return render_template('company.html', app_data=app_data, company=company, applications=all_application, rejected=rejected, hired=hired)
		else:
			applicant = Applicant.query.filter_by(username = session['user']).first()
			applicant = applicant.__dict__
			applications = Application.query.filter_by(applicant_id = applicant['applicant_id']).all()
			all_application = []
			for application in applications:
				
				application = application.__dict__

				company = Company.query.filter_by(company_id = application['company_id']).first().__dict__
				
				application['company'] = company
				
				all_application.append(application)

			
			return render_template('applicant.html', app_data=app_data, applicant=applicant, applications=all_application)
	else:
		return redirect(url_for('login'))

@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
	user = User.query.filter_by(username =username).first()
	if user:
		user = user.__dict__
		if user['user_type'] == 'company':
			user_data = Company.query.filter_by(username= username).first().__dict__
		else:
			user_data = Applicant.query.filter_by(username= username).first().__dict__
			user_data['applicant_name'] = user['name']
		print(user_data)
		return render_template('user.html', app_data=app_data, user_type=user['user_type'], user_data=user_data)
	else:
		flash('No such user found', 'error')
		return render_template('home.html', app_data=app_data)

@app.route('/configure/<user_type>', methods=['GET', 'POST'])  
def configure(user_type):
	if user_type == 'company' and user_type==session['user_type']:
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

	if user_type == 'applicant' and user_type==session['user_type']:
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
			if session['user_type'] == 'company':
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

		print(request.form['post_time'])

		dateobj = datetime.strptime(request.form['post_time'],'%Y-%m-%dT%H:%M:%S.%fZ')

		new_post = Post(post_id=timestamp, post_time=dateobj, company_id=request.form['companyid'], company_name=request.form['companyname'], job_type=request.form['job_type'], job_description=request.form['job_description'])			
		db.session.add(new_post)
		db.session.commit()
		
		return redirect(url_for('home'))

	
@app.route('/applyjob', methods=['GET', 'POST'])
def applyjob():
	if request.method == "POST":
		if 'user' in session:

			data = request.get_data()	
			data = data.decode("utf-8")
			data = json.loads(data)
			print("APPLY JOB")
			print(data)
			applicant = Applicant.query.filter_by(username = session['user']).first().__dict__

			data['applicant_id'] = applicant['applicant_id']
			dateobj = datetime.strptime(data['application']['time'],'%Y-%m-%dT%H:%M:%S.%fZ')			
			
			# applicant_id = db.Column(db.String(100), primary_key=True)
			# post_id = db.Column(db.String(100), primary_key=True)
			# company_id = db.Column(db.String(100), nullable=False)
			# applicant_skill = db.Column(db.Text(), nullable=False)
			# application_time = db.Column(db.Date(), nullable=False)

			new_application = Application(applicant_id=data['applicant_id'], post_id=data['application']['post_id'], company_id=data['application']['company_id'], applicant_skill=data['application']['skills'], application_time=dateobj)
			
			db.session.add(new_application)
			db.session.commit()

			return 'success'
			
@app.route('/application_action', methods=['GET', 'POST'])
def application_action():
	if request.method == 'POST':
		data = request.get_data()	
		data = data.decode("utf-8")
		data = json.loads(data)
		print(data)
		res = db.session.query(Application).filter(Application.post_id == data['applicant']['post_id'], Application.applicant_id == data['applicant']['applicant_id']).update({Application.application_status : data['action']},  synchronize_session = False)
		db.session.commit()
		print(res)
		return 'success'


@app.route('/findjob', methods=['GET', 'POST'])
def findjob():

	username = session['user']

	print(username)

	applicant = Applicant.query.filter_by(username = username).first().__dict__

	applicant_id = applicant['applicant_id']
	all_applied = []
	all_application = Application.query.filter_by(applicant_id=applicant_id).all()
	for application in all_application:
		all_applied.append(application.__dict__['post_id'])

	print(all_applied)

	# print(all_application)	

	posts = Post.query.filter_by().all()
	all_post = []
	for post in posts:
		temp = post.__dict__
		del temp['_sa_instance_state']
		company = Company.query.filter_by(company_id = temp['company_id']).first().__dict__
		temp['company_email'] = company['company_email']
		temp['post_time'] = temp['post_time'].strftime("%Y-%m-%d")
		if (str(temp['post_id']) not in all_applied):
			all_post.append(temp)
	

	all_post.reverse()

	return render_template('findjob.html', app_data=app_data, posts=all_post )

@app.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
	if 'user_type' in session:
		session.pop('user_type', None)
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