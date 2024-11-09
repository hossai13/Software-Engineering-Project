import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your secret key'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'PizzaInfo'

# Initialize MySQL
mysql = MySQL(app)

# Route for the homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

#Route for the user homepage
@app.route('/userhomepage')
def userhomepage():
    if isAdmin():
        return redirect(url_for('admProfile'))
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
        msg = 'Please log in to access your homepage.'
        return redirect(url_for('login'))
    
# route for the admin homepage
@app.route('/adminhomepage')
def adminhomepage():
    if isAdmin():
        return render_template('admhomepage.html')
    else:
        return redirect(url_for('homepage'))

# Route for the menu page
@app.route('/menu')
def menu():
    if isAdmin():
        return redirect(url_for('admMenu'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT itemID, itemName, itemPrice FROM Menu")  # Assuming you have a Menu table
    menu_items = cursor.fetchall()
    return render_template('menu.html', menu_items=menu_items)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # Debugging form data
        print("Form Data:", request.form)

        if 'Username' in request.form and 'Email' in request.form and 'Password' in request.form and 'ConfirmPassword' in request.form:
            username = request.form['Username']  # Corrected variable to match form input
            email = request.form['Email']
            password = request.form['Password']
            admin = "False"
            confirm_password = request.form['ConfirmPassword']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check if account exists (using correct case for 'Email')
            cursor.execute('SELECT * FROM UserInfo WHERE Email = %s', (email,))
            account = cursor.fetchone()
            print("Account Check:", account)  # Check if an account was found

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
                cursor.execute('INSERT INTO UserInfo (Username, Password, Email, isAdmin) VALUES (%s, %s, %s, %s)', (username, password, email, admin))
                mysql.connection.commit()
                print("Insert executed")  # Check if the insert was executed
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    return render_template('registration_form.html', msg=msg)

# Email validation function
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# route for the Login
@app.route('/login', methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST':
        # Debugging form data
        print("Form Data:", request.form)

        if 'Username' in request.form and 'Password' in request.form and 'Email' in request.form:
            username = request.form['Username']
            password = request.form['Password']
            email = request.form['Email']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM UserInfo WHERE Username = %s AND Password = %s AND Email = %s', (username, password, email))
            account = cursor.fetchone()
            print("Account Check:", account)

            if account:
                session['loggedin'] = True
                session['id'] = account['LoginID']
                session['username'] = account['Username']
                msg = 'Logged in successfully!'
                return redirect(url_for('profile'))
            else:
                msg = 'Incorrect username/password/email!'
        else:
            msg = 'Please fill out the form'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# Route for profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    msg = ''
    if isAdmin():
        return redirect(url_for('admProfile'))
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM UserInfo WHERE LoginID = %s', (session['id'],))
        account = cursor.fetchone()
        print("Account Check:", account)
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
    else:
        return redirect(url_for('login'))
    return render_template('profile.html', account=account, msg=msg)

# Route for admin profile page
@app.route('/admProfile', methods=['GET', 'POST']) 
def admProfile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Username, Email FROM UserInfo")
    accounts = cursor.fetchall()
    ## this is for the admin to delete a user
    if 'usernameDelete' in request.form and 'emailDelete' in request.form:
        username = request.form['usernameDelete']
        email = request.form['emailDelete']
        cursor.execute('DELETE FROM UserInfo WHERE Username = %s AND Email = %s', (username, email))
        mysql.connection.commit()
        return redirect(url_for('admProfile'))
    return render_template('admProfile.html', accounts=accounts)

    



# Route for the admin menu page
@app.route('/admMenu', methods=['GET', 'POST'])
def admMenu():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Menu")
    menu_items = cursor.fetchall()
    ## this is for the admin to delete a menu item
    if 'itemName' in request.form:    
        itemName = request.form['itemName']
        cursor.execute('DELETE FROM Menu WHERE itemID = %s', (itemName,))
        mysql.connection.commit()
        return redirect(url_for('admMenu'))
    ## this is for the admin to add a menu item
    if 'itemName' in request.form and 'itemPrice' in request.form:
        itemName = request.form['itemName']
        itemPrice = request.form['itemPrice']
        cursor.execute('INSERT INTO Menu (itemName, itemPrice) VALUES (%s, %s)', (itemName, itemPrice))
        mysql.connection.commit()
        return redirect(url_for('admMenu'))
    ## this is for the admin to update a menu item  
    if 'itemName' in request.form and 'itemPrice' in request.form:
        itemName = request.form['itemName']
        itemPrice = request.form['itemPrice']
        cursor.execute('UPDATE Menu SET itemName = %s, itemPrice = %s WHERE itemID = %s', (itemName, itemPrice, id))
        mysql.connection.commit()
        return redirect(url_for('admMenu'))
    
    return render_template('admMenu.html', menu_items=menu_items)


# this is to check if the user is an admin
def isAdmin():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT isAdmin FROM UserInfo WHERE LoginID = %s', (session['id'],))
    admin = cursor.fetchone()
    if admin and admin['isAdmin'] == "True":
        return True
    else:
        return False    
    

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
