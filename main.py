import math
from io import BytesIO
import time
from flask import Flask, flash, jsonify, render_template, request, session, redirect, url_for, session, Response
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
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
        #this is where an admin can delete reviews
        is_admin = session.get('isAdmin')
        if is_admin:
            if request.method == 'POST':
                if 'delete_review' in request.form:
                    review_id = request.form['delete_review']
                    delete_review(review_id)
                    return redirect(url_for('userhomepage'))
                               
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
        return render_template('userhomepage.html', 
                               username=session['username'], 
                               user_id=session['id'], 
                               current_date=current_date, 
                               reviews=reviews, 
                               view_my_reviews=view_my_reviews, 
                               is_admin=is_admin)
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
                    mysql.connection.rollback()
                    print(f"Database Error: {e}")
                    return "Database Error"
                return redirect(url_for('menu'))

        return render_template(
            'menu.html',
            all_menu_items=all_menu_items,
            menu_items_by_category=menu_items_by_category,
            is_admin=is_admin()
        )
    except Exception as e:
        print(f"Error in /menu route: {e}")
        return "Error loading the menu." 

# Route for pickup times
@app.route('/set-pickup-time', methods=['POST'])
def set_pickup_time():
    data = request.json
    
    if data.get('pickup_time') == "Delivery":
        session['delivery_address'] = data.get('address', "Unknown Address")
        session['pickup_time'] = "Delivery"
    else:
        session['pickup_time'] = data.get('pickup_time', 'ASAP (15-30 min)')
        session.pop('delivery_address', None)
    
    session.modified = True
    return jsonify({"status": "success"}), 200

# Route for checkout
@app.route('/cart')
def cart():
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {'items': [], 'total': 0.0}

    cart_data = session['cart']
    items = cart_data.get('items', [])
    total = round(cart_data.get('total', 0.0), 2)
    pickup_time = session.get('pickup_time', 'ASAP (15-30 min)')
    delivery_address = session.get('delivery_address', None)

    for item in items:
        item['quantity'] = int(float(item['quantity']))
        item['price_per_unit'] = "{:.2f}".format(float(item['price_per_unit']))
        item['total_price'] = "{:.2f}".format(float(item['total_price']))
        if item.get('toppings'):
            item['toppings'] = [
                {'name': topping['name'], 'price': "{:.2f}".format(topping['price'])}
                for topping in item['toppings']
            ]

    if not items:
        return render_template(
            'checkout.html',
            message="Your cart is empty.",
            total=total,
            pickup_time=pickup_time,
            delivery_address=delivery_address
        )

    return render_template(
        'checkout.html',
        items=items,
        total="{:.2f}".format(total),
        pickup_time=pickup_time,
        delivery_address=delivery_address
    )

