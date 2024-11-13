from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import re

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your secret key'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'Jubayads-MacBook-Pro.local'  
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Minecraft100'
app.config['MYSQL_DB'] = 'PizzaInfo'

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
            date_made = request.form['DateMade']

            try:
                cursor = mysql.connection.cursor()
                cursor.execute('''INSERT INTO reviews (username, rating, review_text, date_made)
                                  VALUES (%s, %s, %s, %s)''',
                               (username, rating, review_text, date_made))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('userhomepage'))

            except Exception as error:
                print(f"Error: {error}")
                return "There was an error submitting your review."
            
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT username, rating, review_text, date_made FROM reviews ORDER BY date_made DESC')
        reviews = cursor.fetchall()
        cursor.close()

        return render_template('userhomepage.html', username=session['username'], user_id=session['id'], current_date=current_date, reviews=reviews)
    else:
        return redirect(url_for('login'))

# Route for the menu page
@app.route('/menu')
def menu():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT DISTINCT itemName, itemPrice FROM Menu WHERE itemCategory = 'Pizza' ORDER BY itemName")
    menu_items = cursor.fetchall()
    # this is for deleting the menu items
    if 'loggedin' in session and session.get('is_admin'):
        if request.method == 'POST' and 'delete=name' in request.form:
            item_name = request.form['delete=name']
            cursor.execute('DELETE FROM Menu WHERE itemName = %s', (item_name,))
            mysql.connection.commit()
            return redirect(url_for('menu'))
        if request.method == 'POST' and 'add-item' in request.form and 'add-price' in request.form and 'add-category' in request.form:
            item_name = request.form['add-item']
            item_price = request.form['add-price']
            item_category = request.form['add-category']
            cursor.execute('INSERT INTO Menu (itemName, itemPrice, itemCategory) VALUES (%s, %s, %s)', (item_name, item_price, item_category))
            mysql.connection.commit()
            return redirect(url_for('menu'))
        if request.method == 'POST' and 'update_item' in request.form:
            item_name = request.form['update_item']
            item_price = request.form['update_price']
            cursor.execute('UPDATE Menu SET itemPrice = %s WHERE itemName = %s', (item_price, item_name))
            mysql.connection.commit()
            return redirect(url_for('menu'))
        if request.method == 'POST' and 'special-name' in request.form and 'special-percent' in request.form:
            special_name = request.form['special-name']
            special_percent = request.form['special-percent']
            cursor.execute('UPDATE Menu SET itemPrice = itemPrice * %s WHERE itemName = %s', (1 - float(special_percent) / 100, special_name))
            

            return redirect(url_for('menu'))
    
    return render_template('menu.html', menu_items=menu_items)      


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
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM UserInfo WHERE LoginID = %s', (session['id'],))
        account = cursor.fetchone()

        if 'UsernameChange' in request.form and 'PasswordChange' not in request.form:
            username = request.form['UsernameChange']
            cursor.execute('UPDATE UserInfo SET Username = %s WHERE LoginID = %s', (username, session['id']))
            mysql.connection.commit()
            msg = 'Username updated successfully!'

        if 'PasswordChange' in request.form and 'UsernameChange' not in request.form:
            password = request.form['PasswordChange']
            cursor.execute('UPDATE UserInfo SET Password = %s WHERE LoginID = %s', (password, session['id']))
            mysql.connection.commit()
            msg = 'Password updated successfully!'
        
        # Check if the logged-in user is an admin
        is_admin = account['isAdmin']
        
        return render_template('profile.html', account=account, msg=msg, is_admin=is_admin)
    else:
        return redirect(url_for('login'))
    
@app.route('/admprofile', methods=['GET', 'POST'])
def admprofile():
    if 'loggedin' in session and session.get('is_admin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Handle account deletion if requested
        if request.method == 'POST' and 'delete_account' in request.form:
            user_id = request.form['delete_account']
            cursor.execute('DELETE FROM UserInfo WHERE LoginID = %s', (user_id,))
            mysql.connection.commit()

        # Fetch all user accounts
        cursor.execute('SELECT LoginID, Username, Email, isAdmin FROM UserInfo')
        accounts = cursor.fetchall()

        return render_template('admprofile.html', accounts=accounts)
    else:
        return redirect(url_for('login'))



# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
