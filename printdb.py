# -*- coding: utf-8 -*-
"""
This is a untility that I used to print out the contents of the databases
so that I can verify the correct operation of the app

@author: Hunter Stiles
"""

import sqlite3

con = sqlite3.connect('CVS_COVID.db')
cur = con.cursor()



#print out data to be sure that it is there 
print("Users:")
for row in cur.execute('SELECT * FROM Users ORDER BY name'):
    print(row)
print("--------------------------------")
print("CVS Locations:")
for row in cur.execute('SELECT * FROM CVSLocations ORDER BY city'):
    print(row)
    
cur.close()
con.close()

