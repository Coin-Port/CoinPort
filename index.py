from flask import Flask, render_template
from flask_bootstrap import Bootstrap


app=Flask(__name__)
app.config['SECRET_KEY'] = '98073e958b9c236b3fa0d714c68a2e6c'


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/forgot-password.html')
def forgotPassword():
    return render_template('forgot-password.html')

@app.route('/404.html')
def notFound():
    return render_template('404.html')


if __name__ == "__main__":
	app.run(debug=True)
