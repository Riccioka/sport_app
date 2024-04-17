from flask import Flask, render_template, request, redirect, url_for, session
import re
import psycopg2

app = Flask(__name__)

app.secret_key = 'qwerty'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pilot@localhost:5432/sport_auth'

conn = psycopg2.connect(database="sport_auth", user="postgres",
						password="pilot", host="localhost", port="5432")
cur = conn.cursor()
cur.execute("SELECT * FROM users")

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        conn = psycopg2.connect(database="sport_auth", user="postgres",
                                password="pilot", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        users = cur.fetchall()

        if users:
            session['loggedin'] = True
            session['id'] = users[0][0]
            session['username'] = users[0][1]
            session['name'] = users[0][4]
            session['surname'] = users[0][5]
            msg = 'Logged in successfully !'
            user_id = session.get('id')

            conn = psycopg2.connect(database="sport_auth", user="postgres",
									password="pilot", host="localhost", port="5432")
            cur = conn.cursor()
            cur.execute('SELECT age, height, weight FROM users WHERE id = %s', (user_id,))
            user_data = cur.fetchone()
            conn.close()

            if user_data:
                age, height, weight = user_data

            return render_template('index.html', msg=msg, age=age, height=height, weight=weight)
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

		conn = psycopg2.connect(database="sport_auth", user="postgres",
								password="pilot", host="localhost", port="5432")
		cur = conn.cursor()
		cur.execute('SELECT * FROM users WHERE username = %s', (username,))
		user = cur.fetchone()

		cur.execute('SELECT * FROM users WHERE email = %s', (email,))
		exist_email = cur.fetchone()

		if user or exist_email:
			msg = 'User already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cur.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email,))
			conn.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg=msg)


@app.route('/lk', methods=['GET', 'POST'])
def lk():
	msg = ''
	user_id = session.get('id')

	conn = psycopg2.connect(database="sport_auth", user="postgres",
							password="pilot", host="localhost", port="5432")
	cur = conn.cursor()
	cur.execute('SELECT age, height, weight FROM users WHERE id = %s', (user_id,))
	user_data = cur.fetchone()
	conn.close()

	if user_data:
		age, height, weight = user_data
	else:
		age, height, weight = None, None, None

	if request.method == 'POST' and 'age' in request.form and 'height' in request.form and 'weight' in request.form:
		age = request.form['age']
		height = request.form['height']
		weight = request.form['weight']

		conn = psycopg2.connect(database="sport_auth", user="postgres",
								password="pilot", host="localhost", port="5432")
		cur = conn.cursor()

		cur.execute('UPDATE users SET age = %s, height = %s, weight = %s WHERE id = %s', (age, height, weight, user_id,))

		# cur.execute('UPDATE users  (age, height, weight) VALUES (%s, %s, %s)', (age, height, weight,))
		conn.commit()
		msg = 'Success'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('index.html', msg=msg, age=age, height=height, weight=weight)


@app.route('/edit_person_data', methods=['GET', 'POST'])
def edit_person_data():
    msg = ''
    user_id = session.get('id')

    conn = psycopg2.connect(database="sport_auth", user="postgres",
                            password="pilot", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('SELECT age, height, weight FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    conn.close()

    if not user_data:
        return 'User data not found', 404

    age, height, weight = user_data

    if request.method == 'POST':
        age_form = request.form.get('age')
        height_form = request.form.get('height')
        weight_form = request.form.get('weight')

        if not age_form or not height_form or not weight_form:
            msg = 'Please fill out the form !'
        else:
            try:
                age = int(age_form)
                height = int(height_form)
                weight = int(weight_form)

                if age < 14 or age > 120:
                    msg = 'Incorrect age'
                elif height < 50 or height > 272:
                    msg = 'Invalid height'
                elif weight < 10 or weight > 650:
                    msg = 'Invalid weight'
                else:
                    conn = psycopg2.connect(database="sport_auth", user="postgres",
                                            password="pilot", host="localhost", port="5432")
                    cur = conn.cursor()
                    cur.execute('UPDATE users SET age = %s, height = %s, weight = %s WHERE id = %s',
                                (age, height, weight, user_id,))
                    conn.commit()
                    msg = 'Success'
            except ValueError:
                msg = 'Invalid input format. Age, height, and weight must be integers.'

    return render_template('edit.html', msg=msg, age=age, height=height, weight=weight)


if __name__ == '__main__':
    app.run(debug=True)
