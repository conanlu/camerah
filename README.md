# TECHNICAL SETUP GUIDE
To run this Flask app and make edits on your local machine, do the following. On a base level, this step requires Python 3 and Pip installed.

First, clone the repository to your local machine. Using HTTPS, the command would be as follows: 

git clone https://github.com/conanlu/camerah

For this project, we used virtual environments running Python 3.6 to install packages. These virtual environments can be created in a variety of ways. However, virtual environments are optional. Feel free to skip the next few steps.

We got the latest build of Miniconda (https://docs.conda.io/en/latest/miniconda.html), made sure conda was in our PATH, and ran this command in our Anaconda prompt terminal:

conda create -n py36 python=3.6

We then activated the virtual environment with:

conda activate py36

Regardless if you are in a virtual environment or not, navigate to the cloned directory on your terminal.

Once in your directory, install packages with this command.

pip install -r requirements.txt

Our requirements beyond Flask include OpenCV and Firebase (Firestore). However, after you install these packages, there is one last step before running.

Our Firebase Firestore database is used to load different locations that update daily. It requires security credentials to access and modify, which, for obvious reasons, should not be shared on a public Github repository. If you have an email associated with Harvard, please get the credentials (.json) file with this link:

https://drive.google.com/file/d/1h1W6EkXfd0kh40FPl8q5zFHqwZGFbUU8/view?usp=sharing

(If you are not associated with Harvard and grading this project, please contact for access.) 

Once the .json file is downloaded, place it in the camerah folder. If you are not putting it in the camerah folder, replace the PATH in Line 94 of app.py with your new location. 

With these steps completed, you should be able to run this app on your local machine with:

flask run

# LINK

https://youtu.be/kfleK4UZwKk