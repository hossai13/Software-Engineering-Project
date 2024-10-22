from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your secret key'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'Jubayads-MacBook-Pro.local'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Minecraft100'
app.config['MYSQL_DB'] = 'Testing'

# Initialize MySQL
mysql = MySQL(app)

# Route for the homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route for the menu page
@app.route('/menu')
def menu():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Menu")  # Assuming you have a Menu table
    menu_items = cursor.fetchall()
    return render_template('menu.html', menu_items=menu_items)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # Debugging form data
        print("Form Data:", request.form)

        if 'Username' in request.form and 'Email' in request.form and 'Password' in request.form:
            username = request.form['Username']  # Corrected variable to match form input
            email = request.form['Email']
            password = request.form['Password']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check if account exists (using correct case for 'Email')
            cursor.execute('SELECT * FROM Login WHERE Email = %s', (email,))
            account = cursor.fetchone()
            print("Account Check:", account)  # Check if an account was found

            if account:
                msg = 'Account already exists!'
            elif not validate_email(email):
                msg = 'Invalid email address!'
            elif not email or not password:
                msg = 'Please fill out the form!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            else:
                cursor.execute('INSERT INTO Login (Username, Password, Email) VALUES (%s, %s, %s)', (username, password, email))
                mysql.connection.commit()
                print("Insert executed")  # Check if the insert was executed
                msg = 'You have successfully registered!'
        else:
            msg = 'Please fill out the form!'
    return render_template('registration_form.html', msg=msg)

# Email validation function
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
