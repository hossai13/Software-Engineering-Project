import math
from io import BytesIO
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session, Response
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
app.config['MYSQL_PASSWORD'] = 'root1234'
app.config['MYSQL_DB'] = 'PizzaInfo'

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Initialize MySQL
mysql = MySQL(app)

# Route for the homepage
@app.route('/')
def homepage():
    rating_filter = request.args.get('rating') 
    cursor = mysql.connection.cursor()
    if rating_filter:
        cursor.execute("SELECT header, review_text, username, rating, date_made, photo FROM reviews WHERE rating = %s ORDER BY date_made DESC", [rating_filter])
    else:
        cursor.execute("SELECT header, review_text, username, rating, date_made, photo FROM reviews ORDER BY RAND() LIMIT 5")
    reviews = cursor.fetchall()
    cursor.close()
    return render_template('homepage.html', reviews=reviews, rating_filter=rating_filter)

# Route for the user homepage/restaurant reviews
@app.route('/userhomepage', methods=['GET', 'POST'])
def userhomepage():
    if 'loggedin' in session:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
        if request.method == 'POST':
            user_id = session.get('id')  
            if not isinstance(user_id, int):
                return "Error: Invalid user ID, it must be an integer."
            username = request.form['name']
            rating = request.form['rating']
            review_text = request.form['review']
            header = request.form['header']
            date_made = current_date  
            try:
                if not rating.isdigit():
                    raise ValueError("Rating must be an integer.")
                rating = int(rating) 
                photo = request.files['photo']  
                photo_data = None  
                if photo:
                    photo_data = photo.read() 
                    
                cursor = mysql.connection.cursor()
                cursor.execute('''INSERT INTO reviews (LoginID, username, rating, review_text, header, date_made, photo)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                               (user_id, username, rating, review_text, header, date_made, photo_data))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('userhomepage'))  

            except ValueError as e:
                print(f"Error: {e}")
                return f"Error: {e}"
            except Exception as error:
                print(f"Error: {error}")
                return "There was an error submitting your review."
        
        star_filter = request.args.get('star_rating')  
        view_my_reviews = request.args.get('my_reviews')  
        cursor = mysql.connection.cursor()
        if view_my_reviews: 
            cursor.execute('''SELECT review_id, username, rating, review_text, header, date_made, photo 
                              FROM reviews 
                              WHERE LoginID = %s 
                              ORDER BY date_made DESC''', (session['id'],))
        elif star_filter:  
            cursor.execute('''SELECT review_id, username, rating, review_text, header, date_made, photo 
                              FROM reviews 
                              WHERE rating = %s 
                              ORDER BY date_made DESC''', (star_filter,))
        else:  
            cursor.execute('''SELECT review_id, username, rating, review_text, header, date_made, photo 
                              FROM reviews 
                              ORDER BY date_made DESC''')
        
        reviews = cursor.fetchall()
        cursor.close()

        return render_template('userhomepage.html', username=session['username'], user_id=session['id'], 
                               current_date=current_date, reviews=reviews, view_my_reviews=view_my_reviews)
    else:
        return redirect(url_for('login'))
    
@app.route('/review/photo/<int:review_id>')
def review_photo(review_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT photo FROM reviews WHERE review_id = %s", (review_id,))
    review = cursor.fetchone()
    cursor.close()

    if review and review[0]:
        return Response(review[0], mimetype='image/jpeg')  
    else:
        return Response(open('static/placeholder.jpg', 'rb').read(), mimetype='image/jpeg')

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
            special_percent = request.form['specialPercent']
            special_percent = 1 - (int(special_percent) / 100)
            print (special_percent)
            cursor.execute('UPDATE Menu SET itemPrice = itemPrice * %s WHERE itemName = %s', (special_percent, special_name))
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

@app.route('/update-profile-pic', methods=['POST'])
def update_profile_pic():
    if 'loggedin' in session:
        data = request.get_json()
        new_profile_pic = data.get('profile_pic')

        # Update the database with the new profile picture path
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE UserInfo SET profile_pic = %s WHERE LoginID = %s', (new_profile_pic, session['id']))
        mysql.connection.commit()

        # Check if the update was successful
        cursor.execute('SELECT profile_pic FROM UserInfo WHERE LoginID = %s', (session['id'],))
        result = cursor.fetchone()
        if result and result['profile_pic'] == new_profile_pic:
            return jsonify({'message': 'Profile picture updated successfully!'}), 200
        else:
            return jsonify({'message': 'Failed to update profile picture!'}), 500
    else:
        return jsonify({'message': 'User not logged in!'}), 401

# Route for Profile Management
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM UserInfo WHERE LoginID = %s', (session['id'],))
        account = cursor.fetchone()
        current_profile_pic = account.get('profile_pic', 'Images_Videos/whitepizzausericon.png')

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
            
            # Fetch all user accounts
            cursor.execute('SELECT * FROM UserInfo')
            accounts = cursor.fetchall()
        
        return render_template('profile.html', account=account, msg=msg, is_admin=is_admin, accounts=accounts, current_profile_pic=current_profile_pic)
    else:
        return redirect(url_for('login'))

def is_admin():
    if 'isAdmin' in session:
        return True
    else:
        return False

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
