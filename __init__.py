from flask import Flask, render_template, request
import MySQLdb

from main import main_api

app = Flask(__name__, static_url_path='/static')

app.register_blueprint(main_api)

@app.route("/")
def index():
    print "__init__"
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "SELECT * from nodes;"
    cr.execute(sql)
    results = cr.fetchall()

    return render_template('main.html', results=results)
