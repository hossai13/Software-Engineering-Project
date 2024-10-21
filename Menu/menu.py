from flask import Flask, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'PizzaInfo'
mysql = MySQL(app)

@app.route('/')
def index():
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM UserInfo")
    result = cursor.fetchone()

    return render_template('registration_form.html',result=result)

if __name__ == '__main__':
    app.run(debug=True)