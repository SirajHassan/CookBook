from flask import Flask, request, Response, render_template, flash
import requests
import itertools
from flask_nav import Nav
from flask_nav.elements import *
from flask_wtf.csrf import CSRFProtect
from flask_wtf import CsrfProtect

from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField, SelectField
from wtforms.validators import Regexp, InputRequired,Email,Length, AnyOf
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user, logout_user, current_user, login_required
from flask_bootstrap import Bootstrap

from datetime import datetime

import re
import json
import sys
import os

from flask_heroku import Heroku






app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf = CSRFProtect(app) #changed this
csrf.init_app(app)
heroku = Heroku(app)


# bootstrap stuff
boostrap = Bootstrap(app)

#nav stuff
nav = Nav()
nav.init_app(app)

#login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#SQL stuff ########################################
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/sirajhassan/Desktop/webDev/CookBook/database.db' #local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') #heroku
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
    recipe = db.Column(db.Text) #where summernote data is stored
    type = db.Column(db.String(20))
    #image_link = db.Column(db.String(200))
    time_made = db.Column(db.String(100))

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

        View('Home', 'dashboard'),
        View('Breakfast','breakfast'),
        View('Lunch','lunch'),
        View('Dinner','dinner'),
        View('Dessert','dessert'),
        View('Snacks','snacks'),
        View('Logout','logout'),



    )


################# recipe forms ###########################

class RecipeForm(FlaskForm):
    name = StringField('Name of Recipe', [InputRequired(), Length(min = 1, max = 90)])


#################login stuff ###############################


class LoginForm(FlaskForm):
    username = StringField('Username',validators = [InputRequired(), Length(min = 4, max = 30)])
    family_pin = PasswordField('Family Pin Number', validators = [InputRequired(), Length(min = 4, max = 4)])

class RegisterForm(FlaskForm):
    username = StringField('Username',validators = [InputRequired(),Length(min = 4, max = 30)])
    #password = PasswordField('Password', validators = [InputRequired()])
    new_cook_book = BooleanField('New CookBook')
    family_name = StringField('Family Cook Book Name',validators = [InputRequired(), Length(min = 4, max = 40)])
    family_pin = PasswordField('Family Pin Number (4 values)',validators = [InputRequired(), Length(min = 4, max = 4)])


#function that flask login uses to connect abstract user
#to users in the model
#returns user object based on user id.
@login_manager.user_loader
def load_user(user_id):
    #get data from table in db
    #returns entire object for user id number
    return User.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html",form = LoginForm(), methods=['GET', 'POST'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return render_template("dashboard.html")


    if form.validate_on_submit(): #if form has been submitted properly
        user_exists = db.session.query(User.username).filter_by(username=form.username.data).scalar() is not None

        # if user exists check if pin matches..
        if user_exists == True:
            user = User.query.filter_by(username=form.username.data).first()
            family_id = user.family_id
            family = Family.query.get(family_id)
            pin = family.pin
            #return(str(pin)+ ' ' + str(form.family_pin.data))

            if str(pin) == str(form.family_pin.data): #pin matches
                login_user(user)
                return render_template("dashboard.html")
            else:
                flash('Error, Pin is not correct')
                return render_template("login.html", form = form)


        else:
            flash('Error Username Does not exist try a different name')
            return render_template("login.html", form = form)

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

            else: #add user to database go to login
                db.session.add(family)
                db.session.add(user)#order of family and user might be issue?
                db.session.commit()
                flash('Username: ' + str(form.username.data) + 'created successfully')
                return render_template("login.html", form = LoginForm() , methods=['GET', 'POST'])


        else:

            if (user_exists):
                flash('Error User Name already exists, try a different name')
                return render_template("signup.html", form = form)

            #check if pin matches family
            if(family_exists):
                # check if pin is correct
                fam = db.session.query(Family.name).filter_by(pin= form.family_pin.data, name = form.family_name.data).all() #better way to do this?
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
@login_required
def dashboard():
    return render_template("dashboard.html", name=current_user.username)

##### meals ######

#will search database based on logged in user.
#based on family_id, show recipes that in the family cookbook of the correct type.
#If the user is the creator, offer the option to edit the recipe.
@app.route('/breakfast')
@login_required
def breakfast():

    family = Family.query.filter_by(id=current_user.family_id).first()
    family_recipes = Recipe.query.filter_by(family_id = family.id, type = 'breakfast').all() #these can be viewed
    user_recipes = Recipe.query.filter_by(creator_id = current_user.id , type = 'breakfast').all() #these can be edited

    return(render_template("breakfast.html", family_recipes = family_recipes, size = len(family_recipes), user = current_user))



@app.route('/lunch')
@login_required
def lunch():
    return render_template("lunch.html")

@app.route('/dinner')
@login_required
def dinner():
    return render_template("dinner.html")

@app.route('/dessert')
@login_required
def dessert():
    return render_template("dessert.html")

@app.route('/snacks')
@login_required
def snacks():
    return render_template("snacks.html")

# create a new recipe, store it in db
@app.route('/create/<type>', methods=['GET', 'POST'])
@csrf.exempt
def create(type):
    recipe_form = RecipeForm()
    if request.method == 'POST':
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        family = Family.query.filter_by(id=current_user.family_id).first()

        recipe = Recipe(recipe=request.form.get('editordata'),name =recipe_form.name.data, creator_id = current_user.id,time_made=current_time,type = type)
        family.recipes.append(recipe)
        db.session.add(recipe)
        db.session.add(family)
        db.session.commit()
        # print(request.form.get('editordata'))
        #exec(type+'()') #run type before going to page
        # return render_template(str(type)+".html",form = recipe_form) # go back to page of meal type
        return render_template("dashboard.html",form = recipe_form)

    return render_template("create.html",form = recipe_form)

# pull old recipe from db, edit if creator.


if __name__ == ' __main__':
    #app.debug = True
    app.run()
