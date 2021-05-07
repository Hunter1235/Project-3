Author Hunter Stiles 2021

Application
This application will scan the CVS website for locations in New Jersey
that have vaccine appointments available. When new appointments become
available, it will be recorded in a database. Then, if the newly recorded
availability is at a location that is within a specified radius of the
user's location, it will notify them by text message, phone call, and/or
email. The user will be able to choose to be notified in any combination
of these 3 ways.

Files
admin.py -- This application provides a graphical interface to add, delete and modify
users in the CVS_COVID database.  The main application window consists of 
three buttons,  One to start the add user window, the next to start the
modify/delete user window and the last to exit the application.

CovidApp.py -- This server will scan the CVS website for locations in New Jersey
that have vaccine appointments available. When new appointments become
available, it will be recorded in a database. Then, if the newly recorded
availability is at a location that is within a specified radius of the
user's location, it will notify them by text message, phone call, and/or
email. The user will be able to choose to be notified in any combination
of these 3 ways. The server will scan the site once a day unless the environmental
variable CVSAPP_PERIOD is set.  See environmental variables below for
more details. The app needs to have valid twilio and gmail credentials

createDB.py -- This script creates an initial database for use by the CVS 
COVID Notification app. If the database is recreated, the app will take nearly
two minutes run for the first time. Getting the latitude and longitude takes
about 0.5 seconds and there are a lot of locations that will need to be added
to the database.

printdb.py -- This is a utility that I used to print out the contents of the databases
so that I can verify the correct operation of the app

modifydb.py -- To test or demo the software it is not realistic to wait for CVS to change the
availity for their locations, so  we wrote this script to modify the database.
One city is deleted from the database so that the app can discover a city that 
isn't in the database.  Two have their status set to "Fully Booked" so the 
app will recognized them as locations with new availability.  Atlantc City is
much further away so that their will be a city outside to the users search
raduis (assuming they live near Kean University ;) )

CVS_COVID.db -- an SQL database that is populated with the locations currently on the 
CVS site.  

CVS_status.html -- a saved copy other html table of CVS locations in New Jersey and there
status at the time this file was created.  I used it for testing.  For testing, you might
consider uncommenting the code that reads this file in CovidApp.py and commenting out the
selenium stuff.  Just search for CVS_status.html in the file to find it.  Making this change
will stop you from unnecessarily pounding on the CVS website, or perhaps your trying to get
this to work long after that web page has disappered.


Libraries
the application requires the following libraries
twilio, selenium, geopy, smtplib, pandas, tkinter, sqlite3, os, logging and time
For the application to use selenium it also requires that Google Chrome is
installed along with the webdriver from Chome.  The selenium server is not needed.
More information can be found here 
https://selenium-python.readthedocs.io/installation.html


Environmental Variables

to configure the application you can set the following 

CVSAPP_GMAIL_ID -- the gmail id for sending emails.  Note the 
gmail account must be configured to allow less secure apps to 
send mail. See https://support.google.com/accounts/answer/6010255?hl=en#zippy=
for details.

CVSAPP_GMAIL_PASSWORD  -- the password to the gmail account

CVSAPP_LOG_LEVEL -- the logging level for the logger
the standard levels are NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL

CVSAPP_PERIOD  -- the amount of time to wait before accessing the CVS website
again in seconds

TWILIO_ACCOUNT_SID -- your Twilio Account SID --trial accounts can be created
for free, but come with significant restrictions. see
https://support.twilio.com/hc/en-us/articles/223136107-How-does-Twilio-s-Free-Trial-work-
for details

TWILIO_ACCOUNT_TOKEN  -- your Twilio Account token

