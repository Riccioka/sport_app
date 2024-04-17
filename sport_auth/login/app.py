# # Store this code in 'app.py' file
#
# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_sqlalchemy import SQLAlchemy
# import re
#
# app = Flask(__name__)
#
# app.secret_key = 'qwerty'
#
# # Update the configuration for PostgreSQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pilot@localhost/sport_auth'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)
#
# class Account(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), nullable=False, unique=True)
#     password = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(50), nullable=False, unique=True)
#
#
# db.Model.metadata.reflect(db.engine)
#
# # Initialize the database
# # db.create_all()
#
# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         account = Account.query.filter_by(username=username, password=password).first()
#         if account:
#             session['loggedin'] = True
#             session['id'] = account.id
#             session['username'] = account.username
#             msg = 'Logged in successfully!'
#             return render_template('index.html', msg=msg)
#         else:
#             msg = 'Incorrect username / password!'
#     return render_template('login.html', msg=msg)
#
# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#         account_exist = Account.query.filter_by(username=username).first()
#         if account_exist:
#             msg = 'Account already exists!'
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = 'Invalid email address!'
#         elif not re.match(r'[A-Za-z0-9]+', username):
#             msg = 'Username must contain only characters and numbers!'
#         elif not username or not password or not email:
#             msg = 'Please fill out the form!'
#         else:
#             new_account = Account(username=username, password=password, email=email)
#             db.session.add(new_account)
#             db.session.commit()
#             msg = 'You have successfully registered!'
#     elif request.method == 'POST':
#         msg = 'Please fill out the form!'
#     return render_template('register.html', msg=msg)
#
# if __name__ == '__main__':
#     app.run(debug=True)
#


#
#
#
#
# from flask import Flask, render_template, request, redirect, url_for, session
# from sqlalchemy.sql import text
# import psycopg2
#
# app = Flask(__name__)
#
# conn = psycopg2.connect(database="sport_auth", user="postgres",
# 						password="pilot", host="localhost", port="5432")
#
# # create a cursor
# cur = conn.cursor()
#
# # if you already have any table or not id doesnt matter this
# # will create a products table for you.
# cur.execute(
# 	'''CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, username varchar(50),
# 	 password varchar(255), email varchar(100));''')
#
# # commit the changes
# conn.commit()
#
# # close the cursor and connection
# cur.close()
# conn.close()
#
# @app.route('/')
# @app.route('/login', methods =['GET', 'POST'])
# def login():
# 	msg = ''
#
#     conn = psycopg2.connect(database="sport",
#                             user="postgres",
#                             password="pilot",
#                             host="localhost", port="5432")
#
# 	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
# 		username = request.form['username']
# 		password = request.form['password']
#         cur = conn.cursor()
# 		cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
#         conn.commit()
# 		account = cur.fetchone()
#
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['id']
#             session['username'] = account['username']
#             msg = 'Logged in successfully !'
#             return render_template('index.html', msg = msg)
#         else:
#             msg = 'Incorrect username / password !'
#
# 	return render_template('login.html', msg = msg)
# #
# @app.route('/')
# def index():
# 	# Connect to the database
# 	conn = psycopg2.connect(database="sport",
# 							user="postgres",
# 							password="pilot",
# 							host="localhost", port="5432")
#
# 	# create a cursor
# 	cur = conn.cursor()
#
# 	# Select all products from the table
# 	cur.execute('''SELECT * FROM person''')
#
# 	# Fetch the data
# 	data = cur.fetchall()
#
# 	# close the cursor and connection
# 	cur.close()
# 	conn.close()
#
# 	return render_template('index.html', data=data)
#
#
# @app.route('/create', methods=['POST'])
# def create():
# 	conn = psycopg2.connect(database="sport",
# 							user="postgres",
# 							password="pilot",
# 							host="localhost", port="5432")
#
# 	cur = conn.cursor()
#
# 	# Get the data from the form
# 	firstname = request.form.get('firstname')
# 	lastname = request.form.get('lastname')
# 	email = request.form.get('email')
# 	age = request.form.get('age')
#
# 	# Insert the data into the table
# 	cur.execute(
# 		'''INSERT INTO person (firstname, lastname, email, age) VALUES (%s, %s, %s, %s)''',
# 		(firstname, lastname, email, age))
#
# 	# commit the changes
# 	conn.commit()
#
# 	# close the cursor and connection
# 	cur.close()
# 	conn.close()
#
# 	return redirect(url_for('index'))
#
#
# @app.route('/update', methods=['POST'])
# def update():
# 	conn = psycopg2.connect(database="sport",
# 							user="postgres",
# 							password="pilot",
# 							host="localhost", port="5432")
#
# 	cur = conn.cursor()
#
# 	# Get the data from the form
# 	firstname = request.form['firstname']
# 	lastname = request.form['lastname']
# 	email = request.form['email']
# 	age = request.form['age']
# 	id = request.form['id']
#
# 	# Update the data in the table
# 	cur.execute(
# 		'''UPDATE person SET firstname=%s, lastname=%s, email=%s,	age=%s WHERE id=%s''',
# 		(firstname, lastname, email, age, id))
#
# 	# commit the changes
# 	conn.commit()
# 	return redirect(url_for('index'))
#
#
#
# if __name__ == '__main__':
# 	app.run(debug=True)
#
#




from flask import Flask, render_template, request, redirect, url_for, session
import re
import psycopg2

app = Flask(__name__)

app.secret_key = 'qwerty'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pilot@localhost:5432/sport_auth'

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']

		conn = psycopg2.connect(database="sport", user="postgres",
								password="pilot", host="localhost", port="5432")
		cur = conn.cursor()
		cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
		account = cur.fetchone()

		if account:
			session['loggedin'] = True
			session['id'] = account.id
			session['username'] = account.username
			msg = 'Logged in successfully !'
			return render_template('index.html', msg=msg)
		else:
			msg = 'Incorrect username / password'
	return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']

		conn = psycopg2.connect(database="sport", user="postgres",
								password="pilot", host="localhost", port="5432")
		cur = conn.cursor()
		cur.execute('SELECT * FROM accounts WHERE username = % s', (username,))
		account = cur.fetchone()

		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cur.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
			cur.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg=msg)


if __name__ == '__main__':
	app.run(debug=True)