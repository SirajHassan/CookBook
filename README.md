# CookBook

Project Plan: B

Group Member Names: Siraj Hassan

Link to Live Application: https://sirajscookbook.herokuapp.com/

Existing usernames and pins:
  username: siraj
  family: hassan
  pin: 1234
  
  username: Bobby
  family:hassan
  pin: 1234
  
  username:

Technologies Used:
  - Heroku: Runs the application remotely with PostGres database
  - Here Places API: (https://places.demo.api.here.com/places/)
    - Used for feature to find resturaunts nearby that may serve a certain dish
  - Summernote WYSIWWG Text Editor: (https://summernote.org)
    - This is used to allow users to make a customized recipe page.
      The editor works locally, however IT DOES NOT WORK IN HEROKU.
      
  - Flask-Bootstrap: used to style app
  
  - Flask-Login: used for user session management.
  
  - Project Description:
  
      The goal of this web app is to provide a place where a family can remotely store cooking recipes.
      The app has users, with unique usernames, and each user belongs to a family with a shared cookbook.
      A new user can either join a existing family if they know the family's pin number, or they can start 
      a new one. 

      Once logged into the Cookbook, a user can view recipes created by their family in different categories. 
      (breakfast, lunch, dinner, dessert, snacks) These categories can be accessed from the navigation bar.
      
      In each catergory, there is a list of existing recipes. A user can view any recipe made by their family,
      but they can only modify ones the user has created themselves. The user can also create recipes for 
      any category. 
 
      Recipes are created with the Summernote text editor. The summer note editor allows users to customize their recipes,
      and add pictures. NOTE -- This editor does not work on heroku for some reason. I am not sure why, and did not understand 
      heroku well enough to fix this. Users can still add recipes however, they are not formatted properly. 
      
      Here is an image of what the editor looks like LOCALLY, without Heroku issues:
      
      Creating the recipe:
      ![alt text](https://github.com/SirajHassan/CookBook/blob/master/images/eggs2.png)
      Editing the Recipe:
      ![alt text](https://github.com/SirajHassan/CookBook/blob/master/images/eggs1.png)
      Viewing the Recipe:
      ![alt text](https://github.com/SirajHassan/CookBook/blob/master/images/eggs3.png)
      
      
      
      The feature users can use that involves an API, is located within the list of recipes. The user can click a button to 
      find resturaunts near them that may serve the dish (based of the name of recipe). This data comes from the Here Places
      API. 
      
      
    
    

  
  - List of Controllers:
  
    - @app.route('/') :
      - redirect to /login
    - @login_manager.user_loader : 
      - returns user object, needed for Flask-login
    - @app.route('/logout'): 
      - logs user out, redirected to login page
    - @app.route('/login', methods=['GET', 'POST']) : 
      - logs user in if username and pin exist/corrrect. (WTF forms) Then redirects to 'dashboard'
    - @app.route('/signup', methods=['GET', 'POST']):
      - Runs logic behind inputting new users/familes into database via WTF forms.
    - @app.route('/dashboard'):
      - Route to dashboard or Home page of cookbook
    - @app.route('/breakfast'):
      - This will run the logic to exctract breakfast recipe info from database
    - @app.route('/lunch'):
      - similair to /breakfast
    - @app.route('/dinner'):
      - similair to /breakfast
    - @app.route('/dessert'):
      - similair to /breakfast
    - @app.route('/snack'):
      - similair to /breakfast
    - @app.route('/create/<type>', methods=['GET', 'POST']):
      - This runs the logic behind getting data from user 
        to create a new (type of) recipe and placing it into the database
    - @app.route('/view/<recipe_id>'):
      - Extracts recipe data from database, lets user view it.
    - @app.route('/find/<recipe>',methods=['GET', 'POST'])
      - Takes a recipe and calls API to get data about resturants
        nearby serving dish.
    - @app.route('/list')
      - Lists out resturaunt data
    
  - List of Views: 
    - login.html:
      - Login page for users, can direct to sign up
    - signup.html:
      - Signup page for users, can direct to login
    - dashboard.html:
      - homepage of cookbook, not much information
    - breakfast,lunch,dinner,dessert,snack - .html:
      - pages display list of recipes that family members have made.
        Also displays button to let users create new recipe.
      - Each recipe in list has button to view recipe, find resturants,
        or edit the recipe (if user made it).
    - meals.html :
      - all meal catergory templates inherit from this template.
        Provides nav bar. 
    - create.html :
      - renders a text editor for users to create recipes with and submit
    - edit.html :
      - renders a text editor for users to edit existing recipes 
    - view.html :
      - renders a view of the recipe
    - find.html : 
      - asks for zip code, to find resturaunts
    - list.html:
      - lists resturaunts that match recipe description
    
    
  - Description of Tables and their structure:
  
    There are Three tables:
    
    
    - User:
      In the user table, Users belong to families, and have unique usernames.
    
      - id: user id
      - username: displayed name of user
      - family_id: relation to family table, id number of family 
      
    - Recipes:
      In the recipe table, each recipe belongs to family and have unique creators (users).
      - id: recipe id
      - family_id: relation to family table, id number of family
      - creator_id: id of user who created recipe
      - name: name of recipe
      - type: category of meal
      - time_made: time recipe was made (not used)
      
    - Family: 
      In the family table, families have unique names, a pin (short password) and
      have a one to many relationship with the recipe and user tables rows. 
      - id: family id
      - pin: 4 digit family pin number
      - name: displayed family name
      - users: one to many relationship.. list of users
      - recipes: one to many relationship.. list of recipes
      
 
  - References/Resources:
    - Anthony's videos from PrettyPrinted youtube channel: https://www.youtube.com/channel/UC-QDfvrRIDB6F0bIO4I4HkQ/about
    - Parts of the Miguel Grinberg Flask Tutorial
  
 

  
  
