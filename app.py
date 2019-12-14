from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField, SelectField
from wtforms.validators import Regexp, InputRequired,Email,Length, AnyOf
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user, logout_user, current_user
from flask_bootstrap import Bootstrap
import re
import json



csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

# bootstrap stuff
boostrap = Bootstrap(app)

#nav stuff
nav = Nav()
nav.init_app(app)


#login stuff
login_manager = LoginManager()
login_manager.init_app(app)

#SQL stuff ########################################
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/sirajhassan/Desktop/webDev/CookBook/database.db'
db = SQLAlchemy(app)

#Tables for db
class User(UserMixin,db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30),unique = True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))

class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key = True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    creator_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    recipe = db.Column(db.String(1000))
    image_link = db.Column(db.String(200))
    time_made = db.Column(db.Integer)

#family
class Family(db.Model):
    __tablename__ = 'family'

    id = db.Column(db.Integer, primary_key = True)
    pin = db.Column(db.Integer)
    name = db.Column(db.String(30))
    users = db.relationship('User',backref='family')
    recipes = db.relationship('Recipe',backref='family')





#navigation stuff
@nav.navigation()
def mynavbar():
    return Navbar(
        'Family CookBook',
        View('Home', 'dashboard'),
        View('Breakfast','breakfast'),
        View('Lunch','lunch'),
        View('Dinner','dinner'),
        View('Dessert','dessert'),
        View('Snacks','snacks'),
    )



#################login stuff ###############################


class LoginForm(FlaskForm):
    username = StringField('Username',validators = [InputRequired(), Length(min = 4, max = 20)])
    family_pin = PasswordField('Family Pin Number', validators = [InputRequired(), Length(min = 4, max = 4)])

class RegisterForm(FlaskForm):
    username = StringField('Username',validators = [InputRequired()])
    #password = PasswordField('Password', validators = [InputRequired()])
    new_cook_book = BooleanField('New CookBook')
    family_name = StringField('Family name',validators = [InputRequired(), Length(min = 4, max = 20)])
    family_pin = PasswordField('Family Pin Number',validators = [InputRequired(), Length(min = 4, max = 4)])


#function that flask login uses to connect abstract user
#to users in the model
#returns user object based on user id.
@login_manager.user_loader
def load_user(user_id):
    #get data from table in db
    #returns entire object for user id number
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()


    if form.validate_on_submit(): #if form has been submitted already
        return 'login is good'

    return render_template("login.html", form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit(): #if form has been submitted already
        return 'signup is good'

    return render_template("signup.html", form = form)


################ pages ######################################

#Index page. This will route users to either login or signup.
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

##### meals ######

@app.route('/breakfast')
def breakfast():
    return render_template("breakfast.html")

@app.route('/lunch')
def lunch():
    return render_template("lunch.html")

@app.route('/dinner')
def dinner():
    return render_template("dinner.html")

@app.route('/dessert')
def dessert():
    return render_template("dessert.html")

@app.route('/snacks')
def snacks():
    return render_template("snacks.html")





################# other functions  ####################

#add user to the db
def create_user(name,id,password,family,db):
    print('creating user')

# get all data from recipes and generate to html
# def GenerateRecipes(fam_id):
#     family_recipes = Recipe.query.filter_by(family_id = fam_id)
#     return family_recipes
