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

from uszipcode import SearchEngine



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
#heroku
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xxumqtjlsspfpp:fa743653af5ac11c8612be548e86aeb237beaf86a2a9eb9328d0a4fbf202a866@ec2-174-129-254-218.compute-1.amazonaws.com:5432/d9a94ocif6uehf'
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
    name = StringField('Please Enter Name of Recipe', [InputRequired(), Length(min = 1, max = 90)])

class ZipForm(FlaskForm):
    zip = StringField('Please Enter your Zip code', validators = [InputRequired(),Length(min=5, max=11)])


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
                    return (render_template("login.html", form = form))

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
    form = LoginForm()
    return render_template("login.html", form = form)


@app.route('/dashboard')
@login_required
def dashboard():
    family_name = Family.query.filter_by(id=current_user.family_id).first().name
    return render_template("dashboard.html", name=current_user.username, family_name = family_name )

##### meals ######

#will search database based on logged in user.
#based on family_id, show recipes that in the family cookbook of the correct type.
#If the user is the creator, offer the option to edit the recipe.
@app.route('/breakfast')
@login_required
def breakfast():

    family = Family.query.filter_by(id=current_user.family_id).first()
    users = User.query.filter_by(family_id=current_user.family_id).all()
    family_recipes = Recipe.query.filter_by(family_id = family.id, type = 'breakfast').all() #these can be viewed
    user_recipes = Recipe.query.filter_by(creator_id = current_user.id , type = 'breakfast').all() #these can be edited

    recipe_list = [];
    creator_list = [];
    link_list = [];
    is_creator_list = [];
    for recipe in family_recipes:
        creator = User.query.filter_by(id=recipe.creator_id).first().username
        is_creator = False

        if recipe.creator_id == current_user.id:
            is_creator = True

        #link to search for food item
        link = ''

        recipe_list.append((recipe,creator,link,is_creator,current_user.id))
        # creator_list.append(creator)
        # link_list.append(link)
        # is_creator_list.append(is_creator)


    return(render_template("breakfast.html", recipe_list= recipe_list ))



@app.route('/lunch')
@login_required
def lunch():
    family = Family.query.filter_by(id=current_user.family_id).first()
    users = User.query.filter_by(family_id=current_user.family_id).all()
    family_recipes = Recipe.query.filter_by(family_id = family.id, type = 'lunch').all() #these can be viewed
    user_recipes = Recipe.query.filter_by(creator_id = current_user.id , type = 'lunch').all() #these can be edited

    recipe_list = [];
    creator_list = [];
    link_list = [];
    is_creator_list = [];
    for recipe in family_recipes:
        creator = User.query.filter_by(id=recipe.creator_id).first().username
        is_creator = False

        if recipe.creator_id == current_user.id:
            is_creator = True

        #link to search for food item
        link = ''

        recipe_list.append((recipe,creator,link,is_creator,current_user.id))
        # creator_list.append(creator)
        # link_list.append(link)
        # is_creator_list.append(is_creator)


    return(render_template("lunch.html", recipe_list= recipe_list ))

@app.route('/dinner')
@login_required
def dinner():
    family = Family.query.filter_by(id=current_user.family_id).first()
    users = User.query.filter_by(family_id=current_user.family_id).all()
    family_recipes = Recipe.query.filter_by(family_id = family.id, type = 'dinner').all() #these can be viewed
    user_recipes = Recipe.query.filter_by(creator_id = current_user.id , type = 'dinner').all() #these can be edited

    recipe_list = [];
    creator_list = [];
    link_list = [];
    is_creator_list = [];
    for recipe in family_recipes:
        creator = User.query.filter_by(id=recipe.creator_id).first().username
        is_creator = False

        if recipe.creator_id == current_user.id:
            is_creator = True

        #link to search for food item
        link = ''

        recipe_list.append((recipe,creator,link,is_creator,current_user.id))
        # creator_list.append(creator)
        # link_list.append(link)
        # is_creator_list.append(is_creator)


    return(render_template("dinner.html", recipe_list= recipe_list ))

@app.route('/dessert')
@login_required
def dessert():
    family = Family.query.filter_by(id=current_user.family_id).first()
    users = User.query.filter_by(family_id=current_user.family_id).all()
    family_recipes = Recipe.query.filter_by(family_id = family.id, type = 'dessert').all() #these can be viewed
    user_recipes = Recipe.query.filter_by(creator_id = current_user.id , type = 'dessert').all() #these can be edited

    recipe_list = [];
    creator_list = [];
    link_list = [];
    is_creator_list = [];
    for recipe in family_recipes:
        creator = User.query.filter_by(id=recipe.creator_id).first().username
        is_creator = False

        if recipe.creator_id == current_user.id:
            is_creator = True

        #link to search for food item
        link = ''

        recipe_list.append((recipe,creator,link,is_creator,current_user.id))
        # creator_list.append(creator)
        # link_list.append(link)
        # is_creator_list.append(is_creator)


    return(render_template("dessert.html", recipe_list= recipe_list ))

