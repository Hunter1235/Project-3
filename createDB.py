# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 16:12:21 2021
This script creates an initial database for use by the CVS 
COVID Notification app
If the database is recreated, the app will take nearly 2 minutes run for the
first time. Getting the latitude and longitude takes about 0.5 seconds and
there are a lot of locations that will need to be added to the database.
@author: Hunter Stiles
"""

import sqlite3

con = sqlite3.connect('CVS_COVID.db')
cur = con.cursor()

#create the Users table
cur.execute('DROP TABLE IF EXISTS Users');
cur.execute('CREATE TABLE Users (Name text, Number text, EmailAddr text,\
    StreetAdr text, City text, State text, Latitude float, Longitude float,\
    Distance float, Call bit, Text bit, Email bit )')
users = [('Hunter Stiles', '9085553914', 'stileshu@kean.edu', '167 Anderson Road',\
          'Watchung', 'NJ',  40.62438810, -74.46165232, 20.0, 1, 1, 1 )]
   
cur.executemany('INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', users)

#create the CVSLocations table
cur.execute('DROP TABLE IF EXISTS CVSLocations');
cur.execute('CREATE TABLE CVSLocations (City text, Status text,\
    Latitude float, Longitude float)')
locations = [('union, NJ', 'Fully Booked', 40.6976019, -74.2632024),
             ('atlantic city, NJ', 'Available', 39.3642852, -74.4229351)
             ]

cur.executemany('INSERT INTO CVSLocations VALUES (?,?,?,?)', locations)

con.commit()

#print out data to be sure that it is there 
for row in cur.execute('SELECT * FROM Users ORDER BY name'):
    print(row)
    
for row in cur.execute('SELECT * FROM CVSLocations ORDER BY city'):
    print(row)
    
cur.close()
con.close()
