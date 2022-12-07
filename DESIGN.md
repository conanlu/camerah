# CAMERAH PROJECT DESIGN:

This project utilizes a python file (app.py) that manages various .html pages (stored in the templates folder). It is adapted from the finance PSET and as such utilizes several helper methods from the CS50 staff. The layout of this project is such that photos are stored in the static folder (with icons imbedded into the app in the icons folder and all user-uploaded photos in the photos folder). The .html files are all contained in the templates folder, and all other important files (.css, .py, .db, .md are stored in the main CAMERAH directory) In this document, I will walk through the design of each .html file, as well as the various function and helpers relevant to each.

# SQL DATABASE
To preface, I will explain the SQL database, laid out in schema.sql. The database has a table for users, which stores a unique id, a username, and a hashed password to protect the user's data. There is also a photos table, which contains the id for the photo, the name of each photo, the number of upvotes of each photo, the datetime of the photo, and a foreign key relating the photo to the user who posted it. Through this, the photo is connected to the user who posted it and tracks how many likes it receives. The likes table serves to hold each individual "like" as an object connectinf the user to the photo they liked. This makes it easy in the index function to check which photos the user has and hasn't liked. 

*** Because this project has an element of time dependency, I've retroactively added sample uploads into the SQL database and the photos folder to demonstrate what the site would look like for a user who has been using it for several days ***

# LAYOUT.HTML
Now I will iterate through the .html files beginning with layout.html. This page utilizes JINJA to provide a layout format for all other .html pages. The layout.html file creates a navbar at the top of the page, which has a home button, an upload button, a collage button, and a logout button (or a register/login button if the user is not yet signed in). The layout.html file also specifies how flash alerts are displayed, which is utilized in the functions checking if the user has or hasn't uploaded.

# INDEX.HTML
Continuing on to index.html, the main page: In app.py, the index() funtion allows a user to either GET (load the page) or POST (like a photo) in /index. To do either, the user must be logged in and have uploaded for the day already. The checkUploaded() function in app.py achieves this by searching the database for photos the user has uploaded during the current day with an SQL query. If the query returns no results, we can assume the user has not uploaded yet. Assuming they have done these, if the user attempts to GET from the page, the python file will get necessary information from the SQL database (including all photos posted today (ordered by number of likes, from most to least) and their number of upvotes, and all of those photos that the user has liked), sending them to index.html. In the index.html file, the program takes this information and displays all photos posted today, with a "like" button (which is an animated gif of a heart!) present only below photos not yet liked by the user. If the user attempts to POST to the page, this means they have clicked one of the "like" buttons. The like buttons in the index page are named after the photos they are associated with, allowing the python file to directly associate the button clicked with the photo liked. The file then updates the photos and likes sql databases, and reloads the index page.

# UPLOAD.HTML
Moving on to the upload.html file: In app.py, the upload() function allows a user to either GET (load the page) or POST (upload a photo) in /upload. In order to do either, the user has to be logged in and have NOT uploaded for that day already. The function new_upload_required redirects users to "index" if they try to access "upload" and the SQL query reveals that the user has already uploaded an image that day. Assuming this is true, if the user tries to GET from the page, the python file will load the upload template. The upload.html file is relatively simple. It utilizes a file input to allow a user to select an image file from their device. Because the input is specified as accept="image/*", the user will not be permitted to upload any files that won't load properly on the page. If the user tries to POST to the page by uploading an image, the app.py file will save the image and add it to the photos database, only after replacing all spaces in the image name with underscores. Allowing spaces in an image name creates issues with routing, but creating errors on the users side for these issues is much less user-friendly than just handling them on the server's side. Thus, by replacing all spaces with underscores we solve that issue without ever burening the user. Once this is done, we check redirect the user back to the index page.

# LOGIN.HTML
Now to explain the login.html file: In app.py, the login() function allows a user to either GET (load the page) or POST (attempt to login to an account) in /login. The login function first clears any current session or user_id in order to allow the user to properly sign into a fresh account. Then, if the user is trying to GET (load) the page, it will simply render the login.html template, which is a simple .html file with two fields (username and password), and a submit button. If the user is attempting to POST to the page, app.py will check that the user has sumbitted a username, submitted a password, and that those match a username and password already stored in the users database. If so, it will create a new session for that user and redirect them to the home page.

# REGISTER.HTML
Now to look at the register.html file: In app.py, the register() function allows a user to either GET (load the page) or POST (attempt to register for an account) in /register. If the user tries to GET the page, reigster() will simply load the register.html template which has 3 fields (username, password, confirm password). If the user attempts to POST, app.py will check that the username, password, and confirmation fields are all filled out and valid. If they are the user is added to the users database and redirected to the login screen.

# COLLAGE.HTML, NOCOLLAGE.HTML
The collage.html file is rendered when the user clicks the "collage" button in the navbar (this function only accepts GET parameters because there are no interactive buttons or fields on the collage page). This page will [EXPLAIN COLLAGE.HTML]. The nocollage.html file is called in the event that the user clicks the "collage" button but there have not yet been any photos uploaded by the user. It just displays a message telling the user to return later to see a completed collage.

# APOLOGY.HTML
The apology.html file is called in the event that the user attempts to do anything that might break the server (such as trying to log in without a username or submit an upload without selecting a photo). It was also modified to fit the theme of the website!

# LOGOUT.HTML
The logout() function in app.py just clears the user's session and redirects them to the home page which takes them back to login.

# STYLESHEET.CSS
The stylesheet.css File primarily focuses on formatting including colors, sizes, fonts, and centering images in the index page.

[EXPLAIN CHECK UPLOADED FUNCTION]

checkUploaded, a utility function in app.py, essentially queries the photos table with SQL and returns all photos a user has uploaded. Then, the query extracts the dates of all these photos and evaluates whether any of them were posted on the current day, which was achieved via datetime. If there is one, we can say that the. So the session variable for "uploaded" is set to True. By default, every time checkUpload() is called, it returns false.

[EXPLAIN GET TODAY FUNCTION]

[EXPLAIN CROP FUNCTION]