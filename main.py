from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re

app = Flask(__name__)

# File upload configuration
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Secret key for session management
app.secret_key = 'your secret key'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'PizzaInfo'

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Initialize MySQL
mysql = MySQL(app)

# Route for the homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route for the user homepage/restaurant reviews
@app.route('/userhomepage', methods=['GET', 'POST'])
def userhomepage():
    if 'loggedin' in session:
        current_date = datetime.now().strftime('%Y-%m-%d')
        if request.method == 'POST':
            username = request.form['name']
            rating = request.form['rating']
            review_text = request.form['review']
            header = request.form['header']
            date_made = request.form['DateMade']
            photo = request.files['photo']

            photo_filename = None
            if photo and allowed_file(photo.filename):
                photo_filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

            try:
                cursor = mysql.connection.cursor()
                cursor.execute('''INSERT INTO reviews (username, rating, review_text, header, date_made, photo)
                                  VALUES (%s, %s, %s, %s, %s, %s)''',
                               (username, rating, review_text, header, date_made, photo_filename))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('userhomepage'))
            except Exception as error:
                print(f"Error: {error}")
                return "There was an error submitting your review."
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT username, rating, review_text, header, date_made, photo FROM reviews ORDER BY date_made DESC')
        reviews = cursor.fetchall()
        cursor.close()

        return render_template('userhomepage.html', username=session['username'], user_id=session['id'], current_date=current_date, reviews=reviews)
    else:
        return redirect(url_for('login'))

# Route for the menu page
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT DISTINCT itemName, itemCategory, itemPrice FROM Menu ORDER BY itemName")
    all_menu_items = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT itemName, itemPrice FROM Menu WHERE itemCategory = 'Pizza' ORDER BY itemName")
    menu_items = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT itemName, itemPrice FROM Menu WHERE itemCategory = 'Strombolis'")
    strombolis_items = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT itemName, itemPrice FROM Menu WHERE itemCategory = 'Sandwiches'")
    sandwiches_items = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT itemName, itemPrice FROM Menu WHERE itemCategory = 'Burgers'")
    burgers_items = cursor.fetchall()
    
    if is_admin():
    # this is for deleting the menu items
        if request.method == 'POST' and 'delete_menu' in request.form:
            menu_id = request.form['delete_menu']
            cursor.execute('DELETE FROM menu WHERE itemName = %s', (menu_id,))
            mysql.connection.commit()
        if request.method == 'POST' and 'addName' in request.form and 'addPrice' in request.form and 'addCategory' in request.form:
            item_name = request.form['addName']
            item_price = request.form['addPrice']
            item_category = request.form['addCategory']
            cursor.execute('INSERT INTO menu (itemName, itemPrice, itemCategory) VALUES (%s, %s, %s)', (item_name, item_price, item_category))
            mysql.connection.commit()
            return redirect(url_for('menu'))
        if request.method == 'POST' and 'editName' in request.form and 'updatePrice' in request.form:
            item_name = request.form['editName']
            item_price = request.form['updatePrice']
            cursor.execute('UPDATE Menu SET itemPrice = %s WHERE itemName = %s', (item_price, item_name))
            mysql.connection.commit()
            return redirect(url_for('menu'))
        if request.method == 'POST' and 'specialName' in request.form and 'specialPercent' in request.form:
            special_name = request.form['specialName']
            try:
                special_percent = int(request.form['specialPercent'])
                if special_percent < 0 or special_percent > 100:
                    return "Please enter a valid number for the discount percentage."
                special_percent = 1 - (special_percent / 100)
            except ValueError:
                return "Please enter a valid number for the discount percentage."
            
            print (special_percent)
            try:
                cursor.execute('UPDATE Menu SET itemPrice = itemPrice * %s WHERE itemName = %s', (special_percent, special_name))
                mysql.connection.commit()
            except Exception as error:
                mysql.connection.rollback()
                print(f"Databse Error: {error}")    
                return "There was an error updating the price."

            return redirect(url_for('menu'))
    if is_admin():
        return render_template('menu.html', 
                               all_menu_items=all_menu_items,
                               menu_items=menu_items,
                               strombolis_items=strombolis_items,
                               sandwiches_items=sandwiches_items,
                               burgers_items=burgers_items,
                               is_admin=is_admin())
    else:
        return render_template('menu.html',
                               all_menu_items=all_menu_items,
                               menu_items=menu_items,
                               strombolis_items=strombolis_items,
                               sandwiches_items=sandwiches_items,
                               burgers_items=burgers_items)  

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        print("Form Data:", request.form)

        if 'Username' in request.form and 'Email' in request.form and 'Password' in request.form and 'ConfirmPassword' in request.form:
            username = request.form['Username']
            email = request.form['Email']
            password = request.form['Password']
            confirm_password = request.form['ConfirmPassword']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT * FROM UserInfo WHERE Email = %s', (email,))
            account = cursor.fetchone()
            print("Account Check:", account)

            if account:
                msg = 'Account already exists!'
            elif not validate_email(email):
                msg = 'Invalid email address!'
            elif not email or not password:
                msg = 'Please fill out the form!'
            elif (password != confirm_password):
                msg = 'Passwords do not match!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            else:
                cursor.execute('INSERT INTO UserInfo (Username, Password, Email) VALUES (%s, %s, %s)', (username, password, email))
                mysql.connection.commit()
                print("Insert executed")
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
        else:
            msg = 'Please fill out the form!'
    return render_template('registration_form.html', msg=msg)

