"""
CVS COVID Notification app
This application will scan the CVS website for locations in New Jersey
that have vaccine appointments available. When new appointments become
available, it will be recorded in a database. Then, if the newly recorded
availability is at a location that is within a specified radius of the
user's location, it will notify them by text message, phone call, and/or
email. The user will be able to choose to be notified in any combination
of these 3 ways.'    

@author: Hunter Stiles
"""
import smtplib
import pandas as pd
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from twilio.rest import Client
from selenium import webdriver
import os
import logging
import time

#call calls the user's 
def call(messageVoice, number):
    logging.debug("pressed Send Voice in send popup window")

    logging.debug("sending voice message to " + number  )
    client.calls.create(
        twiml='<Response><Say>' + messageVoice + '</Say></Response>',
        to=number,
        from_='+19085554077'
        )
    logging.info("sent the following text to " + number)
    logging.info(messageVoice)
    
#sentText send a text to the user's phone number
def sendText(messageText, number):
    logging.debug("pressed Send Text in send popup window")
    logging.debug("sending text to " + number  )
    client.messages \
        .create(
            body=messageText,
            to=number,
            from_='+19085554077'
            )
    logging.info("sent the following text to " + number)
    logging.info(messageText)
            
#sendEmail sends an email to the users email address 
def sendEmail(messageEmail, address):
    subject = "Availabile Vaccine Appointments"
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(gmail_id, gmail_password)
    message = f"Subject: {subject}\n\n{messageEmail}"
    smtp_server.sendmail(gmail_id, address, message)
    smtp_server.close()
    logging.info("sent the following email to " + address)
    logging.info(messageEmail)
  

#constructs the message to be sent to the user.  Message may be different for
#each user since locations maybe within only some of the user's search radii
def constructMessage(NotifyUser):
    message = "New CVS appointments are available at these locations "
    cities = NotifyUser['City']
    first = True
    for city in cities:
        if not first:
            message += (", ")
        message += (city.split(',')[0])
        first =False
    print(message)
    return (message)

#NotifyUsers uses the functions call, sendText and sendEmail to notify
#users of newly avaiable appointments, per their contact preferences
def NotifyUsers(Notify):

    if Notify.empty:
        return
    Users = pd.read_sql_query("SELECT * FROM Users", con)
    print(Users)
    for i in Users.index:
        Home = (Users.at[i, 'Latitude'], Users.at[i, 'Longitude'])
        for j in Notify.index:
            Store = (Notify.at[j, 'Latitude'], Notify.at[j, 'Longitude'])
            Notify.at[j, 'Distance'] = geodesic(Home, Store).miles
            
        #limit notifications to store withing the user's desired radius
        NotifyUser = Notify[Notify['Distance'] < Users.at[i, 'Distance']].sort_values(by=['Distance'])

        message = constructMessage(NotifyUser)
        if Users.at[i, 'Call']:
            call(message, Users.at[i, 'Number'])
        if Users.at[i, 'Text']:
            sendText(message, Users.at[i, 'Number'])
        if Users.at[i, 'Email']:
            sendEmail(message, Users.at[i, 'EmailAddr'])


# InsertNewLocs inserts the newly discovered locations into the database
def InsertNewLocs(NewLocs):
    if  NewLocs.empty:
        return
    #set the latitude and longitude for each new city
    #each call to Get_Loc takes about 0.5 seconds
    for i in NewLocs.index:
        NewLocs.at[i, 'Latitude'], NewLocs.at[i, 'Longitude'] = Get_loc(NewLocs.at[i, 'City'])
    
    InsertData = list(NewLocs.itertuples(index=False, name=None))
    logging.info("Adding the following locations to the database:")
    logging.info(InsertData)
    cur.executemany('INSERT INTO CVSLocations VALUES (?,?,?,?)', InsertData)

  
#UpdateStatusDB updates the status for cities in StatusChange
def UpdateStatusDB(StatusChange):
    if  StatusChange.empty:
        return
    #for SQL UPDATE Statement we need only Status first followed by City
    StatusCity = StatusChange[['Status', 'City']]
    UpdateData = list(StatusCity.itertuples(index=False, name=None))
    logging.info("Updating the following Status in the database:")
    logging.info(UpdateData)
    cur.executemany('UPDATE CVSLocations SET Status = ? WHERE City = ?', UpdateData) 
    
