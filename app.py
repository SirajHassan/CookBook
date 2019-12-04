from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp
import re
import json



class WordForm(FlaskForm):

    avail_letters = StringField("Letters", validators= [
        Regexp(r'^[a-z]*$', message="must contain letters only")
    ])

    pattern = StringField("Pattern", validators= [
        Regexp(r'^[a-z.]*$', message="must contain letters or periods (.)")
    ])

    wordLength = SelectField('Length of word', choices=[("Default","Select"),("3", "3"), ("4", "4"),("5", "5"),("6", "6"),("7", "7"),("8", "8"),("9", "9"),("10","10")])
    submit = SubmitField("Go")



csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form)