# Email validation function
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Route for the Login
@app.route('/login', methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST':
        print("Form Data:", request.form)

        if 'Username' in request.form and 'Password' in request.form:
            username = request.form['Username']
            password = request.form['Password']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM UserInfo WHERE Username = %s AND Password = %s', (username, password))
            account = cursor.fetchone()
            print("Account Check:", account)

            if account:
                session['loggedin'] = True
                session['id'] = account['LoginID']
                session['username'] = account['Username']
                msg = 'Logged in successfully!'
                if account['isAdmin']:
                    session['isAdmin'] = True
                return redirect(url_for('userhomepage'))
            else:
                msg = 'Incorrect username/password!'
        else:
            msg = 'Please fill out the form'
    return render_template('login.html', msg=msg)

# Route for logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('isAdmin', None)
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM UserInfo WHERE LoginID = %s', (session['id'],))
        account = cursor.fetchone()

        # Update username
        if 'UsernameChange' in request.form and 'PasswordChange' not in request.form:
            username = request.form['UsernameChange']
            cursor.execute('UPDATE UserInfo SET Username = %s WHERE LoginID = %s', (username, session['id']))
            mysql.connection.commit()
            msg = 'Username updated successfully!'

        # Update password
        if 'PasswordChange' in request.form and 'UsernameChange' not in request.form:
            password = request.form['PasswordChange']
            cursor.execute('UPDATE UserInfo SET Password = %s WHERE LoginID = %s', (password, session['id']))
            mysql.connection.commit()
            msg = 'Password updated successfully!'
        
        # Check if the logged-in user is an admin
        is_admin = account['isAdmin']
        
        # If admin, handle user management
        accounts = []
        if is_admin:
            # Handle account deletion if requested
            if 'delete_account' in request.form:
                user_id = request.form['delete_account']
                cursor.execute('DELETE FROM UserInfo WHERE LoginID = %s', (user_id,))
                mysql.connection.commit()
                msg = 'Account deleted successfully!'
            if is_owner():
                if 'make_admin' in request.form:
                    user_id = request.form['make_admin']
                    cursor.execute('UPDATE UserInfo SET isAdmin = 1 WHERE LoginID = %s', (user_id,))
                    mysql.connection.commit()
                    msg = 'Account promoted to admin!'
                if 'remove_admin' in request.form:
                    user_id = request.form['remove_admin']
                    cursor.execute('UPDATE UserInfo SET isAdmin = 0 WHERE LoginID = %s', (user_id,))
                    mysql.connection.commit()
                    msg = 'Admin status removed!'
            # Fetch all user accounts
            cursor.execute('SELECT * FROM UserInfo')
            accounts = cursor.fetchall()
        
        return render_template('profile.html', account=account, msg=msg, is_admin=is_admin, accounts=accounts)
    else:
        return redirect(url_for('login'))

def is_admin():
    if 'isAdmin' in session:
        return True
    else:
        return False

# this is how we check if the user is the owner account where we check if the account has the same loginID as the owner account
def is_owner():
    if 'id' in session:
        return session['id'] == 1
    else:
        return False

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