#GetModifiedLocations gets the list of cities from the CVS that are either not
#already in the database or the status has changed since the last scan
def GetModifiedLocations():
    
    #get the webdriver for Chrome
    driver = webdriver.Chrome()
    #COVID should be in the title if the page is there
    driver.get('https://www.cvs.com/immunizations/covid-19-vaccine')
    assert 'COVID' in driver.title

    #select New Jersey
    driver.find_element_by_xpath('//*[@id="selectstate"]/option[31]').click()
    
    #click the get started button
    driver.find_element_by_xpath('//*[@id="stateform"]/div[2]/button').click() 
    
    #get the html for the table contain cities and status
    cities=driver.find_element_by_xpath('/html/body/div[2]/div/div[19]/div/div\
        /div/div/div/div[1]/div[2]/div/div/div[2]/div/div[6]/div/div/table').\
        get_attribute('outerHTML')
    
    #put the cities and status into a dataframe.
    StatusWeb  = pd.read_html(cities)
    
    #for testing uncomment the following 2 lines and comment out the selenium
    #stuff so we don't pound on CVS website unessarilly
    #read_html returns al list of dataframes, it this case only one dataframe.
    #so we keep the dataframe instead of a list containing the dataframe.
    #CVSstatus = open('CVS_Status.html','r')
    #StatusWeb  = pd.read_html(CVSstatus.read())[0]
    
    #change City/Town to City to match database
    StatusWeb.rename(columns = {'City/Town' : 'City'}, inplace = True)
    
    StatusDB = pd.read_sql_query("SELECT * FROM CVSLocations", con)
    
    # Merge the list from the web and Database, and keep only those where the 
    # Status is different. Note this includes all locations not already in
    # the database as their status was Null.
    ModifiedLocs = StatusWeb.merge(StatusDB, right_on='City', left_on='City', how='outer')
    ModifiedLocs = ModifiedLocs[ModifiedLocs.Status_x != ModifiedLocs.Status_y]
    ModifiedLocs .drop('Status_y', inplace=True, axis=1)
    ModifiedLocs.rename(columns={'Status_x':'Status'}, inplace=True)
    driver.quit()
    return ModifiedLocs
    
#get the latitude and longitude for the location.  Each call takes about 0.5
#seconds.   If the database is newly created the app will call this for every
#CVS location in the state, which takes a little under 2 minutes.
def Get_loc(City):
    Location= loc.geocode(City);
    return(Location.latitude, Location.longitude)



#set the reporting level for the logger
try:
    gmail_id = os.environ['CVSAPP_GMAIL_ID']
except:
    logging.warning("Unable to get gmail_id from environment")
    gmail_id = "AGmailID"
    
try:
    gmail_password = os.environ['CVSAPP_GMAIL_PASSWORD']
except:
    logging.warning("Unable to get gmail_password from environment")
    gmail_password = "YourPassword"
    
try:
    logLevel = os.environ['CVSAPP_LOG_LEVEL']
except:
    logLevel = logging.DEBUG

#the default period to visit the CV website is 1 day to avoid beating on the 
#website.  For testing or demo purpose just stop and start the server
try:
    logLevel = os.environ['CVSAPP_PERIOD']
except:
    period = 86400
  
#Create the SMS/Phone call Client
try:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
except:
    logging.warning("Unable to get twilio account_sid from environment")
    account_sid = 'a valid twilo sid'

try:
    account_sid = os.environ['TWILIO_ACCOUNT_TOKEN']
except:
    logging.warning("Unable to get twilio auth_token from environment")
    auth_token = 'a valid twilio token'
    
while(True):
    client = Client(account_sid, auth_token)
    
    #Get the user agent for obtain latitude and Longitude and distance between cities
    loc = Nominatim(user_agent="GetLoc")
    
    #open a connection to the database
    con = sqlite3.connect('CVS_COVID.db')
    cur = con.cursor()
    
    #Get new locations and ones that have different status from last web scan.
    ModifiedLocs = GetModifiedLocations()
    
    #Get locations not already in database, i.e.  Latitude == NaN
    NewLocs = ModifiedLocs[pd.isna(ModifiedLocs.Latitude)]
    
    # Now remove the new locations leaving those with a status change.
    StatusChange =  ModifiedLocs[pd.notna(ModifiedLocs.Latitude)]
    
    #for testing uncomment the following line so that
    #don't pound on the geolocation service.   It makes it 
    #so only hillside and hillsbourough can be found.
    ##NewLocs = NewLocs[NewLocs.City.str.match('hil')]
    
    #put newly discover locations it the database.
    InsertNewLocs(NewLocs)   
    
    #Need to notify users of Locations that were Fully Booked but now are Avaiable
    Notify = StatusChange[StatusChange.Status.isin(['Available'])]
    
    #also need to notify user of new locations that are available
    Notify = Notify.append(NewLocs[NewLocs.Status.isin(['Available'])])
    
    NotifyUsers(Notify)
    
    #update the status for locations in the database
    UpdateStatusDB(StatusChange)
    
    con.commit()
    cur.close()
    con.close()

    
    time.sleep(period)