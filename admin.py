# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 14:45:24 2021
This application provides a graphical interface to add, delete and modify
users in the CVS_COVID database.  The main application window consists of 
three buttons,  One to start the add user window, the next to start the
modify/delete user window and the last to exit the application.

@author: Hunter Stiles
"""

import tkinter as tk
from tkinter import ttk
from tkinter import IntVar
import sqlite3
import pandas as pd
import logging
import os
from geopy.geocoders import Nominatim

try:
    logLevel = os.environ['MESSAGE_LOG_LEVEL']
except:
    logLevel = logging.DEBUG
 
#start the logger
logging.basicConfig(format='%(asctime)s %(message)s',  datefmt='%I:%M:%S %p')
logging.getLogger().setLevel(logLevel)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler = logging.FileHandler('messagelog.txt')
filehandler.setFormatter(formatter)
logging.getLogger().addHandler(filehandler)


logging.warning('CVS COVID Notification app started.')
con = sqlite3.connect('CVS_COVID.db')
cur = con.cursor()

#pressing the delete/modify user button in the main app window will 
#call this function
def button_Change():
            
    call = IntVar()
    text = IntVar()
    email = IntVar()
    
    #pressing the delete button will delete the user from the database
    def buttonDelete():
        logging.debug("pressed delete in modify/delete user window")
        name = comboBoxName.get()
        #if they didn't select a user to delete, display and error message
        if not name:
            tk.messagebox.showerror("Must select name",
                "You must select a name to delete from drop the down menu")
            windowChange.focus_force()
            return
        # now delete the user
        cur.execute('DELETE from Users WHERE Name = "%s"' % name)
        con.commit()
        # display message saying the user was deleted
        tk.messagebox.showinfo("Delete", "Deleted " + name + " from system")
        #close the window. focus will return to the main app window
        windowChange.destroy()
        
        
    def buttonUpdate():
        logging.debug("pressed update in add user window")
        name = comboBoxName.get()
        if not name:
            tk.messagebox.showerror("Must select name",
                "Select user from drop down menu and modify it before selecting update")
            windowChange.focus_force()
            return
        
        address = entryAddress.get()
        city = entryCity.get()
        state = entryState.get()
        home= address + ' ' + city + ", " + state
        loc = Nominatim(user_agent="GetLoc")

        homeLoc = loc.geocode(home)
        user = (entryNumber.get(), entryEmailAddr.get(),
               address, city, state, homeLoc.latitude, homeLoc. longitude,
               enteryDistance.get(), call.get(), text.get(), email.get(), name)
        cur.execute('UPDATE USERS SET Number = ?, EmailAddr = ?, StreetAdr = ?,\
                City = ?, State = ?, Latitude = ?, Longitude = ?, Distance = ?,\
                Call = ?, Text = ?, Email= ? WHERE Name = ?', user)
        con.commit()
        logging.info("Updated " + name + " in the database")
        tk.messagebox.showinfo("Updated", "Updated " + name + " in the system")
        windowChange.destroy()
    logging.debug("pressed add User")
    
    # namechanged() is call when the user selects a name from the name combobox.
    # it populates all the other fields in the wind with the users's data
    def nameChanged(event):
        #get the user's name from the combobox
        name=comboBoxName.get()
        #get the users data from the database
        users = pd.read_sql_query('SELECT * FROM Users WHERE Name = "%s"' %  name, con)
        
        #now populate the input fields with the data
        entryAddress.delete(0, 'end')
        entryAddress.insert(0, users.at[0, 'StreetAdr'])
        entryCity.delete(0, 'end')
        entryCity.insert(0, users.at[0, 'City'])
        enteryDistance.delete(0, 'end')
        enteryDistance.insert(0, users.at[0, 'Distance'])
        entryNumber.delete(0, 'end')
        entryNumber.insert(0, users.at[0, 'Number'])
        entryEmailAddr.delete(0, 'end')
        entryEmailAddr.insert(0, users.at[0, 'EmailAddr'])
        if users.at[0, 'Text']:
            checkboxText.select()
        else:
            checkboxText.deselect()
        if users.at[0, 'Call']:
            checkboxCall.select()
        else:
            checkboxCall.deselect()
        if users.at[0, 'Email']:
            checkboxEmail.select()
        else:
            checkboxEmail.deselect()
        
        print(df)
        print('new name selected')
    
    #create the window to display user data
    windowChange = tk.Toplevel(root)
    windowChange.geometry('500x400')
    windowChange.title('Delete/Modify User')
    
    #each frame gets it's own row in the grid, This frame is for the user name
    frameName = tk.Frame(windowChange)
    frameName.grid(row=0, sticky='w')
    labelName = tk.Label(frameName, text='  Name:  ')
    df = pd.read_sql_query("SELECT Name FROM Users ORDER BY name", con)
    logging.debug(df)
    comboBoxName = ttk.Combobox(frameName, values=df['Name'].tolist())
    comboBoxName.bind("<<ComboboxSelected>>", nameChanged)
    labelName.pack(pady = 10, side = 'left')
    comboBoxName.pack(side = 'left')
    
    #frame to hold the street address.
    frameAddress = tk.Frame(windowChange)
    frameAddress.grid(row=1, sticky='w')
    labelAddress = tk.Label(frameAddress, text='  Address:  ')
    entryAddress = tk.Entry(frameAddress, width = 45)
    labelAddress.pack(pady = 10, side = 'left')
    entryAddress.pack(side = 'left')

    #frame for the city and state.  For now this app only works for NJ
    #so the state is prepopulated and read-only
    frameCityState = tk.Frame(windowChange)
    frameCityState.grid(row=2, sticky='w')
    labelCity = tk.Label(frameCityState, text='  City:  ')
    entryCity = tk.Entry(frameCityState, width = 30)
    labelState = tk.Label(frameCityState, text='             State:  ')
    entryState = tk.Entry(frameCityState, width = 2)
    entryState.insert(0, 'NJ')
    entryState.config(state='disabled')
    labelCity.pack(pady = 10, side = 'left')
    entryCity.pack(side = 'left')
    labelState.pack(side = 'left')
    entryState.pack(side = 'left')

    #frame contains the search distance(radius) in miles
    frameDistance  = tk.Frame(windowChange)
    frameDistance.grid(row=3, sticky='w')
    labelDistance = tk.Label(frameDistance, text='  Search radius (miles):  ')
    enteryDistance = tk.Entry(frameDistance, width = 4)
    enteryDistance.insert(0, '20')
    labelDistance.pack(pady = 10, side = 'left')
    enteryDistance.pack(side = 'left')
    
    #frame for users phone number
    frameNumber  = tk.Frame(windowChange)
    frameNumber.grid(row=4, sticky='w')
    labelNumber = tk.Label(frameNumber, text='  Phone Number:  ')
    entryNumber = tk.Entry(frameNumber, width = 15)
    labelNumber.pack(pady = 10, side = 'left')
    entryNumber.pack(side = 'left')
    
    #frame for users email
    frameEmail  = tk.Frame(windowChange)
    frameEmail.grid(row=5, sticky='w')
    labelEmailAddr = tk.Label(frameEmail, text='  Email:  ')
    entryEmailAddr = tk.Entry(frameEmail, width = 30)
    labelEmailAddr.pack(pady = 10, side = 'left')
    entryEmailAddr.pack(side = 'left')
    
    #frame for the user's contact preference (text, phone call or email)
    frameCheckbox  = tk.Frame(windowChange)
    frameCheckbox.grid(row=6, sticky='w')
    lablelPref = tk.Label(frameCheckbox, text='  Contact Perference:  ')
    checkboxText = tk.Checkbutton(frameCheckbox, variable = text, text='Text')
    checkboxCall = tk.Checkbutton(frameCheckbox, variable = call, text='Call')
    checkboxEmail = tk.Checkbutton(frameCheckbox, variable = email, text='Email')
    lablelPref.pack(side = 'left')
    checkboxText.pack(pady = 10, side = 'left')
    checkboxCall.pack(padx = 5, side = 'left')
    checkboxEmail.pack(side = 'left')
    
    #frame for the update, delete  and cancel buttons
    frameButtons = tk.Frame(windowChange)
    frameButtons.grid(row=7)
    buttonSubmit = tk.Button(frameButtons, text='Update', command=buttonUpdate)
    buttonSubmit.grid(row = 1, column = 1)
    buttonCancel = tk.Button(frameButtons, text='Delete', command=buttonDelete)
    buttonCancel.grid(row = 1, column = 2)
    buttonCancel = tk.Button(frameButtons, text='Cancel', command=windowChange.destroy)
    buttonCancel.grid(row = 1, column = 3)
 
# The add button creates the window for adding a user.
def button_Add():
    call = IntVar()
    text = IntVar()
    email = IntVar()
    def button_submit():
        logging.debug("pressed submit in add user window")
        name = entryName.get()
        address = entryAddress.get()
        city = entryCity.get()
        state = entryState.get()
        home= address + ' ' + city + ", " + state
        loc = Nominatim(user_agent="GetLoc")

        homeLoc = loc.geocode(home)
        user = (name, entryNumber.get(), entryEmailAddr.get(),
               address, city, state, homeLoc.latitude, homeLoc. longitude,
               enteryDistance.get(), call.get(), text.get(), email.get())
        cur.execute('INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', user)
        con.commit()
        logging.info("added " + name + "to the directory")
        tk.messagebox.showinfo("Added", "Added " + name + " to system")
        windowAddUser.destroy()
    logging.debug("pressed add User")

    #create the window to input user data
    windowAddUser = tk.Toplevel(root)
    windowAddUser.geometry('500x400')
    windowAddUser.title('Add User')
    
    #each frame gets it's own row in the grid, This frame is for the user name
    frameName = tk.Frame(windowAddUser)
    frameName.grid(row=0, sticky='w')
    labelName = tk.Label(frameName, text='  Name:  ')
    entryName = tk.Entry(frameName, width = 30)
    labelName.pack(pady = 10, side = 'left')
    entryName.pack(side = 'left')
    
    #frame to hold the street address.  If left empty, the program still
    #works, however the geolocation is less accurate.  Uses the town
    #instead of the exact address.  Entering just the street is also OK
    frameAddress = tk.Frame(windowAddUser)
    frameAddress.grid(row=1, sticky='w')
    labelAddress = tk.Label(frameAddress, text='  Address:  ')
    entryAddress = tk.Entry(frameAddress, width = 45)
    labelAddress.pack(pady = 10, side = 'left')
    entryAddress.pack(side = 'left')

    #frame for the city and state.  For now this app only works for NJ
    #so the state is prepopulated and read-only
    frameCityState = tk.Frame(windowAddUser)
    frameCityState.grid(row=2, sticky='w')
    labelCity = tk.Label(frameCityState, text='  City:  ')
    entryCity = tk.Entry(frameCityState, width = 30)
    labelState = tk.Label(frameCityState, text='             State:  ')
    entryState = tk.Entry(frameCityState, width = 2)
    entryState.insert(0, 'NJ')
    entryState.config(state='disabled')
    labelCity.pack(pady = 10, side = 'left')
    entryCity.pack(side = 'left')
    labelState.pack(side = 'left')
    entryState.pack(side = 'left')
    
    #frame contains the search distance(radius) in miles
    frameDistance  = tk.Frame(windowAddUser)
    frameDistance.grid(row=3, sticky='w')
    labelDistance = tk.Label(frameDistance, text='  Search radius (miles):  ')
    enteryDistance = tk.Entry(frameDistance, width = 4)
    enteryDistance.insert(0, '20')
    labelDistance.pack(pady = 10, side = 'left')
    enteryDistance.pack(side = 'left')
    
    #frame for users phone number
    frameNumber  = tk.Frame(windowAddUser)
    frameNumber.grid(row=4, sticky='w')
    labelNumber = tk.Label(frameNumber, text='  Phone Number:  ')
    entryNumber = tk.Entry(frameNumber, width = 15)
    labelNumber.pack(pady = 10, side = 'left')
    entryNumber.pack(side = 'left')
    
    #frame for users email
    frameEmail  = tk.Frame(windowAddUser)
    frameEmail.grid(row=5, sticky='w')
    labelEmailAddr = tk.Label(frameEmail, text='  Email:  ')
    entryEmailAddr = tk.Entry(frameEmail, width = 30)
    labelEmailAddr.pack(pady = 10, side = 'left')
    entryEmailAddr.pack(side = 'left')
    
    #frame to record user's contact preference (text, phone call or email)
    frameCheckbox  = tk.Frame(windowAddUser)
    frameCheckbox.grid(row=6, sticky='w')
    lablelPref = tk.Label(frameCheckbox, text='  Contact Perference:  ')
    checkboxText = tk.Checkbutton(frameCheckbox, variable = text, text='Text')
    checkboxCall = tk.Checkbutton(frameCheckbox, variable = call, text='Call')
    checkboxEmail = tk.Checkbutton(frameCheckbox, variable = email, text='Email')
    lablelPref.pack(side = 'left')
    checkboxText.pack(pady = 10, side = 'left')
    checkboxCall.pack(padx = 5, side = 'left')
    checkboxEmail.pack(side = 'left')

    #frame for the submit and cancel buttons
    frameButtons = tk.Frame(windowAddUser)
    frameButtons.grid(row=7)
    buttonSubmit = tk.Button(frameButtons, text='Submit', command=button_submit)
    buttonSubmit.grid(row = 1, column = 1)
    buttonCancel = tk.Button(frameButtons, text='Cancel', command=windowAddUser.destroy)
    buttonCancel.grid(row = 1, column = 2)

# mail application window
root = tk.Tk()
root.option_add('*Font', '18')
root.title("COVID Vaccine Notification System")
root.geometry("350x200")

#this frame contains three buttons. One opens the "Add User" window.  The
#next opens the "Delete/Modify User window and the last exits the program.
frameButtons = tk.Frame(root)
frameButtons.pack()
buttonDir = tk.Button(frameButtons, text = "Add User", height = 3, 
                      width = 10, command = button_Add)
buttonDir.pack(side="left", pady = 50)
buttonConnect = tk.Button(frameButtons, text = "Delete/\nModify User",
                          height = 3, width = 10, command = button_Change)
buttonConnect.pack(side="left")
buttonSend = tk.Button(frameButtons, text = "Exit", height = 3,
                       width = 10, command = root.destroy)
buttonSend.pack(side="right")

root.mainloop()