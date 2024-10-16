from flask import Flask, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'naliah'
app.config['MYSQL_DB'] = 'menu'

mysql = MySQL(app)

@app.route('/')
def index():
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM menu_t")
    result = cursor.fetchone()

    return render_template('menu.html',result=result)

if __name__ == '__main__':
    app.run(debug=True)