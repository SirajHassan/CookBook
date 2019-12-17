# CookBook

Project Plan: B

Group Member Names: Siraj Hassan

Link to Live Application: https://sirajscookbook.herokuapp.com/

Technologies Used:
  - Heroku: Runs the application remotely with PostGres database
  - Here Places API: (https://places.demo.api.here.com/places/)
    - Used for feature to find resturaunts nearby that may serve a certain dish
  - Summernote WYSIWWG Text Editor: (https://summernote.org)
    - This is used to allow users to make a customized recipe page.
      The editor works locally, however IT DOES NOT WORK IN HEROKU.
      
  - Flask-Bootstrap: used to style app
  
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
      
      ![alt text](https://github.com/SirajHassan/CookBook/blob/master/images/eggs2.png)
      ![alt text](https://github.com/SirajHassan/CookBook/blob/master/images/eggs1.png)
      ![alt text](https://github.com/SirajHassan/CookBook/blob/master/images/eggs3.png)
      
      
      
      
      
      The feature users can use that involves an API, is located within the list of recipes. The user can click a button to 
      find resturaunts near them that may serve the dish (based of the name of recipe). This data comes from the Here Places
      API. 
      
      
    
    

  
  - List of Controllers:

  - List of Views: 

  - Description of Tables and their structure:
 
  - References/Resources:
    - Anthony's videos from PrettyPrinted youtube channel: https://www.youtube.com/channel/UC-QDfvrRIDB6F0bIO4I4HkQ/about
    - Parts of the Miguel Grinberg Flask Tutorial
  
 

  
  