@app.route('/snacks')
@login_required
def snacks():
    family = Family.query.filter_by(id=current_user.family_id).first()
    users = User.query.filter_by(family_id=current_user.family_id).all()
    family_recipes = Recipe.query.filter_by(family_id = family.id, type = 'snacks').all() #these can be viewed
    user_recipes = Recipe.query.filter_by(creator_id = current_user.id , type = 'snacks').all() #these can be edited

    recipe_list = [];
    creator_list = [];
    link_list = [];
    is_creator_list = [];
    for recipe in family_recipes:
        creator = User.query.filter_by(id=recipe.creator_id).first().username
        is_creator = False

        if recipe.creator_id == current_user.id:
            is_creator = True

        #link to search for food item
        link = ''

        recipe_list.append((recipe,creator,link,is_creator,current_user.id))
        # creator_list.append(creator)
        # link_list.append(link)
        # is_creator_list.append(is_creator)


    return(render_template("snacks.html", recipe_list= recipe_list ))

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

@app.route('/edit/<recipe_id>', methods=['GET', 'POST'])
@csrf.exempt
def edit(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    name = recipe.name
    html = recipe.recipe

    recipe_form = RecipeForm()
    if request.method == 'POST':
        new_recipe=request.form.get('editordata')
        new_name =recipe_form.name.data
        recipe.recipe=new_recipe
        db.session.add(recipe)
        db.session.commit()


        return render_template("dashboard.html",form = recipe_form)

    return render_template("edit.html",form = recipe_form,name = name,html = html)


@app.route('/view/<recipe_id>')
@login_required
def view(recipe_id):

    recipe = Recipe.query.filter_by(id=recipe_id).first()
    name = recipe.name
    html = recipe.recipe
    creator = User.query.filter_by(id=recipe.creator_id).first().username

    return render_template("view.html", html = html, name = name, creator = creator)


@app.route('/find/<recipe>',methods=['GET', 'POST'])
# @login_required
# The following will take in the recipe name.
# There will be a form for the zip code.
# Then it will list the resturaunts nearby with dishes that are similair.
def find(recipe):

    apiKey = 'ylbFVFBsz1DCXmnedrKizaClp3_XgMF1LNMXuGTBVTo'

    form = ZipForm()

    # if zip code submitted
    if request.method == 'POST':

        resturant_list = []

        zip = request.form.get('zip')
        search = SearchEngine(simple_zipcode=True)
        zipcode = search.by_zipcode(str(zip))
        lat = zipcode.lat
        lng = zipcode.lng

        cors_api_url = 'https://cors-anywhere.herokuapp.com/'
        placeUrl = 'https://places.cit.api.here.com/places/v1/autosuggest?at='+ str(lat) + ',' + str(lng) +'&q='
        placeKey =  'ylbFVFBsz1DCXmnedrKizaClp3_XgMF1LNMXuGTBVTo'
        placeCode = '&app_code=U69BAgH1-nFOA3RjsxFvqQ'
        placeID = '&app_id=nIaXQgZgY4aHEActVeSn'
        placeParameter = str(recipe);

        # url = cors_api_url + placeUrl +placeParameter + placeID + placeCode
        url = placeUrl +placeParameter + placeID + placeCode
        #print(url)

        if (str(lat) != 'None') & (str(lng) != 'None'):

            try:
                response = requests.get(url)
                # data = response.text
                # parsed = json.loads(data)
                r = response.json()
                size = len(r['results'])

                #make list of resturants nearby..
                if (size > 1):

                    for rest in r['results']:
                        try:
                            location = rest['highlightedVicinity']
                            name = rest['highlightedTitle']
                            print(name + location)
                            resturant_list.append((name,location))

                        except:
                            print('error line 534')

                    return (render_template("list.html", list = resturant_list))

                flash('No Resturants Nearby With This Dish')
                return (render_template("find.html" , form = form))


            except:
                flash('Error')
                return (render_template("find.html" , form = form))
        else:
            flash('Invalid Zip Code')
            return (render_template("find.html" , form = form))




    return (render_template("find.html" , form = form))



@app.route('/list')
# @login_required
#takes list of resturants and displays them
def list():
    print('listing')
    return (render_template("list.html" , list = []))








if __name__ == ' __main__':
    #app.debug = True
    app.run()
