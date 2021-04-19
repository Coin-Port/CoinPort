from flask import Flask, render_template
from flask_bootstrap import Bootstrap
#from flask_wtf import FlaskForm
#from wtforms import StringField
#from wtforms.validators import DataRequired, Length
#from forms import RegistrationForm

app=Flask(__name__)
app.config['SECRET_KEY'] = '98073e958b9c236b3fa0d714c68a2e6c'


#class RegistrationForm(FlaskForm):
#    Symbol1 = StringField('Symbol1', validators=[DataRequired(), Length(min=1, max=5)])
#    Symbol2 = StringField('Symbol2', validators=[DataRequired(), Length(min=1, max=5)])

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
