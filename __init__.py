from flask import Flask, render_template, request

from main import main_api

app = Flask(__name__, static_url_path='/static')

app.register_blueprint(main_api)

@app.route("/")
def index():
    print "main"
    return render_template('main.html')

