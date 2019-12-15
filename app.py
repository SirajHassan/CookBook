from flask import Flask, request, Response, render_template, flash
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/sirajhassan/Desktop/webDev/CookBook/test_database.db'
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

#family - groups users into one cookbook
class Family(db.Model):
    __tablename__ = 'family'

    id = db.Column(db.Integer, primary_key = True)
    pin = db.Column(db.Integer)
    name = db.Column(db.String(40),unique = True)
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
    username = StringField('Username',validators = [InputRequired(), Length(min = 4, max = 30)])
    family_pin = PasswordField('Family Pin Number', validators = [InputRequired(), Length(min = 4, max = 4)])

class RegisterForm(FlaskForm):
    username = StringField('Username',validators = [InputRequired()])
    #password = PasswordField('Password', validators = [InputRequired()])
    new_cook_book = BooleanField('New CookBook')
    family_name = StringField('Family Cook Book Name',validators = [InputRequired(), Length(min = 4, max = 40)])
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


    if form.validate_on_submit(): #if form has been submitted properly
        return 'login is good'

    return render_template("login.html", form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit(): #if form has been submitted properly

        #check if user and family exist already..
        family_exists = db.session.query(Family.name).filter_by(name=form.family_name.data).scalar() is not None
        user_exists = db.session.query(User.username).filter_by(username=form.username.data).scalar() is not None

        if (form.new_cook_book.data == True): # make new cookbook
            user = User(username = form.username.data)
            family = Family(pin = form.family_pin.data, name = form.family_name.data, users =[user])

            if (family_exists == True):
                flash('Error Family CookBook Name exists, try a different name')
                if (user_exists == True):
                    flash('Error Username Exists try a different name')

                return render_template("signup.html", form = form)

            if (user_exists == True):
                flash('Error Username Exists try a different name')
                return render_template("signup.html", form = form)

            else:
                db.session.add(family)
                db.session.add(user)#order of family and user might be issue?
                db.session.commit()

            return('user added')

        else:

            if (user_exists):
                flash('Error User Name already exists, try a different name')
                return render_template("signup.html", form = form)

            #check if pin matches family
            if(family_exists):
                # check if pin is correct
                fam = db.session.query(Family.name).filter_by(pin= form.family_pin.data, name = form.family_name.data).all() #better way to do this
                if fam != []: # pin and name exist as combo
                    user = User(username = form.username.data)
                    family = Family.query.filter_by(name=form.family_name.data).first()

                    # add user to family.. if user exists send error..
                    db.session.add(user)
                    family.users.append(user)
                    db.session.add(family)
                    db.session.commit()
                    return ('success')

                else:
                    #report pin does not match
                    flash('Pin does not match')
                    return render_template("signup.html", form = form)

            else:
                #report family does not exist.
                flash('Family Name does not exists')
                return render_template("signup.html", form = form)

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