#Route for Order Placement
@app.route('/place-order', methods=['POST'])
def place_order():
    if 'cart' not in session or not session['cart']['items']:
        return jsonify({'error': 'Your cart is empty'}), 400

    cart = session['cart']
    items = cart['items']
    total = cart['total']
    user_id = session.get('id')
    
    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        cur = mysql.connection.cursor()

        order_id = user_id * 1000000 + int(time.time())  
        order_datetime = datetime.now()
        order_details = []

        for item in items:
            item_id = item['id']
            item_name = item['name']
            quantity = item['quantity']
            size = item.get('size', None)
            toppings = item.get('toppings', [])

            toppings_str = ",".join([topping['name'] for topping in toppings]) if toppings else None

            cur.execute("""
                INSERT INTO OrderHistory (orderID, LoginID, itemID, item_name, size, date_ordered, quantity, toppings, total_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (order_id, user_id, item_id, item_name, size, order_datetime, quantity, toppings_str, item['total_price']))

            order_details.append({
                'order_id': order_id,
                'item_name': item_name,
                'size': size,
                'date_ordered': order_datetime,
                'quantity': quantity,
                'toppings': toppings_str,
                'total_price': item['total_price']
            })
        mysql.connection.commit()
        cur.close()
        
        current_time = datetime.now()
        can_cancel = (current_time - order_datetime) <= timedelta(minutes=5)
        session['last_order'] = {
            'total': total, 
            'items': order_details, 
            'order_datetime': order_datetime,
            'can_cancel': can_cancel
        }

        return render_template('status.html', orders=order_details, total=total, can_cancel=can_cancel)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#Route for Order Cancellation
@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    order_id = request.form.get('order_id')
    user_id = session.get('id')

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT orderID, date_ordered FROM OrderHistory
            WHERE orderID = %s AND LoginID = %s
        """, (order_id, user_id))

        order = cur.fetchone()

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        order_datetime = order[1]  
        current_datetime = datetime.now()
        if current_datetime - order_datetime > timedelta(minutes=5):
            return jsonify({'error': 'Order cancellation period has passed'}), 400

        cur.execute("""
            DELETE FROM OrderHistory WHERE orderID = %s AND LoginID = %s
        """, (order_id, user_id))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('userhomepage'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/order-history', methods=['GET'])
def order_history():
    if 'id' not in session:
        return redirect(url_for('login')) 

    user_id = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT o.orderID, o.date_ordered, o.total_price, m.itemName, o.size, o.quantity
        FROM OrderHistory o
        LEFT JOIN Menu m ON o.itemID = m.itemID
        WHERE o.LoginID = %s
        ORDER BY o.date_ordered DESC
    ''', (user_id,))

    orders = cursor.fetchall()
    order_list = []
    for order in orders:
        order_list.append({
            'orderID': order[0],
            'date_ordered': order[1],
            'total_price': order[2],
            'itemName': order[3],
            'size': order[4],
            'quantity': order[5]
        })

    cursor.close()

@app.route('/rewards', methods=['GET'])
def rewards():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Points FROM UserInfo WHERE LoginID = %s', (session['id'],))
        points = cursor.fetchone()
        cursor.close()
    return render_template('rewards.html', points=points)

@app.route('/update_points', methods=['GET','POST'])
# Input a negative number to subtract points aka redeem
def update_points(amount):
    if 'loggedin' in session:
        points = amount * 100
        if points > 0:
            percent = points * .10 # 10%
            points = points + percent
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE UserInfo SET Points=Points + %s WHERE LoginID = %s', (points, session['id'],))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'success'}) 
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT Points FROM UserInfo WHERE LoginID = %s', (session['id'],))
            userPoints = cursor.fetchone()
            if (userPoints['Points'] + points) >= 0:
                cursor.execute('UPDATE UserInfo SET Points=Points + %s WHERE LoginID = %s', (points, session['id'],))
                mysql.connection.commit()
                cursor.close()
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'failed - not enough points'})   

@app.route('/redeem_rewards', methods=['POST'])
def redeem_rewards():
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {'items': [], 'total': 0.0}
    
    cart_data = session['cart']
    item = request.get_json()

    item_id = item.get('id')
    item_name = item.get('name')
    item_price = item.get('price', 0.0)
    item_points = item.get('points', 0)
    item_quantity = item.get('quantity', 1)
    item_category = item.get('category')
    item_toppings = item.get('toppings', [])
    item_size = item.get('size')
    item_total_price = item.get('total_price', item_price * item_quantity)
    item_total_points = item.get('total_points', item_points * item_quantity)

    update_points((item_points/100) * -1)
    existing_item = next((i for i in cart_data['items'] if i['id'] == item_id), None)

    if existing_item:
        existing_item['quantity'] += item_quantity
        existing_item['total_price'] += item_total_price
        existing_item['total_points'] += item_total_points
    else:
        new_item = {
            'id': item_id,
            'name': item_name,
            'price_per_unit': item_price,
            'points': item_points,
            'quantity': item_quantity,
            'category': item_category,
            'toppings': item_toppings,
            'size': item_size,
            'total_price': item_total_price,
            'total_points': item_total_points
        }
        cart_data['items'].append(new_item)
    cart_data['total'] += item_total_price

    session['cart'] = cart_data
    session.modified = True

    return jsonify({'status': 'success', 'cart': cart_data})

#Inventory commands
def fill_inventory():
    # Fills SQL inventory table
    # ONLY RUN ONCE, THEN COMMENT STATEMENT OUT
    # Placed in logout for ease. Login, then logout and your table should be filled.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    for i in range(1, 391): 
        cursor.execute('INSERT INTO inventory (itemID, quantity) VALUES (%s, 99)', (i,))
    mysql.connection.commit()
    cursor.close()

def refill_stock():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    for i in range(1, 391): 
        cursor.execute('UPDATE inventory SET quantity=99 WHERE inventoryID = %s', (i,))
    mysql.connection.commit()
    cursor.close()

@app.route('/reduce_stock')
def reduce_stock(itemID, quantity):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE inventory SET quantity=quantity - %s WHERE itemID = %s', (quantity, itemID))
    mysql.connection.commit()
    cursor.close()

@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('''
            SELECT o.orderID AS order_id, o.date_ordered, o.total_price, m.itemName AS item_name, 
                   o.size, o.quantity, o.toppings
            FROM OrderHistory o
            LEFT JOIN Menu m ON o.itemID = m.itemID
            WHERE o.orderID = %s AND o.LoginID = %s
        ''', (order_id, session['id']))
        orders = cursor.fetchall()

        total = sum(order['total_price'] for order in orders)

        return render_template('status.html', orders=orders, total=total)
    except Exception as e:
        print(f"Error loading order confirmation: {e}")
        return "Error loading order confirmation", 500
    finally:
        cursor.close()


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
                if account['LoginID'] == 1:
                    session['isOwner'] = True
                return redirect(url_for('userhomepage'))
            else:
                msg = 'Incorrect username/password!'
        else:
            msg = 'Please fill out the form'
    return render_template('login.html', msg=msg)

# Route for logout
@app.route('/logout')
def logout():
    # fill_inventory()
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('isAdmin', None)
    session.pop('isOwner', None)
    return redirect(url_for('login'))

@app.route('/update-profile-pic', methods=['POST'])
def update_profile_pic():
    if 'loggedin' in session:
        data = request.get_json()
        new_profile_pic = data.get('profile_pic')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE UserInfo SET profile_pic = %s WHERE LoginID = %s', (new_profile_pic, session['id']))
        mysql.connection.commit()

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
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch user details
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

    # Check if the logged-in user is an admin or owner
    is_admin = account['isAdmin']
    # Check if the logged-in user is the owner
    is_owner = session.get('isOwner')

    # Fetch order history for the user
    cursor.execute('''
        SELECT o.orderID, o.date_ordered, o.total_price, m.itemName, ps.size, o.quantity
        FROM OrderHistory o
        LEFT JOIN Menu m ON o.itemID = m.itemID
        LEFT JOIN PizzaSizes ps ON o.size = ps.sizeID
        WHERE o.LoginID = %s
        ORDER BY o.date_ordered DESC
    ''', (session['id'],))
    order_history = cursor.fetchall()

    # Handle admin-specific tasks
    accounts = []
    if is_admin:
        # Handle account deletion if requested
        if 'delete_account' in request.form:
            user_id = request.form['delete_account']
            cursor.execute('DELETE FROM UserInfo WHERE LoginID = %s', (user_id,))
            mysql.connection.commit()
            msg = 'Account deleted successfully!'

        # Handle user promotions and demotions
        if is_owner:
            # Handle user promotions and demotions where if they are a user, they become an admin and vice versa
            if 'toggle_admin' in request.form:
                user_id = request.form['toggle_admin']
                cursor.execute('SELECT isAdmin FROM UserInfo WHERE LoginID = %s', (user_id,))
                mysql.connection.commit()
                user = cursor.fetchone()
                if user['isAdmin']:
                    cursor.execute('UPDATE UserInfo SET isAdmin = 0 WHERE LoginID = %s', (user_id,))
                    mysql.connection.commit()
                    msg = 'User demoted to regular user!'
                else:
                    cursor.execute('UPDATE UserInfo SET isAdmin = 1 WHERE LoginID = %s', (user_id,))
                    mysql.connection.commit()
                    msg = 'User promoted to admin!'

        # Fetch all user accounts for admin view
        cursor.execute('SELECT * FROM UserInfo')
        accounts = cursor.fetchall()

    cursor.close()

    # Render the profile page
    return render_template(
        'profile.html',
        account=account,
        msg=msg,
        is_admin=is_admin,
        is_owner=is_owner,
        current_profile_pic=current_profile_pic,
        accounts=accounts,
        order_history=order_history
    )

# Function to delete a review
def delete_review(review_id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM reviews WHERE review_id = %s', (review_id,))
    mysql.connection.commit()
    cursor.close()

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
