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
app.config['MYSQL_PASSWORD'] = '2113284'
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

@app.route('/api/item_sizes/<int:item_id>', methods=['GET'])
def get_item_sizes(item_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT size, price FROM PizzaSizes WHERE itemID = %s', (item_id,))
        sizes = cursor.fetchall()
        cursor.close()

        for size in sizes:
            size['price'] = float(size['price'])

        return jsonify(sizes)
    except Exception as e:
        print(f"Error fetching sizes: {e}")
        return jsonify({"error": "Failed to fetch sizes."}), 500

@app.route('/api/item_toppings/<int:item_id>', methods=['GET'])
def get_item_toppings(item_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT itemCategory FROM Menu WHERE itemID = %s', (item_id,))
        item = cursor.fetchone()

        if not item:
            return jsonify({"error": "Item not found."}), 404

        if item['itemCategory'] != 'Pizza':
            return jsonify({"error": "Toppings are only available for Pizza items."}), 400

        cursor.execute('SELECT toppingName, price FROM Toppings')
        toppings = cursor.fetchall()
        cursor.close()

        if not toppings:
            return jsonify({"error": "No toppings found."}), 404

        for topping in toppings:
            topping['price'] = float(topping['price'])

        return jsonify(toppings)
    except Exception as e:
        print(f"Error fetching toppings for item ID {item_id}: {e}")
        return jsonify({"error": "Failed to fetch toppings due to server error."}), 500
    
@app.route('/api/cart', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def cart_api():
    if 'cart' not in session:
        session['cart'] = {'items': [], 'total': 0.0}

    cart = session['cart']

    if request.method == 'GET':
        return jsonify(cart)

    elif request.method == 'POST':
        data = request.json
        item_id = data.get('id')
        item_name = data.get('name')
        quantity = data.get('quantity', 1)
        price = data.get('price')
        size = data.get('size', None)
        category = data.get('category', None)
        toppings = data.get('toppings', [])

        if not item_id or not item_name or price is None:
            return jsonify({'error': 'Invalid item data'}), 400

        topping_total = sum([topping['price'] for topping in toppings])
        total_price = (price + topping_total) * quantity

        existing_item = next((item for item in cart['items']
                            if item['id'] == item_id and item['size'] == size and item['toppings'] == toppings), None)

        if existing_item:
            existing_item['quantity'] += quantity
            existing_item['total_price'] = existing_item['quantity'] * (price + topping_total)
        else:
            cart['items'].append({
                'id': item_id,
                'name': item_name,
                'quantity': quantity,
                'price_per_unit': price,
                'size': size,
                'category': category,
                'toppings': toppings,
                'total_price': total_price
            })

        cart['total'] = sum(item['total_price'] for item in cart['items'])
        session.modified = True
        return jsonify(cart)

    elif request.method == 'PATCH':
        data = request.json
        item_id = data.get('id')
        quantity = data.get('quantity')

        if not item_id or quantity is None:
            return jsonify({'error': 'Invalid item data'}), 400

        for item in cart['items']:
            if item['id'] == item_id:
                item['quantity'] = quantity
                item['total_price'] = item['quantity'] * (item['price_per_unit'] + sum(topping['price'] for topping in item['toppings']))
                break
        else:
            return jsonify({'error': 'Item not found in cart'}), 404

        cart['total'] = sum(item['total_price'] for item in cart['items'])
        session.modified = True
        return jsonify(cart)

    elif request.method == 'DELETE':
        data = request.json
        item_id = data.get('id')

        if not item_id:
            return jsonify({'error': 'Invalid item data'}), 400

        cart['items'] = [item for item in cart['items'] if item['id'] != item_id]


        cart['total'] = sum(item['total_price'] for item in cart['items'])
        session.modified = True
        return jsonify(cart)

    return jsonify({'error': 'Method not allowed'}), 405

# Route for the menu page
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch all menu items
        cursor.execute("SELECT DISTINCT itemName, itemCategory, itemPrice FROM Menu ORDER BY itemName")
        all_menu_items = cursor.fetchall()
        
        # Fetch categories from the Categories table
        cursor.execute("SELECT itemCategory FROM Categories ORDER BY categoryOrder")
        categories = cursor.fetchall()
        
        # Fetch all menu items grouped by category
        menu_items_by_category = {}
        for category in categories:
            cursor.execute("""
                SELECT DISTINCT
                    m.itemID, m.itemName, m.itemCategory,
                    COALESCE(MIN(ps.price), m.itemPrice) AS defaultPrice,
                    CASE
                        WHEN MIN(ps.price) IS NOT NULL THEN TRUE
                        ELSE FALSE
                    END AS hasSizes
                FROM
                    Menu m
                LEFT JOIN
                    PizzaSizes ps ON m.itemID = ps.itemID
                WHERE
                    m.itemCategory = %s
                GROUP BY
                    m.itemID, m.itemName, m.itemCategory, m.itemPrice
                ORDER BY
                    m.itemName;
            """, (category['itemCategory'],))
            menu_items_by_category[category['itemCategory']] = cursor.fetchall()
        
        # Close the cursor
        cursor.close()

        # Admin-specific functionality
        if request.method == 'POST' and is_admin():
            # Delete menu item
            if 'delete_menu' in request.form:
                menu_id = request.form['delete_menu']
                cursor = mysql.connection.cursor()
                cursor.execute('DELETE FROM Menu WHERE itemID = %s', (menu_id,))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('menu'))

            # Add a new menu item
            if 'addName' in request.form and 'addPrice' in request.form and 'addCategory' in request.form:
                item_name = request.form['addName']
                item_price = request.form['addPrice']
                item_category = request.form['addCategory']
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO Menu (itemName, itemPrice, itemCategory) VALUES (%s, %s, %s)', 
                               (item_name, item_price, item_category))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('menu'))

            # Update an existing menu item
            if 'editName' in request.form and 'updatePrice' in request.form:
                item_name = request.form['editName']
                item_price = request.form['updatePrice']
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE Menu SET itemPrice = %s WHERE itemName = %s', (item_price, item_name))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('menu'))

            # Apply a special discount to a menu item
            if 'specialName' in request.form and 'specialPercent' in request.form:
                special_name = request.form['specialName']
                try:
                    special_percent = int(request.form['specialPercent'])
                    if special_percent < 0 or special_percent > 100:
                        return "Special percent must be between 0 and 100"
                    discount_factor = 1 - (special_percent / 100)
                except ValueError:
                    return "Special percent must be an integer"
                
                try:
                    cursor = mysql.connection.cursor()
                    cursor.execute('UPDATE Menu SET itemPrice = itemPrice * %s WHERE itemName = %s', 
                                   (discount_factor, special_name))
                    mysql.connection.commit()
                    cursor.close()
                except Exception as e:
                    mysql.connection.rollback()  # Rollback transaction on error
                    print(f"Database Error: {e}")
                    return "Database Error"
                return redirect(url_for('menu'))

        # Render the menu page with all items and categories
        return render_template(
            'menu.html',
            all_menu_items=all_menu_items,
            menu_items_by_category=menu_items_by_category,
            is_admin=is_admin()
        )
    except Exception as e:
        print(f"Error in /menu route: {e}")
        return "Error loading the menu." 

@app.route('/cart')
def cart():
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {'items': [], 'total': 0.0}

    cart_data = session['cart']
    items = cart_data.get('items', [])
    total = cart_data.get('total', 0.0)

    return render_template('checkout.html', items=items, total=total)

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
            if is_owner():
                if 'promote_user' in request.form:
                    user_id = request.form['promote_user']
                    cursor.execute('UPDATE UserInfo SET isAdmin = 1 WHERE LoginID = %s', (user_id,))
                    mysql.connection.commit()
                    msg = 'User promoted to admin!'
                if 'demote_admin' in request.form:
                    user_id = request.form['demote_admin']
                    cursor.execute('UPDATE UserInfo SET isAdmin = 0 WHERE LoginID = %s', (user_id,))
                    mysql.connection.commit()
                    msg = 'Admin demoted to user!'
                
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

def is_owner():
    if session['id'] == 1:
        return True
    else:
        return False


# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
